#!/usr/bin/env python3
"""Preview a source finding and optionally create an email draft. Never sends mail."""
from __future__ import annotations
import argparse
from email.message import EmailMessage
from email.policy import SMTP
import hashlib
import json
from pathlib import Path

RECIPIENT = "lilitarikiralv@gmail.com"


def prepare(report, subject):
    if not subject.strip() or any(c in subject for c in "\r\n"):
        raise ValueError("Use one non-empty subject line")
    data = Path(report).read_bytes()
    if len(data) > 64 * 1024:
        raise ValueError("Keep the report below 64 KiB; link separately reviewed public evidence")
    body = data.decode("utf-8-sig").replace("\r\n", "\n")
    if not body.strip():
        raise ValueError("Report is empty")
    if not body.endswith("\n"):
        body += "\n"
    exact = {"to": RECIPIENT, "subject": subject.strip(), "body": body, "attachments": []}
    digest = hashlib.sha256(json.dumps(exact, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return exact, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", type=Path, required=True, help="User-reviewed UTF-8 text/Markdown")
    p.add_argument("--subject", default="JK/MotS workflow: proposed research finding")
    p.add_argument("--draft", type=Path, help="Optional new .eml path; never overwrite a file")
    args = p.parse_args()
    try:
        exact, digest = prepare(args.report, args.subject)
        if args.draft:
            if args.draft.suffix.lower() != ".eml":
                raise ValueError("Draft path must end in .eml")
            message = EmailMessage(policy=SMTP)
            message["To"] = exact["to"]
            message["Subject"] = exact["subject"]
            message.set_content(exact["body"])
            with args.draft.open("xb") as f:
                f.write(message.as_bytes())
        print(json.dumps({"status": "draft_only_not_sent", "report_sha256": digest,
                          "review_required": "Show this exact content and obtain explicit permission before any email send.",
                          **exact}, indent=2, ensure_ascii=True))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "not_sent", "error": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
