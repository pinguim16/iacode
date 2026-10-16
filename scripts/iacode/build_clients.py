#!/usr/bin/env python3
"""Build the dependency-free CLI tarball and VSIX from a closed, audited file inventory.

No npm lifecycle, workspace build hook or network download is executed. The VSIX is the standard
OPC ZIP consumed by VS Code, not a self-installing executable. Installation is tested separately.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = "packages/contracts/src/iacode_contracts/desktop_protocol.json"
CORE = {
    "client.cjs": "apps/cli/src/client.cjs",
    "snapshot.cjs": "apps/cli/src/snapshot.cjs",
    "desktop_protocol.json": PROTOCOL,
}
CLI = {
    "package.json": "apps/cli/package.json",
    "README.md": "apps/cli/README.md",
    "bin/iacode.cjs": "apps/cli/bin/iacode.cjs",
    **{f"src/{name}": source for name, source in CORE.items()},
}
EDITOR = {
    "extension/package.json": "apps/vscode-extension/package.json",
    "extension/README.md": "apps/vscode-extension/README.md",
    "extension/out/extension.cjs": "apps/vscode-extension/src/extension.cjs",
    **{f"extension/out/core/{name}": source for name, source in CORE.items()},
}


def source_bytes(mapping: dict[str, str]) -> dict[str, bytes]:
    result = {}
    for target, source in mapping.items():
        path = ROOT / source
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"client build input is not a regular file: {source}")
        data = path.read_bytes()
        if path.suffix in {".cjs", ".mjs"} and b"\r" in data:
            raise ValueError(f"client executable inputs must use LF line endings: {source}")
        result[target] = data
    return result


def vsix_metadata() -> dict[str, bytes]:
    package = json.loads((ROOT / "apps/vscode-extension/package.json").read_text(encoding="utf-8"))
    identity = " ".join(
        f"{name}={quoteattr(package[key])}"
        for name, key in (("Id", "name"), ("Version", "version"), ("Publisher", "publisher"))
    )
    manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
<Metadata><Identity Language="en-US" {identity}/>
<DisplayName>{escape(package["displayName"])}</DisplayName>
<Description xml:space="preserve">{escape(package["description"])}</Description>
<Tags/><Categories>Other</Categories><GalleryFlags/>
<Properties><Property Id="Microsoft.VisualStudio.Code.Engine"
Value={quoteattr(package["engines"]["vscode"])}/>
<Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="ui"/>
<Property Id="Microsoft.VisualStudio.Code.ExecutesCode" Value="true"/></Properties></Metadata>
<Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation><Dependencies/>
<Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest"
Path="extension/package.json" Addressable="true"/>
<Asset Type="Microsoft.VisualStudio.Services.Content.Details"
Path="extension/README.md" Addressable="true"/></Assets>
</PackageManifest>"""
    types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="json" ContentType="application/json"/>
<Default Extension="cjs" ContentType="application/javascript"/>
<Default Extension="md" ContentType="text/markdown"/>
<Default Extension="vsixmanifest" ContentType="text/xml"/></Types>"""
    return {"extension.vsixmanifest": manifest.encode(), "[Content_Types].xml": types.encode()}


def write_target(path: Path, data: bytes) -> None:
    if path.is_symlink():
        raise ValueError("refusing a redirected package output")
    path.write_bytes(data)


def build(directory: Path) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    cli_files = source_bytes(CLI)
    editor_files = {**source_bytes(EDITOR), **vsix_metadata()}
    for package_name in ("apps/cli/package.json", "apps/vscode-extension/package.json"):
        package = json.loads((ROOT / package_name).read_text(encoding="utf-8"))
        if any(
            package.get(field)
            for field in ("dependencies", "optionalDependencies", "devDependencies")
        ):
            raise ValueError("dependency-free builder refuses an undeclared dependency graph")
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(cli_files.items()):
            info = tarfile.TarInfo("package/" + name)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o755 if name.startswith("bin/") else 0o644
            archive.addfile(info, io.BytesIO(data))
    zipped = io.BytesIO()
    with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(editor_files.items()):
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    outputs = {
        "iacode-cli-0.1.0.tgz": gzip.compress(tar_buffer.getvalue(), mtime=0),
        "iacode-0.1.0.vsix": zipped.getvalue(),
    }
    result = {
        "kind": "CLIENT_BUILD_NOT_FUNCTIONAL_ACCEPTANCE",
        "result": "PASS",
        "protocolDigest": hashlib.sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
        "sourceHashes": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in sorted(set(CLI.values()) | set(EDITOR.values()))
        },
        "artifacts": {},
    }
    for name, data in outputs.items():
        write_target(directory / name, data)
        result["artifacts"][name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "sizeBytes": len(data),
        }
    write_target(directory / "BUILD.json", (json.dumps(result, indent=2) + "\n").encode())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/clients")
    arguments = parser.parse_args()
    print(json.dumps(build(arguments.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
