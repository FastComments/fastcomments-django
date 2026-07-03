#!/usr/bin/env python3
"""Bump the package version in pyproject.toml (the single source of truth).

`fastcomments_django.__version__` reads the installed metadata, so the version
lives only here.
"""

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python bump.py <new_version>   (e.g. python bump.py 0.2.0)")
        return 1

    new_version = sys.argv[1]
    pyproject = Path(__file__).resolve().parent / "pyproject.toml"
    text = pyproject.read_text()
    text, count = re.subn(r'(?m)^version = ".*"$', f'version = "{new_version}"', text, count=1)
    if count != 1:
        print("error: could not find a single version line in pyproject.toml")
        return 1
    pyproject.write_text(text)

    print(f"Bumped version to {new_version}")
    print(f"Next: git tag v{new_version} && git push origin v{new_version} && gh release create v{new_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
