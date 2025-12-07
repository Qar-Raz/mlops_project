import os
import torch
import io
import time
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from pydantic import BaseModel
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
from optimum.onnxruntime import ORTModelForImageClassification
from llama_cpp import Llama
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from dotenv import load_dotenv

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. PROMETHEUS METRICS ---
# Latency Trackers
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Total endpoint latency")
CV_LATENCY = Histogram("cv_inference_latency_seconds", "CV model inference time")
LLM_LATENCY = Histogram("llm_inference_latency_seconds", "LLM generation time")
GUARD_LATENCY = Histogram("guard_latency_seconds", "Guardrails validation time")

# Counters
# Counters
REQUEST_COUNT = Counter("app_requests_total", "Total requests processed", ["endpoint", "status"])

# UPDATE THIS LINE: Add 'violation_type' label
GUARD_FAILURES = Counter("guard_failures_total", "Guardrail violations", ["violation_type"])
# --- CONFIGURATION ---
MODEL_DIR = os.getenv("MODEL_DIR", "models")
CV_DIR = os.path.join(MODEL_DIR, "flora_cv_model")
ONNX_DIR = os.path.join(MODEL_DIR, "flora_cv_onnx")
RAG_DIR = os.path.join(MODEL_DIR, "flora_rag_db")
GGUF_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
GGUF_PATH = os.path.join(MODEL_DIR, GGUF_FILE)

# Global dictionary to hold loaded models
sys_comps = {}

@app.on_event("startup")
async def startup_event():
    print("⚙️ Initializing System Components...")

    # 1. Load Computer Vision Model (Prioritize ONNX for speed)
    if os.path.exists(ONNX_DIR):
        print("🚀 Loading ONNX CV Model...")
        sys_comps["cv_model"] = ORTModelForImageClassification.from_pretrained(ONNX_DIR)
        sys_comps["cv_proc"] = AutoImageProcessor.from_pretrained(ONNX_DIR)
    elif os.path.exists(CV_DIR):
        print("⚠️ ONNX not found. Loading standard PyTorch model...")
        sys_comps["cv_model"] = AutoModelForImageClassification.from_pretrained(CV_DIR)
        sys_comps["cv_proc"] = AutoImageProcessor.from_pretrained(CV_DIR)
    else:
        # Fallback error if download script failed
        raise RuntimeError(f"❌ CV Models missing! Checked: {ONNX_DIR} and {CV_DIR}")

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


@app.get("/metrics")
def metrics():
    """Exposes Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    start_time = time.time()
    endpoint = "/predict"
    
    try:
        # --- A. CV INFERENCE ---
        cv_start = time.time()
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
        inputs = sys_comps["cv_proc"](img, return_tensors="pt")
        
        with torch.no_grad():
            outputs = sys_comps["cv_model"](**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            conf, pred_idx = torch.max(probs, dim=-1)
            diagnosis = sys_comps["cv_model"].config.id2label[pred_idx.item()]
        
        CV_LATENCY.observe(time.time() - cv_start)

        # --- B. RAG RETRIEVAL ---
        # Search for treatment info specific to the disease
        docs = sys_comps["rag"].similarity_search(
            query=f"{diagnosis} treatment", k=2
        )
        context_text = "\n".join([d.page_content[:500] for d in docs])

        # --- C. LLM GENERATION ---
        prompt = f"<|system|>\nYou are a plant disease expert.\n<|user|>\nContext: {context_text}\nQuestion: Explain {diagnosis} and how to treat it.\n<|assistant|>\n"
        
        llm_start = time.time()
        output = sys_comps["llm"](
            prompt, max_tokens=512, stop=["<|user|>"], echo=False
        )
        raw_response = output["choices"][0]["text"].strip()
        LLM_LATENCY.observe(time.time() - llm_start)

        # --- D. GUARDRAILS VALIDATION ---
        final_response = raw_response
        
        # ... inside /predict and /chat ...
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
                GUARD_FAILURES.labels(violation_type=violation_type).inc()
                
                logging.warning(f"Guardrail triggered: {violation_type}")
                final_response = "I cannot answer that due to safety guidelines regarding content policies."
                
            except Exception as e:
                # Generic error fallback
                GUARD_FAILURES.labels(violation_type="ERROR").inc()
                final_response = "I cannot answer that."
            finally:
                GUARD_LATENCY.observe(time.time() - guard_start)

        # Success Metric
        REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()
        REQUEST_LATENCY.observe(time.time() - start_time)

        return {
            "diagnosis": diagnosis,
            "confidence": f"{conf.item()*100:.1f}%",
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
        # --- LLM GENERATION ---
        prompt = f"<|system|>\nYou are a plant disease expert.\n<|user|>\nContext: {payload.context}\nQuestion: {payload.question}\n<|assistant|>\n"

        llm_start = time.time()
        output = sys_comps["llm"](
            prompt, max_tokens=512, stop=["<|user|>"], echo=False
        )
        raw_response = output["choices"][0]["text"].strip()
        LLM_LATENCY.observe(time.time() - llm_start)

        # --- GUARDRAILS VALIDATION ---
        final_response = raw_response
        
        if sys_comps.get("guard"):
            guard_start = time.time()
            try:
                validated = sys_comps["guard"].validate(raw_response)
                
                if hasattr(validated, 'validated_output'):
                    final_response = validated.validated_output
                    
            except Exception as e:
                # VIOLATION DETECTED
                GUARD_FAILURES.inc()
                logging.warning(f"Guardrail blocked chat: {e}")
                final_response = "I cannot answer that question as it violates safety policies."
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