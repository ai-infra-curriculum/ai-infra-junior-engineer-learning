# Module 007 — APIs & Web Services Resources

## Official documentation

- **FastAPI documentation** — [fastapi.tiangolo.com](https://fastapi.tiangolo.com/). The fastest-growing Python web framework; async-native; excellent docs that double as a tutorial.
- **Uvicorn documentation** — [uvicorn.org](https://www.uvicorn.org/). The ASGI server you'll run FastAPI on.
- **Pydantic documentation** — [docs.pydantic.dev](https://docs.pydantic.dev/). Schema validation. Read the migration guide if you're learning fresh (v1 vs. v2 differences).
- **HTTP/1.1 specification (RFC 7230-7235)** — required reading once; you'll go back to it.

## Web frameworks compared

- **FastAPI** — modern, async-first, ML-friendly. The recommended default for new ML APIs.
- **Flask** — older, sync, smaller. Common in legacy ML codebases.
- **Django** — full-featured, more than you usually need for ML serving. Strong for general web apps.
- **Starlette** — what FastAPI is built on. Use directly if you want the lowest-level async toolkit.

## Books

- **Designing Web APIs** by Brenda Jin et al. (O'Reilly). Good general design principles.
- **API Design Patterns** by JJ Geewax. Comprehensive patterns reference.
- **High-Performance Python (2nd ed.)** by Micha Gorelick & Ian Ozsvald. Covers async + concurrency in production Python.

## API design references

- **REST API design rulebook** — [restful-api-design.readthedocs.io](https://restful-api-design.readthedocs.io/).
- **JSON:API specification** — [jsonapi.org](https://jsonapi.org/). A specification for JSON API design.
- **Google API Design Guide** — [cloud.google.com/apis/design](https://cloud.google.com/apis/design). Pragmatic.
- **GraphQL** — [graphql.org](https://graphql.org/). Alternative to REST. Good for complex client needs; overkill for simple ML serving.
- **gRPC** — [grpc.io](https://grpc.io/). Binary-protocol RPC. Use for high-throughput internal service-to-service.

## ML-specific API patterns

- **TorchServe documentation** — [pytorch.org/serve](https://pytorch.org/serve/). PyTorch's serving framework.
- **TensorFlow Serving** — [tensorflow.org/tfx/serving](https://www.tensorflow.org/tfx/serving). TF's serving framework.
- **BentoML** — [bentoml.com](https://www.bentoml.com/). Higher-level ML serving framework.
- **vLLM** — [vllm.ai](https://vllm.ai/). The standard for LLM serving (PagedAttention, continuous batching).
- **Triton Inference Server** — [github.com/triton-inference-server/server](https://github.com/triton-inference-server/server). NVIDIA's high-performance serving runtime.

## Async + concurrency

- **asyncio** documentation — [docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html).
- **httpx** — [www.python-httpx.org](https://www.python-httpx.org/). Async HTTP client. Replaces `requests` in async code.
- **aiohttp** — older async HTTP library; still common.

## Monitoring + observability

- **prometheus_client** — [github.com/prometheus/client_python](https://github.com/prometheus/client_python). Python instrumentation for Prometheus.
- **OpenTelemetry Python** — [opentelemetry.io/docs/instrumentation/python](https://opentelemetry.io/docs/instrumentation/python/). Distributed tracing standard.
- **Sentry** — [sentry.io/for/python](https://sentry.io/for/python/). Error tracking with great FastAPI integration.

## Security

- **OWASP API Security Top 10** — [owasp.org/www-project-api-security](https://owasp.org/www-project-api-security/). Required reading for any production API.
- **FastAPI Security** — [fastapi.tiangolo.com/tutorial/security](https://fastapi.tiangolo.com/tutorial/security/). Auth patterns covered.

## Cross-references in this curriculum

- Module 001 (Python) and Module 005 (Docker) are foundational.
- Engineer track's `mod-101 exercise-08` covers production-grade model serving.
- Engineer track's `mod-110-llm-infrastructure` covers LLM serving at depth.
- Security track's `mod-004-network-security` covers gateway hardening.
