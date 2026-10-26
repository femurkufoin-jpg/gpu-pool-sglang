Days 5â€“7: GPU Benchmark Plan
1. Objective
Prepare a repeatable procedure to evaluate GPU model placement, deployment architecture, and gateway routing for the GPU pool project. The existing benchmark harness measures request success, throughput, and latency against an OpenAI-compatible chat-completion endpoint.
Real performance comparisons require access to the target GPU servers and actual SGLang workers. Local mock results are functional test evidence only.
2. Existing Benchmark Harness
Script: benchmarks/benchmark_gateway.py
The script supports:
Configurable gateway URL and model name
Configurable prompt and request count
Concurrency levels of 1, 8, and 32
Request timeout configuration
Successful and failed request counts
Throughput in requests per second
Mean, p50, p95, and maximum latency
JSON output for repeatable results
The existing unit test is tests/test_benchmark_gateway.py.
3. Experiment A: GPU Model Sizing
Test candidate models on the available GPUs.
GPU
Memory
Measurements
RTX 3060
12 GB
Model memory, KV-cache capacity, latency, throughput, out-of-memory events
RTX 3060 Ti
8 GB
Model memory, KV-cache capacity, latency, throughput, out-of-memory events
Evaluate suitable quantized 7Bâ€“8B models on 12 GB GPUs, including AWQ or GPTQ where supported. Evaluate smaller embedding models, such as BGE-M3 if compatible with the available memory and runtime, on 8 GB GPUs.
Record the exact model, quantization, SGLang version, GPU type, memory usage, and whether the model loads successfully. Do not assume that a model fits based only on its parameter count.
4. Experiment B: Independent Replicas vs Tensor Parallelism
Compare:
Two independent model replicas, one per GPU.
A tensor-parallel deployment using two GPUs, where supported by the model and hardware.
Run the same model, prompt set, request count, and warm-up procedure at concurrency 1, 8, and 32. Repeat each run and report the median result.
Record:
Requests per second
Mean, p50, and p95 latency
Successful and failed requests
GPU memory usage
GPU utilization
Model load time
For tensor parallelism across separate hosts, measure network bandwidth and latency first. The routed link may be unsuitable for the high-volume communication required by distributed inference.
5. Experiment C: Cache-Aware vs Round-Robin Routing
Use a consistent system prompt and repeated RAG context to create opportunities for prefix-cache reuse.
Compare the supported cache-aware routing policy with round-robin routing under the same workload. Record:
Throughput and latency
Prefix-cache hit rate, if exposed by the runtime or gateway
Successful and failed requests
Worker distribution
Token counts and workload details
Confirm the gateway actually supports the selected cache-aware policy before running the comparison. Do not infer cache hits from latency alone.
6. Result Recording
Store each run with its date, model, quantization, GPU, architecture, routing policy, concurrency, request count, and raw JSON output.
Keep mock results separate from real GPU results. The file benchmarks/mock-results.json contains local mock measurements and must not be used as GPU performance evidence.
7. Current Status
Benchmark harness implemented and its existing unit test passed.
Local mock benchmark completed at concurrency 1, 8, and 32, with 8 requests per run and no failed requests.
Real GPU model sizing and performance comparisons remain pending GPU access.
Cache-aware routing and distributed tensor-parallel performance remain unverified until tested on the actual deployment.
8. Completion Criteria
The benchmark stage is complete when the model-sizing observations are recorded, both deployment architectures are measured under the specified concurrency levels, both routing policies are compared using the same workload, and raw results and conclusions are committed to the repository.
9. Day 6: Repeated Mock Benchmark and Architecture Comparison Preparation
Objective
Validate the benchmark harness using three repetitions at concurrency 1, 8, and 32, and prepare a fair comparison between independent model replicas and tensor parallelism (TP=2).
Environment and method
Gateway: http://127.0.0.1:30000
Model label: Qwen/Qwen2.5-3B-Instruct
Architecture label: replicas
Routing-policy label: round_robin
Requests per repetition: 8
Repetitions per concurrency level: 3
Raw results: benchmarks/mock-day6-replicas.json
Mock benchmark results
Concurrency | Median throughput (req/s) | Median mean latency (s) | Median p50 latency (s) | Median p95 latency (s) | Succeeded / Failed
1 | 24.7105 | 0.0403 | 0.0307 | 0.0825 | 24 / 0
8 | 33.0988 | 0.1905 | 0.1961 | 0.2327 | 24 / 0
32 | 40.3392 | 0.1631 | 0.1604 | 0.1904 | 24 / 0
All 72 requests succeeded across nine repetitions. These measurements are from the local mock gateway and are not real SGLang inference or GPU-performance results.
Replica versus TP=2 procedure (pending GPU access)
1. Deploy two independent SGLang workers, with one model replica per suitable GPU, behind the gateway.
2. Deploy the same model and compatible configuration using tensor parallelism across two GPUs.
3. Use the same prompt, request count, concurrency levels (1, 8, and 32), warm-up procedure, and repetitions for both architectures.
4. Record model and quantization, GPU type and memory, model-load time, throughput, mean/p50/p95 latency, request successes and failures, and GPU utilization.
5. Save raw JSON results and compare medians across repetitions.
6. If TP spans hosts, measure network bandwidth and latency before drawing conclusions.
The --architecture and --routing-policy options record experiment labels only. They do not deploy or configure the selected architecture or routing policy.
Day 6 status
Completed: repeated local mock-gateway benchmark at concurrency 1, 8, and 32.
Completed: results saved to benchmarks/mock-day6-replicas.json.
Verified: both unit tests pass and gateway health returned OK.
Pending: actual GPU replica and TP=2 benchmarks because the target GPU servers are unavailable.
Pending: production architecture recommendations based on real GPU measurements.
Mock results validate the benchmark workflow only. They must not be used to claim that replicas outperform TP=2 or to make a production performance recommendation.
## 10. Day 6: High-Concurrency RoundRobin Retest
Purpose
Investigate the earlier concurrency-32 failures and verify the local mock gateway after correcting the routing-policy mismatch.
Initial failure
Raw results: benchmarks/mock-day6-load-test.json
At concurrency 1, 100/100 requests succeeded.
At concurrency 8, 100/100 requests succeeded.
At concurrency 32, 28/100 requests succeeded and 72 failed with HTTP 503 no_available_workers errors. Gateway metrics and logs showed circuit-breaker activity.
Investigation and correction
Both Nomad mock workers and the gateway health endpoint subsequently returned healthy responses. Gateway metrics showed both worker circuit breakers had opened during previous traffic. Inspection also established that the running gateway used cache_aware even though the benchmark metadata said round_robin.
The gateway was recreated using the round_robin policy. Its startup logs confirmed RoundRobin, and the gateway and both worker health checks passed.
Retest results
Raw results: benchmarks/mock-day6-round-robin-retest.json
Requests per concurrency level: 100
Repetitions: 1
| Concurrency | Succeeded | Failed | Throughput (req/s) | Mean latency (s) | P95 latency (s) |
|---:|---:|---:|---:|---:|---:|
| 1 | 100 | 0 | 31.8135 | 0.0313 | 0.0460 |
| 8 | 100 | 0 | 32.0829 | 0.2382 | 1.0625 |
| 32 | 100 | 0 | 40.1043 | 0.7144 | 1.0257 |
Interpretation
The retest completed all 300 requests without failures after the gateway was configured for RoundRobin. Mean and tail latency increased under concurrency, so throughput alone should not be treated as the only performance indicator.
This was one retest repetition, not a statistically robust performance comparison. The earlier failed run is retained and must not be discarded. The result does not prove the underlying circuit-breaker issue can never recur.
Validation
The benchmark JSON was confirmed to exist. Both benchmark unit tests passed, and git diff --check reported no whitespace errors.
Limitations and status
These results use local mock workers, not actual SGLang inference on GPUs. They do not establish GPU performance, prefix-cache hit rates, or production-grade recovery. Real GPU replica-versus-TP=2 and routing-policy comparisons remain pending GPU access.
