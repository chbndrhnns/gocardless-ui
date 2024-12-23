import json
from pathlib import Path

project_dir = Path(__file__).parents[2]

LINKS_FILE = Path(project_dir / "data" / "account-links.json")


def read_links():
    try:
        if not LINKS_FILE.exists():
            LINKS_FILE.parent.mkdir(parents=True, exist_ok=True)
            write_links({"links": []})
            return {"links": []}

        with open(LINKS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error reading links: {str(e)}")


def write_links(data):
    try:
        LINKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LINKS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise Exception(f"Error writing links: {str(e)}")
