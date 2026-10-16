# IACode CLI

Standalone, dependency-free access to the existing local runtime. No project command or generated
code executes on the host. The CLI never applies a generated patch or submits a quality verdict.
Gate 5 acceptance is tracked in `docs/checkpoints/LATEST.md`; source presence is not a verdict.

Build with `python scripts/iacode/build_clients.py`. Install the resulting
`artifacts/clients/iacode-cli-0.1.0.tgz` using `npm install --global PATH_TO_TARBALL` or an explicit
private `--prefix`. No registry publication is required. Node **22.23.2+ in major 22** or
**24.19.0+ in major 24** is required; other versions fail with exit 2 before connecting. The
installed package includes the exact shared protocol and no third-party runtime dependency.

Run `iacode help` for the closed command/flag set and JSON output contract. Configure an explicit
`--endpoint http://127.0.0.1:PORT` (or `http://[::1]:PORT`) / `IACODE_DESKTOP_ENDPOINT`, plus the
expiring credential in `IACODE_DESKTOP_TOKEN`. Never put the credential on argv, in a workspace
setting, in a task, in Git or in a report. `doctor` authenticates the runtime and contract.

Typical flow (replace uppercase placeholders; none is a credential):

```text
iacode doctor
iacode preview --root WORKSPACE
iacode snapshot --root WORKSPACE --approve EXACT_MANIFEST_DIGEST
iacode new-id
iacode start --snapshot SNAPSHOT_UUID --task "Inspect the source and run its tests in the sandbox" --team coding --request-id STABLE_UUID --approve
iacode read --run-id RUN_UUID
iacode follow --run-id RUN_UUID --after 0
iacode cancel --run-id RUN_UUID --approve
iacode quality-start --snapshot SNAPSHOT_UUID --digest ARCHIVE_SHA256 --request-id ANOTHER_STABLE_UUID --approve
iacode quality-follow --run-id QUALITY_RUN_ID
```

`preview` prints inventory/hashes, not file contents, and uploads nothing. `snapshot` re-reads
current bounded UTF-8 files and requires the exact approved digest. Private/control/dependency
paths are excluded; links, ambiguous names and oversized/binary input are refused. The authenticated
API performs canonical content scanning **before persistence**. This is not proof that an unknown
secret format can never exist; do not select sensitive source for upload.

Mutations are never automatically retried. Preserve `--request-id` before creation/reproduction.
On an uncertain result, use `lookup --request-id UUID`, `quality-lookup --request-id UUID`,
`snapshot-lookup --digest MANIFEST_SHA256`, or `read`/`quality-read` for cancellation. `found=false`
does not prove that an in-flight request cannot commit later. A deliberate retry uses the same
identity and exact inputs with fresh explicit approval, never a newly generated identity.
Signed canonical pre-effect refusals are definite rejections; other errors remain uncertain.

`events`/`quality-events` are ordered pages. `follow`/`quality-follow` emit JSON lines and preserve
the last cursor for resumption; they drain events after terminal observation. Ctrl+C stops only
the local observer, never the remote task. Cancellation requested is not cancellation completed:
observe the real terminal state/cleanup acknowledgement. Quality output includes checks, findings,
evidence and the server-derived verdict, never a client-selected denominator.

Exit codes: **0** successful command (creation only means accepted); **1** failed terminal run or
quality verdict; **2** local usage/configuration/installation; **3** remote CANCELLED terminal;
**4** uncertain mutation; **5** transport/refusal/observation deadline; **130** local interruption.
All output is JSON, terminal controls are escaped and raw server errors/credentials are not echoed.

See [Desktop runbook](https://github.com/pinguim16/iacode/blob/main/docs/runbooks/DESKTOP-CLIENTS.md) for authenticated server setup,
limitations, removal and editor integration.
