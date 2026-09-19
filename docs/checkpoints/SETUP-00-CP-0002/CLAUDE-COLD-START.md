# Claude Code Cold-Start Evidence

Result: `BLOCKED_AUTHENTICATION`

This is not a cross-provider PASS. It proves that the detected Claude Code executable starts from a clean clone, then stops before model execution because the local installation is not authenticated.

## Isolated input

- Clone command: `git clone --no-local --quiet E:\iacode C:\Users\cesar\AppData\Local\Temp\iacode-claude-validation-cp0002-9dea2af-a1\repo`
- Clone commit: `9dea2af84cb70b38077f1442be1b6155922cb7a4`
- Git porcelain status before Claude: empty
- Git porcelain status after Claude: empty
- Started: `2026-09-19T07:23:43Z`
- Finished: `2026-09-19T07:23:46Z`

## Exact Claude invocation

Executed from the clone root in PowerShell:

```powershell
$prompt = 'Follow the repository resume protocol using only checked-in files. Report the current Gate and status, run the checkpoint validator and the validation commands allowed by the current checkpoint, and make no file changes.'
& 'C:\Users\cesar\.local\bin\claude.exe' -p $prompt --effort xhigh --permission-mode dontAsk --tools 'Read,Bash' --no-session-persistence --output-format json
```

## Sanitized result

- Process exit code: `1`
- `is_error`: `true`
- Result: `Not logged in · Please run /login`
- API duration: `0 ms`
- Input, cache, and output tokens: `0`
- Model usage: empty
- Total cost: `0`
- Permission denials: empty

Volatile session identifiers were omitted because they do not help reproduce or validate the result. The empty Git status before and after establishes that the attempt made no file changes. The temporary clone was removed after evidence capture.
