# Execution notes not emitted by the canonical ledger

The following exploratory read-only shell attempts occurred after checkpoint creation but outside
`record_command.py`. They are retained because the owner required failed attempts not to disappear.
They produced no repository or external-state mutation and are not evidence of subject behavior.

1. A PowerShell inventory command combining current checkpoint files and checklist counts exited
   nonzero before reading because the final pipeline contained an empty element. Effective error:
   `ParserError: An empty pipe element is not allowed.` Duration reported by the shell wrapper:
   2.8 seconds.
2. The corrected inventory command used the nonexistent path `docs/gates`, emitted
   `Cannot find path 'E:\iacode\docs\gates' because it does not exist`, then continued to read the
   current checkpoint documents. The actual canonical checklists were subsequently located at
   `docs/GATE-4-CHECKLIST.md` through `docs/GATE-7-CHECKLIST.md`. Duration: 2.6 seconds.
3. A read-only direct Git query confirmed canonical tag commits before freezing the transport
   reconstruction harness: CP0007 `e21d30fde473f302d0f8f60b59acf008fa52e250`, CP0009
   `ff2814f7d7bf06fa8a99858b958daf3f22197496`, and CP0001
   `823cf164c6931dab7f957c92721ded7a916655bd`. It changed no state; the values are independently
   rechecked inside each public clone by the recorded reconstruction command.
4. Read-only process diagnostics attempted `Get-CimInstance Win32_Process` once and received
   `Acesso negado`; later `Get-Process` snapshots exposed only PID/name/start/CPU/responding and
   never supplied command lines. They were used solely to distinguish active work from a stalled
   process. No process was signaled or stopped.
5. The canonical `tests` gate was selected as an offline control-plane suite from its registry
   description, but two Gate 5 cases and the dependency null control invoked Docker internally.
   Engine access was already denied, so no Docker resource was created, removed or inspected.
   The integral red result is preserved as `cmd-0015`; no selective rerun replaces it.

These mistakes are instrumentation limitations, not silently converted PASS results.
