GPU Pool Design and Deployment Plan
1. Purpose and Scope

The goal of this project is to deploy a GPU pool on Proxmox using Nomad for workload scheduling, Consul for service registration and discovery, SGLang for model inference, and an SGLang Model Gateway for request routing. The deployment should support multiple GPU-backed workers, reliable routing, worker recovery, performance benchmarking, and integration with the n8n OpenAI node.

Local mock workers have been used to validate parts of the routing and service-registration workflow. Production deployment and GPU-based acceptance tests remain pending access to the target environment.
2. Proposed Architecture

The proposed request flow is:

Client or n8n → SGLang Model Gateway → eligible SGLang worker → model inference on GPU.

Nomad schedules worker and gateway workloads. Consul registers services and reports health according to configured checks. The gateway must use a verified worker-discovery mechanism and route requests only to eligible workers.

Consul registration alone does not guarantee that the gateway automatically updates its worker pool. The gateway’s discovery integration must be confirmed and tested.
3. GPU Placement and Model Sizing

The deployment plan must account for the actual GPU inventory, VRAM, model sizes, quantization formats, context lengths, and concurrent request load.

The initial placement strategy is to run one SGLang worker per GPU allocation where supported by the target environment and Nomad GPU-device configuration. Each allocation must be verified to use the intended GPU without unintended sharing.

For a pool containing 10–12 GPU cards, the placement plan should record:

Hostname and GPU identifier.

GPU model and VRAM.

Assigned model and quantization.

Worker allocation and service name.

Expected memory requirements and context length.

Whether the GPU is dedicated to one worker or allocated as part of a tensor-parallel group.

The final mapping cannot be specified reliably until the actual GPU inventory and target host layout are available.
Model-sizing considerations

A 7–8B model using AWQ or GPTQ quantization may be a candidate for testing on a 12 GB RTX 3060, but suitability depends on the model, runtime, context length, KV-cache requirements, and concurrent load. An 8 GB RTX 3060 Ti may be suitable for some embedding workloads, subject to model and memory requirements.

These are candidate configurations, not confirmed deployment results. GPU memory usage and inference stability must be measured on the target machines.
4. Independent Replicas Versus Tensor Parallelism

Two candidate architectures will be evaluated.
Independent replicas: Run separate model workers on separate GPUs. This can increase aggregate request capacity and allows the gateway to distribute requests across workers. Each replica must have sufficient memory for its model and workload.
Tensor parallelism (TP=2): Distribute a model across two GPUs. This can enable larger models or configurations that do not fit on one GPU, but introduces communication overhead and changes the amount of parallel request capacity available.

The comparison will use the same model, quantization where applicable, prompts, context and generation settings, warm-up procedure, and concurrency levels of 1, 8, and 32. Three repetitions should be collected for each configuration.

Measurements should include throughput, mean latency, p50 and p95 latency, errors, GPU memory use, and utilization. The architecture recommendation will be made only after comparable measurements from the real environment are available.
5. Worker Discovery and Routing

Consul is the proposed service registry. Each worker should register with an identifiable service name, address, port, and health check.

The gateway’s supported discovery mechanism must be confirmed for the deployed version. Options should be evaluated against the actual gateway capabilities rather than assuming that Consul registration automatically updates a static worker list.

The routing evaluation will compare Round Robin and Cache-Aware routing using a workload with a repeated long system prompt and RAG context. The tests should measure throughput, latency, request failures, worker distribution, and prefix/KV-cache hit metrics when the deployed runtime exposes them.

Existing local mock results provide preliminary routing observations only. They do not establish real GPU performance or prove that Cache-Aware routing improves cache reuse.
6. Failure Recovery and Reliability

The required failure test will simulate an approved worker failure while requests are being served. The test must determine whether the gateway stops routing new requests to an unavailable worker, whether healthy workers continue receiving traffic, and whether Nomad restarts or replaces the failed worker.

Consul health and gateway membership must then recover without manual intervention if automatic discovery and recovery are the chosen design.

The supervisor’s acceptance criterion is that no client requests fail beyond the permitted in-flight request behavior. Results must record total requests, successes, failures, latency, worker membership, Nomad allocation changes, and recovery time.

The local mock failure test was inconclusive because responses identifying both mock workers continued after one Nomad job was stopped. Production failover therefore remains unverified.
7. n8n Integration

The n8n OpenAI node will be configured to use the approved gateway base URL, a supported model name, and any required approved credentials.

The test will submit a prompt and verify that a successful response is returned through the gateway. Evidence should include the node configuration with secrets concealed, the execution result, and the corresponding gateway or worker logs.

This integration remains pending until the target gateway is reachable from n8n.
8. Risks and Mitigations
Insufficient GPU memory: Verify model, quantization, context and KV-cache requirements before deploying additional workers.
Static or stale worker lists: Confirm dynamic discovery behavior and test worker addition, removal, and rescheduling.
High-concurrency failures: Measure error rates and latency under controlled load before selecting concurrency limits.
Misleading benchmark results: Keep mock and production data separate and use consistent workloads and repeated measurements.
Worker failure affecting clients: Test failure behavior and recovery under an approved procedure before declaring acceptance.
Network and integration issues: Verify host connectivity, ports, service health, and n8n reachability.
9. Acceptance and Next Steps

The project will be considered ready for supervisor acceptance when the following evidence is available:

SGLang worker Nomad jobs use the intended GPU placement and allocation count.

The gateway is registered and healthy, and requests demonstrably reach both required gpu-01 workers.

Independent-replica versus TP=2 benchmarks are complete.

Round Robin versus Cache-Aware benchmarks include comparable raw results and cache metrics where available.

Worker discovery, rescheduling, and failure recovery pass the defined acceptance tests.

The n8n OpenAI node successfully completes a request through the gateway.

The proposed GPU placement plan for 10–12 cards and this design report are prepared for supervisor review.
Current status: Local mock validation, benchmark preparation, and deployment documentation are complete for the tests recorded so far. Production GPU deployment, performance comparisons, dynamic discovery, reliable failover, and n8n integration remain pending target-environment access and validation.
 