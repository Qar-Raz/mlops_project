import os
import torch
import io
from prometheus_fastapi_instrumentator import Instrumentator
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
)
from optimum.onnxruntime import ORTModelForImageClassification
from llama_cpp import Llama


from dotenv import load_dotenv
#for prometheus grafana setup
import time
from backend.metrics import (
    record_llm_metrics,
    record_rag_metrics,
    cv_request_duration,
    set_model_info,
    estimate_token_count
)

load_dotenv()

try:
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

app = FastAPI(title="Flora-Bot API")

# --- Prometheus Monitoring Setup ---
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    inprogress_name="inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app)
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = os.getenv("MODEL_DIR", "models")
CV_DIR = os.path.join(MODEL_DIR, "flora_cv_model")
ONNX_DIR = os.path.join(MODEL_DIR, "flora_cv_onnx")
RAG_DIR = os.path.join(MODEL_DIR, "flora_rag_db")
GGUF_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
GGUF_PATH = os.path.join(MODEL_DIR, GGUF_FILE)


sys_comps = {}

class ChatPayload(BaseModel):
    question: str
    context: str
    diagnosis: str

@app.on_event("startup")
async def startup_event():
    print("⚙️ Initializing Free Tier Mode (CPU)...")

    # 1. Load Computer Vision Model (Prefer ONNX)
    if os.path.exists(ONNX_DIR):
        print("🚀 Loading ONNX Optimized CV Model...")
        sys_comps["cv_model"] = ORTModelForImageClassification.from_pretrained(ONNX_DIR)
        sys_comps["cv_proc"] = AutoImageProcessor.from_pretrained(ONNX_DIR)
    elif os.path.exists(CV_DIR):
        print("⚠️ ONNX model not found. Loading standard PyTorch model...")
        sys_comps["cv_model"] = AutoModelForImageClassification.from_pretrained(CV_DIR)
        sys_comps["cv_proc"] = AutoImageProcessor.from_pretrained(CV_DIR)
    else:
 
        raise RuntimeError("❌ CV Models missing! Run download_models.py")

    embed_fn = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    sys_comps["rag"] = Chroma(persist_directory=RAG_DIR, embedding_function=embed_fn)

    print(f"🚀 Loading GGUF Optimized LLM: {GGUF_FILE}...")
    if not os.path.exists(GGUF_PATH):
        raise RuntimeError(
            f"❌ GGUF Model missing at {GGUF_PATH}! Run download_models.py"
        )

    sys_comps["llm"] = Llama(
        model_path=GGUF_PATH,
        n_ctx=2048,  # Context window
        n_threads=4,  # Number of CPU threads to use
        verbose=False,
    )
#for prometheus grafana setup func starts
    set_model_info(
    cv_model="flora_cv_model (ONNX)" if os.path.exists(ONNX_DIR) else "flora_cv_model",
    llm_model=GGUF_FILE,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)
#for prometheus grafana setup func ends
    print("API READY.")

#for prometheus grafana setup
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Flora-Bot API",
        "version": "2.0",
        "endpoints": ["/health", "/metrics", "/predict", "/chat"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "models_loaded": {
            "cv_model": "cv_model" in sys_comps,
            "llm": "llm" in sys_comps,
            "rag": "rag" in sys_comps,
        },
        "timestamp": time.time()
    }


#for prometheus grafana, updated predict and chat
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # ============ CV MODEL INFERENCE ============
        cv_start = time.time()
        img = Image.open(io.BytesIO(await file.read())).convert("RGB")
        inputs = sys_comps["cv_proc"](img, return_tensors="pt")
        with torch.no_grad():
            outputs = sys_comps["cv_model"](**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            conf, pred_idx = torch.max(probs, dim=-1)
            diagnosis = sys_comps["cv_model"].config.id2label[pred_idx.item()]
        
        cv_duration = time.time() - cv_start
        cv_request_duration.labels(endpoint="/predict").observe(cv_duration)

        # ============ RAG RETRIEVAL ============
        rag_start = time.time()
        docs = sys_comps["rag"].similarity_search(
            query=f"{diagnosis} treatment", k=2, filter={"disease": diagnosis}
        )

        if not docs:
            docs = sys_comps["rag"].similarity_search(f"{diagnosis} treatment", k=2)
        
        rag_duration = time.time() - rag_start
        record_rag_metrics(
            endpoint="/predict",
            duration=rag_duration,
            num_docs=len(docs)
        )
        
        context_text = "\n".join([d.page_content[:500] for d in docs])

        # ============ LLM INFERENCE ============
        llm_start = time.time()
        
        # Few-Shot Prompting Strategy (Winner of M2_D1 Experiments)
        examples = """
Example 1:
Context: Apple___Apple_scab
Question: My apple tree leaves have olive-green spots. What should I do?
Answer: This is Apple Scab. Remove fallen leaves to reduce spores and apply fungicides like captan early in the season.

Example 2:
Context: Tomato___Early_blight
Question: I see dark rings on my tomato leaves. How do I fix it?
Answer: This is Tomato Early Blight. Improve air circulation, avoid overhead watering, and apply copper-based fungicides.
"""
        prompt = f"<|system|>\nYou are a plant disease expert. Answer the question based on the context.\n{examples}\n<|user|>\nContext: {context_text}\nQuestion: Explain {diagnosis} and how to treat it.\n<|assistant|>\n"

        # Estimate input tokens
        input_tokens = estimate_token_count(prompt)
        
        # GGUF Inference
        output = sys_comps["llm"](
            prompt, max_tokens=512, stop=["<|user|>", "<|system|>"], echo=False
        )
        response = output["choices"][0]["text"].strip()
        
        # Get actual token usage from llama.cpp output
        output_tokens = output["usage"]["completion_tokens"]
        actual_input_tokens = output["usage"]["prompt_tokens"]
        
        llm_duration = time.time() - llm_start
        
        # Record LLM metrics
        record_llm_metrics(
            endpoint="/predict",
            duration=llm_duration,
            input_tokens=actual_input_tokens,
            output_tokens=output_tokens,
            model_type="tinyllama"
        )

        return {
            "diagnosis": diagnosis,
            "confidence": f"{conf.item()*100:.1f}%",
            "explanation": response,
            "chat_context": context_text,
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat")
async def chat(payload: ChatPayload):
    try:
        llm_start = time.time()
        
        # Few-Shot Prompting Strategy (Winner of M2_D1 Experiments)
        examples = """
Example 1:
Context: Apple___Apple_scab
Question: My apple tree leaves have olive-green spots. What should I do?
Answer: This is Apple Scab. Remove fallen leaves to reduce spores and apply fungicides like captan early in the season.

Example 2:
Context: Tomato___Early_blight
Question: I see dark rings on my tomato leaves. How do I fix it?
Answer: This is Tomato Early Blight. Improve air circulation, avoid overhead watering, and apply copper-based fungicides.
"""
        prompt = f"<|system|>\nYou are a plant disease expert. Answer the question based on the context.\n{examples}\n<|user|>\nContext: {payload.context}\nQuestion: {payload.question}\n<|assistant|>\n"

        # GGUF Inference
        output = sys_comps["llm"](
            prompt, max_tokens=512, stop=["<|user|>", "<|system|>"], echo=False
        )
        
        # Get token usage
        output_tokens = output["usage"]["completion_tokens"]
        input_tokens = output["usage"]["prompt_tokens"]
        
        llm_duration = time.time() - llm_start
        
        # Record LLM metrics
        record_llm_metrics(
            endpoint="/chat",
            duration=llm_duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_type="tinyllama"
        )
        
        return {"answer": output["choices"][0]["text"].strip()}
    except Exception as e:
        return {"error": str(e)}