import json
import sys

from app.main import app


def generate_openapi(output_path: str = "docs/openapi.json"):
    with open(output_path, "w") as f:
        json.dump(app.openapi(), f, indent=2, ensure_ascii=False)
    print(f">>> OpenAPI spec berhasil digenerate ke {output_path} <<<")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "docs/openapi.json"
    generate_openapi(path)
