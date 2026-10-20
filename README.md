GPU Pool on Proxmox, Scheduled by Nomad

Project Overview

This project explores how to deploy and manage GPU-backed Large Language Model (LLM) inference services on a Proxmox-based environment using Nomad for scheduling, SGLang for model serving, and SGLang Model Gateway for request routing.

The objective is to provide an OpenAI-compatible endpoint that applications such as n8n, Redmine AI helpers, and RAG applications can use to access language models.

Objectives

* Deploy one SGLang worker per available GPU where supported.
* Use Nomad to schedule workers and recover failed allocations.
* Place the Model Gateway in front of the workers.
* Register services with Consul for service discovery.
* Compare independent GPU replicas with tensor parallelism where hardware permits.
* Evaluate cache-aware routing against round-robin routing.
* Prepare repeatable benchmark scripts and document measured results.
* Develop a deployment and scaling plan for a future pool of 10–12 GPUs.

Planned Architecture

Applications send OpenAI-compatible requests to the Model Gateway. The gateway routes requests to available SGLang workers. Nomad manages worker allocations and restarts failed tasks, while Consul provides service registration and discovery.

Applications (n8n, RAG, Redmine)
                |
                v
       SGLang Model Gateway
                |
                v
       Consul service discovery
                |
        +-------+-------+
        |               |
        v               v
   SGLang Worker 1  SGLang Worker 2
      GPU 0            GPU 1
        |               |
        +-------+-------+
                |
       Nomad scheduling
                |
       Proxmox GPU hosts

This is the target architecture. Exact gateway configuration, service discovery integration, and GPU allocation details will be confirmed against the installed software versions and available cluster.

Technology Stack

* Proxmox: Virtualization and host infrastructure.
* Nomad: Workload scheduling and recovery.
* SGLang: LLM inference serving.
* SGLang Model Gateway: Request routing and worker management.
* Consul: Service registration and discovery.
* Docker: Container packaging and local development checks.
* Python: Benchmark scripts and testing utilities.

Planned Experiments

1. Identify model and quantization options appropriate for 12 GB RTX 3060 GPUs, accounting for model memory, runtime overhead, and KV cache.
2. Compare two independent workers with a tensor-parallel deployment across two GPUs.
3. Compare cache-aware routing with round-robin routing using repeated prompts and shared context.
4. Evaluate service discovery and worker registration/removal options.
5. Consider routing multiple model types, including chat, embeddings, and vision.
6. Test worker failure, gateway behavior, and Nomad recovery.
7. Measure network bandwidth and latency between hosts before drawing conclusions about cross-host tensor parallelism.

Repository Structure

gpu-pool-sglang/
├── benchmarks/
├── docs/
├── gateway/
├── nomad/
├── scripts/
├── tests/
└── README.md

The directories will contain benchmark scripts, design notes, gateway configuration, Nomad job specifications, helper scripts, and tests as the project develops.

Current Development Environment

Local development is being performed on Windows using Visual Studio Code, PowerShell, Git, Python, Docker Desktop, and WSL 2.

The local machine reports Intel UHD Graphics 600 rather than an NVIDIA GPU. Therefore, actual CUDA inference, GPU performance measurements, and GPU allocation tests must be performed on the assigned NVIDIA GPU servers.

Validation and Evidence

Results will be recorded according to what has actually been tested.

* Local checks will be identified as local validation.
* Mock or simulated tests will be identified as simulations.
* GPU benchmarks and cluster deployment results will only be reported after they have been run on the appropriate hardware.
* Any pending tests or access blockers will be documented.

Current Status

Initial project structure created.

The repository files, configurations, benchmark scripts, and design documentation are being prepared. Deployment and hardware-dependent experiments remain pending until the required cluster access is available.

Known Constraints

* No NVIDIA GPU is available on the local development machine.
* Access to the target GPU cluster is not yet available.
* Model selection and benchmark conclusions must be verified on the actual hardware.
* GPU capacity, driver versions, CUDA compatibility, and gateway integration must be confirmed before deployment.

Troubleshooting

A troubleshooting log will be added as real issues are encountered and resolved. Only observed issues and verified fixes will be recorded.

Deliverables

* Nomad job specification for SGLang GPU workers.
* Nomad job specification for the Model Gateway.
* Consul service registration and discovery configuration.
* Repeatable benchmark scripts and raw results.
* A design document covering placement, routing, scaling, failure recovery, and risks.
* Evidence of successful requests and worker recovery on the GPU cluster.

Local Validation and Testing
The project has been checked locally on Windows using PowerShell and Visual Studio Code.
Automated Test
Run the benchmark test with:

python -m unittest discover -s tests -v
Verified result: The benchmark test passed (Ran 1 test ... OK).
Local Mock Worker
A Flask-based mock worker was tested locally at 127.0.0.1:8000.

GET /health returned an OK status.

POST /v1/chat/completions returned a mock chat-completion response using local-mock-model.

These checks confirm that the mock worker responds to requests. They do not confirm actual SGLang inference or GPU performance.
Infrastructure Limitations
The development laptop does not have an available NVIDIA GPU, and the target GPU host and running Nomad agent were not accessible during local validation.

Consequently, the following tasks remain pending:

Running SGLang on the assigned GPU hardware.

Verifying GPU allocation and real model inference.

Testing gateway-to-worker communication and Consul service discovery.

Running performance benchmarks against real workers.

Testing worker failure recovery and the complete cluster deployment.
Troubleshooting Record
Local validation was used to make progress while the GPU infrastructure was unavailable. Benchmark tests and the mock worker were checked independently so that local results would not be confused with real GPU inference results.

Additional troubleshooting details and manual test results are recorded in docs/day1-2-manual-test.md.