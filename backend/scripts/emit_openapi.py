"""Write `backend/openapi.json` by importing the app.

**Never by running a server.** No task in this build depends on a live process, no ASGI
server is declared as a dependency, and the frontend generates its client from the
committed file with the backend not running. Importing the app and calling `app.openapi()`
is the whole of it.

Run from `backend/`:

    uv run python scripts/emit_openapi.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402  — after the path insert, by necessity

OUTPUT = Path(__file__).resolve().parent.parent / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    operations = sorted(
        operation["operationId"]
        for path in schema["paths"].values()
        for operation in path.values()
    )
    print(f"wrote {OUTPUT.relative_to(OUTPUT.parent.parent)}")
    print(f"openapi {schema['openapi']}, {len(operations)} operations")
    for one in operations:
        print(f"  {one}")


if __name__ == "__main__":
    main()
