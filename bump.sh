#!/bin/bash
# Bump the package version in pyproject.toml and fastcomments_django/__init__.py.
set -e

if [ -z "$1" ]; then
  echo "Usage: ./bump.sh <new_version>"
  echo "Example: ./bump.sh 0.2.0"
  exit 1
fi

NEW_VERSION=$1

sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
sed -i "s/^__version__ = .*/__version__ = \"$NEW_VERSION\"/" fastcomments_django/__init__.py

echo "Bumped version to $NEW_VERSION"
echo "Next: git tag v$NEW_VERSION && git push origin v$NEW_VERSION && gh release create v$NEW_VERSION"
