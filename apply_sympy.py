lines = [line.rstrip('\n').split(':')[0] for line in open('sympy.txt')]
lines = filter(lambda line: not line.startswith("@"), lines)
lines = ["git merge latest origin/pr/"+line for line in lines]
import subprocess, shlex
for cmd in lines:
	print(cmd)
	if subprocess.run(shlex.split(cmd)).returncode != 0:
		print(">> FAIL")
		input()