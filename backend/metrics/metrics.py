from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests"
)

SUCCESS_COUNT = Counter(
    "app_success_total",
    "Total number of successful responses"
)

ERROR_COUNT = Counter(
    "app_errors_total",
    "Total number of errors"
)

FEEDBACK_ERROR_COUNT = Counter(
    "app_feedback_errors_total",
    "Errors storing feedback"
)

INVALID_QUERY_COUNT = Counter(
    "app_invalid_query_total",
    "Total number of invalid queries"
)

FEEDBACK_COUNT = Counter(
    "app_feedback_total",
    "Total feedback received",
    ["rating"]
)

FEEDBACK_FETCH_COUNT = Counter(
    "app_feedback_fetch_total",
    "Number of times feedback list is requested"
)

FEEDBACK_RETURNED_COUNT = Histogram(
    "app_feedback_returned_count",
    "Number of feedback items returned"
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_ms",
    "Total request latency in ms"
)

RAG_LATENCY = Histogram(
    "app_rag_latency_ms",
    "RAG retrieval latency in ms"
)

LLM_LATENCY = Histogram(
    "app_llm_latency_ms",
    "LLM call latency in ms"
)

FEEDBACK_LATENCY = Histogram(
    "app_feedback_latency_ms",
    "Latency for feedback operations"
)