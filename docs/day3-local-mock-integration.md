Day 3–4: Local Mock Gateway Integration and Recovery
1. Objective
The objective was to test the basic integration between two Nomad-managed mock workers and the SGLang Model Gateway before accessing the actual GPU infrastructure.
The local mock environment was used to verify worker availability, gateway routing, basic failover, and worker redeployment. These tests validate the local integration workflow only; they do not demonstrate real SGLang model inference.
2. Local Environment
The following components were used:
Nomad: Ran the mock worker jobs as local allocations.
Consul: A local development instance was available for service-discovery experimentation. Automatic Consul-based gateway worker discovery was not verified by this test.
SGLang Model Gateway: Exposed its API on port 30000 and metrics on port 29000.
Mock Worker 1: Served on port 18000.
Mock Worker 2: Served on port 18001.
Docker: Ran the local Consul and gateway containers.
PowerShell: Used to submit Nomad jobs and send HTTP requests.
Local files
nomad/local-mock-worker.nomad.hcl
nomad/local-mock-worker-2.nomad.hcl
nomad/sglang-worker.nomad.hcl
nomad/sglang-gateway.nomad.hcl
tests/mock_worker.py
gateway/gateway-config.yaml
The two local-mock-worker job files were local testing files and remained untracked in Git. They were not added to the production Nomad configuration.
3. Day 3 — Two Workers and Gateway Integration
3.1 Starting the workers
Two mock worker jobs were submitted to Nomad. Each worker exposed a local HTTP endpoint so that the gateway could send requests to it.
Worker 1 used port 18000, and Worker 2 used port 18001.
The gateway was configured with both worker URLs and the round_robin routing policy.
3.2 Health verification
The following endpoints were used during testing:
Component
Endpoint
Observed result
Worker 1
http://127.0.0.1:18000/health
mock-worker-ok
Worker 2
http://127.0.0.1:18001/health
mock-sglang-worker-2-ok
Gateway
http://127.0.0.1:30000/health
OK
These results confirmed that the mock endpoints and gateway were responding during the local integration test.
3.3 Gateway routing test
Chat-completion requests were sent to:
http://127.0.0.1:30000/v1/chat/completions
The requests used the mock model name mock-model.
Six requests were observed alternating between the two mock workers:
mock-worker-2
mock-worker-1
mock-worker-2
mock-worker-1
mock-worker-2
mock-worker-1
This demonstrated basic round-robin request distribution in the local mock environment.
3.4 Metrics verification
Gateway metrics were inspected at:
http://127.0.0.1:29000/metrics
The observed metrics included:
smg_worker_health
smg_worker_cb_outcomes_total
smg_worker_selection_total
smg_router_upstream_responses_total
smg_http_responses_total
Metrics showed both configured workers healthy during successful test observations and recorded successful upstream responses. Some cumulative counters also contained failures from earlier requests; those historical counters were not treated as proof of a current outage.
3.5 Day 3 conclusion
The local mock integration demonstrated that the gateway could communicate with both configured workers, route requests to each worker, and expose health and metrics endpoints.
Day 3 result: Basic two-worker gateway integration verified with mock services.
4. Day 4 — Failure, Failover, and Recovery
4.1 Stopping Worker 1
The following command was used to stop Worker 1:
nomad job stop local-mock-worker
Nomad subsequently reported the job as:
Job status: dead (stopped)
Allocation status: complete
Desired allocation state: stop
This confirmed that Worker 1 had been stopped through Nomad.
4.2 Gateway failover test
While Worker 1 was stopped, a chat-completion request was sent through the gateway:
Invoke-RestMethod -Uri http://127.0.0.1:30000/v1/chat/completions -Method Post -ContentType "application/json" -Body '{"model":"mock-model","messages":[{"role":"user","content":"Day 4 failover test"}]}'
The request returned a response identifying mock-worker-2.
This verified that the gateway successfully served a request through Worker 2 while Worker 1 was stopped.
4.3 Restoring Worker 1
Worker 1 was resubmitted to Nomad using:
nomad job run .\nomad\local-mock-worker.nomad.hcl
The deployment output reported:
Job ID: local-mock-worker
Job version: 4
Deployment status: successful
Description: Deployment completed successfully
This confirms that Nomad accepted the job and completed its deployment. The screenshot of the deployment output did not independently establish the new allocation’s health after deployment, so that health check is not claimed here.
4.4 Day 4 conclusion
The local test demonstrated basic gateway failover to Worker 2 while Worker 1 was stopped, followed by a successful Nomad redeployment of Worker 1.
The test did not establish that every request survives every failure scenario, that no client requests fail during an outage, or that Nomad automatically restarts a stopped job without resubmission.
Day 4 result: Basic mock gateway failover and worker redeployment verified.
5. Troubleshooting and Observations
Gateway and worker availability
Worker availability was checked using the local health endpoints and gateway metrics. The gateway health endpoint returned OK, and the successful failover request identified Worker 2.
Stopped job versus failed task
Stopping a Nomad job intentionally changes its desired state to stopped. This differs from a task process unexpectedly failing while Nomad is expected to restart it under the configured restart policy. The controlled stop-and-resubmit test therefore demonstrates failover and redeployment, not automatic recovery from every task failure.
Metrics interpretation
Gateway metrics are cumulative counters. A failure recorded earlier may remain visible after the workers recover. Metrics must be interpreted alongside current worker health and the timing of each test.
6. Limitations and Remaining Work
The following items remain outside the evidence established by these local mock tests:
Real GPU inference: No real SGLang inference was verified on RTX 3060 GPUs.
Production worker discovery: Automatic Consul-based addition and removal of gateway workers was not demonstrated.
Zero-failure recovery: No sustained concurrent-load test established that all client requests succeed during worker failure.
Benchmark results: Real GPU throughput and latency comparisons have not been established by this mock integration.
Application integration: A successful request from an n8n OpenAI node has not been established by the evidence in this document.
These are pending verification items, not claims that the implementation has failed.
7. Overall Conclusion
Days 3 and 4 established a working local mock integration between two Nomad-managed worker services and the SGLang Model Gateway. Both workers were reachable during integration testing, requests were observed alternating between workers, gateway metrics were available, a request succeeded through Worker 2 while Worker 1 was stopped, and Worker 1 was subsequently redeployed successfully through Nomad.
This provides a useful foundation for the next stages of the project: real GPU testing, benchmarking, service-discovery design, and more comprehensive failure testing.
The results in this document are limited to the local mock environment and should not be presented as verified production GPU inference results.

