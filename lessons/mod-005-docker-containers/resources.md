# Module 005 — Docker & Containers Resources

## Official documentation

- **Docker documentation** — [docs.docker.com](https://docs.docker.com/). The authoritative reference.
- **Dockerfile best practices** — [docs.docker.com/develop/develop-images/dockerfile_best-practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/). Read this; you will write Dockerfiles for the rest of your career.
- **OCI Image Format Specification** — [github.com/opencontainers/image-spec](https://github.com/opencontainers/image-spec). The standard underneath Docker images.

## Books

- **Docker: Up & Running (3rd ed.)** by Sean Kane and Karl Matthias. The standard practical reference.
- **Container Security** by Liz Rice (O'Reilly). Concise, modern, covers the security surface you'll need for production.
- **Docker Deep Dive** by Nigel Poulton. Up-to-date covering the modern Docker landscape.

## Online courses

- **Docker Mastery (Bret Fisher)** on Udemy. The most-recommended Docker course.
- **Play with Docker** — [labs.play-with-docker.com](https://labs.play-with-docker.com/). Free browser-based Docker sandboxes.

## Key tools beyond Docker

- **BuildKit** — [docs.docker.com/build/buildkit](https://docs.docker.com/build/buildkit/). The modern Docker build engine. Fast multi-stage builds, secrets at build time, multi-arch.
- **buildx** — Docker CLI plugin for BuildKit; multi-platform builds.
- **Trivy** — [trivy.dev](https://trivy.dev/). Image vulnerability + SBOM scanning. Run it on every build.
- **dive** — [github.com/wagoodman/dive](https://github.com/wagoodman/dive). Inspect what's in a Docker image layer by layer.
- **hadolint** — [github.com/hadolint/hadolint](https://github.com/hadolint/hadolint). Dockerfile linter.

## ML-specific container references

- **NVIDIA NGC Catalog** — [catalog.ngc.nvidia.com](https://catalog.ngc.nvidia.com/). NVIDIA-curated GPU-ready container images for PyTorch, TensorFlow, CUDA. Use these as base images for ML workloads.
- **PyTorch official images** — [hub.docker.com/r/pytorch/pytorch](https://hub.docker.com/r/pytorch/pytorch).
- **Chainguard images** — [chainguard.dev/chainguard-images](https://www.chainguard.dev/chainguard-images). Distroless, minimal, signed base images. Good for production hardening.

## Container alternatives + adjacent

- **Podman** — [podman.io](https://podman.io/). Daemonless Docker alternative; rootless by default. Drop-in for most Docker commands.
- **containerd** — [containerd.io](https://containerd.io/). The container runtime Docker itself uses underneath; also what Kubernetes uses.
- **Buildah / Skopeo** — Red Hat container tools that work without a daemon.

## Production patterns

- **12-Factor App** — [12factor.net](https://12factor.net/). 12 principles for cloud-native applications. Most apply directly to containerized ML workloads.
- **Docker security cheat sheet** — [cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html).

## Cross-references in this curriculum

- Module 006 (Kubernetes) — orchestrating your containers.
- Module 007 (APIs) — containerizing your ML serving APIs.
- Engineer track's `mod-103-containerization` for production-grade Docker patterns.
- Security track's `mod-008-runtime-security` for container runtime security.
- Security track's `mod-010-supply-chain-security` for image signing + SBOMs.
