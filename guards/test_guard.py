import json
import os
import subprocess
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
guard = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "guard.py")


def verdict(fmt, payload):
    result = subprocess.run(
        [sys.executable, "-I", "-S", guard, fmt],
        input=payload.encode("utf-8"),
        capture_output=True,
        timeout=30,
    )
    if result.returncode == 2:
        return "deny"
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
