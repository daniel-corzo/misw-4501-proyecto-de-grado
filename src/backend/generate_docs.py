#!/usr/bin/env python3
"""
Generates a merged OpenAPI spec from all TravelHub API microservices.

Worker services (e.g. notificaciones) are intentionally excluded — they expose
a /health endpoint for monitoring but no business REST API.

Usage:
    python3 generate_docs.py <output_dir>

Output:
    <output_dir>/openapi.json  — merged OpenAPI 3.x spec
    <output_dir>/docs.html     — static Swagger UI pointing to /api/openapi.json
"""

import json
import os
import subprocess
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Services that expose a REST API.
# Workers (e.g. notificaciones) are excluded — they have /health but no business endpoints.
API_SERVICES = [
    "auth",
    "usuarios",
    "busqueda",
    "hoteles",
    "inventario",
    "reservas",
    "pagos",
]

SWAGGER_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TravelHub API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: '/api/openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: 'StandaloneLayout',
    });
  </script>
</body>
</html>
"""


def get_service_spec(service: str) -> dict | None:
    """
    Imports the FastAPI app for the given service in an isolated subprocess
    and returns its OpenAPI spec dict. Returns None on failure.
    """
    script = (
        f"import sys; "
        f"sys.path.insert(0, '{BACKEND_DIR}/common'); "
        f"sys.path.insert(0, '{BACKEND_DIR}/{service}'); "
        f"from app.main import app; "
        f"import json; print(json.dumps(app.openapi()))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        print(f"  [warn] {service}: {result.stderr.strip()[:200]}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  [warn] {service}: invalid JSON in spec output", file=sys.stderr)
        return None


def merge_specs(specs: list[dict]) -> dict:
    merged = {
        "openapi": "3.1.0",
        "info": {
            "title": "TravelHub API",
            "description": "Aggregated API documentation for all TravelHub microservices.",
            "version": "1.0.0",
        },
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {},
        },
        "tags": [],
    }
    for spec in specs:
        merged["paths"].update(spec.get("paths", {}))
        components = spec.get("components", {})
        merged["components"]["schemas"].update(components.get("schemas", {}))
        merged["components"]["securitySchemes"].update(components.get("securitySchemes", {}))
        for tag in spec.get("tags", []):
            if tag not in merged["tags"]:
                merged["tags"].append(tag)
    return merged


def main() -> None:
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(output_dir, exist_ok=True)

    specs = []
    for service in API_SERVICES:
        print(f"  → {service}...", file=sys.stderr)
        spec = get_service_spec(service)
        if spec:
            specs.append(spec)

    merged = merge_specs(specs)

    openapi_path = os.path.join(output_dir, "openapi.json")
    with open(openapi_path, "w") as f:
        json.dump(merged, f, indent=2)

    docs_path = os.path.join(output_dir, "docs.html")
    with open(docs_path, "w") as f:
        f.write(SWAGGER_HTML)

    print(
        f"Docs generated: {len(specs)}/{len(API_SERVICES)} services "
        f"→ {openapi_path}, {docs_path}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
