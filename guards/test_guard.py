import json
import os
import subprocess
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
CONFIGS = {
    "claude": os.path.join("~", ".claude", "settings.json"),
    "codex": os.path.join(os.environ.get("CODEX_HOME") or os.path.join("~", ".codex"), "hooks.json"),
    "agy": os.path.join("~", ".gemini", "config", "hooks.json"),
}
PROBES = {
    "claude": ({"tool_name": "Bash", "tool_input": {"command": "cat ~/.netrc"}}, {"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    "codex": ({"tool_name": "Bash", "tool_input": {"command": "cat ~/.netrc"}}, {"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    "agy": ({"toolCall": {"name": "run_command", "args": {"CommandLine": "cat ~/.netrc"}}}, {"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}}),
}


def hook_commands(value):
    if isinstance(value, dict):
        command, args = value.get("command"), value.get("args")
        if isinstance(command, str) and isinstance(args, list) and any("ai-global-config-guard.py" in str(a) for a in args):
            yield tuple([command] + [str(a) for a in args])
        elif isinstance(command, str) and "ai-global-config-guard.py" in command:
            yield command
        for item in value.values():
            yield from hook_commands(item)
    elif isinstance(value, list):
        for item in value:
            yield from hook_commands(item)


def check_hook(tool):
    path = os.path.expanduser(CONFIGS[tool])
    with open(path, encoding="utf-8") as config:
        commands = list(dict.fromkeys(hook_commands(json.load(config))))
    if not commands:
        print(f"FAIL: {path} holds no ai-global-config guard hook")
        return 1
    failures = 0
    for command in commands:
        exec_form = isinstance(command, tuple)
        for expect, event in zip(("deny", "allow"), PROBES[tool]):
            result = subprocess.run(list(command) if exec_form else command, shell=not exec_form, input=json.dumps(event).encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            out = result.stdout.decode("utf-8", errors="replace").strip()
            if tool == "agy":
                try:
                    got = json.loads(out).get("decision")
                except ValueError:
                    got = f"bad output, exit {result.returncode}"
                ok = result.returncode == 0 and got == expect
            else:
                err = result.stderr.decode("utf-8", errors="replace")
                if result.returncode == 2 and ("Blocked by the ai-global-config guard" in err or "The ai-global-config guard protects" in err):
                    got = "deny"
                elif result.returncode == 0:
                    got = "allow"
                else:
                    got = f"exit {result.returncode}"
                ok = got == expect
            print(f"{'PASS' if ok else 'FAIL'} hook {expect} probe ({'exec' if exec_form else 'shell'} form): got {got}")
            failures += not ok
    print(f"{path}: {len(commands)} hook command(s), {failures} failed")
    return 1 if failures else 0


if len(sys.argv) == 3 and sys.argv[1] == "--hook" and sys.argv[2] in CONFIGS:
    sys.exit(check_hook(sys.argv[2]))
guard = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "guard.py")
with open(guard, "rb"):
    pass


def verdict(fmt, payload):
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-S", guard, fmt],
            input=payload.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "error: timeout"
    if result.returncode == 2:
        err = result.stderr.decode("utf-8", errors="replace")
        if fmt != "agy" and ("Blocked by the ai-global-config guard" in err or "The ai-global-config guard protects" in err):
            return "deny"
        return f"error {result.returncode}"
    if result.returncode != 0:
        return f"error {result.returncode}"
    out = result.stdout.decode("utf-8", errors="replace").strip()
    if not out:
        return "error: no output" if fmt == "agy" else "allow"
    try:
        data = json.loads(out)
    except ValueError:
        return "error: bad output"
    decision = data.get("decision") or data.get("hookSpecificOutput", {}).get("permissionDecision")
    return {"deny": "deny", "force_ask": "ask", "ask": "ask"}.get(decision, "allow")


failures = 0
count = 0
with open(os.path.join(here, "test-vectors.jsonl"), encoding="utf-8") as vectors:
    for line in vectors:
        case = json.loads(line)
        count += 1
        payload = case["raw"] if "raw" in case else json.dumps(case["input"])
        got = verdict(case["format"], payload)
        if got != case["expect"]:
            failures += 1
            print(f"FAIL vector {count}: expected {case['expect']}, got {got}")

words = " ".join(f"word{i}" for i in range(1000))
long = [
    ("claude", {"tool_name": "Bash", "tool_input": {"command": f'git commit -m "{words}"'}}, "allow"),
    ("claude", {"tool_name": "PowerShell", "tool_input": {"command": f"git commit -m @'\n{words}\n'@"}}, "allow"),
]
for fmt, event, expect in long:
    count += 1
    got = verdict(fmt, json.dumps(event))
    if got != expect:
        failures += 1
        print(f"FAIL vector {count}: expected {expect}, got {got}")

slow = [
    ("claude", {"tool_name": "Bash", "tool_input": {"command": ": " + ".ssh/" * 40000 + "x"}}),
    ("claude", {"tool_name": "Bash", "tool_input": {"command": ".claude/sessions/" * 40000}}),
    ("claude", {"tool_name": "Bash", "tool_input": {"command": "kubectl config view " * 20000}}),
    ("claude", {"tool_name": "Bash", "tool_input": {"command": ".env." + "a." * 100000 + "!"}}),
    ("claude", {"tool_name": "Read", "tool_input": {"file_path": "a/" * 800000 + "x/.ssh/id"}}),
    ("claude", {"tool_name": "Bash", "tool_input": {"command": "ls " + "a " * 200000}}),
    ("codex", {"tool_name": "Bash", "tool_input": {"command": "cd a; " * 3000 + "ls " + "b " * 1500}}),
    ("codex", {"tool_name": "Bash", "tool_input": {"command": "cd a;" * 3999 + " x"}}),
    ("codex", {"tool_name": "Bash", "tool_input": {"command": " ".join(f"cd d{i}; cat f{i}" for i in range(1500))}}),
    ("claude", {"tool_name": "Bash", "tool_input": {"command": "cd //192.0.2.1/share && cat notes.txt"}}),
    ("claude", {"tool_name": "PowerShell", "tool_input": {"command": "Set-Location \\\\192.0.2.1\\share; Get-Content notes.txt"}}),
    ("claude", {"tool_name": "Read", "tool_input": {"file_path": "\\??\\UNC\\192.0.2.1\\share\\notes.txt"}}),
]
for fmt, event in slow:
    count += 1
    start = time.monotonic()
    verdict(fmt, json.dumps(event))
    if time.monotonic() - start > 2:
        failures += 1
        print(f"FAIL vector {count}: took {time.monotonic() - start:.1f} s")

print(f"{count} vectors, {failures} failed")
sys.exit(1 if failures else 0)
