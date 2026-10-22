"""Read-only ownership/use assessment of the exact retired public validation copy."""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import utc_now, write_json
from owned_docker_scope import docker

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]

TARGET = ROOT / "var/gate7-sealed-public-20261019-181247"
SUBJECT = "823cf164c6931dab7f957c92721ded7a916655bd"


def main():
    expected = ROOT.resolve() / "var/gate7-sealed-public-20261019-181247"
    if (
        TARGET.resolve(strict=True) != expected
        or TARGET.is_symlink()
        or TARGET.is_junction()
        or not expected.is_relative_to(ROOT.resolve() / "var")
    ):
        raise ValueError("Retired target is redirected or outside the exact runtime subtree")

    def git(*args):
        result = subprocess.run(
            ["git", "-C", str(TARGET), *args], capture_output=True, timeout=60, check=True
        )
        return result.stdout.decode("utf-8", errors="strict").strip()

    report = {
        "observedAt": utc_now(),
        "kind": "READ_ONLY_RETIRED_CLONE_ASSESSMENT",
        "target": str(expected),
        "deletionPerformed": False,
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "remote": git("remote", "get-url", "origin"),
        "gitDirectory": git("rev-parse", "--absolute-git-dir"),
        "trackedOrUntrackedChanges": git("status", "--porcelain").splitlines(),
        "ignoredPaths": git("status", "--short", "--ignored=matching").splitlines(),
        "localBranches": git(
            "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads"
        ).splitlines(),
        "localConfigurationKeys": git("config", "--local", "--name-only", "--list").splitlines(),
        "linkedGitObjects": (TARGET / ".git/objects/info/alternates").exists(),
        "linkedWorktrees": (TARGET / ".git/worktrees").exists(),
    }
    redirects, files, total = [], 0, 0
    pending = [TARGET]
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            if path.is_symlink() or path.is_junction():
                redirects.append(path.relative_to(TARGET).as_posix())
            elif path.is_dir():
                pending.append(path)
            else:
                files += 1
                total += path.stat().st_size
    report.update(redirectedEntries=redirects, regularFiles=files, bytes=total)
    env = {**os.environ, "IACODE_RETIRED_CLONE_NEEDLE": TARGET.name}
    query = (
        "$retiredCloneNeedle=$env:IACODE_RETIRED_CLONE_NEEDLE; "
        "@(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and "
        "$_.CommandLine.IndexOf($retiredCloneNeedle,[StringComparison]::OrdinalIgnoreCase) -ge 0 } "
        "| Select-Object ProcessId,Name) | ConvertTo-Json -Compress"
    )
    processes = subprocess.run(
        ["powershell", "-NoProfile", "-Command", query],
        env=env,
        capture_output=True,
        timeout=30,
        check=True,
    )
    report["processReferences"] = json.loads(processes.stdout.decode("utf-8") or "[]")
    identities = docker(["container", "ls", "--all", "--quiet"]).splitlines()
    references = []
    for identity in identities:
        mounts = json.loads(
            docker(["container", "inspect", "--format", "{{json .Mounts}}", identity])
        )
        if any(TARGET.name.casefold() in str(row.get("Source", "")).casefold() for row in mounts):
            references.append(identity)
    report["containerMountReferences"] = references
    allowed_keys = {
        "core.repositoryformatversion",
        "core.filemode",
        "core.bare",
        "core.logallrefupdates",
        "core.symlinks",
        "core.ignorecase",
        "core.longpaths",
        "remote.origin.url",
        "remote.origin.fetch",
        "branch.main.remote",
        "branch.main.merge",
    }
    allowed_ignored = {
        "!! packages/common/src/iacode_common/__pycache__/",
        "!! scripts/development-ledger/__pycache__/",
    }
    eligible = (
        report["head"] == SUBJECT
        and not report["branch"]
        and report["remote"] == "https://github.com/pinguim16/iacode.git"
        and Path(report["gitDirectory"]).resolve() == expected / ".git"
        and not report["trackedOrUntrackedChanges"]
        and set(report["ignoredPaths"]) <= allowed_ignored
        and report["localBranches"] == ["refs/heads/main " + SUBJECT]
        and set(report["localConfigurationKeys"]) <= allowed_keys
        and not any(
            report[key]
            for key in (
                "linkedGitObjects",
                "linkedWorktrees",
                "redirectedEntries",
                "processReferences",
                "containerMountReferences",
            )
        )
    )
    report["eligibleForExactOwnerCleanup"] = eligible
    folder = CHECKPOINT / "retired-clone-observations"
    folder.mkdir(exist_ok=True)
    index = len(list(folder.glob("run-*.json"))) + 1
    write_json(folder / f"run-{index:04d}.json", report)
    print(
        json.dumps(
            {
                "target": str(expected),
                "eligibleForExactOwnerCleanup": eligible,
                "processReferences": report["processReferences"],
                "containerMountReferenceCount": len(references),
                "deletionPerformed": False,
            }
        )
    )
    return 0 if eligible else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
