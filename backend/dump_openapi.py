import json

from app.main import app


def dump():
    schema = app.openapi()
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)


if __name__ == "__main__":
    dump()
