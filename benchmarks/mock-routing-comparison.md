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
