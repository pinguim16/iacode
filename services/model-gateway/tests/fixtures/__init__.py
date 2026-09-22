"""Deterministic doubles for the gateway suite.

Nothing in this package is reachable from a runtime path. The provider policy names no fake
provider, the application composes the SQLAlchemy stores, and the suite asserts both rather than
trusting the directory name to keep them apart.
"""
