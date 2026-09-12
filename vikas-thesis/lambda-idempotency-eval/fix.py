import sys

path = "vikas-thesis/lambda-idempotency-eval/src/lambda_fn/paths.py"
with open(path, "r") as f:
    orig = f.read()

# I messed it up, so let's get it right from git
import subprocess
subprocess.check_call(["git", "checkout", "--", path])

with open(path, "r") as f:
    clean = f.read()

with open("/tmp/p4.py", "r") as f:
    p4 = f.read()

new_content = clean.replace("PATHS = {\"P1\": p1, \"P2\": p2, \"P3\": p3}", p4 + "\nPATHS = {\"P1\": p1, \"P2\": p2, \"P3\": p3, \"P4\": p4}")

with open(path, "w") as f:
    f.write(new_content)
