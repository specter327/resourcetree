"""Install each built artifact into a clean virtual environment and smoke-test it."""

from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv


def python_in(environment: Path) -> Path:
    executable = "python.exe" if os.name == "nt" else "python"
    scripts = "Scripts" if os.name == "nt" else "bin"
    return environment / scripts / executable


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribution", required=True)
    parser.add_argument("--import-name", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--core-wheel")
    args = parser.parse_args()

    artifacts = sorted(glob.glob("dist/*.whl") + glob.glob("dist/*.tar.gz"))
    if len(artifacts) != 2:
        raise SystemExit(f"expected exactly one wheel and one sdist, got: {artifacts}")

    for artifact in artifacts:
        with tempfile.TemporaryDirectory(prefix="distribution-smoke-") as temporary:
            root = Path(temporary)
            environment = root / "venv"
            venv.EnvBuilder(with_pip=True).create(environment)
            python = python_in(environment)
            if args.core_wheel:
                subprocess.check_call([str(python), "-m", "pip", "install", "--no-deps", args.core_wheel])
            subprocess.check_call([str(python), "-m", "pip", "install", artifact])
            code = (
                "from importlib import metadata; import "
                + args.import_name
                + " as package; "
                + f"assert metadata.version({args.distribution!r}) == {args.version!r}; "
                + "assert package.__file__ is not None; "
                + "print(package.__file__)"
            )
            result = subprocess.run(
                [str(python), "-c", code],
                cwd=root,
                check=True,
                text=True,
                capture_output=True,
            )
            print(f"PASS {Path(artifact).name}: {result.stdout.strip()}")


if __name__ == "__main__":
    main()
