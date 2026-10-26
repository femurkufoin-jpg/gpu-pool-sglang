"""Benchmark an OpenAI-compatible SGLang gateway endpoint."""
import argparse
import asyncio
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
import aiohttp

async def send_request(session, url, model, prompt, semaphore):
   payload = {
       "model": model,
       "messages": [{"role": "user", "content": prompt}],
       "max_tokens": 32,
       "temperature": 0,
   }
   async with semaphore:
       started = time.perf_counter()
       try:
           async with session.post(
               f"{url.rstrip('/')}/v1/chat/completions",
               json=payload,
           ) as response:
               body = await response.text()
               elapsed = time.perf_counter() - started
               if response.status >= 400:
                   return {
                       "ok": False,
                       "latency_seconds": elapsed,
                       "error": f"HTTP {response.status}: {body[:300]}",
                   }
               try:
                   data = json.loads(body)
               except json.JSONDecodeError:
                   return {
                       "ok": False,
                       "latency_seconds": elapsed,
                       "error": "Response was not valid JSON",
                   }
               return {
                   "ok": True,
                   "latency_seconds": elapsed,
                   "prompt_tokens": data.get("usage", {}).get(
                       "prompt_tokens", 0
                   ),
                   "completion_tokens": data.get("usage", {}).get(
                       "completion_tokens", 0
                   ),
               }
       except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
           return {
               "ok": False,
               "latency_seconds": time.perf_counter() - started,
               "error": str(exc),
           }

def percentile(values, pct):
   if not values:
       return None
   index = max(
       0,
       min(
           len(values) - 1,
           int((pct / 100) * len(values) + 0.999) - 1,
       ),
   )
   return round(values[index], 4)

async def run_benchmark(args, concurrency, repetition):
   timeout = aiohttp.ClientTimeout(total=args.timeout)
   semaphore = asyncio.Semaphore(concurrency)
   async with aiohttp.ClientSession(timeout=timeout) as session:
       started = time.perf_counter()
       results = await asyncio.gather(
           *[
               send_request(
                   session,
                   args.url,
                   args.model,
                   args.prompt,
                   semaphore,
               )
               for _ in range(args.requests)
           ]
       )
       duration = time.perf_counter() - started
   successful = [result for result in results if result["ok"]]
   latencies = [result["latency_seconds"] for result in successful]
   ordered = sorted(latencies)
   return {
       "repetition": repetition,
       "url": args.url,
       "model": args.model,
       "concurrency": concurrency,
       "requests_requested": args.requests,
       "requests_succeeded": len(successful),
       "requests_failed": len(results) - len(successful),
       "duration_seconds": round(duration, 4),
       "requests_per_second": round(len(successful) / duration, 4)
       if duration
       else 0,
       "latency_mean_seconds": round(statistics.mean(latencies), 4)
       if latencies
       else None,
       "latency_p50_seconds": percentile(ordered, 50),
       "latency_p95_seconds": percentile(ordered, 95),
       "latency_max_seconds": round(max(latencies), 4)
       if latencies
       else None,
       "errors": [
           result["error"] for result in results if not result["ok"]
       ][:10],
   }

def median_or_none(values):
   return round(statistics.median(values), 4) if values else None

def summarize_repetitions(concurrency, runs):
   return {
       "concurrency": concurrency,
       "repetitions": len(runs),
       "median_requests_per_second": median_or_none(
           [run["requests_per_second"] for run in runs]
       ),
       "median_latency_mean_seconds": median_or_none(
           [
               run["latency_mean_seconds"]
               for run in runs
               if run["latency_mean_seconds"] is not None
           ]
       ),
       "median_latency_p50_seconds": median_or_none(
           [
               run["latency_p50_seconds"]
               for run in runs
               if run["latency_p50_seconds"] is not None
           ]
       ),
       "median_latency_p95_seconds": median_or_none(
           [
               run["latency_p95_seconds"]
               for run in runs
               if run["latency_p95_seconds"] is not None
           ]
       ),
       "total_requests_succeeded": sum(
           run["requests_succeeded"] for run in runs
       ),
       "total_requests_failed": sum(
           run["requests_failed"] for run in runs
       ),
   }

def main():
   parser = argparse.ArgumentParser(
       description="Benchmark an OpenAI-compatible SGLang gateway."
   )
   parser.add_argument("--url", default="http://127.0.0.1:30000")
   parser.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
   parser.add_argument(
       "--prompt",
       default="Explain what a GPU does in two sentences.",
   )
   parser.add_argument("--requests", type=int, default=8)
   parser.add_argument(
       "--concurrency", type=int, nargs="+", default=[1, 8, 32]
   )
   parser.add_argument("--timeout", type=int, default=120)
   parser.add_argument("--repetitions", type=int, default=3)
   parser.add_argument(
       "--architecture",
       default="unspecified",
       help="Experiment architecture label, e.g. replicas or tp2",
   )
   parser.add_argument(
       "--routing-policy",
       default="unspecified",
       help="Experiment routing label, e.g. round_robin or cache_aware",
   )
   parser.add_argument("--output", default="benchmarks/results.json")
   args = parser.parse_args()
   if (
       args.requests < 1
       or args.repetitions < 1
       or any(concurrency < 1 for concurrency in args.concurrency)
   ):
       parser.error(
           "--requests, --repetitions, and concurrency values "
           "must be at least 1"
       )
   all_runs = []
   summaries = []
   for concurrency in args.concurrency:
       concurrency_runs = []
       for repetition in range(1, args.repetitions + 1):
           print(
               f"Concurrency={concurrency}, "
               f"repetition={repetition}/{args.repetitions}, "
               f"requests={args.requests}..."
           )
           run = asyncio.run(
               run_benchmark(args, concurrency, repetition)
           )
           concurrency_runs.append(run)
           all_runs.append(run)
           print(json.dumps(run, indent=2))
       summaries.append(
           summarize_repetitions(concurrency, concurrency_runs)
       )
   output_path = Path(args.output)
   output_path.parent.mkdir(parents=True, exist_ok=True)
   report = {
       "generated_at": datetime.now(timezone.utc).isoformat(),
       "note": (
           "Measurements describe only the configured endpoint. "
           "Mock endpoint results are not GPU performance evidence. "
           "Architecture and routing labels are user-supplied metadata."
       ),
       "configuration": {
           "url": args.url,
           "model": args.model,
           "requests_per_repetition": args.requests,
           "repetitions": args.repetitions,
           "concurrency_levels": args.concurrency,
           "architecture": args.architecture,
           "routing_policy": args.routing_policy,
       },
       "runs": all_runs,
       "median_summaries": summaries,
   }
   output_path.write_text(
       json.dumps(report, indent=2),
       encoding="utf-8",
   )
   print("\nMedian summaries:")
   print(json.dumps(summaries, indent=2))
   print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
   main()