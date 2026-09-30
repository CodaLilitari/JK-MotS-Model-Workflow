#!/usr/bin/env python3
"""Read-only 3DO hierarchy / KEY allocation inspector; not a full format validator."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def clean(text):
    return "\n".join(line.split("#", 1)[0].strip() for line in text.splitlines())


def one_int(text, pattern, label):
    values = re.findall(pattern, text, re.I | re.M)
    if len(values) != 1:
        raise ValueError(f"Expected one {label} declaration; found {len(values)}")
    return int(values[0])


def parse_model(text):
    text = clean(text)
    count = one_int(text, r"^HIERARCHY\s+NODES\s+(\d+)\s*$", "HIERARCHY NODES")
    block = re.split(r"^HIERARCHY\s+NODES\s+\d+\s*$", text, flags=re.I | re.M)[1]
    block = re.split(r"^SECTION\s*:", block, flags=re.I | re.M)[0]
    nodes = []
    for line in block.splitlines():
        if not line.strip():
            continue
        match = re.match(r"^(\d+):\s+(.+)$", line)
        if not match:
            raise ValueError("Unrecognized hierarchy record")
        fields = match[2].split()
        if len(fields) < 17:
            raise ValueError("Truncated hierarchy record")
        nodes.append({"index": int(match[1]), "mesh": int(fields[2]),
                      "parent": int(fields[3]), "child": int(fields[4]),
                      "sibling": int(fields[5]), "children": int(fields[6]),
                      "name": " ".join(fields[16:])})
    if [n["index"] for n in nodes] != list(range(count)):
        raise ValueError("Hierarchy indices/count are not consecutive and consistent")
    if not nodes:
        raise ValueError("Empty model hierarchy")
    for node in nodes:
        for field in ("parent", "child", "sibling"):
            if not -1 <= node[field] < count:
                raise ValueError(f"Node {node['index']} {field} is outside hierarchy")
        seen = set()
        current = node["index"]
        while current != -1:
            if current in seen:
                raise ValueError("Parent cycle in hierarchy")
            seen.add(current)
            current = nodes[current]["parent"]
    return {"hierarchy_nodes": count, "nodes": nodes}


def parse_key(text):
    text = clean(text)
    joints = one_int(text, r"^JOINTS\s+(\d+)\s*$", "JOINTS")
    count = one_int(text, r"^NODES\s+(\d+)\s*$", "NODES")
    indices = []
    for line in text.splitlines():
        if re.match(r"^NODE\b", line, re.I):
            match = re.fullmatch(r"NODE\s+(\d+)", line, re.I)
            if not match:
                raise ValueError("Malformed or negative KEY NODE index")
            indices.append(int(match[1]))
    if len(indices) != count or len(set(indices)) != len(indices):
        raise ValueError("KEY NODE records are duplicated or disagree with NODES count")
    if any(x >= joints for x in indices):
        raise ValueError("KEY track index is outside declared JOINTS allocation")
    return {"joints": joints, "node_records": count, "track_indices": indices}


def read_record(path, parser):
    data = path.read_bytes()
    return {"file": path.name, "sha256": hashlib.sha256(data).hexdigest(),
            **parser(data.decode("latin1"))}


def inspect(model_path, keys, reference_keys=(), detail_start=None):
    model = read_record(model_path, parse_model)
    parsed_keys = [read_record(p, parse_key) for p in keys]
    refs = [read_record(p, parse_key) for p in reference_keys]
    issues = []
    observations = []
    for key in parsed_keys:
        if key["joints"] < model["hierarchy_nodes"]:
            issues.append({"file": key["file"], "kind": "allocation_too_small",
                           "required": model["hierarchy_nodes"], "actual": key["joints"]})
        outside = [n for n in key["track_indices"] if n >= model["hierarchy_nodes"]]
        if outside:
            observations.append({"file": key["file"], "kind": "tracks_absent_from_model", "indices": outside,
                                 "meaning": "Not automatically invalid; reserve the original declared domain before appending details"})
    reserved = max((k["joints"] for k in refs), default=None)
    if detail_start is not None:
        if not 0 <= detail_start <= model["hierarchy_nodes"]:
            raise ValueError("detail-start must be within model index domain or its end")
        if reserved is None:
            raise ValueError("detail-start requires reference-keys for the original rig domain")
        if detail_start < reserved:
            issues.append({"kind": "detail_overlaps_reserved_domain", "detail_start": detail_start,
                           "reference_joint_domain": reserved})
    return {"schema_version": 1, "status": "issues_found" if issues else "checks_passed",
            "scope": "Hierarchy indices, parent cycles, KEY allocation and optional reserved domain only; no runtime certification",
            "model": model, "keys": parsed_keys, "reference_keys": refs,
            "reserved_joint_domain": reserved, "issues": issues, "observations": observations}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--keys", type=Path, nargs="+", required=True,
                   help="Exact local KEY files used by the candidate; pass all relevant states")
    p.add_argument("--reference-keys", type=Path, nargs="*", default=[],
                   help="Original rig KEYs before allocation padding, to reserve the complete original domain")
    p.add_argument("--detail-start", type=int, help="First appended detail-node index")
    args = p.parse_args()
    try:
        result = inspect(args.model, args.keys, args.reference_keys, args.detail_start)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "input_error", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
