"""Rotate the static API_KEY used for admin / service auth."""
from __future__ import annotations

import secrets
import sys


def main() -> None:
    new_key = secrets.token_urlsafe(48)
    print("NEW API_KEY (update your secret store):")
    print(new_key)


if __name__ == "__main__":
    sys.exit(main() or 0)
