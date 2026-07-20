import subprocess
import os
from pathlib import Path
out = []
cmds = [
    [r"C:\Program Files\Git\cmd\git.exe", "--version"],
    [r"C:\Program Files\Git\cmd\git.exe", "init"],
    [r"C:\Program Files\Git\cmd\git.exe", "status"]
]
for cmd in cmds:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out.append(f'CMD: {cmd}')
        out.append(f'RETURN: {p.returncode}')
        out.append(f'STDOUT: {p.stdout.strip()}')
        out.append(f'STDERR: {p.stderr.strip()}')
    except Exception as e:
        out.append(f'EXC: {e}')
Path('git_debug_log.txt').write_text('\n'.join(out), encoding='utf-8')
