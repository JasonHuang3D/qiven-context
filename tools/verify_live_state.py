from pathlib import Path
import subprocess, sys, yaml
ROOT=Path(__file__).resolve().parents[1]
data=yaml.safe_load((ROOT/"state/repositories.yaml").read_text(encoding="utf-8"))
failed=False
for repo in data["repositories"]:
    path=Path(repo["local_path"]); expected=repo["main_sha"]
    if not path.is_dir(): print(f"{repo['name']}: MISSING {path}"); failed=True; continue
    cmd=["git","-c",f"safe.directory={path.as_posix()}","-C",str(path),"rev-parse",f"refs/heads/{repo['default_branch']}"]
    try: actual=subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e: print(f"{repo['name']}: ERROR {e.output.strip()}"); failed=True; continue
    ok=actual==expected; print(f"{repo['name']}: {actual} {'PASS' if ok else 'FAIL expected '+expected}"); failed |= not ok
sys.exit(1 if failed else 0)
