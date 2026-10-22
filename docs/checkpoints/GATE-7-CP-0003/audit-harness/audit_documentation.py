"""Run the unchanged sealed relative-link checker against the current corrective delivery."""

from acceptance_evidence import sealed_module

if __name__ == "__main__":
    raise SystemExit(sealed_module("audit_documentation").main())
