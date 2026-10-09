"""verify_manifest.py: SHA-256 inventory of every tracked file in this repository.

    python verify_manifest.py --write   # regenerate public_manifest.json
    python verify_manifest.py --check   # verify every file against it (exit 1 on any mismatch)

Uses `git ls-files` when available so that ignored and untracked files are excluded; otherwise walks the tree,
skipping .git, caches, virtual environments and build outputs. The manifest itself is excluded from the inventory.

Both modes also check the nine files deposited on Zenodo (papers/ and lean_check/) against the MD5 checksums that
Zenodo reports for them, so the copies here stay byte-identical to the deposits. --write refuses to run if one differs.
"""
import argparse, hashlib, json, os, subprocess, sys

MANIFEST = "public_manifest.json"
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".pytest_cache", "build"}

SHORT = "10.5281/zenodo.23265572"     # The Unique Games Theorem: A Short Self-Contained Proof (with companion note)
FAITHFUL = "10.5281/zenodo.23264902"  # A Compressed Presentation of OpenAI's Proof (with the Lean check files)
ZENODO = {  # path: (record DOI, MD5 reported by Zenodo)
    "papers/ugc_short_proof.pdf": (SHORT, "18da9267a1717005f280d8cd4ddfc2e5"),
    "papers/ugc_short_proof.tex": (SHORT, "e3b2047cb80e10cdf4ce5a057955a6df"),
    "papers/ugc_short_proof_companion_note.pdf": (SHORT, "327ef0950b57e2f1b72b5e289e98404c"),
    "papers/ugc_short_proof_companion_note.tex": (SHORT, "375294bc0a7b573ceb3f79a1b3c8a623"),
    "papers/ugc_faithful_presentation.pdf": (FAITHFUL, "bd09e185a204a963c49b70f8feccf1f3"),
    "papers/ugc_faithful_presentation.tex": (FAITHFUL, "b3826a872914dd4e477e6a13906a00cd"),
    "lean_check/ugc_lean_check.py": (FAITHFUL, "3f517aa9deaf47a16a5d4e0aeb74b60c"),
    "lean_check/ugc-lean-ugt-check.log": (FAITHFUL, "b80b3812c0699acbb1facac32ade0bd0"),
    "lean_check/ugc_out.zip": (FAITHFUL, "c03fdef52368078ccaee8f133ecb25ad"),
}


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files", "-z"], check=True, capture_output=True).stdout
        files = [f.decode() for f in out.split(b"\0") if f]
        if files:
            return sorted(f for f in files if f != MANIFEST and os.path.isfile(f))
    except Exception:
        pass
    files = []
    for root, dirs, names in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            p = os.path.relpath(os.path.join(root, n), ".").replace(os.sep, "/")
            if p != MANIFEST and not n.endswith((".pyc", ".DS_Store")):
                files.append(p)
    return sorted(files)


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def zenodo_mismatches():
    bad = []
    for path, (doi, md5) in sorted(ZENODO.items()):
        if not os.path.isfile(path):
            bad.append(f"missing-zenodo-file: {path} (doi:{doi})")
        elif digest(path, "md5") != md5:
            bad.append(f"differs-from-zenodo: {path} (doi:{doi})")
    return bad


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    deposit_errors = zenodo_mismatches()
    for line in deposit_errors:
        print(line)
    if a.write and deposit_errors:
        print(f"FAIL: not writing {MANIFEST}; restore the Zenodo files first")
        sys.exit(1)
    files = tracked_files()
    current = {f: {"sha256": digest(f), "bytes": os.path.getsize(f)} for f in files}
    if a.write:
        with open(MANIFEST, "w", encoding="utf-8") as out:
            json.dump({"algorithm": "sha256", "files": len(current), "entries": current}, out, indent=1)
            out.write("\n")
        print(f"wrote {MANIFEST}: {len(current)} files")
        return
    with open(MANIFEST, encoding="utf-8") as f:
        ref = json.load(f)["entries"]
    missing = sorted(set(ref) - set(current)); extra = sorted(set(current) - set(ref))
    changed = sorted(f for f in set(ref) & set(current) if ref[f]["sha256"] != current[f]["sha256"])
    for label, items in (("missing", missing), ("untracked-by-manifest", extra), ("changed", changed)):
        for f in items:
            print(f"{label}: {f}")
    ok = not (missing or extra or changed or deposit_errors)
    print(f"{'OK' if ok else 'FAIL'}: {len(current)} files checked against {MANIFEST}; "
          f"{len(ZENODO) - len(deposit_errors)}/{len(ZENODO)} Zenodo files byte-identical")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
