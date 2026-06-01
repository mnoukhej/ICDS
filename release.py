from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "ICDS_App"
VERSION_FILE = ROOT_DIR / "version.json"
BUILD_SCRIPT = APP_DIR / "build.bat"
SETUP_SCRIPT = APP_DIR / "SetupBuilder.iss"
INSTALLER_OUTPUT_DIR = APP_DIR / "output"
APP_NAME = "ICDS AutoDesk"


def run_command(command, cwd=ROOT_DIR, env=None, capture_output=False, check=True):
    printable = " ".join(f'"{part}"' if " " in part else part for part in command)
    print(f"> {printable}")

    result = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=capture_output,
    )

    if check and result.returncode != 0:
        if capture_output:
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {printable}")

    return result


def read_version_metadata():
    with VERSION_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_version_metadata(version, repo_slug):
    download_url = (
        f"https://github.com/{repo_slug}/releases/download/v{version}/"
        f"ICDSAutoDesk_Setup_v{version}.exe"
    )
    payload = {
        "version": version,
        "url": download_url,
    }

    with VERSION_FILE.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    return download_url


def validate_version(version):
    if not re.fullmatch(r"\d+(?:\.\d+)*", version):
        raise ValueError(
            "Version must be numeric segments separated by dots, for example 4.1 or 4.1.2."
        )
    return version


def bump_version(current_version, bump_part):
    numbers = [int(part) for part in current_version.split(".")]

    if bump_part == "major":
        return f"{numbers[0] + 1}.0"

    if bump_part == "minor":
        second = numbers[1] if len(numbers) > 1 else 0
        return f"{numbers[0]}.{second + 1}"

    numbers[-1] += 1
    return ".".join(str(part) for part in numbers)


def get_repo_slug():
    remote_url = run_command(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
    ).stdout.strip()

    https_match = re.search(r"github\.com/([^/]+/[^/.]+)(?:\.git)?$", remote_url)
    ssh_match = re.search(r"github\.com:([^/]+/[^/.]+)(?:\.git)?$", remote_url)

    match = https_match or ssh_match
    if match:
        return match.group(1)

    metadata = read_version_metadata()
    url_match = re.search(r"github\.com/([^/]+/[^/]+)/releases/download/", metadata.get("url", ""))
    if url_match:
        return f"{url_match.group(1)}/{url_match.group(2)}"

    raise RuntimeError("Could not determine the GitHub repository slug from git remote or version.json.")


def locate_iscc():
    candidates = [
        os.environ.get("INNO_SETUP_COMPILER"),
        shutil.which("ISCC.exe"),
        shutil.which("iscc.exe"),
        shutil.which("iscc"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    for candidate in candidates:
        if candidate and Path(candidate.strip('"')).exists():
            return candidate.strip('"')

    raise RuntimeError(
        "Inno Setup compiler not found. Install Inno Setup 6 or set INNO_SETUP_COMPILER to ISCC.exe."
    )


def locate_gh():
    for name in ("gh.exe", "gh"):
        candidate = shutil.which(name)
        if candidate:
            return candidate
    raise RuntimeError(
        "GitHub CLI not found. Install 'gh' and run 'gh auth login' before publishing releases."
    )


def build_executable():
    env = os.environ.copy()
    env["NO_PAUSE"] = "1"
    run_command(["cmd.exe", "/c", BUILD_SCRIPT.name], cwd=APP_DIR, env=env)


def build_installer(version):
    iscc_path = locate_iscc()
    run_command(
        [iscc_path, f"/DMyAppVersion={version}", SETUP_SCRIPT.name],
        cwd=APP_DIR,
    )

    installer_path = INSTALLER_OUTPUT_DIR / f"ICDSAutoDesk_Setup_v{version}.exe"
    if not installer_path.exists():
        raise RuntimeError(f"Installer was not created: {installer_path}")

    return installer_path


def ensure_version_changed(new_version, current_version, skip_git):
    if new_version == current_version and not skip_git:
        raise RuntimeError(
            f"Requested version '{new_version}' matches the current version. "
            "Use --version with a new value or use --skip-git for a publish-only rerun."
        )


def commit_and_push_release(version):
    tag_name = f"v{version}"

    tag_check = run_command(
        ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag_name}"],
        capture_output=True,
        check=False,
    )
    if tag_check.returncode == 0:
        raise RuntimeError(f"Git tag '{tag_name}' already exists.")

    diff_check = run_command(
        ["git", "diff", "--quiet", "HEAD", "--", VERSION_FILE.name],
        check=False,
    )
    if diff_check.returncode == 0:
        raise RuntimeError("version.json did not change, so there is nothing new to commit.")

    run_command(["git", "add", VERSION_FILE.name])
    run_command(["git", "commit", "-m", f"Release v{version}", "--", VERSION_FILE.name])
    run_command(["git", "tag", tag_name])
    run_command(["git", "push", "origin", "HEAD"])
    run_command(["git", "push", "origin", tag_name])


def publish_github_release(version, repo_slug, installer_path, notes):
    gh_path = locate_gh()
    tag_name = f"v{version}"

    release_exists = run_command(
        [gh_path, "release", "view", tag_name, "--repo", repo_slug],
        capture_output=True,
        check=False,
    )

    if release_exists.returncode == 0:
        run_command(
            [
                gh_path,
                "release",
                "upload",
                tag_name,
                str(installer_path),
                "--repo",
                repo_slug,
                "--clobber",
            ]
        )
        return

    release_notes = notes or f"Automated release for {APP_NAME} v{version}."
    run_command(
        [
            gh_path,
            "release",
            "create",
            tag_name,
            str(installer_path),
            "--repo",
            repo_slug,
            "--title",
            f"{APP_NAME} v{version}",
            "--notes",
            release_notes,
        ]
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build and publish a new ICDS AutoDesk release."
    )
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument(
        "--version",
        help="Explicit version to release, for example 4.1",
    )
    version_group.add_argument(
        "--bump",
        choices=("patch", "minor", "major"),
        default="patch",
        help="Automatically bump the version. Default: patch",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional GitHub release notes.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building the executable and installer.",
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Skip git commit, tag, and push steps.",
    )
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Skip GitHub Release publishing.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    repo_slug = get_repo_slug()
    metadata = read_version_metadata()
    current_version = validate_version(str(metadata["version"]).strip())
    next_version = validate_version(args.version or bump_version(current_version, args.bump))

    ensure_version_changed(next_version, current_version, args.skip_git)
    download_url = write_version_metadata(next_version, repo_slug)
    installer_path = INSTALLER_OUTPUT_DIR / f"ICDSAutoDesk_Setup_v{next_version}.exe"

    if not args.skip_build:
        build_executable()
        installer_path = build_installer(next_version)
    elif not installer_path.exists():
        raise RuntimeError(
            f"--skip-build was used but the installer does not exist: {installer_path}"
        )

    if not args.skip_git:
        commit_and_push_release(next_version)

    if not args.skip_publish:
        publish_github_release(next_version, repo_slug, installer_path, args.notes)

    print()
    print(f"Release version: {next_version}")
    print(f"Installer: {installer_path}")
    print(f"Update URL: {download_url}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Release failed: {exc}", file=sys.stderr)
        sys.exit(1)
