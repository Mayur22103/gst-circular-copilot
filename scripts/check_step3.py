"""Checks that every Step 3 task is done. Run: uv run python scripts/check_step3.py"""
import subprocess
from pathlib import Path

results = []

def check(name, ok, hint=""):
    results.append(ok)
    print(("✅ " if ok else "❌ ") + name + ("" if ok else f"   -> {hint}"))

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()

def read_env(path):
    data = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data

KEYS = ["DATABASE_URL", "QDRANT_URL", "QDRANT_API_KEY", "GROQ_API_KEY"]

# 1. Files exist, no .txt mistakes
check(".env exists", Path(".env").exists(), "create .env in the repo's top folder")
check(".env.example exists", Path(".env.example").exists(), "create .env.example")
check("no .txt versions", not Path(".env.txt").exists() and not Path(".env.example.txt").exists(),
      "rename .env.txt / .env.example.txt")

# 2. .env has correct values
env = read_env(".env") if Path(".env").exists() else {}
check(".env has all 4 keys", all(k in env for k in KEYS), f"keys needed: {KEYS}")
db = env.get("DATABASE_URL", "")
check("DATABASE_URL starts with postgresql+psycopg://", db.startswith("postgresql+psycopg://"),
      "change postgresql:// to postgresql+psycopg://")
check("DATABASE_URL has sslmode=require", "sslmode=require" in db, "add ?sslmode=require at the end")
check("QDRANT_URL starts with https://", env.get("QDRANT_URL", "").startswith("https://"), "copy the cluster URL again")
check("QDRANT_API_KEY is filled", bool(env.get("QDRANT_API_KEY")), "paste your Qdrant API key")

# 3. .env.example has the keys but NO values
ex = read_env(".env.example") if Path(".env.example").exists() else {}
check(".env.example has all 4 keys, all empty", all(k in ex for k in KEYS) and not any(ex.values()),
      "keys only, no values (never put secrets here)")

# 4. Git safety
check(".env is ignored by git", git("check-ignore", ".env") == ".env", "add .env to .gitignore")

# 5. qdrant-client installed
check("qdrant-client in pyproject.toml", "qdrant-client" in Path("pyproject.toml").read_text(),
      "run: uv add qdrant-client")

# 6. config.py loads
try:
    from gst_copilot.config import DATABASE_URL, QDRANT_URL, QDRANT_API_KEY
    check("config.py loads settings", True)
except Exception as e:
    check("config.py loads settings", False, repr(e))
    DATABASE_URL = None

# 7. Neon connects
if DATABASE_URL:
    try:
        from sqlalchemy import create_engine, text
        with create_engine(DATABASE_URL).connect() as conn:
            version = conn.execute(text("select version()")).scalar()
        check(f"Neon connects ({version.split(',')[0]})", True)
    except Exception as e:
        check("Neon connects", False, repr(e)[:150])

    # 8. Qdrant Cloud connects
    try:
        from qdrant_client import QdrantClient
        cols = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY).get_collections()
        check(f"Qdrant Cloud connects ({len(cols.collections)} collections)", True)
    except Exception as e:
        check("Qdrant Cloud connects", False, repr(e)[:150])

# 9. Committed and pushed
tracked = git("ls-files", "src/gst_copilot/config.py", ".env.example", "pyproject.toml", "uv.lock").split()
check("config.py, .env.example, pyproject.toml, uv.lock are committed", len(tracked) == 4, "git add + commit them")
check("nothing left uncommitted", git("status", "--porcelain") == "", "run git status and commit")
check("pushed to GitHub", "ahead" not in git("status", "-sb"), "run git push")

print(f"\n{sum(results)}/{len(results)} checks passed")