import pathlib
import runpy
import shutil
import subprocess
import tempfile
import unittest

validate = runpy.run_path(str(pathlib.Path(__file__).with_name("validate-mirror.py")))["validate"]


class ValidateMirrorTest(unittest.TestCase):
    def test_script_preserves_old_snapshot_on_failure(self):
        self.run_script_case(fail=True)

    def test_script_promotes_valid_snapshot_and_retains_backup(self):
        self.run_script_case(fail=False)

    def run_script_case(self, fail):
        source = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            shutil.copy(source / "mirror.sh", root)
            (root / "scripts").mkdir()
            shutil.copy(source / "scripts/validate-mirror.py", root / "scripts")
            (root / "docs").mkdir()
            (root / "docs/old.md").write_text("old")
            (root / "settings.toml").write_text("")
            binary = root / "gcp-docs-mirror-tools"
            binary.write_text('''#!/bin/bash
set -e
while [[ $# -gt 0 ]]; do
    case "$1" in
        -docs) docs=$2 ;;
        -logs) logs=$2 ;;
        -metadata) metadata=$2 ;;
    esac
    shift 2
done
mkdir -p "$docs" "$logs"
echo new > "$docs/new.md"
echo 'file_count: 1' > "$metadata"
''' + ('echo "404 https://example.test/new"' if fail else 'echo ""') + ' > "$logs/failed.txt"\n')
            result = subprocess.run(["bash", "mirror.sh", "v0.3.1"], cwd=root, capture_output=True, text=True)
            if fail:
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((root / "docs/old.md").read_text(), "old")
                self.assertFalse((root / "docs/new.md").exists())
            else:
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((root / "docs/new.md").read_text().strip(), "new")
                backups = list((root / ".tmp").glob("mirror.*/previous/docs/old.md"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].read_text(), "old")

    def test_snapshot_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            stage = root / "stage"
            (stage / "docs").mkdir(parents=True)
            (stage / "logs").mkdir()
            (stage / "metadata.yaml").write_text("file_count: 1\n")
            failures = stage / "logs/failed.txt"
            failures.write_text("")
            previous = root / "previous"
            previous.mkdir()
            baseline = root / "failed.txt"
            with self.assertRaisesRegex(ValueError, "no documents"):
                validate(stage, previous, baseline)
            (stage / "docs/a.md").write_text("A")
            validate(stage, previous, baseline)
            failures.write_text("404 https://example.test/new\n")
            with self.assertRaisesRegex(ValueError, "new fetch failures"):
                validate(stage, previous, baseline)
            baseline.write_text(failures.read_text())
            validate(stage, previous, baseline)
            for i in range(10):
                (previous / f"{i}.md").write_text("Old document")
            with self.assertRaisesRegex(ValueError, "dropped"):
                validate(stage, previous, baseline)


if __name__ == "__main__":
    unittest.main()
