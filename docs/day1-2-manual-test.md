Day 1–2: SGLang Worker Preparation and Manual Testing

Day 1 — Project Understanding and Setup

The project, GPU Pool on Proxmox, Scheduled by Nomad, aims to deploy SGLang inference workers on individual GPUs and route OpenAI-compatible requests through the SGLang Model Gateway. Nomad will manage worker scheduling, while service discovery will support worker registration and gateway routing.

The initial repository structure and project configuration files were prepared. The main components include the Nomad worker and gateway job specifications, gateway configuration reference, manual testing documentation, and benchmark tooling.

Day 2 — Worker Configuration and Testing Preparation

The Nomad worker specification, nomad/sglang-worker.nomad.hcl, was validated successfully using the Nomad CLI. The gateway job specification, nomad/sglang-gateway.nomad.hcl, also passed syntax validation.

The validation output warned that the Nomad agent could not be reached. Therefore, the checks confirm configuration syntax only; they do not confirm live deployment, GPU allocation, or driver availability.

A benchmark harness was created at benchmarks/benchmark_gateway.py. It sends requests to an OpenAI-compatible chat-completions endpoint and records request outcomes and latency. The unit test tests/test_benchmark_gateway.py was created and passed locally.

The benchmark changes were committed as 75f6e8e with the message test: add gateway benchmark harness, pushed to GitHub, and merged into main through Pull Request #2. The merge commit was c960234.

Verified Local Results

* Nomad worker job syntax validation: successful.
* Nomad gateway job syntax validation: successful.
* Python benchmark script syntax check: successful.
* Benchmark command-line help: successful.
* Benchmark unit tests: one test passed.
* Git changes were pushed and merged into main.

Outstanding Manual Tests

The following tests require access to the GPU host and a running Nomad cluster:

1. Start an SGLang worker using an available GPU.
2. Check the worker health endpoint.
3. Send a real inference request and confirm the response.
4. Record model-loading results and GPU memory usage.
5. Verify communication between the worker and gateway.
6. Confirm Nomad scheduling and service registration.

Access Limitation

SSH access to the GPU host is not currently available. The local environment has no detected NVIDIA GPU, and a running Nomad agent could not be reached during validation. Consequently, live inference and cluster deployment have not been verified.

Day 1–2 Outcome

Initial project understanding, configuration preparation, local validation, benchmark implementation, and benchmark unit testing have been completed. Actual GPU-worker testing remains pending until access to the required infrastructure is provided.