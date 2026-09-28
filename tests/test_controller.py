from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_controller.py"
spec = importlib.util.spec_from_file_location("validate_controller", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class ControllerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = (ROOT / ".github" / "workflows" / "reconcile.yml").read_text(encoding="utf-8")

    def test_current_controller_passes(self) -> None:
        module.validate(self.workflow)

    def test_arbitrary_ref_is_rejected(self) -> None:
        mutated = self.workflow.replace(
            "ref: ${{ steps.source.outputs.sha }}",
            "ref: ${{ inputs.ref }}",
        )
        with self.assertRaises(SystemExit):
            module.validate(mutated)

    def test_pr_secret_path_is_rejected(self) -> None:
        mutated = self.workflow.replace(
            "  workflow_dispatch:\n",
            "  workflow_dispatch:\n  pull_request:\n",
        )
        with self.assertRaises(SystemExit):
            module.validate(mutated)

    def test_artifact_persistence_is_rejected(self) -> None:
        mutated = self.workflow + "\n# actions/upload-artifact\n"
        with self.assertRaises(SystemExit):
            module.validate(mutated)


if __name__ == "__main__":
    unittest.main()
