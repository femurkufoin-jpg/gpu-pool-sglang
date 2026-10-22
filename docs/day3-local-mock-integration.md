
# Day 3: Local Mock Workers and Gateway Integration

Date: 22 October 2026

## Objective

Test the SGLang Model Gateway with two local mock workers while GPU-host access remains unavailable.

## Environment

- Nomad: local development agent.

- Consul: local development server.

- Mock worker 1: `http://127.0.0.1:18000`.

- Mock worker 2: `http://127.0.0.1:18001`.

- Gateway API: `http://127.0.0.1:30000`.

- Gateway metrics: `http://127.0.0.1:29000/metrics`.

- Routing policy: `round_robin`.

## Work Completed and Verified

1. Deployed two local mock workers through separate Nomad job specifications.

2. Verified that both mock workers responded to health checks.

3. Started the SGLang Model Gateway container with both mock worker URLs.

4. Confirmed that the gateway health endpoint returned a successful response.

5. Sent chat-completion requests through the gateway.

6. Sent six consecutive requests and observed responses alternating between `mock-worker-1` and `mock-worker-2`.

7. Inspected gateway metrics and observed successful upstream responses and successful worker outcomes for both worker URLs.

8. Checked Git status. The `main` branch matched `origin/main`; the two local mock job files were untracked.

## Results

The local mock integration test passed. The gateway successfully routed requests to both mock workers using round-robin routing, and its metrics recorded successful responses.

## Limitations

The mock workers simulate responses; they do not load an SGLang model or perform GPU inference. These results do not establish real model performance, GPU allocation, or production readiness.

Automatic Consul-based worker discovery has not been verified. Worker-failure behavior, client request handling during failure, and Nomad recovery still require testing. Integration with n8n and the required benchmark comparisons also remain outstanding.

## Evidence to Retain

- Nomad status for both mock worker jobs.

- Successful health-check responses.

- Gateway health response.

- Six-request output showing alternating mock worker identities.

- Gateway metrics showing successful outcomes for both worker URLs.

## Day 3 Outcome

Local gateway integration with two mock workers and round-robin request distribution was verified. The next step is to test worker failure and recovery without claiming that mock results represent real GPU inference.

Day 4 — Mock Worker Failure and Recovery
Objective
Test whether Nomad restarts a mock worker after its process stops and whether the gateway remains available.
Results
Stopped the Python process serving mock Worker 1 on port 18000.
Confirmed that Nomad restarted the worker. The allocation showed 4 total restarts and the task running again.
Sent a subsequent chat-completion request through the gateway; the response identified mock-worker-2.
Checked the gateway health endpoint at http://127.0.0.1:30000/health; it returned OK.
Limitations
This verifies basic recovery in the local mock environment. It does not establish zero failed client requests during recovery, automatic Consul-based worker discovery, or real SGLang GPU inference.
Conclusion
The local gateway and mock workers demonstrated basic routing and Nomad process-restart behavior. Further testing is required for production failure handling.