"""
Minimal app to test Prometheus/Grafana WITHOUT models
"""
import time
import random
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from backend.metrics import (
    record_llm_metrics,
    record_rag_metrics,
    cv_request_duration,
    guardrail_violations_total,
    set_model_info,
)

app = FastAPI(title="Metrics Test API")

# Prometheus setup
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


@app.on_event("startup")
async def startup():
    print("🚀 Metrics Test API Starting...")
    set_model_info(
        cv_model="test_cv_model",
        llm_model="test_llm",
        embedding_model="test_embeddings"
    )
    print("✅ Ready to generate metrics!")


@app.get("/")
async def root():
    return {
        "message": "Metrics Test API",
        "endpoints": ["/health", "/metrics", "/test-llm", "/test-rag", "/test-all"]
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/test-llm")
async def test_llm():
    """Generate fake LLM metrics"""
    duration = random.uniform(0.5, 3.0)
    input_tokens = random.randint(50, 500)
    output_tokens = random.randint(20, 200)
    
    record_llm_metrics(
        endpoint="/test-llm",
        duration=duration,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model_type="tinyllama"
    )
    
    return {
        "message": "LLM metrics recorded",
        "duration": duration,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }


@app.get("/test-all")
async def test_all():
    """Generate all types of metrics at once"""
    # LLM metrics
    record_llm_metrics(
        endpoint="/test-all",
        duration=random.uniform(1.0, 3.0),
        input_tokens=random.randint(100, 500),
        output_tokens=random.randint(50, 200),
        model_type="tinyllama"
    )
    
    # RAG metrics
    record_rag_metrics(
        endpoint="/test-all",
        duration=random.uniform(0.2, 0.8),
        num_docs=random.randint(2, 5)
    )
    
    # CV metrics
    cv_request_duration.labels(endpoint="/test-all").observe(random.uniform(0.3, 1.0))
    
    return {"message": "All metrics recorded!"}


@app.get("/generate-load")
async def generate_load():
    """Generate a bunch of metrics quickly"""
    for i in range(10):
        record_llm_metrics(
            endpoint="/generate-load",
            duration=random.uniform(0.5, 2.0),
            input_tokens=random.randint(50, 400),
            output_tokens=random.randint(20, 150),
            model_type="tinyllama"
        )
    
    return {"message": "Generated 10 metric entries"}