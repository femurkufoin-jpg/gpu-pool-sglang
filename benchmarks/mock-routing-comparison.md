# Mock Routing Policy Comparison
## Objective
Compare round-robin and cache-aware routing through the local SGLang Model Gateway using mock workers.
## Test configuration
- Gateway endpoint: `http://127.0.0.1:30000`
- Model identifier: `mock-model`
- Prompt: `Repeated routing test prompt`
- Requests per concurrency level: 8
- Concurrency levels: 1, 8, and 32
- Routing policies: round-robin and cache-aware
## Results
| Concurrency | Policy | Successful | Failed | Requests/sec | Mean latency (s) | P95 latency (s) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Round-robin | 8 | 0 | 22.8164 | 0.0434 | 0.0887 |
| 1 | Cache-aware | 8 | 0 | 17.9760 | 0.0553 | 0.1051 |
| 8 | Round-robin | 8 | 0 | 23.9435 | 0.2899 | 0.3253 |
| 8 | Cache-aware | 8 | 0 | 22.7067 | 0.3044 | 0.3435 |
| 32 | Round-robin | 8 | 0 | 26.6581 | 0.2694 | 0.2879 |
| 32 | Cache-aware | 8 | 0 | 24.1430 | 0.2722 | 0.3144 |
## Interpretation
Round-robin had higher measured throughput and lower mean and P95 latency at all three concurrency settings in this run. All requests succeeded.
These measurements are preliminary mock-environment results. Only eight requests were sent at each concurrency level, so the results are not sufficient to establish a general performance advantage.
The mock workers do not reproduce GPU inference, SGLang prefix caching, or realistic KV-cache behavior. Therefore, these results cannot establish which policy performs better on real GPU workers.
## Raw evidence
- `benchmarks/mock-round-robin-retry.json`
- `benchmarks/mock-cache-aware-retry.json`
## Outstanding work
Repeat the comparison on real SGLang workers using the same model, prompt workload, request count, concurrency settings, and warm-up procedure. Record cache-hit metrics if available, repeat each test, and compare the results before recommending a production routing policy.
## Recovery and Load-Test Findings
### Recovery benchmark
The recovery test was saved to `benchmarks/mock-routing-recovery.json`.
The displayed test results show:
| Concurrency | Requests requested | Succeeded | Failed |
|---:|---:|---:|---:|
| 1 | 20 | 20 | 0 |
| 8 | 20 | 20 | 0 |
These results show successful requests at the displayed concurrency levels during this recovery benchmark.
### High-concurrency observation
An earlier load test recorded failures at concurrency 32. Gateway logs showed HTTP 503 responses, unavailable-worker errors, and circuit-breaker activity. This indicates that the mock setup did not handle that workload reliably during the observed run.
The gateway and both mock worker health endpoints subsequently responded successfully:
- Worker 1: `http://127.0.0.1:18000/health`
- Worker 2: `http://127.0.0.1:18001/health`
- Gateway: `http://127.0.0.1:30000/health`
Gateway metrics recorded both successful and failed upstream outcomes. These are cumulative metrics, so historical failures should not be interpreted as proof that the workers were still failing at the time of the health checks.
### Raw evidence
The following JSON files preserve benchmark results:
- `benchmarks/mock-round-robin-retry.json`
- `benchmarks/mock-cache-aware-retry.json`
- `benchmarks/mock-routing-recovery.json`
### Limitations
These tests use mock workers, not real SGLang model inference on GPUs. They do not establish real GPU throughput, prefix-cache hit rates, or production-grade failure recovery. The results are local integration evidence only.
### Next steps
When GPU workers become available:
1. Repeat the routing comparison using real SGLang workers.
2. Use the same model, prompt workload, request count, concurrency settings, and warm-up procedure for both policies.
3. Record cache-hit metrics if available.
4. Repeat each test and compare the results before recommending a production routing policy.
## Day 6 RoundRobin Retest
Raw results:
- `benchmarks/mock-day6-load-test.json` — initial high-concurrency run; concurrency 32 had 72 failures out of 100.
- `benchmarks/mock-day6-round-robin-retest.json` — retest after recreating the gateway with RoundRobin; all 100 requests succeeded at concurrency 1, 8, and 32.
The earlier gateway was configured with `cache_aware` while the benchmark metadata said `round_robin`. The gateway was recreated with the correct RoundRobin policy, its startup logs confirmed the policy, and the gateway and both mock worker health checks passed. The retest completed 300/300 requests successfully.
This is evidence of a successful local mock retest, not proof of real GPU performance or a definitive explanation of every earlier 503. The retest used one repetition; repeat runs are needed for stronger performance conclusions. Both raw result files are intentionally retained.
## Day 6 Repeatability Results
The repeatability run is recorded in `benchmarks/mock-day6-round-robin-repeatability.json`. Two repetitions of 100 requests were run at each concurrency level (1, 8, and 32). All 600 requests succeeded.
| Concurrency | Median throughput (req/s) | Median mean latency (s) | Median p95 latency (s) | Failed requests |
|---:|---:|---:|---:|---:|
| 1 | 17.7861 | 0.0660 | 0.1705 | 0 |
| 8 | 52.3803 | 0.1469 | 0.2630 | 0 |
| 32 | 47.9731 | 0.6048 | 1.1631 | 0 |
The results show successful mock requests in these runs, with increased latency at higher concurrency. They do not prove GPU performance, guarantee future circuit-breaker behavior, or establish a production routing recommendation.

## Day 6: Cache-Aware Routing Comparison (Mock Only)
The gateway was configured with `--policy cache_aware`. Its startup log confirmed the active CacheAware policy, and the gateway health endpoint and both mock worker health endpoints responded successfully before the full benchmark.
Raw results:
- `benchmarks/mock-day6-cache-aware-smoke.json` — 2-request smoke test
- `benchmarks/mock-day6-cache-aware-comparison.json` — full comparison workload
Workload:
- 100 requests per repetition
- 2 repetitions per concurrency level
- Concurrency levels: 1, 8, and 32
- Total requested: 600
Results:
| Concurrency | Requested | Succeeded | Failed | Median throughput (req/s) | Median p95 latency |
|---:|---:|---:|---:|---:|---:|
| 1 | 200 | 200 | 0 | 27.1633 | 0.0788 s |
| 8 | 200 | 200 | 0 | 56.8782 | 0.2520 s |
| 32 | 200 | 46 | 154 | 10.9342* | 1.0168 s* |
*At concurrency 32, repetition 1 had 46 successes and 54 failures; repetition 2 had 0 successes and 100 failures. The median throughput and latency are not reliable indicators of stable performance at this load.
The failures returned HTTP 503 with `no_available_workers` and the message that all circuits were open or unhealthy. This indicates a significant mock-gateway reliability issue at concurrency 32 that requires further investigation.
Limitations:
- These are local mock-worker measurements, not real SGLang inference or GPU performance.
- The RoundRobin repeatability run and CacheAware comparison were not necessarily executed under identical conditions; differences must not be interpreted as a conclusive policy ranking.
- No cache-hit rate was measured. Latency alone does not establish cache effectiveness.
- The gateway was subsequently restored to RoundRobin. Its startup log confirmed the RoundRobin policy, and the gateway and both worker health checks passed.
Conclusion: the cache-aware test succeeded at concurrency 1 and 8 but experienced substantial failures at concurrency 32. A controlled, repeated comparison with identical conditions and cache-hit metrics remains necessary before recommending a production routing policy.
