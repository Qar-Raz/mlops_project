"""
Custom Prometheus Metrics for LLM Monitoring
Tracks: Latency, Token Usage, Cost, and Guardrail Violations
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# ============================================================================
# METRIC DEFINITIONS
# ============================================================================

# 1. LATENCY METRICS
llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'Time spent processing LLM requests',
    ['endpoint', 'model_type'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

cv_request_duration = Histogram(
    'cv_request_duration_seconds',
    'Time spent processing CV model requests',
    ['endpoint'],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)
)

rag_retrieval_duration = Histogram(
    'rag_retrieval_duration_seconds',
    'Time spent retrieving documents from vector store',
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# 2. TOKEN USAGE METRICS
llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total number of tokens processed',
    ['token_type', 'endpoint']  # token_type: input, output
)

llm_tokens_per_request = Histogram(
    'llm_tokens_per_request',
    'Distribution of tokens per request',
    ['token_type', 'endpoint'],
    buckets=(50, 100, 200, 500, 1000, 2000, 4000)
)

# 3. COST METRICS (based on token usage)
llm_estimated_cost_total = Counter(
    'llm_estimated_cost_total_usd',
    'Estimated cumulative cost in USD',
    ['model_type', 'endpoint']
)

llm_cost_per_request = Histogram(
    'llm_cost_per_request_usd',
    'Estimated cost per request in USD',
    ['endpoint'],
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1)
)

# 4. GUARDRAIL METRICS (Placeholder for future implementation)
guardrail_violations_total = Counter(
    'guardrail_violations_total',
    'Total number of guardrail violations',
    ['violation_type', 'endpoint']  # violation_type: pii, toxicity, prompt_injection, etc.
)

guardrail_checks_total = Counter(
    'guardrail_checks_total',
    'Total number of guardrail checks performed',
    ['check_type', 'endpoint']
)

# 5. RAG-SPECIFIC METRICS
rag_documents_retrieved = Histogram(
    'rag_documents_retrieved',
    'Number of documents retrieved per query',
    ['endpoint'],
    buckets=(0, 1, 2, 3, 5, 10)
)

rag_retrieval_relevance_score = Histogram(
    'rag_retrieval_relevance_score',
    'Relevance score of retrieved documents',
    ['endpoint'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

# 6. MODEL HEALTH METRICS
model_info = Info('model_info', 'Information about loaded models')
active_requests = Gauge('active_llm_requests', 'Number of requests currently being processed')

# ============================================================================
# COST CALCULATION HELPERS
# ============================================================================

# Pricing per 1K tokens (example rates - adjust based on your model)
TOKEN_PRICING = {
    'tinyllama': {
        'input': 0.00001,   # $0.00001 per 1K input tokens (example)
        'output': 0.00002,  # $0.00002 per 1K output tokens (example)
    },
    'default': {
        'input': 0.00001,
        'output': 0.00002,
    }
}

def calculate_cost(input_tokens: int, output_tokens: int, model_type: str = 'tinyllama') -> float:
    """
    Calculate estimated cost based on token usage
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_type: Type of model (for pricing lookup)
    
    Returns:
        Estimated cost in USD
    """
    pricing = TOKEN_PRICING.get(model_type, TOKEN_PRICING['default'])
    input_cost = (input_tokens / 1000) * pricing['input']
    output_cost = (output_tokens / 1000) * pricing['output']
    return input_cost + output_cost

# ============================================================================
# METRIC RECORDING HELPERS
# ============================================================================

def record_llm_metrics(
    endpoint: str,
    duration: float,
    input_tokens: int,
    output_tokens: int,
    model_type: str = 'tinyllama'
):
    """
    Record all LLM-related metrics for a request
    
    Args:
        endpoint: API endpoint name
        duration: Request duration in seconds
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_type: Type of model used
    """
    # Record latency
    llm_request_duration.labels(endpoint=endpoint, model_type=model_type).observe(duration)
    
    # Record token usage
    llm_tokens_total.labels(token_type='input', endpoint=endpoint).inc(input_tokens)
    llm_tokens_total.labels(token_type='output', endpoint=endpoint).inc(output_tokens)
    llm_tokens_per_request.labels(token_type='input', endpoint=endpoint).observe(input_tokens)
    llm_tokens_per_request.labels(token_type='output', endpoint=endpoint).observe(output_tokens)
    
    # Record cost
    cost = calculate_cost(input_tokens, output_tokens, model_type)
    llm_estimated_cost_total.labels(model_type=model_type, endpoint=endpoint).inc(cost)
    llm_cost_per_request.labels(endpoint=endpoint).observe(cost)

def record_rag_metrics(endpoint: str, duration: float, num_docs: int, relevance_scores: list = None):
    """
    Record RAG retrieval metrics
    
    Args:
        endpoint: API endpoint name
        duration: Retrieval duration in seconds
        num_docs: Number of documents retrieved
        relevance_scores: Optional list of relevance scores
    """
    rag_retrieval_duration.observe(duration)
    rag_documents_retrieved.labels(endpoint=endpoint).observe(num_docs)
    
    if relevance_scores:
        for score in relevance_scores:
            rag_retrieval_relevance_score.labels(endpoint=endpoint).observe(score)

def record_guardrail_violation(violation_type: str, endpoint: str):
    """
    Record a guardrail violation (placeholder for future implementation)
    
    Args:
        violation_type: Type of violation (e.g., 'pii', 'toxicity', 'prompt_injection')
        endpoint: API endpoint where violation occurred
    """
    guardrail_violations_total.labels(violation_type=violation_type, endpoint=endpoint).inc()

def record_guardrail_check(check_type: str, endpoint: str):
    """
    Record that a guardrail check was performed
    
    Args:
        check_type: Type of check performed
        endpoint: API endpoint name
    """
    guardrail_checks_total.labels(check_type=check_type, endpoint=endpoint).inc()

# ============================================================================
# DECORATOR FOR AUTOMATIC METRIC TRACKING
# ============================================================================

def track_llm_request(endpoint: str, model_type: str = 'tinyllama'):
    """
    Decorator to automatically track LLM request metrics
    
    Usage:
        @track_llm_request(endpoint='/predict', model_type='tinyllama')
        async def my_endpoint():
            # Your code here
            return result, input_tokens, output_tokens
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_requests.inc()
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Expecting function to return (result, input_tokens, output_tokens)
                if isinstance(result, tuple) and len(result) == 3:
                    actual_result, input_tokens, output_tokens = result
                    record_llm_metrics(endpoint, duration, input_tokens, output_tokens, model_type)
                    return actual_result
                else:
                    # If function doesn't return token counts, just record duration
                    llm_request_duration.labels(endpoint=endpoint, model_type=model_type).observe(duration)
                    return result
            finally:
                active_requests.dec()
        return wrapper
    return decorator

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def estimate_token_count(text: str) -> int:
    """
    Rough estimation of token count
    Rule of thumb: 1 token ≈ 4 characters for English text
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    return len(text) // 4

def set_model_info(cv_model: str, llm_model: str, embedding_model: str):
    """
    Set metadata about loaded models
    
    Args:
        cv_model: Computer vision model name
        llm_model: LLM model name
        embedding_model: Embedding model name
    """
    model_info.info({
        'cv_model': cv_model,
        'llm_model': llm_model,
        'embedding_model': embedding_model
    })