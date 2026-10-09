from pathlib import Path

folders = [
    "data/raw", "data/parsed", "data/eval",
    "src/gst_copilot/scrape", "src/gst_copilot/parse",
    "src/gst_copilot/index", "src/gst_copilot/retrieve",
    "src/gst_copilot/agent", "src/gst_copilot/api",
    "app", "scripts", "tests",
]

for f in folders:
    Path(f).mkdir(parents=True, exist_ok=True)
    # an empty __init__.py makes each src folder a Python package
    if f.startswith("src/"):
        (Path(f) / "__init__.py").touch()

(Path("src/gst_copilot") / "__init__.py").touch()
# .gitkeep lets git track the empty data folders
for f in ["data/raw", "data/parsed", "data/eval"]:
    (Path(f) / ".gitkeep").touch()

print("Structure created")