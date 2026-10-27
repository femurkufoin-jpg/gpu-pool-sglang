GPU Pool Deployment Checklist
Project: GPU Pool on Proxmox with Nomad, Consul, SGLang Workers, and SGLang Model Gateway
Purpose: Prepare and validate deployment to the target GPU environment after SSH access is granted.
Current status: Local mock validation completed. Production GPU deployment and acceptance tests are pending target-environment access.
1. Access and Environment Readiness
â˜ Obtain approved SSH access to the target environment.
â˜ Confirm target hostnames, addresses, usernames, and access method with the supervisor.
â˜ Inventory available GPUs, VRAM, GPU models, and driver versions.
â˜ Verify NVIDIA drivers and nvidia-smi on each intended GPU host.
â˜ Confirm Nomad client/server health and datacenter configuration.
â˜ Confirm Consul health and service-catalog access.
â˜ Confirm Docker, Python, and required SGLang/Gateway versions.
â˜ Confirm available disk space, model-cache space, network bandwidth, and ports.
â˜ Record baseline system status before deployment.
Evidence: Host inventory, GPU inventory, version outputs, Nomad status, and Consul status.
2. Configuration Review
â˜ Review the production Nomad SGLang worker job.
â˜ Verify GPU device access and allocation constraints.
â˜ Ensure the number of worker allocations matches the intended GPU placement plan.
â˜ Verify model, quantization, context length, and memory settings against available VRAM.
â˜ Review nomad/sglang-gateway.nomad.hcl.
â˜ Confirm the gatewayâ€™s supported worker-discovery mechanism and routing-policy options for the selected version.
â˜ Verify that only healthy, eligible workers enter the routing pool.
â˜ Confirm gateway and worker service registration in Consul.
â˜ Confirm required ports, firewall rules, and inter-host connectivity.
â˜ Check that secrets and tokens are not committed to Git.
â˜ Capture the Git commit hash and configuration version used for deployment.
Important: Consul registration alone does not prove that the gateway dynamically discovers worker changes. Validate the selected integration before claiming discovery is complete.
3. Deploy SGLang Workers
â˜ Start with one worker on a selected GPU.
â˜ Verify the Nomad allocation is running and healthy.
â˜ Verify GPU visibility from the worker environment.
â˜ Confirm model loading completes without out-of-memory errors.
â˜ Test the worker health endpoint.
â˜ Test a direct OpenAI-compatible chat-completion request.
â˜ Record startup time, model, quantization, VRAM usage, and response status.
â˜ Deploy the remaining workers according to the approved GPU placement plan.
â˜ Confirm each worker has the correct GPU placement and service registration.
Evidence: Nomad allocation status, worker logs, GPU utilization, model-load result, and direct inference response.
4. Deploy and Validate the Gateway
â˜ Deploy the gateway using the reviewed production Nomad job.
â˜ Confirm the gateway allocation is healthy.
â˜ Verify the gateway health endpoint.
â˜ Confirm all intended workers are discoverable and eligible.
â˜ Send a chat-completion request through the gateway.
â˜ Verify the response and record which worker served the request where observable.
â˜ Confirm requests can reach both intended workers.
â˜ Verify routing policy configuration and gateway logs.
â˜ Confirm monitoring and relevant metrics are available.
Acceptance evidence: Healthy gateway, successful gateway inference, and observable request distribution across both gpu-01 workers, as required by the supervisor.
5. Benchmark Independent Replicas vs. TP=2
â˜ Confirm model, quantization, prompt, context length, and generation settings.
â˜ Establish a repeatable warm-up and measurement procedure.
â˜ Test independent replicas at concurrency 1, 8, and 32.
â˜ Test TP=2 under the same workload and concurrency levels.
â˜ Run three repetitions for each configuration.
â˜ Record throughput, mean latency, p50, p95, failures, and GPU memory.
â˜ Capture GPU utilization and relevant host/network metrics.
â˜ Save raw benchmark results and document the test environment.
â˜ Compare latency and throughput before recommending an architecture.
Rule: Benchmark metadata labels do not deploy replicas or TP=2. Verify the actual architecture and GPU placement before recording results.
6. Benchmark Round Robin vs. Cache-Aware Routing
â˜ Confirm both policies are supported by the deployed gateway version.
â˜ Use the same workers and model configuration for both runs.
â˜ Prepare a repeatable workload containing a long shared system prompt and RAG context.
â˜ Define repeated-prefix and request-order behavior.
â˜ Warm up the system consistently before measurements.
â˜ Run each policy at concurrency 1, 8, and 32.
â˜ Repeat each test three times.
â˜ Record throughput, latency, failures, and worker distribution.
â˜ Capture prefix/KV-cache hit metrics if exposed by the deployed version.
â˜ Document measurement limitations and environmental differences.
â˜ Make a recommendation only after reviewing the comparable raw results.
7. Worker Discovery and Rescheduling
â˜ Confirm the selected discovery implementation.
â˜ Register each worker with the correct Consul service and health check.
â˜ Verify only healthy, eligible workers enter the gatewayâ€™s routing pool.
â˜ Add a worker and verify the gatewayâ€™s routing pool updates.
â˜ Remove a worker and verify the gateway stops routing new requests to it.
â˜ Reschedule a worker through Nomad and observe service registration changes.
â˜ Confirm the gateway handles membership changes without manual intervention if dynamic discovery is the chosen design.
â˜ Capture Consul catalog, health, gateway logs, and routing evidence.
Acceptance evidence: The gateway recognizes worker additions and removals using the approved discovery mechanism.
8. Worker Failure and Recovery
â˜ Establish a healthy baseline with multiple workers.
â˜ Record successful request rate and current worker membership.
â˜ Simulate failure of one worker using an approved test procedure.
â˜ Send requests through the gateway during the failure.
â˜ Record successes, failures, retries, latency, and the affected in-flight request.
â˜ Verify new requests are routed to healthy workers.
â˜ Verify Nomad restarts or replaces the failed worker as expected.
â˜ Verify Consul health and gateway membership recover.
â˜ Repeat the test and preserve raw evidence.
Acceptance criterion: No failed client requests beyond the permitted in-flight request behavior specified by the supervisor. Do not claim this criterion passes unless measured results demonstrate it.
9. n8n Integration
â˜ Confirm the approved gateway URL is reachable from n8n.
â˜ Configure the n8n OpenAI node with the required base URL, model, and approved credentials.
â˜ Send a test request through the OpenAI node.
â˜ Verify a successful response.
â˜ Check connectivity, authentication, and model errors if the request fails.
â˜ Capture the successful node execution as evidence.
10. Final Deliverables
â˜ Nomad worker job with GPU placement constraints and intended allocation count.
â˜ Gateway Nomad job and verified service registration.
â˜ Verified worker-discovery implementation and failure-recovery evidence.
â˜ Benchmark script and raw results.
â˜ Replica-versus-TP=2 comparison table.
â˜ Round Robin-versus-Cache-Aware comparison table, including cache metrics where available.
â˜ GPU placement plan for 10â€“12 cards.
â˜ Two-to-three-page design write-up covering architecture, discovery, trade-offs, and risks.
â˜ n8n integration evidence.
â˜ Final Git commit hash and reproducible deployment instructions.
â˜ Supervisor review and acceptance.
11. Rollback and Safety
â˜ Record the currently deployed job versions and configuration.
â˜ Keep a known-good version of the Nomad jobs and gateway configuration.
â˜ Define rollback steps before changing production jobs.
â˜ Avoid stopping all healthy workers during deployment.
â˜ Perform failure injection only with authorization and a recovery plan.
â˜ Never commit secrets, private keys, or access tokens.
â˜ Confirm service health after rollback or recovery.
Deployment Status
Local mock work: Completed for the documented tests.
Production deployment: Pending target-environment access and authorization.
GPU performance benchmarks: Pending.
Dynamic discovery and production failure recovery: Pending validation.
n8n integration: Pending validation.
