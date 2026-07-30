import json
from pathlib import Path

from housepy.main import app

OUTPUT_PATH = Path("docs/api/openapi.json")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(app.openapi(), indent=2))


if __name__ == "__main__":
    main()
