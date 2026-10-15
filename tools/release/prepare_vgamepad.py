# 从锁定源码构建 vgamepad，避免在构建机器上启动交互式驱动安装。
"""Prepare the locked Windows vgamepad dependency without installing a driver."""

from __future__ import annotations

import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.request


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True, help="Target Windows virtual environment interpreter")
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("The wheel must be built on Windows to include the Windows client DLLs.")
    target_python = args.python.resolve(strict=True)
    with (ROOT / "uv.lock").open("rb") as stream:
        package = next(item for item in tomllib.load(stream)["package"] if item["name"] == "vgamepad")
    if package["version"] != "0.1.0":
        raise RuntimeError("Reassess the driver-installer workaround for the new locked vgamepad version.")
    source = package["sdist"]
    with urllib.request.urlopen(source["url"], timeout=60) as response:
        archive_bytes = response.read()
    if f"sha256:{hashlib.sha256(archive_bytes).hexdigest()}" != source["hash"]:
        raise RuntimeError("vgamepad source archive does not match uv.lock.")

    with tempfile.TemporaryDirectory(prefix="nte-vgamepad-") as temporary:
        stage = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
            archive.extractall(stage, filter="data")
        source_root = stage / "vgamepad-0.1.0"
        wheels = stage / "wheels"
        # setup.py skips its blocking msiexec call when egg_info is the first
        # command. Both commands then run once, against unchanged locked source.
        subprocess.run(
            [sys.executable, "setup.py", "egg_info", "bdist_wheel", "--dist-dir", str(wheels)],
            cwd=source_root,
            check=True,
        )
        # Install by package name, not a direct wheel URL, so the subsequent
        # locked sync can reuse this registry dependency without rebuilding it.
        subprocess.run(
            ["uv", "pip", "install", "--python", str(target_python), "--no-deps", "--no-index",
             "--find-links", str(wheels), "vgamepad==0.1.0"],
            check=True,
        )


if __name__ == "__main__":
    main()
