# Day 9 – Consul Gateway Discovery and Worker Recovery
## Objective
Implement and test a synchronization approach between Consul service discovery and the SGLang Model Gateway. The goal is to ensure that healthy workers are registered with the gateway and workers that are no longer healthy can be removed.
## 1. Implementation
Created `scripts/consul_gateway_sync.py`.
The script:
- Queries configured Consul services through the Consul HTTP API.
- Retrieves all registered workers and identifies healthy workers.
- Builds worker URLs using the Consul service address and port.
- Reads the gateway worker registry through `GET /workers`.
- Identifies workers that need to be added or removed.
- Uses `POST /workers` to register newly discovered healthy workers.
- Uses `DELETE /workers/{worker_id}` to request removal of managed workers.
- Supports dry-run mode by default.
- Requires `--apply` before making gateway changes.
- Saves previously managed worker URLs in `.git/consul-gateway-sync-state.json`.
- Supports `--managed-url` for explicitly identifying a previously managed worker when Consul has deregistered it.
- Includes a safety check that prevents synchronization when registered managed workers exist but none are healthy.
## 2. Discovery and recovery tests
Three mock workers were registered with Consul and the SGLang Gateway.
The gateway worker registry confirmed three workers:
- `http://host.docker.internal:18000`
- `http://host.docker.internal:18001`
- `http://host.docker.internal:18002`
All three were reported healthy.
### Three-worker traffic distribution
Twelve OpenAI-compatible chat completion requests were sent through the gateway.
| Mock worker | Successful responses |
|---|---:|
| Worker 1 | 4 |
| Worker 2 | 4 |
| Worker 3 | 4 |
| Total | 12 |
Result: 12/12 successful responses, with traffic evenly distributed across the three mock workers.
This verifies mock gateway routing and worker registration. It does not represent real GPU inference performance.
## 3. Worker removal and synchronization
The third mock worker was stopped using Nomad.
The synchronization script was tested with an explicitly managed URL because the stopped Nomad job could deregister its Consul service.
The script identified the third worker as a removal candidate and submitted a gateway DELETE request.
The gateway registry subsequently showed two workers:
- Worker 1
- Worker 2
The third worker was then brought back into service. Consul reported it healthy, and the script discovered it as an addition.
After applying synchronization, the gateway registry again showed three healthy workers.
This demonstrates that the controller can add a newly discovered worker and remove a previously managed worker when supplied with its ownership information.
## 4. Nomad task restart test
The third worker allocation was signalled during the recovery test.
The allocation status showed:
- Client status: running after recovery
- Task status: running
- Total restarts: 1
- A termination event with exit code 1
- A subsequent task restart event
The worker health endpoint later returned:
`{"status": "ok", "worker": "mock-worker-3"}`
This confirms that Nomad restarted the signalled mock task.
The gateway synchronization and Nomad restart are separate operations in the current implementation. Continuous automatic synchronization during worker failure has not yet been demonstrated.
## 5. Automated tests
Created `tests/test_consul_gateway_sync.py`.
The tests verify:
- Synchronization stops when managed workers exist but no workers are healthy.
- Synchronization is allowed when healthy workers are available.
The full project test suite returned:
`4 passed`
The synchronization script also passed Python compilation with:
`python -m py_compile scripts/consul_gateway_sync.py`
## 6. Production configuration review
The production worker job is defined in:
`nomad/sglang-worker.nomad.hcl`
It requests one `nvidia/gpu` device and runs SGLang with tensor parallelism set to 1.
The production gateway job is defined in:
`nomad/sglang-gateway.nomad.hcl`
It registers the gateway with Consul and uses cache-aware routing. Its current worker URL is static, so the synchronization controller still needs to be integrated into an automatically running workflow.
## 7. Limitations and next steps
The following work remains:
- Run the synchronization controller continuously or trigger it automatically when Consul changes.
- Verify automatic gateway removal and re-registration during a Nomad reschedule without manual intervention.
- Integrate dynamic discovery with the production SGLang gateway job.
- Validate the production GPU worker deployment on gpu-01.
- Confirm the gateway handles in-flight requests during real worker failure.
- Test the n8n OpenAI-compatible integration.
The current three-worker results use local mock workers, not actual GPU-backed SGLang inference.
## Day 9 conclusion
Day 9 established a working Consul-to-gateway synchronization prototype, persistent worker ownership tracking, safe dry-run behaviour, and dynamic worker registration and removal. Three mock workers were successfully registered and received evenly distributed gateway traffic. The Nomad task restart test also confirmed recovery of a signalled mock worker.
The implementation provides a foundation for automated service discovery and recovery. Production GPU failover and continuous controller execution remain to be validated.
