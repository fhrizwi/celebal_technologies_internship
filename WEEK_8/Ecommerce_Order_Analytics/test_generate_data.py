import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GenerateDataTests(unittest.TestCase):
    def test_script_creates_csv_files(self):
        root = Path(__file__).resolve().parent
        data_dir = root / "data"
        if data_dir.exists():
            for file in data_dir.glob("*.csv"):
                file.unlink()

        result = subprocess.run(
            [sys.executable, "scripts/generate_data.py"],
            cwd=root,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue((data_dir / "customers.csv").exists())
        self.assertGreater((data_dir / "customers.csv").stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
