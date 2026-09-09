#!/usr/bin/env python3
"""Verify a ShareXtract release wheel is the dependency-minimal core artifact."""
from __future__ import annotations

import argparse
import email
import hashlib
import json
import pathlib
import re
import sys
import zipfile


def fail(message: str) -> None:
    print(f"release wheel verification failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    wheel = pathlib.Path(args.wheel).resolve()
    version = args.version.strip()
    expected_name = f"sharextract-{version}-py3-none-any.whl"
    if wheel.name != expected_name:
        fail(f"unexpected wheel filename {wheel.name!r}; expected {expected_name!r}")

    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        wheel_names = [name for name in names if name.endswith(".dist-info/WHEEL")]
        if len(metadata_names) != 1 or len(wheel_names) != 1:
            fail("wheel must contain exactly one METADATA and one WHEEL file")
        if any(name.endswith((".pyc", ".pyo")) or "/__pycache__/" in name for name in names):
            fail("compiled Python cache files must not be shipped")
        if any(name.startswith((".git/", "tests/")) for name in names):
            fail("repository/test internals must not be shipped in the core wheel")

        metadata = email.message_from_bytes(archive.read(metadata_names[0]))
        wheel_meta = email.message_from_bytes(archive.read(wheel_names[0]))

    if metadata.get("Name", "").lower() != "sharextract":
        fail(f"metadata Name drifted: {metadata.get('Name')!r}")
    if metadata.get("Version", "") != version:
        fail(f"metadata Version drifted: {metadata.get('Version')!r}")
    if metadata.get("License-Expression", "") != "Apache-2.0":
        fail(f"SPDX license metadata drifted: {metadata.get('License-Expression')!r}")
    license_files = metadata.get_all("License-File") or []
    if "LICENSE" not in license_files:
        fail(f"LICENSE file metadata missing: {license_files!r}")
    if wheel_meta.get("Root-Is-Purelib", "").lower() != "true":
        fail("core wheel must remain pure Python")
    tags = wheel_meta.get_all("Tag") or []
    if "py3-none-any" not in tags:
        fail(f"universal py3 tag missing: {tags!r}")

    requirements = metadata.get_all("Requires-Dist") or []
    unguarded = [item for item in requirements if not re.search(r";\s*extra\s*==", item)]
    if unguarded:
        fail(f"core wheel gained required runtime dependencies: {unguarded!r}")

    wheel_sha256 = sha256(wheel)
    skill_path = pathlib.Path(__file__).resolve().parents[1] / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8")
    pin = re.search(
        r"https://github\.com/wuaishare/sharextract/releases/download/"
        r"v(?P<version>[0-9]+\.[0-9]+\.[0-9]+)/"
        r"sharextract-(?P=version)-py3-none-any\.whl#sha256=(?P<sha>[a-f0-9]{64})",
        skill,
    )
    if not pin:
        fail("SKILL.md must pin the release wheel URL and a 64-character SHA-256 digest")
    if pin.group("version") != version:
        fail(f"SKILL.md release version drifted: {pin.group('version')!r}")
    if pin.group("sha") != wheel_sha256:
        fail(f"SKILL.md wheel digest drifted: {pin.group('sha')} != {wheel_sha256}")

    result = {
        "ok": True,
        "contract": "sharextract_release_wheel_v1",
        "wheel": wheel.name,
        "version": version,
        "sha256": sha256(wheel),
        "coreRuntimeDependencyCount": len(unguarded),
        "optionalRequirementCount": len(requirements),
        "purePython": True,
        "tag": "py3-none-any",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
