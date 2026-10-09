#!/usr/bin/env python3
"""Official Lean 4 / Comparator check of OpenAI's "Unique Games Theorem" formalization.

Repository: https://github.com/openai/math (directory lean/), pinned below.
Follows lean/README.md and lean/ComparatorChallenges/README.md:
    lake update ; lake exe cache get ; lake env comparator ComparatorChallenges/UniqueGamesTheorem.json
plus an independent `#print axioms OAI.UniqueGamesTheorem.theorem11` check.

Self-contained (cloud_run.py uploads only this file to Kaggle). Runs on Kaggle CPU (as root -> drops to an
unprivileged user, Comparator README assumption 6) or on the Oracle VM (as ubuntu). Heavy files live in /tmp
(Kaggle) or ~/ugc_work (Oracle); only small text files go to /kaggle/working/ugc_out (Kaggle) or ./out_remote.
Written 2026-10-09 for Ariel (loop name `ugc`).
"""
import os, pwd, shutil, subprocess, sys, time

PIN = "fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb"   # openai/math main HEAD on 2026-10-09 (merge of PR #1, 2026-10-07)
ON_KAGGLE = os.path.isdir("/kaggle/working")
if ON_KAGGLE:
    WORK, OUT = "/tmp/ugc", "/kaggle/working/ugc_out"
    DEADLINE_S = 11 * 3600 + 15 * 60          # Kaggle kills sessions at 12 h; leave time to write outputs
else:
    WORK, OUT = os.path.expanduser("~/ugc_work"), os.path.abspath("out_remote")
    DEADLINE_S = int(os.environ.get("UGC_DEADLINE_S", 230 * 60))   # cloud_run oracle caps a job at 240 min

JOB_SH = r'''#!/usr/bin/env bash
# Runs as an unprivileged user. Each phase logs to $WORK/logs/<phase>.log; tails and facts go to $OUT.
set -uo pipefail
set -a
umask 022
PIN=__PIN__
REPO=https://github.com/openai/math.git
COMPARATOR_REPO=https://github.com/leanprover/comparator.git
# comparator tag v4.34.0 = last commit before the v4.35 release-candidate bumps; later commits only bump the toolchain.
COMPARATOR_REV=d03acab154d269c06e60e4de7e4cc85deebff94b
# lean4export tag v4.34.0 (the rev pinned in comparator v4.34.0's lake-manifest); used only by the fallback path.
LEAN4EXPORT_REPO=https://github.com/leanprover/lean4export.git
LEAN4EXPORT_REV=076e8e57707e813375e8f9da8bf989799ace9680
LANDRUN_REPO=https://github.com/Zouuup/landrun.git
LANDRUN_REV=811cfff51ceaf3d9843708aa6d22e9b84ccac8b4        # landrun main HEAD on 2026-10-09 (README: build from main)
GO_VER=1.26.9
GO_SHA_amd64=42d158b4d8f7b61ac0a830567c940a86098fb7aac52e467a5ebec03ef5cc2f8d
GO_SHA_arm64=4a97373d49fcacdcf3694fea368a500b00ee3e963974f3e7514132717632f052
CFG=ComparatorChallenges/UniqueGamesTheorem.json
SOL=OAI.Computability.UniqueGames.Main
CHAL=ComparatorChallenges.UniqueGamesTheorem
THM=OAI.UniqueGamesTheorem.theorem11

LOGS=$WORK/logs; SRC=$WORK/src; LEAN_DIR=$WORK/src/lean; BIN=$WORK/bin
mkdir -p "$LOGS" "$OUT" "$BIN" "$HOME"
PATH="$BIN:$HOME/.elan/bin:$WORK/go/bin:$PATH"
GOTOOLCHAIN=local; GOPATH=$WORK/gopath; GOCACHE=$WORK/gocache; GOFLAGS=-modcacherw
GIT_TERMINAL_PROMPT=0
T0=$(date +%s)
TIMINGS=$OUT/timings.txt; FACTS=$OUT/facts.txt; PROGRESS=$OUT/progress.txt; SUMMARY=$OUT/SUMMARY.txt
echo "phase rc seconds start_utc" > "$TIMINGS"; : > "$FACTS"; : > "$PROGRESS"
set +a

note() { echo "[$(date -u +%H:%M:%S) +$(( ($(date +%s)-T0)/60 ))m] $*" | tee -a "$PROGRESS"; }
fact() { echo "$1: $2" >> "$FACTS"; }
remaining() { echo $(( DEADLINE_EPOCH - $(date +%s) )); }
clean_tail() { tr '\r' '\n' < "$1" | grep -v '^[[:space:]]*$' | tail -n "$2"; }

# phase NAME FUNCTION : runs FUNCTION in its own bash under a timeout of the remaining time budget.
phase() {
  local name=$1 fn=$2 rem s e rc
  rem=$(remaining)
  if [ "$rem" -le 120 ]; then note "SKIP $name: out of time"; echo "$name SKIPPED_NO_TIME 0 -" >> "$TIMINGS"; return 124; fi
  echo "$name" > "$WORK/current_phase"
  s=$(date +%s); note "START $name (budget left $((rem/60)) min)"
  timeout --kill-after=60 "$rem" bash -c "$fn" > "$LOGS/$name.log" 2>&1
  rc=$?; e=$(date +%s)
  echo "$name $rc $((e-s)) $(date -u -d @"$s" +%FT%TZ)" >> "$TIMINGS"
  clean_tail "$LOGS/$name.log" 200 > "$OUT/log_tail_$name.txt"
  note "END $name rc=$rc after $(( (e-s)/60 ))m$(( (e-s)%60 ))s"
  return $rc
}

heartbeat() {
  while sleep 300; do
    local p f; p=$(cat "$WORK/current_phase" 2>/dev/null || echo "?"); f="$LOGS/$p.log"
    [ -f "$f" ] || continue
    echo "[hb $(date -u +%H:%M:%S) +$(( ($(date +%s)-T0)/60 ))m] phase=$p"
    tail -c 6000 "$f" | tr '\r' '\n' | grep -v '^[[:space:]]*$' | tail -n 3 | cut -c1-300 | sed 's/^/    /'
    { echo "phase=$p at $(date -u +%FT%TZ)"; tail -c 30000 "$f" | tr '\r' '\n' | grep -v '^[[:space:]]*$' | tail -n 80; } > "$OUT/live_tail.txt"
    { df -h "$WORK" | tail -1; free -m; uptime; } > "$OUT/live_machine.txt" 2>&1
  done
}

p_sysinfo() {
  echo "date_utc: $(date -u +%FT%TZ)"; echo "id: $(id)"; uname -a; head -4 /etc/os-release
  echo "nproc: $(nproc)"; free -g; df -h "$WORK"
  echo "lsm: $(cat /sys/kernel/security/lsm 2>&1)"
  echo "max_map_count: $(cat /proc/sys/vm/max_map_count 2>&1)"
  grep -E 'NoNewPrivs|Seccomp' /proc/self/status
  for t in git curl tar gcc clang systemd-run; do echo "$t: $(command -v $t) $($t --version 2>&1 | head -1)"; done
}

p_clone() {
  set -e
  mkdir -p "$SRC"; cd "$SRC"
  git init -q . && git remote add origin "$REPO"
  # only lean/'s top-level files, its patches, all challenge files, and the Computability library (UGC lives there);
  # the UGC import closure has no other OAI imports (checked below), so nothing else can affect this check.
  # (pattern file written directly: works with old git versions that lack `sparse-checkout set --no-cone`)
  git config core.sparseCheckout true; mkdir -p .git/info
  printf '%s\n' '/lean/*' '!/lean/*/' '/lean/patches/' '/lean/ComparatorChallenges/' '/lean/OAI/Computability/' > .git/info/sparse-checkout
  git --version
  git fetch -q --depth 1 --filter=blob:none origin "$PIN"
  git checkout -q FETCH_HEAD
  echo "HEAD $(git rev-parse HEAD)"; [ "$(git rev-parse HEAD)" = "$PIN" ]
  git log -1 --format='commit %H%ncommitted %cI%nsubject %s'
  echo "origin main now: $(git ls-remote origin refs/heads/main)"
  echo "UGC tree hash: $(git rev-parse HEAD:lean/OAI/Computability/UniqueGames)"
  echo "UGC .lean files: $(find lean/OAI/Computability/UniqueGames -name '*.lean' | wc -l)"
  echo "UGC lines: $(find lean/OAI/Computability/UniqueGames -name '*.lean' -print0 | xargs -0 cat | wc -l)"
  sha256sum lean/lean-toolchain lean/lakefile.lean lean/lake-manifest.json "lean/$CFG" lean/ComparatorChallenges/UniqueGamesTheorem.lean \
    lean/OAI/Computability/UniqueGames/Main.lean lean/OAI/Computability/UniqueGames/Theorem.lean
  echo "--- OAI imports that are not in the checkout (must be empty):"
  grep -rhoE '^import OAI[.A-Za-z0-9_]*' lean/OAI/Computability/UniqueGames lean/ComparatorChallenges/UniqueGamesTheorem.lean \
    | sed 's/^import //' | sort -u | while read -r m; do [ -f "lean/$(echo "$m" | tr . /).lean" ] || echo "MISSING $m"; done
  echo "--- non-OAI import roots:"
  grep -rhoE '^import [A-Za-z0-9_]+' lean/OAI/Computability/UniqueGames lean/ComparatorChallenges/UniqueGamesTheorem.lean | sort | uniq -c
}

p_elan() {
  set -e
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$WORK/elan-init.sh"
  sh "$WORK/elan-init.sh" -y --no-modify-path --default-toolchain none
  elan toolchain install "$(cat "$LEAN_DIR/lean-toolchain")"
  cd "$LEAN_DIR"; elan --version; lean --version; lake --version
}

p_lake_update() {
  cd "$LEAN_DIR"
  lake update; rc=$?
  echo "lake update rc=$rc"
  git status --short | head -50
  git diff --stat -- lake-manifest.json lean-toolchain
  git diff -- lake-manifest.json lean-toolchain > "$OUT/manifest_diff_after_lake_update.txt"
  return $rc
}

p_cache_get() {
  cd "$LEAN_DIR"
  lake exe cache get || { echo "cache get failed once; retrying"; sleep 30; lake exe cache get; }
  rc=$?
  du -sh .lake/packages/mathlib/.lake/build 2>&1; du -sh .lake 2>&1; df -h "$WORK"
  return $rc
}

p_tools_lean() {
  set -e
  cd "$WORK"; git clone -q "$COMPARATOR_REPO" comparator; cd comparator; git checkout -q "$COMPARATOR_REV"
  echo "comparator $(git rev-parse HEAD) (upstream toolchain $(cat lean-toolchain))"
  # Build comparator and lean4export with the project's exact Lean, so lean4export can read the project's .olean files.
  cp "$LEAN_DIR/lean-toolchain" lean-toolchain
  if lake build lean4export comparator; then
    echo "TOOLS_MODE=both built with $(cat lean-toolchain)"
    ln -sf "$PWD/.lake/build/bin/comparator" "$BIN/comparator"
    ln -sf "$PWD/.lake/packages/lean4export/.lake/build/bin/lean4export" "$BIN/lean4export"
    echo "lean4export $(git -C .lake/packages/lean4export rev-parse HEAD)"
  else
    echo "override build failed; fallback: comparator on its own toolchain, lean4export $LEAN4EXPORT_REV on the project's"
    git checkout -q lean-toolchain; lake build comparator
    ln -sf "$PWD/.lake/build/bin/comparator" "$BIN/comparator"
    cd "$WORK"; git clone -q "$LEAN4EXPORT_REPO" lean4export; cd lean4export; git checkout -q "$LEAN4EXPORT_REV"
    cp "$LEAN_DIR/lean-toolchain" lean-toolchain; lake build lean4export
    ln -sf "$PWD/.lake/build/bin/lean4export" "$BIN/lean4export"
    echo "TOOLS_MODE=fallback (comparator on $(cat "$WORK/comparator/lean-toolchain"), lean4export on $(cat lean-toolchain))"
  fi
  cp "$WORK/comparator/scripts/fake-landrun.sh" "$BIN/fake-landrun.sh"; chmod +x "$BIN/fake-landrun.sh"
  ls -la "$BIN"
}

p_landrun_build() {
  set -e
  case "$(uname -m)" in x86_64) ga=amd64; gs=$GO_SHA_amd64;; aarch64) ga=arm64; gs=$GO_SHA_arm64;; *) echo "arch?"; exit 1;; esac
  curl -sSfL "https://go.dev/dl/go${GO_VER}.linux-${ga}.tar.gz" -o "$WORK/go.tgz"
  echo "$gs  $WORK/go.tgz" | sha256sum -c -
  tar -C "$WORK" -xzf "$WORK/go.tgz"; go version
  git clone -q "$LANDRUN_REPO" "$WORK/landrun-src"; cd "$WORK/landrun-src"; git checkout -q "$LANDRUN_REV"
  echo "landrun $(git rev-parse HEAD)"
  go build -o "$BIN/landrun" cmd/landrun/main.go
  "$BIN/landrun" --version 2>&1 || true
}

p_sandbox_test() {
  t=$WORK/sbtest; mkdir -p "$t/allowed"; tb=$(type -P touch); tt=$(type -P true)
  echo "touch=$tb true=$tt"
  L=(timeout 120 "$BIN/landrun" --best-effort --ro / --rw /dev -ldd -add-exec)
  "${L[@]}" -- "$tt"; echo "rc_true=$?"
  "${L[@]}" --rwx "$t/allowed" -- "$tb" "$t/allowed/ok"; echo "rc_allowed=$?"
  "${L[@]}" --rwx "$t/allowed" -- "$tb" "$t/forbidden"; echo "rc_forbidden=$?"
  [ -e "$t/forbidden" ] && echo "forbidden_created=yes" || echo "forbidden_created=no"
  [ -e "$t/allowed/ok" ] && echo "allowed_created=yes" || echo "allowed_created=no"
  echo "--- debug run:"; timeout 120 "$BIN/landrun" --log-level debug --best-effort --ro / -ldd -add-exec -- "$tt" 2>&1 | tail -n 25
  echo "--- systemd-run --user probe:"
  if command -v systemd-run >/dev/null && timeout 30 systemd-run --user --wait --pipe --quiet -- true; then echo "systemd_run_user=yes"; else echo "systemd_run_user=no"; fi
}

p_comparator() {
  cd "$LEAN_DIR"
  # absolute real path (the documented env-var alternative to PATH lookup), so landrun's -add-exec sees the real binary
  export COMPARATOR_LEAN4EXPORT; COMPARATOR_LEAN4EXPORT=$(readlink -f "$BIN/lean4export")
  echo "mode=$CMP_MODE landrun=${COMPARATOR_LANDRUN:-$(command -v landrun)} lean4export=$COMPARATOR_LEAN4EXPORT comparator=$(readlink -f "$(command -v comparator)") systemd_run=$USE_SYSTEMD_RUN"
  echo "command: lake env comparator $CFG"
  if [ "$USE_SYSTEMD_RUN" = 1 ]; then
    systemd-run --property=RestrictAddressFamilies=~AF_UNIX --user --wait --pipe --quiet -E PATH="$PATH" -E HOME="$HOME" \
      -E COMPARATOR_LEAN4EXPORT="$COMPARATOR_LEAN4EXPORT" \
      ${COMPARATOR_LANDRUN:+-E COMPARATOR_LANDRUN="$COMPARATOR_LANDRUN"} --working-directory "$LEAN_DIR" -- bash -c "lake env comparator $CFG"
  else
    lake env comparator "$CFG"
  fi 2>&1 | while IFS= read -r line; do printf '%s %s\n' "$(date -u +%H:%M:%S)" "$line"; done
  rc=${PIPESTATUS[0]}; echo "comparator rc=$rc"; return "$rc"
}

p_build_explicit() {
  cd "$LEAN_DIR"; lake build "$SOL" "$CHAL"
}

p_axioms() {
  mkdir -p "$WORK/checks"
  printf 'import %s\n#check @%s\n#print axioms %s\n' "$SOL" "$THM" "$THM" > "$WORK/checks/SolutionAxioms.lean"
  printf 'import %s\n#check @%s\n#print axioms %s\n' "$CHAL" "$THM" "$THM" > "$WORK/checks/ChallengeStatement.lean"
  cd "$LEAN_DIR"
  echo "===== solution ($SOL)"; lake env lean "$WORK/checks/SolutionAxioms.lean"; r1=$?; echo "rc_solution=$r1"
  echo "===== challenge ($CHAL)"; lake env lean "$WORK/checks/ChallengeStatement.lean"; echo "rc_challenge=$?"
  return $r1
}

export -f p_sysinfo p_clone p_elan p_lake_update p_cache_get p_tools_lean p_landrun_build p_sandbox_test p_comparator p_build_explicit p_axioms

finalize() {
  trap - EXIT
  pkill -P "$HB" 2>/dev/null; kill "$HB" 2>/dev/null
  # full logs of the decisive phases when small; tails exist for every phase
  for n in comparator_real comparator_fake build_explicit axioms sandbox_test lake_update; do
    f="$LOGS/$n.log"; [ -f "$f" ] && [ "$(stat -c %s "$f")" -lt 5000000 ] && tr '\r' '\n' < "$f" > "$OUT/full_$n.log"
  done
  # solution section of the axioms log, joined into one line (the #check type can span many lines)
  sec=$(awk '/^===== solution/{f=1} /^===== challenge/{f=0} f' "$LOGS/axioms.log" 2>/dev/null | tr '\n' ' ')
  ax=$(echo "$sec" | grep -oE "depends on axioms: \[[^]]*\]" | head -1)
  axioms_ok="NOT CHECKED"
  if [ -n "$ax" ]; then
    list=$(echo "$ax" | sed 's/.*\[//; s/\].*//' | tr -d ' ' | tr ',' '\n' | grep -v '^$')
    bad=$(echo "$list" | grep -vxE 'propext|Quot\.sound|Classical\.choice' | tr '\n' ' ')
    if [ -z "$bad" ]; then axioms_ok="OK (only permitted axioms; no sorryAx)"; else axioms_ok="NOT OK: extra axioms: $bad"; fi
  elif echo "$sec" | grep -q "does not depend on any axioms"; then axioms_ok="OK (no axioms)"; fi
  echo "$sec" | grep -q "rc_solution=0" || axioms_ok="$axioms_ok; WARNING: the solution check file did not compile cleanly"
  {
    echo "UGC Lean check: openai/math lean/, Comparator config $CFG"
    echo "finished_utc: $(date -u +%FT%TZ)   wall: $(( ($(date +%s)-T0)/60 )) min"
    cat "$FACTS"
    echo "comparator_verdict_real_landrun: ${VERDICT_REAL:-NOT RUN}"
    echo "comparator_verdict_fake_landrun: ${VERDICT_FAKE:-NOT RUN}"
    echo "explicit_lake_build_rc: ${BUILD_RC:-NOT RUN}"
    echo "print_axioms: ${ax:-<none parsed; see full_axioms.log>}"
    echo "axioms_verdict: $axioms_ok"
    echo "--- timings (phase rc seconds start):"; cat "$TIMINGS"
    echo "--- #check / #print axioms output:"; tr '\r' '\n' < "$LOGS/axioms.log" 2>/dev/null | head -c 20000
  } > "$SUMMARY"
  note "DONE; summary in $SUMMARY"
}

heartbeat & HB=$!
trap finalize EXIT

phase sysinfo p_sysinfo
fact machine "$(uname -m), $(nproc) cores, $(free -g | awk '/Mem:/{print $2}') GB RAM, kernel $(uname -r)"
fact run_as "$(id -un) (uid $(id -u))"
fact deadline_utc "$(date -u -d @"$DEADLINE_EPOCH" +%FT%TZ)"

phase clone p_clone || { fact fatal "clone failed"; exit 1; }
fact commit "$(git -C "$SRC" rev-parse HEAD)"
grep -q MISSING "$LOGS/clone.log" && fact warning "some OAI imports missing from sparse checkout (see log_tail_clone.txt)"
fact toolchain "$(cat "$LEAN_DIR/lean-toolchain")"

phase elan p_elan || { fact fatal "elan/toolchain install failed"; exit 1; }
fact lean_version "$(cd "$LEAN_DIR" && lean --version)"

if phase lake_update p_lake_update; then fact lake_update "ok ($(wc -l < "$OUT/manifest_diff_after_lake_update.txt") diff lines in lake-manifest.json/lean-toolchain)"
else fact lake_update "FAILED (continuing with the committed manifest)"; fi

phase cache_get p_cache_get || { fact fatal "lake exe cache get failed (a Mathlib source build does not fit the time budget)"; exit 1; }
fact cache_get ok

phase tools_lean p_tools_lean; TL=$?
fact tools_lean "$([ $TL = 0 ] && grep -m1 '^TOOLS_MODE=' "$LOGS/tools_lean.log" || echo "FAILED rc=$TL")"
phase landrun_build p_landrun_build; LB=$?
fact landrun_build "$([ $LB = 0 ] && echo ok || echo "FAILED rc=$LB")"

SANDBOX=unavailable; USE_SYSTEMD_RUN=0
if [ $LB = 0 ]; then
  phase sandbox_test p_sandbox_test
  sb=$LOGS/sandbox_test.log
  if grep -q '^rc_true=0' "$sb" && grep -q '^rc_allowed=0' "$sb"; then
    if grep -q '^forbidden_created=no' "$sb"; then SANDBOX=enforcing; else SANDBOX=runs-but-not-enforcing; fi
  else SANDBOX=broken; fi
  grep -q '^systemd_run_user=yes' "$sb" && USE_SYSTEMD_RUN=1
fi
fact landrun_sandbox "$SANDBOX"
fact systemd_run_guard "$([ $USE_SYSTEMD_RUN = 1 ] && echo used || echo "not available (README's systemd-run AF_UNIX guard skipped)")"
export USE_SYSTEMD_RUN

if [ $TL = 0 ]; then
  if [ "$SANDBOX" = enforcing ] || [ "$SANDBOX" = runs-but-not-enforcing ]; then
    CMP_MODE=real phase comparator_real p_comparator; rc=$?
    if [ $rc = 0 ] && grep -q "Your solution is okay!" "$LOGS/comparator_real.log"; then VERDICT_REAL="PASS (Your solution is okay!)"
    else VERDICT_REAL="FAIL rc=$rc"; fi
  fi
fi

phase build_explicit p_build_explicit; BUILD_RC=$?

if [ $TL = 0 ] && [ "${VERDICT_REAL:-NOT RUN}" != "PASS (Your solution is okay!)" ]; then
  # landrun missing/broken, or the sandboxed run failed: run the same Comparator checks without the sandbox (fake-landrun shim)
  USE_SYSTEMD_RUN=0 CMP_MODE=fake COMPARATOR_LANDRUN="$BIN/fake-landrun.sh" phase comparator_fake p_comparator; rc=$?
  if [ $rc = 0 ] && grep -q "Your solution is okay!" "$LOGS/comparator_fake.log"; then VERDICT_FAKE="PASS (Your solution is okay!) [no sandbox]"
  else VERDICT_FAKE="FAIL rc=$rc"; fi
fi

phase axioms p_axioms
exit 0
'''


def main():
    t0 = time.time()
    print(f"UGC Lean check: openai/math@{PIN}; kaggle={ON_KAGGLE}; work={WORK}; out={OUT}; "
          f"deadline {DEADLINE_S // 60} min; comparator v4.34.0 (d03acab) + lean4export v4.34.0 built on the project's "
          f"toolchain; landrun main@811cfff", flush=True)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    job = os.path.join(WORK, "job.sh")
    with open(job, "w") as f:
        f.write(JOB_SH.replace("__PIN__", PIN))
    home = os.path.join(WORK, "home")
    os.makedirs(home, exist_ok=True)
    base_path = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    if os.path.isdir("/opt/conda/bin"):
        base_path += ":/opt/conda/bin"
    env = {"HOME": home, "PATH": base_path, "WORK": WORK, "OUT": OUT, "LANG": "C.UTF-8", "TERM": "dumb",
           "DEADLINE_EPOCH": str(int(t0 + DEADLINE_S))}
    kw = {}
    if os.geteuid() == 0:
        # Comparator README assumption 6: do not run under a privileged user.
        subprocess.run(["useradd", "-M", "-d", home, "-s", "/bin/bash", "ugcchk"], check=False)
        try:
            pw = pwd.getpwnam("ugcchk")
            for d in (WORK, OUT, home):
                shutil.chown(d, pw.pw_uid, pw.pw_gid)
            shutil.chown(job, pw.pw_uid, pw.pw_gid)
            kw = {"user": pw.pw_uid, "group": pw.pw_gid, "extra_groups": []}
            env.update({"USER": "ugcchk", "LOGNAME": "ugcchk"})
            print(f"running the check as unprivileged user ugcchk (uid {pw.pw_uid})", flush=True)
        except Exception as e:
            print(f"could not create an unprivileged user ({e}); running as root", flush=True)
    rc = subprocess.run(["bash", job], cwd=WORK, env=env, **kw).returncode
    print(f"job.sh exit {rc} after {(time.time() - t0) / 60:.1f} min", flush=True)
    summary = os.path.join(OUT, "SUMMARY.txt")
    if os.path.exists(summary):
        print(open(summary).read(), flush=True)
    for n in sorted(os.listdir(OUT)):
        print(f"  {n}  {os.path.getsize(os.path.join(OUT, n))} B", flush=True)
    return 0   # the verdict is in SUMMARY.txt; exit 0 so the platform keeps every output file


if __name__ == "__main__":
    sys.exit(main())
