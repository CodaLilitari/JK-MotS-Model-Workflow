"""A findings preview is a local draft, with no sending route or implicit consent."""
from email import policy
from email.parser import BytesParser
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/jk-mots-model-workflow/scripts/prepare_finding.py"
spec = importlib.util.spec_from_file_location("finding", SCRIPT)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


class FindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = self.root / "finding.md"
        self.report.write_text("A synthetic finding.\nSource credit: someone.\n", encoding="utf-8")

    def test_hash_binds_exact_recipient_subject_body_and_no_attachments(self):
        report, digest = f.prepare(self.report, "One finding")
        self.assertEqual(report["to"], "lilitarikiralv@gmail.com")
        self.assertEqual(report["attachments"], [])
        self.assertNotEqual(digest, f.prepare(self.report, "Changed subject")[1])
        self.report.write_text("Changed payload", encoding="utf-8")
        self.assertNotEqual(digest, f.prepare(self.report, "One finding")[1])

    def test_rejects_header_injection(self):
        with self.assertRaises(ValueError):
            f.prepare(self.report, "Finding\r\nBcc: unexpected@example.com")

    def test_draft_readback_and_no_existing_file_replacement(self):
        draft = self.root / "report.eml"
        command = [sys.executable, str(SCRIPT), "--report", str(self.report), "--draft", str(draft)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual(preview["status"], "draft_only_not_sent")
        message = BytesParser(policy=policy.default).parsebytes(draft.read_bytes())
        self.assertEqual(str(message["To"]), f.RECIPIENT)
        self.assertIsNone(message["From"])
        self.assertEqual(message.get_content().replace("\r\n", "\n"), preview["body"])
        original = draft.read_bytes()
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(draft.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
