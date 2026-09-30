"""Synthetic localhost API contract tests; no Comfy process, weights or GPU work."""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "skills/jk-mots-model-workflow/scripts/comfy_bridge.py"
SPEC = importlib.util.spec_from_file_location("workflow_comfy_bridge", SCRIPT)
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)
JOB = "00000000-0000-4000-8000-000000000001"
GRAPH = {
    "1": {"class_type": "LoadImage", "inputs": {"image": "original.png"}},
    "2": {"class_type": "SyntheticMesh", "inputs": {"image": ["1", 0]}},
    "3": {"class_type": "SaveGLB", "inputs": {"mesh": ["2", 0], "filename_prefix": "study/candidate"}}
}
INFO = {
    "LoadImage": {"python_module": "nodes", "input": {"required": {"image": ["STRING"]}}},
    "SyntheticMesh": {"python_module": "comfy_extras.synthetic_test", "input": {"required": {"image": ["IMAGE"]}}},
    "SaveGLB": {"python_module": "comfy_extras.nodes_save_3d", "output_node": True,
                "input": {"required": {"mesh": ["MESH"], "filename_prefix": ["STRING"]}}}
}


class FixtureServer(ThreadingHTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, value, status=200):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.server.calls.append(("GET", self.path))
        if self.path == "/system_stats":
            self.send_json({"system": {"comfyui_version": "synthetic-fixture", "argv": ["PRIVATE-ARG-NOT-TO-SAVE"]}, "devices": []})
        elif self.path.startswith("/object_info/"):
            name = self.path.removeprefix("/object_info/")
            self.send_json({name: self.server.info[name]} if name in self.server.info else {})
        elif self.path == "/history/" + JOB:
            self.send_json(copy.deepcopy(self.server.history))
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "http://example.invalid/forbidden")
            self.end_headers()
        else:
            self.send_json({"error": "unknown fixture route"}, 404)

    def do_POST(self):
        payload = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.calls.append(("POST", self.path))
        if self.path == "/upload/image":
            self.server.uploads.append(payload)
            self.send_json({"name": "renamed-by-server.png", "subfolder": "accepted", "type": "input"})
        elif self.path == "/prompt":
            self.server.prompts.append(json.loads(payload))
            if self.server.reject:
                self.send_json({"error": {"type": "prompt_outputs_failed_validation"},
                                "node_errors": {"3": {"errors": [{"type": "bad_fixture_input"}]}}}, 400)
            else:
                self.send_json({"prompt_id": JOB, "number": 0, "node_errors": {}})
        else:
            self.send_json({"error": "unknown fixture route"}, 404)


class ComfyBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = FixtureServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="jk-mots-comfy-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.output = self.root / "comfy-output"
        (self.output / "study").mkdir(parents=True)
        self.mesh_bytes = b"synthetic fixture bytes; not a validated GLB"
        (self.output / "study/candidate.glb").write_bytes(self.mesh_bytes)
        self.graph_path = self.root / "graph.json"
        self.graph_path.write_text(json.dumps(GRAPH), encoding="utf-8")
        self.client = bridge.Client(self.url, timeout=2)
        self.server.calls, self.server.uploads, self.server.prompts = [], [], []
        self.server.info = copy.deepcopy(INFO)
        self.server.reject = False
        self.server.history = {JOB: {"status": {"completed": True, "status_str": "success", "messages": []},
                                    "outputs": {"3": {"3d": [{"filename": "candidate.glb", "subfolder": "study", "type": "output"}]}}}}

    def test_default_cli_preflight_is_read_only_and_does_not_save_server_argv(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = bridge.main(["--url", self.url, "--workflow", str(self.graph_path)])
        self.assertEqual(code, 0)
        self.assertTrue(all(method == "GET" for method, route in self.server.calls))
        self.assertNotIn("PRIVATE-ARG", stream.getvalue())
        self.assertEqual(json.loads(stream.getvalue())["status"], "preflight_passed")
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["comfy-output", "graph.json"])

    def test_missing_native_class_and_api_nodes_prevent_submission(self):
        for mode in ("missing", "api", "custom"):
            with self.subTest(mode=mode):
                self.server.info = copy.deepcopy(INFO)
                if mode == "missing":
                    del self.server.info["SyntheticMesh"]
                elif mode == "api":
                    self.server.info["SyntheticMesh"]["api_node"] = True
                else:
                    self.server.info["SyntheticMesh"]["python_module"] = "custom_nodes.unreviewed"
                with self.assertRaisesRegex(bridge.BridgeError, "Preflight refused"):
                    bridge.run_job(self.client, GRAPH, self.root / mode, self.output, wait_seconds=0)
                self.assertFalse((self.root / mode).exists())
        self.assertEqual(self.server.prompts, [])

    def test_upload_uses_returned_name_and_collects_3d_history_output(self):
        image = self.root / "approved.png"
        image.write_bytes(b"synthetic image fixture bytes")
        run = self.root / "run"
        result = bridge.run_job(self.client, GRAPH, run, self.output,
                                [f"1.image={image}"], wait_seconds=0)
        self.assertEqual(len(self.server.prompts), 1)
        self.assertEqual(self.server.prompts[0]["prompt"]["1"]["inputs"]["image"], "accepted/renamed-by-server.png")
        self.assertEqual(GRAPH["1"]["inputs"]["image"], "original.png")
        self.assertIn(b'name="overwrite"\r\n\r\nfalse', self.server.uploads[0])
        self.assertEqual(result["status"], "collected")
        self.assertEqual((run / result["artifacts"][0]["file"]).read_bytes(), self.mesh_bytes)
        self.assertEqual(json.loads((run / "submission.json").read_text())["prompt_id"], JOB)
        self.assertEqual(json.loads((run / "manifest.json").read_text())["artifacts"], result["artifacts"])

    def test_validation_error_preserves_details_and_never_requeues(self):
        self.server.reject = True
        run = self.root / "rejected"
        with self.assertRaisesRegex(bridge.BridgeError, "HTTP 400"):
            bridge.run_job(self.client, GRAPH, run, self.output, wait_seconds=0)
        self.assertEqual(len(self.server.prompts), 1)
        details = json.loads((run / "error-details.json").read_text())
        self.assertIn("3", details["node_errors"])
        self.assertEqual(json.loads((run / "failure.json").read_text())["status"], "submission_rejected")
        self.assertTrue((run / "attempt.json").is_file())
        self.assertFalse((run / "manifest.json").exists())

    def test_failed_or_interrupted_history_is_not_collected(self):
        for event in ("execution_error", "execution_interrupted"):
            with self.subTest(event=event):
                self.server.history[JOB]["status"]["messages"] = [[event, {"prompt_id": JOB}]]
                run = self.root / event
                with self.assertRaisesRegex(bridge.BridgeError, "failed or was interrupted"):
                    bridge.run_job(self.client, None, run, self.output, resume=JOB, wait_seconds=0)
                self.assertFalse(list(run.glob("artifact-*")))
                self.assertTrue((run / "error-details.json").is_file())
        self.assertFalse(any(method == "POST" for method, route in self.server.calls))

    def test_timeout_retains_prompt_id_without_cancel_or_resubmit(self):
        self.server.history = {}
        run = self.root / "pending"
        with self.assertRaisesRegex(bridge.BridgeError, "Polling timed out"):
            bridge.run_job(self.client, GRAPH, run, self.output, wait_seconds=0)
        self.assertEqual(len(self.server.prompts), 1)
        self.assertEqual(json.loads((run / "failure.json").read_text())["prompt_id"], JOB)
        self.assertFalse(any(route in ("/interrupt", "/queue", "/history") for method, route in self.server.calls))

    def test_output_traversal_is_refused_even_after_successful_execution(self):
        (self.root / "outside.glb").write_bytes(b"private")
        self.server.history[JOB]["outputs"]["3"]["3d"][0]["subfolder"] = ".."
        run = self.root / "unsafe-output"
        with self.assertRaisesRegex(bridge.BridgeError, "Unsafe artifact path"):
            bridge.run_job(self.client, None, run, self.output, resume=JOB, wait_seconds=0)
        self.assertFalse(list(run.glob("artifact-*")))
        self.assertEqual((self.root / "outside.glb").read_bytes(), b"private")

    def test_missing_saver_or_unconfirmed_success_cannot_be_a_success_manifest(self):
        for mode in ("no-output", "no-status"):
            with self.subTest(mode=mode):
                self.server.history[JOB]["status"] = {"completed": True, "status_str": "success", "messages": []}
                if mode == "no-output":
                    self.server.history[JOB]["outputs"] = {}
                else:
                    del self.server.history[JOB]["status"]["status_str"]
                run = self.root / mode
                with self.assertRaises(bridge.BridgeError):
                    bridge.run_job(self.client, None, run, self.output, resume=JOB, wait_seconds=0)
                self.assertFalse((run / "manifest.json").exists())

    def test_optional_native_latent_output_is_preserved_without_loading_it(self):
        latent = self.output / "study/source.latent"
        latent.write_bytes(b"synthetic latent bytes, never deserialized by the bridge")
        self.server.history[JOB]["outputs"]["4"] = {
            "latents": [{"filename": "source.latent", "subfolder": "study", "type": "output"}]}
        run = self.root / "latent-copy"
        result = bridge.run_job(self.client, None, run, self.output, resume=JOB, wait_seconds=0)
        records = [a for a in result["artifacts"] if a["kind"] == "latents"]
        self.assertEqual(len(records), 1)
        self.assertEqual((run / records[0]["file"]).read_bytes(), latent.read_bytes())

    def test_remote_origins_credentials_paths_and_redirects_are_refused(self):
        for url in ("http://example.com:8188", "https://127.0.0.1:8188", "http://user:password@localhost:8188",
                    "http://localhost:8188/proxy", "http://localhost:8188/?secret=value"):
            with self.subTest(url=url), self.assertRaises(bridge.BridgeError):
                bridge.Client(url)
        with self.assertRaisesRegex(bridge.BridgeError, "redirects"):
            self.client.get("/redirect")

    def test_api_graph_required_and_existing_run_directory_preserved(self):
        self.graph_path.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
        with self.assertRaisesRegex(bridge.BridgeError, "raw API graph"):
            bridge.graph_from_file(self.graph_path)
        run = self.root / "existing"
        run.mkdir()
        (run / "keep.txt").write_bytes(b"unchanged")
        with self.assertRaises(FileExistsError):
            bridge.run_job(self.client, GRAPH, run, self.output, wait_seconds=0)
        self.assertEqual((run / "keep.txt").read_bytes(), b"unchanged")
        self.assertEqual(self.server.prompts, [])

    def test_uncertain_submission_preserves_attempt_and_does_not_retry(self):
        run = self.root / "unknown"
        with mock.patch.object(self.client, "post", side_effect=bridge.BridgeError("response lost")) as post:
            with self.assertRaisesRegex(bridge.BridgeError, "response lost"):
                bridge.run_job(self.client, GRAPH, run, self.output, wait_seconds=0)
        self.assertEqual(post.call_count, 1)
        self.assertEqual(json.loads((run / "failure.json").read_text())["status"], "submission_outcome_unknown")
        self.assertTrue((run / "attempt.json").is_file())


if __name__ == "__main__":
    unittest.main()
