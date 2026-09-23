"""IACode Sandbox: policy-isolated execution of an agent's tools.

The service behind `GATE 3 — SANDBOX`. An agent's tool request becomes a structured execution
request, is checked against the canonical Sandbox Tool Policy, and runs inside a disposable,
hardened container that owns one run's workspace. See docs/runbooks/SANDBOX.md.
"""

__version__ = "0.1.0"
