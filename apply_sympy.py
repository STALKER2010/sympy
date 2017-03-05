"""
Apply sympy PRs
"""

import subprocess
import shlex

lines = [line.rstrip('\n').split(':')[0] for line in open('sympy.txt')]
lines = filter(lambda line: not line.startswith("@"), lines)
lines = ["git merge latest source/pr/"+line for line in lines]

for cmd in lines:
    print(cmd)
    if subprocess.run(shlex.split(cmd)).returncode != 0:
        print(">> FAIL")
        input()
