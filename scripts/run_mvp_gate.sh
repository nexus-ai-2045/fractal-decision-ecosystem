#!/usr/bin/env bash
# scripts/run_mvp_gate.ps1 と同じ検査をする bash 版の入口。
# - Python 3.11 以上を探す（python3 → python の順。壊れた pyenv の shim は飛ばす）。
# - `python -m scripts.mvp_gate_check` に引数をそのまま渡す。
# - ゲートの出力が本当に出たか、終了コード 0 なのに成功を報告していないかを確かめる。
# 終了コード: Python が無い・ゲートの出力が無い・0 なのに成功の報告が無いときは 1。
# それ以外は mvp_gate_check の終了コードをそのまま返す（ps1 と同じ）。
# ゲートの出力は stdout、診断（WARNING/ERROR/使った Python）は stderr に出す。
set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/.." || exit 1

probe_code='import json
import sys
print(json.dumps({
    "marker": "fde-mvp-gate-python-probe",
    "ok": sys.version_info >= (3, 11),
    "version": list(sys.version_info[:3]),
    "executable": sys.executable,
}))
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'

warn() { printf 'WARNING: %s\n' "$*" >&2; }
err() { printf 'ERROR: %s\n' "$*" >&2; }

is_pyenv_shim_failure() {
    local text="$1"
    grep -Eqi '(^|[^[:alnum:]_])pyenv([^[:alnum:]_]|$)' <<<"$text" || return 1
    grep -Eqi 'not found|no such command|version .* is not installed|command .* was found but .* could not be loaded' <<<"$text"
}

gate_really_ran() {
    local text="$1"
    grep -Eq 'FDE MVP GATE CHECK[[:space:]]+(OK|ERROR)' <<<"$text" && return 0
    grep -Eq '"overall"[[:space:]]*:[[:space:]]*"(ok|error)"' <<<"$text" &&
        grep -Eq '"checks"[[:space:]]*:' <<<"$text"
}

gate_succeeded() {
    local text="$1"
    grep -Eq 'FDE MVP GATE CHECK[[:space:]]+OK' <<<"$text" && return 0
    grep -Eq '"overall"[[:space:]]*:[[:space:]]*"ok"' <<<"$text" &&
        grep -Eq '"checks"[[:space:]]*:' <<<"$text"
}

python_cmd=""
python_version=""
for candidate in python3 python; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
        warn "Skipping $candidate: Python probe could not run."
        continue
    fi
    probe_output="$("$candidate" -c "$probe_code" 2>&1)"
    probe_rc=$?
    if is_pyenv_shim_failure "$probe_output"; then
        warn "Skipping $candidate: pyenv shim is not usable for the MVP gate."
        continue
    fi
    if [ "$probe_rc" -ne 0 ]; then
        warn "Skipping $candidate: Python 3.11+ probe failed."
        continue
    fi
    if grep -Eq '"marker"[[:space:]]*:[[:space:]]*"fde-mvp-gate-python-probe"' <<<"$probe_output" &&
        grep -Eq '"ok"[[:space:]]*:[[:space:]]*true' <<<"$probe_output"; then
        python_cmd="$candidate"
        python_version="$(sed -nE 's/.*"version"[[:space:]]*:[[:space:]]*\[([0-9]+),[[:space:]]*([0-9]+),[[:space:]]*([0-9]+)\].*/\1.\2.\3/p' <<<"$probe_output" | head -n 1)"
        break
    fi
done

if [ -z "$python_cmd" ]; then
    err "Python 3.11+ was not found. Install Python or make either 'python3' or 'python' available on PATH without a broken pyenv shim, then rerun this script."
    exit 1
fi

printf 'Using Python command: %s (%s)\n' "$python_cmd" "$python_version" >&2
gate_output="$("$python_cmd" -m scripts.mvp_gate_check "$@" 2>&1)"
gate_exit_code=$?
[ -n "$gate_output" ] && printf '%s\n' "$gate_output"

if ! gate_really_ran "$gate_output"; then
    err "MVP gate did not produce the expected gate output. Treating this as a failed gate run."
    exit 1
fi

if [ "$gate_exit_code" -eq 0 ] && ! gate_succeeded "$gate_output"; then
    err "MVP gate did not report success. Treating this as a failed gate run."
    exit 1
fi

exit "$gate_exit_code"
