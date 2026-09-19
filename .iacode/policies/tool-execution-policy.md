# Tool Execution Policy

Use the least privilege and smallest scope required. Before execution, establish the working directory and validate destructive targets. Capture relevant command, sanitized arguments, timestamp, duration, exit code, and artifact locations.

Never log secrets. Do not force push, hard reset, destructively clean, or rewrite history without explicit authorization and a validated checkpoint immediately before the action.

No result is PASS merely because a command was proposed; it must have executed successfully and its output must support the claim.
