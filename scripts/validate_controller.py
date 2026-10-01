#!/usr/bin/env python3
"""Fail closed if the public Composer runner drifts outside Decision 0020."""

from __future__ import annotations

from pathlib import Path

WORKFLOW = Path(".github/workflows/reconcile.yml")


def validate(text: str) -> None:
    required = [
        "workflow_dispatch:",
        "repository_dispatch:",
        "types: [composer-reconcile]",
        'cron: "55 * * * *"',
        "SOURCE_REPO: academic-door/academic-door-composer",
        "environment: production",
        "repository: academic-door/academic-door-composer",
        "ref: ${{ steps.source.outputs.sha }}",
        "persist-credentials: false",
        "COMPOSER_SOURCE_TOKEN",
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
        "python scripts/validate_bundle.py --site site",
        "python -m unittest discover -s tests -v",
        "node --test tests/*.test.mjs",
        "wrangler@4.107.0 deploy --config wrangler.jsonc",
        "d1 migrations apply PUBLICATIONS_DB --remote",
        'STATE_ISSUE_TITLE: "[runtime-state] Composer production acceptance"',
    ]
    missing = [value for value in required if value not in text]
    if missing:
        raise SystemExit(f"missing required controller contract: {missing}")

    on_block = text.split("permissions:", 1)[0]
    forbidden_triggers = [
        "pull_request:",
        "pull_request_target:",
        "issue_comment:",
        "workflow_run:",
    ]
    present_triggers = [value for value in forbidden_triggers if value in on_block]
    if present_triggers:
        raise SystemExit(f"forbidden production trigger surface: {present_triggers}")

    forbidden = [
        "actions/upload-artifact",
        "repository: ${{",
        "ref: ${{ inputs.",
        "github.event.pull_request",
        "github.event.client_payload",
    ]
    present = [value for value in forbidden if value in text]
    if present:
        raise SystemExit(f"forbidden production-controller surface: {present}")

    if "contents: write" in text:
        raise SystemExit("production reconcile must not require public-repo contents write")

    if "issues: write" not in text:
        raise SystemExit("public-safe acceptance marker requires bounded issues write")


def main() -> int:
    if not WORKFLOW.is_file():
        raise SystemExit(f"missing workflow: {WORKFLOW}")
    validate(WORKFLOW.read_text(encoding="utf-8"))
    print("Decision 0020 public-runner controller contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
