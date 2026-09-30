#!/usr/bin/env python3
"""Local Comfy API preflight, explicit submission and bounded GLB/image collection.

Standard library only. No service startup, node/model installation, cancellation,
automatic resubmission, cloud endpoint, or image conversion. Workflows must be
reviewed API-format graphs. Custom nodes are refused by this narrow bridge.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import ipaddress
import json
import mimetypes
import os
from pathlib import Path
import re
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


class BridgeError(Exception):
    def __init__(self, message, details=None, http_status=None):
        super().__init__(message)
        self.details = details
        self.http_status = http_status


def local_url(value):
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != "http" or parsed.username or parsed.password
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise BridgeError("Use an HTTP loopback origin without credentials, path, query or fragment")
    host = parsed.hostname
    if host == "localhost":
        host = "127.0.0.1"
    try:
        if not ipaddress.ip_address(host).is_loopback:
            raise ValueError()
        port = parsed.port if parsed.port is not None else 8188
        if port < 1:
            raise ValueError()
    except (ValueError, TypeError):
        raise BridgeError("Only literal loopback addresses or localhost are supported") from None
    return f"http://{'[' + host + ']' if ':' in host else host}:{port}"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise BridgeError("HTTP redirects are refused")


class Client:
    def __init__(self, url, timeout=10):
        self.url = local_url(url)
        self.timeout = timeout
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def request(self, route, payload=None, content_type="application/json"):
        if not route.startswith("/") or route.startswith("//"):
            raise BridgeError("Invalid API route")
        request = urllib.request.Request(self.url + route, data=payload,
                                         headers={"Content-Type": content_type})
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                data = response.read(8 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            body = exc.read(1024 * 1024)
            try:
                details = json.loads(body)
            except (ValueError, UnicodeDecodeError):
                details = {"http_status": exc.code, "body": body.decode("utf-8", errors="replace")}
            raise BridgeError(f"Comfy HTTP {exc.code}", details, exc.code) from None
        except (OSError, urllib.error.URLError) as exc:
            raise BridgeError(f"Comfy connection failed: {type(exc).__name__}") from None
        if len(data) > 8 * 1024 * 1024:
            raise BridgeError("API response exceeds the 8 MiB limit")
        try:
            value = json.loads(data)
        except (ValueError, UnicodeDecodeError):
            raise BridgeError("Comfy returned invalid JSON") from None
        if not isinstance(value, dict):
            raise BridgeError("Comfy returned a non-object API response")
        return value

    def get(self, route):
        return self.request(route)

    def post(self, route, value):
        return self.request(route, json.dumps(value).encode("utf-8"))


def graph_from_file(path):
    graph = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(graph, dict) or not graph or "nodes" in graph or "prompt" in graph:
        raise BridgeError("Expected the raw API graph, not UI workflow JSON or a /prompt envelope")
    for node_id, node in graph.items():
        if (not isinstance(node_id, str) or not node_id or not isinstance(node, dict)
                or not isinstance(node.get("class_type"), str)
                or not isinstance(node.get("inputs"), dict)):
            raise BridgeError("Each API graph node needs class_type and inputs")
    return graph


def preflight(client, graph=None, node_classes=()):
    stats = client.get("/system_stats")
    classes = sorted(set(node_classes) | {n["class_type"] for n in (graph or {}).values()})
    report = {"status": "preflight_passed", "server": client.url, "nodes": [], "issues": [],
              "system": {k: stats.get("system", {}).get(k) for k in
                         ("os", "python_version", "comfyui_version", "pytorch_version")},
              "devices": [{k: d.get(k) for k in ("name", "type", "vram_total", "vram_free")}
                          for d in stats.get("devices", [])]}
    for class_type in classes:
        info = client.get("/object_info/" + urllib.parse.quote(class_type, safe="")).get(class_type)
        if not isinstance(info, dict):
            report["issues"].append(f"Missing node class: {class_type}")
            continue
        module = info.get("python_module", "")
        native = module == "nodes" or module.startswith("comfy_extras.")
        if info.get("api_node") or not native:
            report["issues"].append(f"Non-native or API node refused: {class_type}")
        required = info.get("input", {}).get("required", {})
        report["nodes"].append({"class_type": class_type, "python_module": module,
                                "api_node": bool(info.get("api_node")),
                                "required_inputs": sorted(required),
                                "output_node": bool(info.get("output_node"))})
        for node_id, node in (graph or {}).items():
            if node["class_type"] == class_type:
                absent = set(required) - set(node["inputs"])
                if absent:
                    report["issues"].append(f"Node {node_id} missing required inputs: {', '.join(sorted(absent))}")
    if report["issues"]:
        report["status"] = "preflight_failed"
    report["scope"] = "Node presence and required input names only; server validates links, types and model choices on submission. No inference proof."
    return report


def components(value, allow_empty=False):
    if allow_empty and value == "":
        return []
    if not isinstance(value, str) or ":" in value:
        raise BridgeError("Unsafe artifact path")
    parts = value.replace("\\", "/").split("/")
    for part in parts:
        if (part in ("", ".", "..") or part != part.rstrip(" .")
                or re.search(r'[<>"|?*\x00-\x1f]', part)
                or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part)):
            raise BridgeError("Unsafe artifact path")
    return parts


def unlinked(path):
    absolute = Path(os.path.abspath(path))
    for item in reversed([absolute, *absolute.parents]):
        try:
            mode = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode.st_mode) or getattr(mode, "st_file_attributes", 0) & 0x400:
            raise BridgeError("Linked/reparse path refused")
    return absolute


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(value, out, indent=2, ensure_ascii=True)
        out.write("\n")


def parse_input_map(values, graph):
    selected = []
    seen = set()
    for value in values:
        try:
            target, filename = value.split("=", 1)
            node_id, input_name = target.split(".", 1)
        except ValueError:
            raise BridgeError("Input mapping must be NODE.image=exact-local-file") from None
        if (target in seen or node_id not in graph or input_name != "image"
                or graph[node_id]["class_type"] != "LoadImage"):
            raise BridgeError("Only unique native LoadImage NODE.image mappings are supported")
        path = unlinked(Path(filename))
        if not path.is_file() or path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            raise BridgeError("Input must be an exact PNG, JPEG or WebP file")
        components(path.name)
        if path.stat().st_size > 64 * 1024 * 1024:
            raise BridgeError("Input exceeds the 64 MiB upload limit")
        seen.add(target)
        selected.append((node_id, input_name, path))
    return selected


def upload_image(client, path):
    data = path.read_bytes()
    if len(data) > 64 * 1024 * 1024:
        raise BridgeError("Input exceeds the 64 MiB upload limit")
    boundary = "comfybridge" + uuid.uuid4().hex
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    # A fresh name avoids accidentally changing an existing input referenced by another job.
    upload_name = "bridge-" + uuid.uuid4().hex + path.suffix.lower()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\nfalse\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{upload_name}\"\r\n"
            f"Content-Type: {content_type}\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    response = client.request("/upload/image", body, "multipart/form-data; boundary=" + boundary)
    if response.get("type") != "input":
        raise BridgeError("Upload response did not identify an input file", response)
    filename = components(response.get("name"))
    if len(filename) != 1:
        raise BridgeError("Upload returned a non-basename filename")
    name = "/".join(components(response.get("subfolder", ""), allow_empty=True) + filename)
    return name, {"source_name": path.name, "bytes": len(data),
                  "sha256": hashlib.sha256(data).hexdigest(), "server_input": name}


def poll_history(client, prompt_id, wait_seconds, poll_seconds):
    deadline = time.monotonic() + wait_seconds
    while True:
        history = client.get("/history/" + urllib.parse.quote(prompt_id, safe=""))
        entry = history.get(prompt_id)
        if isinstance(entry, dict):
            status = entry.get("status", {})
            failed = any(isinstance(m, list) and m and m[0] in ("execution_error", "execution_interrupted")
                         for m in status.get("messages", []))
            if failed or status.get("status_str") == "error":
                raise BridgeError("Comfy execution failed or was interrupted", entry)
            if status.get("completed"):
                if status.get("status_str") != "success":
                    raise BridgeError("Completed history lacks explicit success", entry)
                return entry
        if time.monotonic() >= deadline:
            raise BridgeError("Polling timed out; job may still be queued/running. Resume by prompt_id; do not automatically resubmit.")
        time.sleep(min(poll_seconds, max(0, deadline - time.monotonic())))


def collect_outputs(history, output_root, run_dir):
    root = unlinked(output_root).resolve()
    records = []
    seen = set()
    for node_id, outputs in history.get("outputs", {}).items():
        for kind in ("3d", "images", "latents"):
            for descriptor in outputs.get(kind, []):
                if not isinstance(descriptor, dict) or descriptor.get("type") != "output":
                    continue
                filename = components(descriptor.get("filename"))
                if len(filename) != 1:
                    raise BridgeError("Output filename must be a basename")
                parts = components(descriptor.get("subfolder", ""), allow_empty=True) + filename
                relative = "/".join(parts)
                if relative.casefold() in seen:
                    continue
                seen.add(relative.casefold())
                source = unlinked(root.joinpath(*parts))
                if not source.resolve().is_relative_to(root) or not source.is_file():
                    raise BridgeError("Output is missing or outside the configured Comfy output root")
                if source.suffix.lower() not in (".glb", ".obj", ".ply", ".stl", ".png", ".jpg", ".jpeg", ".webp", ".latent"):
                    raise BridgeError("Unsupported output format; use self-contained GLB or a supported image/mesh")
                # Local names are generated, never taken verbatim from server output.
                destination = run_dir / f"artifact-{len(records):03d}{source.suffix.lower()}"
                digest = hashlib.sha256()
                size = 0
                with source.open("rb") as src, destination.open("xb") as dst:
                    for block in iter(lambda: src.read(1024 * 1024), b""):
                        digest.update(block)
                        dst.write(block)
                        size += len(block)
                records.append({"node_id": node_id, "kind": kind, "server_relative_path": relative,
                                "file": destination.name, "bytes": size, "sha256": digest.hexdigest()})
    if not records:
        raise BridgeError("Successful execution had no supported output artifacts; inspect the saved history and saver node")
    return records


def run_job(client, graph, run_dir, output_root, mappings=(), resume=None, wait_seconds=900, poll_seconds=1):
    run_dir = unlinked(run_dir)
    root = unlinked(output_root)
    if not root.is_dir() or not run_dir.parent.is_dir():
        raise BridgeError("Comfy output root and run directory parent must already exist")
    selected = parse_input_map(mappings, graph or {}) if not resume else []
    if resume:
        try:
            resume = str(uuid.UUID(resume))
        except (ValueError, AttributeError):
            raise BridgeError("Resume requires a UUID prompt_id") from None
    else:
        report = preflight(client, graph)
        if report["issues"]:
            raise BridgeError("Preflight refused submission", report)
    run_dir.mkdir(exist_ok=False)
    record = {"server": client.url, "mode": "resume" if resume else "submit", "status": "preparing"}
    prompt_id = resume
    try:
        if resume:
            write_json(run_dir / "attempt.json", {**record, "prompt_id": resume})
        else:
            prompt = copy.deepcopy(graph)
            write_json(run_dir / "preflight.json", report)
            write_json(run_dir / "original-graph.json", graph)
            uploads = []
            for node_id, key, path in selected:
                name, receipt = upload_image(client, path)
                prompt[node_id]["inputs"][key] = name
                uploads.append({"node_id": node_id, "input": key, **receipt})
                write_json(run_dir / f"upload-{len(uploads):03d}.json", uploads[-1])
            payload = {"prompt": prompt, "client_id": str(uuid.uuid4())}
            write_json(run_dir / "submitted-graph.json", prompt)
            record["status"] = "submission_outcome_unknown"
            write_json(run_dir / "attempt.json", {**record, "client_id": payload["client_id"],
                       "graph_sha256": hashlib.sha256(json.dumps(prompt, sort_keys=True).encode()).hexdigest()})
            response = client.post("/prompt", payload)  # Deliberately never retried.
            write_json(run_dir / "submission.json", response)
            if response.get("error") or not response.get("prompt_id"):
                record["status"] = "submission_rejected_or_invalid_response"
                raise BridgeError("Prompt was not accepted", response)
            prompt_id = str(uuid.UUID(response["prompt_id"]))
        record.update({"prompt_id": prompt_id, "status": "queued_or_running"})
        history = poll_history(client, prompt_id, wait_seconds, poll_seconds)
        write_json(run_dir / "history.json", history)
        record.update({"status": "execution_succeeded_collection_pending"})
        record["artifacts"] = collect_outputs(history, root, run_dir)
        record["status"] = "collected"
        record["scope"] = "Comfy reports execution success; listed bytes copied and hashed. Geometry, appearance and game compatibility remain unverified."
        write_json(run_dir / "manifest.json", record)
        return record
    except (BridgeError, OSError, ValueError) as exc:
        if (record["status"] == "submission_outcome_unknown" and isinstance(exc, BridgeError)
                and exc.http_status == 400 and isinstance(exc.details, dict) and "error" in exc.details):
            record["status"] = "submission_rejected"
        if isinstance(exc, BridgeError) and exc.details is not None:
            write_json(run_dir / "error-details.json", exc.details)
        record.update({"error": str(exc)})
        if prompt_id:
            record["prompt_id"] = prompt_id
        write_json(run_dir / "failure.json", record)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8188")
    parser.add_argument("--workflow", type=Path, help="Raw API-format graph exported from the installed Comfy frontend")
    parser.add_argument("--node", action="append", default=[], help="Exact node class to query during read-only preflight")
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--submit", action="store_true", help="Explicitly upload mapped inputs and queue exactly one workflow")
    operation.add_argument("--resume", help="Collect one existing prompt_id without requeuing; use a fresh run directory")
    parser.add_argument("--input", action="append", default=[], help="With --submit: NODE.image=exact-local-image")
    parser.add_argument("--run-dir", type=Path, help="Fresh output directory; its parent must exist")
    parser.add_argument("--output-root", type=Path, help="Exact Comfy output directory on this same machine")
    parser.add_argument("--http-timeout", type=float, default=10)
    parser.add_argument("--wait-seconds", type=float, default=900)
    parser.add_argument("--poll-seconds", type=float, default=1)
    args = parser.parse_args(argv)
    try:
        if args.http_timeout <= 0 or args.wait_seconds < 0 or args.poll_seconds <= 0:
            raise BridgeError("Timeouts must be positive; wait-seconds may be zero for one history check")
        client = Client(args.url, args.http_timeout)
        graph = graph_from_file(args.workflow) if args.workflow else None
        if args.submit or args.resume:
            if not args.run_dir or not args.output_root or (args.submit and not graph):
                raise BridgeError("Submission needs --workflow; submit/resume require --run-dir and --output-root")
            if args.resume and (args.workflow or args.input):
                raise BridgeError("Resume uses an existing job and cannot take a workflow or new inputs")
            report = run_job(client, graph, args.run_dir, args.output_root, args.input, args.resume,
                             args.wait_seconds, args.poll_seconds)
        else:
            if args.input or args.run_dir or args.output_root:
                raise BridgeError("Input uploads and artifact directories require explicit --submit or --resume")
            report = preflight(client, graph, args.node)
        print(json.dumps(report, indent=2))
        return 1 if report.get("issues") else 0
    except (BridgeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
