# Day 7: Controlled Routing Benchmark and Analysis Plan
## Objective
Prepare a reproducible comparison of RoundRobin and CacheAware routing for the GPU Pool SGLang project. Existing local mock results are preliminary evidence only; this plan defines the conditions required for a fair comparison.
## Current baseline
- RoundRobin repeatability evidence:
 `benchmarks/mock-day6-round-robin-repeatability.json`
- CacheAware comparison evidence:
 `benchmarks/mock-day6-cache-aware-comparison.json`
- CacheAware smoke-test evidence:
 `benchmarks/mock-day6-cache-aware-smoke.json`
- GPU benchmark procedure:
 `docs/day6-gpu-benchmark-runbook.md`
- Benchmark harness:
 `benchmarks/benchmark_gateway.py`
The existing RoundRobin and CacheAware runs must not be treated as a conclusive policy ranking. They use mock workers, do not measure real SGLang prefix-cache behavior, and were not guaranteed to run under identical conditions.
## Controlled comparison procedure
When suitable GPU-backed SGLang workers are available:
1. Use the same model, model configuration, prompt, request count, concurrency levels, timeout, and warm-up procedure for both routing policies.
2. Use the same two healthy workers and the same gateway image/version.
3. Run RoundRobin and CacheAware separately at concurrency 1, 8, and 32.
4. Run at least three repetitions per policy and concurrency level.
5. Record the active gateway policy from startup logs before each run.
6. Save each raw benchmark result to a separate JSON file.
7. Capture gateway and worker health before and after each run.
8. Record errors and HTTP status codes; do not discard failed runs.
9. Record cache-hit metrics only if a reliable gateway metric is available. Do not infer cache hits from latency.
10. Compare median throughput, mean latency, p50/p95 latency, success/failure counts, and cache-hit rate when available.
## Required measurements
For every policy and concurrency level, record:
- Requested, successful, and failed requests
- Throughput in requests per second
- Mean, p50, p95, and maximum latency
- HTTP status codes and gateway error messages
- Gateway image/version and active routing policy
- Model identifier and prompt/workload details
- Worker health before and after the run
- Cache-hit metrics, if exposed and verified
- GPU type, memory, utilization, and model configuration for real GPU tests
## Mock-environment follow-up
The existing CacheAware mock run recorded 154 failures out of 200 requests at concurrency 32 across two repetitions. Errors included HTTP 503 `no_available_workers`.
Follow-up investigation should determine whether the failures are associated with worker circuit-breaker behavior, gateway load handling, or other configuration/runtime conditions. Preserve the original failure evidence. A successful health check after a test does not by itself prove that the gateway recovered correctly during traffic.
If repeating the mock test, use identical request counts, concurrency levels, timeouts, gateway version, worker setup, and repetition counts for both policies. Label all results as mock-only.
## Acceptance criteria
- [ ] Both policies tested under matched conditions.
- [ ] At least three repetitions completed per policy and concurrency level, or deviations documented.
- [ ] Raw JSON results preserved for every run, including failures.
- [ ] Active policy verified from gateway startup logs.
- [ ] Throughput, latency, and failure results compared.
- [ ] Cache-hit rate included only if a reliable metric is available.
- [ ] Conclusions distinguish mock tests from real SGLang GPU inference.
- [ ] No production routing recommendation made from mock results alone.
## GPU and architecture limitations
Real SGLang inference and the comparison of independent replicas against tensor parallelism (TP=2) remain pending access to suitable NVIDIA GPU hardware.
The benchmark script's `--architecture` and `--routing-policy` options record experiment labels. They do not deploy an architecture or change the running gateway policy.
## Day 7 outcome
The controlled benchmark procedure and acceptance criteria are documented. Actual GPU results and a conclusive routing-policy recommendation remain pending the required environment and measurements.
## Worker Discovery Decision — Proposed
**Preferred initial approach:** Use Consul as the source of truth for healthy SGLang workers. Render the current worker URL list into the gateway's supported `--worker-urls` configuration and perform a controlled gateway restart when worker membership changes.
**Why this approach:** The current gateway job passes worker URLs as command-line arguments. The project has not yet verified native Consul watch or automatic worker registration/removal in the selected SGLang Model Gateway version. The rendered-list approach avoids assuming that Consul registration alone updates the gateway's routing pool.
**Local validation required:**
- Confirm the selected gateway version and its supported configuration options.
- Verify that the worker service query returns only healthy, eligible workers.
- Confirm that the rendered list contains both mock workers and produces valid gateway arguments.
- Test adding and removing a mock worker, then verify the gateway uses the updated list after restart.
- Verify gateway health and request success after each change.
**Limitations:** This is a proposed discovery design, not a completed integration. The current local gateway uses explicit mock worker URLs. Production discovery, real SGLang inference, and failure recovery remain pending validation.
