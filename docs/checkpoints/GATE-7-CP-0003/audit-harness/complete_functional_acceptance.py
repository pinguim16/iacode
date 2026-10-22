"""Use the unchanged sealed functional mapping only after exact current complete execution."""

from acceptance_evidence import current_execution, main

__all__ = ["current_execution", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
