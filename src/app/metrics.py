from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Request count
REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total LLM requests",
    ["endpoint", "status"]
)

# Latency histogram
REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

# Tokens and cost
TOKENS_USED = Gauge(
    "llm_tokens_last_request",
    "Tokens used in last LLM request"
)

ESTIMATED_COST = Gauge(
    "llm_estimated_cost_usd",
    "Estimated cost of last LLM request"
)

# Guardrail violations
GUARDRAIL_VIOLATIONS = Counter(
    "guardrail_violations_total",
    "Number of guardrail violations",
    ["rule"]
)

def start_metrics_server(port: int = 8001):
    start_http_server(port)
