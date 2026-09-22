"""Thin, stable entry points for the gates `.iacode/policies/quality-gates.json` declares.

Each module here runs one gate and exits with its result. They exist so the registry can name a
command that does not change when the underlying invocation does: the registry is policy, and a
policy that has to be edited whenever a container flag changes is a policy nobody trusts.
"""
