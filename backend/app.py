import os
import io
import time
import logging
import numpy as np
import onnxruntime as ort
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from pydantic import BaseModel
from PIL import Image
from transformers import AutoImageProcessor, AutoConfig
from llama_cpp import Llama
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
import threading
import shutil

# --- CUSTOM MODULES ---
# Uses the lightweight guard_utils.py we created
from guard_utils import get_llm_guard

load_dotenv()

# Fix for ChromaDB on some systems (SQLite version mismatch)
try:
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

app = FastAPI(title="Flora-Bot API")

# --- PROMETHEUS INSTRUMENTATION ---
# Instrument the app but do NOT expose /metrics automatically
# We handle /metrics manually below to update system stats before scraping
Instrumentator().instrument(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. CUSTOM METRICS (Optional but good) ---
# Latency Trackers
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Total endpoint latency")
CV_LATENCY = Histogram("cv_inference_latency_seconds", "CV model inference time")
LLM_LATENCY = Histogram("llm_inference_latency_seconds", "LLM generation time")
GUARD_LATENCY = Histogram("guard_latency_seconds", "Guardrails validation time")

# Counters
REQUEST_COUNT = Counter(
    "app_requests_total", "Total requests processed", ["endpoint", "status"]
)
GUARD_FAILURES = Counter(
    "guard_failures_total", "Guardrail violations", ["violation_type", "source"]
)
LLM_TOKEN_USAGE = Counter("llm_token_usage_total", "Total LLM tokens used", ["type"])

# Gauges (System)
THREAD_COUNT = Gauge("system_active_threads", "Number of active threads")
DISK_USAGE = Gauge("system_disk_usage_percent", "System Disk Usage Percentage")

# --- CONFIGURATION ---
MODEL_DIR = os.getenv("MODEL_DIR", "models")
ONNX_DIR = os.path.join(MODEL_DIR, "flora_cv_onnx")
RAG_DIR = os.path.join(MODEL_DIR, "flora_rag_db")
GGUF_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
GGUF_PATH = os.path.join(MODEL_DIR, GGUF_FILE)

# Global dictionary to hold loaded models
sys_comps = {}


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


def update_system_stats():
    try:
        # Thread Count (Concurrency)
        tc = threading.active_count()
        THREAD_COUNT.set(tc)

        # Disk Usage (Storage)
        total, used, free = shutil.disk_usage("/")
        disk_percent = (used / total) * 100
        DISK_USAGE.set(disk_percent)
    except Exception as e:
        logging.error(f"Error updating system stats: {e}")


@app.get("/metrics")
async def metrics():
    update_system_stats()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.on_event("startup")
async def startup_event():
    print("⚙️ Initializing System Components...")

    if os.getenv("SKIP_MODELS") == "true":
        print("⚠️ SKIP_MODELS is set. Skipping model loading for testing/canary.")
        return

    # 1. Load Computer Vision Model (Raw ONNX Runtime - No PyTorch)
    if os.path.exists(ONNX_DIR):
        print("🚀 Loading ONNX CV Model (Slim Mode)...")
        model_path = os.path.join(ONNX_DIR, "model.onnx")
        sys_comps["cv_sess"] = ort.InferenceSession(model_path)
        sys_comps["cv_proc"] = AutoImageProcessor.from_pretrained(ONNX_DIR)
        sys_comps["cv_config"] = AutoConfig.from_pretrained(ONNX_DIR)
    else:
        raise RuntimeError(
            f"❌ ONNX Model missing at {ONNX_DIR}. Please upload the converted model to S3."
        )

    # 2. Load RAG Database
    print("📚 Loading RAG Database...")
    embed_fn = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    sys_comps["rag"] = Chroma(persist_directory=RAG_DIR, embedding_function=embed_fn)

    # 3. Load LLM (GGUF)
    print(f"🧠 Loading GGUF LLM: {GGUF_FILE}...")
    if not os.path.exists(GGUF_PATH):
        raise RuntimeError(f"❌ GGUF Model missing at {GGUF_PATH}")

    sys_comps["llm"] = Llama(
        model_path=GGUF_PATH,
        n_ctx=2048,
        n_threads=4,
        verbose=False,
    )

    # 4. Load Guardrails (Lightweight)
    print("🛡️ Loading Guardrails...")
    try:
        sys_comps["guard"] = get_llm_guard()
        if sys_comps["guard"]:
            print("✅ Guardrails Active")
        else:
            print("⚠️ Guardrails initialized but returned None.")
    except Exception as e:
        print(f"⚠️ Guardrails Error: {e}")
        sys_comps["guard"] = None

    print("✅ API READY.")


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    start_time = time.time()
    endpoint = "/predict"

    try:
        # --- A. CV INFERENCE (Numpy/ONNX) ---
        cv_start = time.time()
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")

        # Preprocess (returns numpy array)
        inputs = sys_comps["cv_proc"](img, return_tensors="np")

        # Run Inference
        sess = sys_comps["cv_sess"]
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: inputs["pixel_values"]})
        logits = outputs[0][0]  # First batch item

        # Post-process (Numpy)
        probs = softmax(logits)
        pred_idx = np.argmax(probs)
        conf = probs[pred_idx]
        diagnosis = sys_comps["cv_config"].id2label[pred_idx]

        CV_LATENCY.observe(time.time() - cv_start)

        # --- B. RAG RETRIEVAL ---
        # Search for treatment info specific to the disease
        docs = sys_comps["rag"].similarity_search(query=f"{diagnosis} treatment", k=2)
        context_text = "\n".join([d.page_content[:500] for d in docs])

        # --- C. LLM GENERATION ---
        prompt = f"<|system|>\nYou are a plant disease expert.\n<|user|>\nContext: {context_text}\nQuestion: Explain {diagnosis} and how to treat it.\n<|assistant|>\n"

        llm_start = time.time()
        output = sys_comps["llm"](prompt, max_tokens=512, stop=["<|user|>"], echo=False)
        raw_response = output["choices"][0]["text"].strip()
        LLM_LATENCY.observe(time.time() - llm_start)

        # Record Token Usage
        if "usage" in output:
            LLM_TOKEN_USAGE.labels(type="prompt").inc(
                output["usage"].get("prompt_tokens", 0)
            )
            LLM_TOKEN_USAGE.labels(type="completion").inc(
                output["usage"].get("completion_tokens", 0)
            )

        # --- D. GUARDRAILS VALIDATION ---
        final_response = raw_response

        # Only validate the LLM output, not the diagnosis itself
        if sys_comps.get("guard"):
            guard_start = time.time()
            try:
                validated = sys_comps["guard"].validate(raw_response)
                if validated.validated_output:
                    final_response = validated.validated_output

            except ValueError as e:
                error_str = str(e)
                violation_type = "UNKNOWN"

                # Extract the category from our custom error message
                if "UNSAFE:" in error_str:
                    violation_type = error_str.split(":")[1]

                # Increment metric with specific label
                GUARD_FAILURES.labels(
                    violation_type=violation_type, source="model_output"
                ).inc()

                logging.warning(f"Guardrail triggered: {violation_type}")
                final_response = "I cannot answer that due to safety guidelines regarding content policies."

            except Exception:
                # Generic error fallback
                GUARD_FAILURES.labels(
                    violation_type="ERROR", source="model_output"
                ).inc()
                final_response = "I cannot answer that."
            finally:
                GUARD_LATENCY.observe(time.time() - guard_start)

        # Success Metric
        REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()
        REQUEST_LATENCY.observe(time.time() - start_time)

        return {
            "diagnosis": diagnosis,
            "confidence": f"{conf*100:.1f}%",
            "explanation": final_response,
            "chat_context": context_text,
        }

    except Exception as e:
        # Error Metric
        REQUEST_COUNT.labels(endpoint=endpoint, status="error").inc()
        logging.error(f"Prediction Error: {e}")
        return {"error": str(e)}


class ChatPayload(BaseModel):
    question: str
    context: str


@app.post("/chat")
async def chat(payload: ChatPayload):
    start_time = time.time()
    endpoint = "/chat"

    try:
        # --- 0. INPUT VALIDATION (Guardrails) ---
        # Check the user's question BEFORE sending to LLM
        if sys_comps.get("guard"):
            try:
                sys_comps["guard"].validate(payload.question)
            except ValueError as e:
                error_str = str(e)
                violation_type = "UNKNOWN"
                if "UNSAFE:" in error_str:
                    violation_type = error_str.split(":")[1]

                GUARD_FAILURES.labels(
                    violation_type=violation_type, source="user_input"
                ).inc()
                logging.warning(f"Guardrail blocked input: {e}")
                return {
                    "answer": "I cannot answer that question as it violates safety policies."
                }

        # --- LLM GENERATION ---
        prompt = f"<|system|>\nYou are a plant disease expert.\n<|user|>\nContext: {payload.context}\nQuestion: {payload.question}\n<|assistant|>\n"

        llm_start = time.time()
        output = sys_comps["llm"](prompt, max_tokens=512, stop=["<|user|>"], echo=False)
        raw_response = output["choices"][0]["text"].strip()
        LLM_LATENCY.observe(time.time() - llm_start)

        # Record Token Usage
        if "usage" in output:
            LLM_TOKEN_USAGE.labels(type="prompt").inc(
                output["usage"].get("prompt_tokens", 0)
            )
            LLM_TOKEN_USAGE.labels(type="completion").inc(
                output["usage"].get("completion_tokens", 0)
            )

        # --- GUARDRAILS VALIDATION ---
        final_response = raw_response

        if sys_comps.get("guard"):
            guard_start = time.time()
            try:
                validated = sys_comps["guard"].validate(raw_response)

                if hasattr(validated, "validated_output"):
                    final_response = validated.validated_output

            except Exception as e:
                # VIOLATION DETECTED
                error_str = str(e)
                violation_type = "UNKNOWN"
                if "UNSAFE:" in error_str:
                    violation_type = error_str.split(":")[1]

                GUARD_FAILURES.labels(
                    violation_type=violation_type, source="model_output"
                ).inc()
                logging.warning(f"Guardrail blocked chat: {e}")
                final_response = (
                    "I cannot answer that question as it violates safety policies."
                )
            finally:
                GUARD_LATENCY.observe(time.time() - guard_start)

        # Success Metric
        REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()
        REQUEST_LATENCY.observe(time.time() - start_time)

        return {"answer": final_response}

    except Exception as e:
        # Error Metric
        REQUEST_COUNT.labels(endpoint=endpoint, status="error").inc()
        logging.error(f"Chat Error: {e}")
        return {"error": str(e)}
