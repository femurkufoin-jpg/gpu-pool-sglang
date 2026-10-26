
# Day 6: GPU Benchmark Execution Runbook

## Purpose

Prepare a reproducible comparison of two independent SGLang model replicas against tensor parallelism (TP=2). This runbook is a procedure, not evidence that either deployment has been tested.

## Current status

- Local mock benchmark: completed.

- Benchmark harness unit tests: previously passed.

- Real GPU replica-versus-TP=2 comparison: pending GPU access.

- Production architecture recommendation: pending real measurements.

## 1. Preconditions

Before collecting real GPU results, confirm:

- Access to the target GPU servers and permission to run both deployment configurations.

- The exact SGLang version and model identifier.

- The GPU type, VRAM capacity, and number of available GPUs.

- The selected model and quantization load successfully.

- Two independent replicas can be reached through the gateway.

- A TP=2 deployment can be started using two supported GPUs.

- Both configurations expose a compatible OpenAI-style chat-completion endpoint.

- The gateway and workers pass their health checks.

Do not use local mock workers for the real GPU experiment.

## 2. Keep the workload consistent

Use the same model, quantization, prompt, request count, timeout, concurrency levels, warm-up procedure, and repetition count for both configurations.

Initial benchmark workload:

- Requests per repetition: 100

- Concurrency levels: 1, 8, and 32

- Repetitions: 3

- Warm-up: use the same documented warm-up procedure for both configurations

- Endpoint: the gateway serving the configuration under test

The benchmark script's --architecture and --routing-policy arguments record metadata labels. They do not deploy replicas, enable TP=2, or change the gateway's actual routing policy.

## 3. Measure the independent-replica configuration

First, deploy and verify two independent SGLang replicas using one model replica per suitable GPU. Confirm the gateway actually routes requests to both workers.

Record:

- Gateway URL and model identifier

- Model and quantization

- SGLang and gateway versions

- GPU model, VRAM, utilization, and memory usage

- Model load time

- Requests per second

- Mean, p50, and p95 latency

- Successful and failed requests

After substituting the real gateway URL and model identifier, run:

```powershell

python .\benchmarks\benchmark_gateway.py `

  --url "<REPLICA_GATEWAY_URL>" `

  --model "<MODEL_ID>" `

  --prompt "Explain how a web request travels through an application." `

  --requests 100 `

  --concurrency 1 8 32 `

  --repetitions 3 `

  --architecture replicas `

  --routing-policy round_robin `

  --output benchmarks/gpu-replicas.json

```

Only run this after the actual replica deployment is ready. The command itself does not create the deployment.

## 4. Measure the TP=2 configuration

Deploy the same model with tensor parallelism across two supported GPUs. Verify the deployment and gateway endpoint before benchmarking.

Use the same workload and settings:

```powershell

python .\benchmarks\benchmark_gateway.py `

  --url "<TP2_GATEWAY_URL>" `

  --model "<MODEL_ID>" `

  --prompt "Explain how a web request travels through an application." `

  --requests 100 `

  --concurrency 1 8 32 `

  --repetitions 3 `

  --architecture tp2 `

  --routing-policy round_robin `

  --output benchmarks/gpu-tp2.json

```

Replace the placeholders with real values. Do not run with mock endpoints and label the results as GPU measurements.

## 5. Capture GPU information

On the GPU host, capture `nvidia-smi` output before and during each configuration's benchmark. Record the GPU model, total VRAM, used VRAM, utilization, and any out-of-memory events.

Record model load time separately from request latency. Save dated logs or screenshots as evidence. Use the same observation method for both configurations.

If TP=2 spans two hosts, measure network latency and bandwidth and record the connection path before interpreting performance.

## 6. Results table

Fill this table only with verified raw results.

| Architecture | Concurrency | Throughput (req/s) | Mean latency (s) | p50 (s) | p95 (s) | Succeeded | Failed | GPU memory/utilization |

|---|---:|---:|---:|---:|---:|---:|---:|---|

| Replicas | 1 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

| Replicas | 8 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

| Replicas | 32 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

| TP=2 | 1 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

| TP=2 | 8 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

| TP=2 | 32 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

Compare the median across the three repetitions for each concurrency level. Preserve the raw JSON files. Investigate failed requests, outliers, and model or hardware differences before drawing conclusions.

## 7. Decision criteria

Do not select an architecture on throughput alone. Compare throughput, tail latency, reliability, GPU memory headroom, model load time, and operational complexity.

If measurements are incomplete or the workload is not comparable, state that the evidence is insufficient to recommend a winner.

## 8. Acceptance checklist

- [ ] Two independent replicas deployed and verified on real GPUs.

- [ ] TP=2 deployed and verified on real GPUs.

- [ ] Same workload and three repetitions completed at concurrency 1, 8, and 32.

- [ ] GPU memory, utilization, and model load time recorded.

- [ ] Raw JSON results saved for both architectures.

- [ ] Results table and limitations documented.

- [ ] Architecture recommendation supported by measured results.

Until GPU access is available, the hardware-dependent checklist items remain pending.

