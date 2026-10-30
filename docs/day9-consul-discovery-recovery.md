# Day 9 — Consul Service Discovery and Worker Recovery
**Date:** 30 October 2026  
**Project:** GPU Pool with SGLang, Nomad and Consul  
**Repository:** https://github.com/femurkufoin-jpg/gpu-pool-sglang
## 1. Objective
Day 9 focused on building and validating a Consul-to-SGLang-Gateway
synchronization controller.
The objective was to discover healthy workers, register them dynamically,
remove stale workers and restore gateway registrations after worker recovery.
All Day 9 routing and recovery tests used local mock workers, not physical GPUs.
## 2. Three-worker registration and routing
Created a third disposable mock worker:
- Nomad job: `local-mock-worker-3`
- Consul service: `mock-sglang-worker-3`
- Worker URL: `http://host.docker.internal:18002`
- Health endpoint: `/health`
The worker was configured to return OpenAI-compatible chat completion responses.
A twelve-request gateway routing test produced:
| Worker | Successful responses |
|---|---:|
| Worker 1 — port 18000 | 4 |
| Worker 2 — port 18001 | 4 |
| Worker 3 — port 18002 | 4 |
| **Total** | **12** |
All twelve requests returned valid OpenAI-compatible responses.
This verified balanced distribution across three mock workers.
## 3. Consul synchronization controller
Created `scripts/consul_gateway_sync.py`.
The controller:
1. Queries configured Consul services.
2. Retrieves registered and healthy workers.
3. Reads the gateway registry using `GET /workers`.
4. Identifies healthy workers missing from the gateway.
5. Identifies previously managed workers that are no longer healthy.
6. Adds workers using `POST /workers`.
7. Removes stale workers using `DELETE /workers/{worker_id}`.
The script defaults to dry-run mode. Changes require `--apply`.
### 3.1 Stale-worker discovery issue
Stopping `local-mock-worker-3` caused Nomad to deregister its Consul
service, but the gateway still retained the worker.
The original controller could not identify the stale URL because it
was no longer present in Consul.
### 3.2 Controller improvement
The controller was extended to support:
- Persistent managed-worker state.
- Explicit previously managed URLs through `--managed-url`.
- A configurable state file.
- Dry-run and apply modes.
The default state file is:
`.git/consul-gateway-sync-state.json`
The state file is kept inside local Git metadata and is not intended
to be committed.
### 3.3 Stale-worker removal
The controller was run with worker 3 explicitly identified as managed:
`--managed-url http://host.docker.internal:18002`
The dry-run identified worker 3 for removal.
Applying the synchronization removed worker 3 from the gateway.
The registry then contained two workers and reported `total: 2`.
A subsequent dry-run showed no additions or removals.
## 4. Automated tests
Executed:
`python -m pytest -q`
Result:
`4 passed in 3.35s`
Tests covered benchmark calculations, successful response latency
recording and controller safety behavior.
Python compilation was also verified:
`python -m py_compile scripts/consul_gateway_sync.py`
Compilation succeeded.
## 5. Nomad automatic recovery test
Worker 3 was redeployed:
`nomad job run nomad/local-mock-worker-3.nomad.hcl`
The deployment succeeded.
Allocation ID:
`70fdd08f`
The worker task was deliberately terminated:
`nomad alloc signal -s SIGKILL 70fdd08f mock-worker-3`
### 5.1 Nomad recovery evidence
Inspected:
`nomad alloc status 70fdd08f`
Verified:
- Allocation desired state: `run`.
- Client status: `running`.
- Task status: `running`.
- Total restarts: `1`.
- Termination exit code: `1`.
- Nomad recorded a `Restarting` event.
- Nomad subsequently recorded a `Started` event.
The restart delay was approximately 16.84 seconds.
Nomad automatically restarted the failed Python task inside the same
allocation. A replacement allocation was not required.
### 5.2 Consul health recovery
Executed:
`Invoke-RestMethod "http://127.0.0.1:18002/health"`
Result:
- Status: `ok`
- Worker: `mock-worker-3`
Consul health was checked using:
`Invoke-RestMethod "http://127.0.0.1:8500/v1/health/service/mock-sglang-worker-3?passing=true"`
The service was passing and its HTTP health check returned `200 OK`.
### 5.3 Gateway rediscovery
After recovery, the controller dry-run identified worker 3 as a new
healthy worker to add.
The controller was applied:
`python scripts/consul_gateway_sync.py --services mock-sglang-worker mock-sglang-worker-2 mock-sglang-worker-3 --gateway http://127.0.0.1:30000 --apply`
The gateway accepted the registration:
- Worker URL: `http://host.docker.internal:18002`
- Worker ID: `f698d1ad-8d7c-4337-b45d-c69e19043fe4`
- Registration status: `accepted`
The final gateway registry reported `total: 3`.
All three workers were listed as healthy.
## 6. Troubleshooting
### Issue 1: Stale worker remained in gateway
Cause: The original controller did not retain URLs after Consul
deregistered their services.
Resolution: Added persistent state and the `--managed-url` option.
### Issue 2: PowerShell multiline command errors
Cause: Backtick continuation characters were not pasted correctly.
Resolution: Used complete single-line PowerShell commands.
### Issue 3: Direct worker health request failed
The Windows host could not reach the worker using
`host.docker.internal:18002`.
Resolution: The localhost endpoint `127.0.0.1:18002/health`
returned the expected healthy response. Consul independently
confirmed the configured worker address was healthy.
### Issue 4: Gateway did not automatically restore worker 3
Cause: The synchronization controller was not running continuously.
Resolution: Manually executed the controller after Consul reported
the worker healthy.
Continuous controller execution remains outstanding.
## 7. Day 9 results
| Activity | Result |
|---|---|
| Three mock workers registered | Verified |
| Twelve-request balanced routing | Verified |
| Consul worker discovery | Verified |
| Stale worker removal | Verified |
| Persistent controller state | Verified |
| Four project tests | Passed |
| Nomad failure simulation | Verified |
| Automatic Nomad task restart | Verified |
| Consul health recovery | Verified |
| Gateway rediscovery | Verified manually |
| Final three-worker registry | Verified |
## 8. Outstanding work
1. Run the synchronization controller continuously as a managed service.
2. Test client requests during worker failure and measure failed requests.
3. Validate recovery with real SGLang GPU workers.
4. Verify production gateway registration and discovery.
5. Test the n8n OpenAI integration.
6. Complete real GPU benchmarking and remaining assignment criteria.
These Day 9 tests used local mock HTTP workers. They do not prove
real GPU inference recovery, prefix-cache performance or zero
client-request failures during an outage.
## 9. Conclusion
Day 9 established a working prototype for Consul-based worker discovery
and gateway synchronization.
The controller discovered healthy workers, removed stale gateway
registrations and restored a worker registration after Nomad automatically
restarted its task.
The expected control-plane recovery sequence was demonstrated using
three local mock workers.
The next step is continuous controller execution under Nomad, followed
by the remaining failure-acceptance tests and production GPU validation.
