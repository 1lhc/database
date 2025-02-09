from prometheus_client import start_http_server, Counter, Histogram

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)

def monitor_requests(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        latency = time.time() - request.start_time
        REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
        return response
    