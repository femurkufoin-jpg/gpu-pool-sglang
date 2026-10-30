import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

def request_json(url, method="GET", payload=None):
   data = None
   headers = {}
   if payload is not None:
       data = json.dumps(payload).encode("utf-8")
       headers["Content-Type"] = "application/json"
   request = urllib.request.Request(
       url,
       data=data,
       headers=headers,
       method=method,
   )
   with urllib.request.urlopen(request, timeout=10) as response:
       body = response.read().decode("utf-8")
       return json.loads(body) if body else {}

def worker_url(entry):
   service = entry.get("Service", {})
   node = entry.get("Node", {})
   address = service.get("Address") or node.get("Address")
   port = service.get("Port")
   if not address or not port:
       return None
   return f"http://{address}:{port}"

def ensure_safe_to_sync(managed, desired):
   if managed and not desired:
       raise SystemExit(
           "Safety stop: Consul has registered workers but none are healthy. "
           "No gateway changes were made."
       )

def load_state(state_file):
   path = Path(state_file)
   if not path.exists():
       return set()
   data = json.loads(path.read_text(encoding="utf-8"))
   return set(data.get("managed_urls", []))

def save_state(state_file, urls):
   path = Path(state_file)
   path.parent.mkdir(parents=True, exist_ok=True)
   path.write_text(
       json.dumps(
           {"managed_urls": sorted(urls)},
           indent=2,
       ),
       encoding="utf-8",
   )

def main():
   parser = argparse.ArgumentParser(
       description="Synchronize Consul workers with the SGLang Gateway."
   )
   parser.add_argument(
       "--consul",
       default="http://127.0.0.1:8500",
       help="Consul API address",
   )
   parser.add_argument(
       "--gateway",
       default="http://127.0.0.1:30000",
       help="SGLang Gateway address",
   )
   parser.add_argument(
       "--services",
       nargs="+",
       required=True,
       help="Consul service names to synchronize",
   )
   parser.add_argument(
       "--managed-url",
       action="append",
       default=[],
       help="Previously managed worker URL; may be supplied more than once",
   )
   parser.add_argument(
       "--state-file",
       default=".git/consul-gateway-sync-state.json",
       help="Persistent file containing previously managed worker URLs",
   )
   parser.add_argument(
       "--apply",
       action="store_true",
       help="Apply gateway changes; default is dry-run",
   )
   args = parser.parse_args()
   desired = set()
   registered = set()
   # Read workers currently registered in Consul.
   for service_name in args.services:
       encoded = urllib.parse.quote(service_name, safe="")
       base = f"{args.consul}/v1/health/service/{encoded}"
       all_entries = request_json(base)
       healthy_entries = request_json(base + "?passing=true")
       registered.update(
           url
           for entry in all_entries
           if (url := worker_url(entry))
       )
       desired.update(
           url
           for entry in healthy_entries
           if (url := worker_url(entry))
       )
   # Recover ownership information even when Consul has deregistered a worker.
   previously_managed = load_state(args.state_file)
   explicitly_managed = set(args.managed_url)
   managed = previously_managed | explicitly_managed | registered | desired
   # Read the gateway's existing worker registry.
   registry = request_json(f"{args.gateway}/workers")
   current = {
       worker["url"]: worker
       for worker in registry.get("workers", [])
       if worker.get("url")
   }
   additions = sorted(desired - current.keys())
   removals = [
       current[url]
       for url in sorted(managed - desired)
       if url in current
   ]
   print("Consul healthy workers:", sorted(desired))
   print("Previously managed workers:", sorted(previously_managed))
   print("Explicitly managed workers:", sorted(explicitly_managed))
   print("Workers to add:", additions)
   print(
       "Managed workers to remove:",
       [
           {"url": worker["url"], "id": worker["id"]}
           for worker in removals
       ],
   )
   ensure_safe_to_sync(managed, desired)
   if not args.apply:
       print("DRY RUN: no gateway changes or state updates made.")
       return
   # Add newly discovered healthy workers.
   for url in additions:
       result = request_json(
           f"{args.gateway}/workers",
           method="POST",
           payload={
               "url": url,
               "worker_type": "regular",
           },
       )
       print("Registration queued:", url, result)
   # Remove previously managed workers no longer healthy in Consul.
   for worker in removals:
       worker_id = urllib.parse.quote(worker["id"], safe="")
       request_json(
           f"{args.gateway}/workers/{worker_id}",
           method="DELETE",
       )
       print("Removal requested:", worker["url"])
   # Save the latest healthy worker set after successful synchronization.
   save_state(args.state_file, desired)
   print("Synchronization requests submitted.")
   print("State saved:", args.state_file)

if __name__ == "__main__":
   try:
       main()
   except (
       urllib.error.URLError,
       TimeoutError,
       ValueError,
       KeyError,
   ) as exc:
       raise SystemExit(
           f"Sync aborted; inspect the error before retrying: {exc}"
       )
