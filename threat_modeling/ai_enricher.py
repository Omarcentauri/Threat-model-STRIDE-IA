import os
import sys
import json
import requests

AI_KEY = os.getenv("AI_API_KEY")
AI_URL = os.getenv("AI_API_URL")
MODEL_NAME = os.getenv("AI_MODEL_NAME", "gpt-4o-mini")

# Paths where the PyTM report may live. Default is `tm/threats.md`, but in CI
# the artifact can be downloaded into a nested directory.
REPORT_CANDIDATES = [
    os.getenv("REPORT_PATH", "tm/threats.md"),
    os.path.join("pytm-output", "threats.md"),
    os.path.join("pytm-output", "tm", "threats.md"),
    "threats.md",
]
OUTPUT_PATH = "tm/threats_ai.json"

def load_report():
    for path in REPORT_CANDIDATES:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    print("ERROR: No se encontró el reporte de PyTM.")
    print("Se buscaron estas rutas:", ", ".join(REPORT_CANDIDATES))
    sys.exit(1)

def call_ai(report_text):
    if not AI_KEY or not AI_URL:
        print("ERROR: Variables AI_API_KEY o AI_API_URL no configuradas.")
        sys.exit(1)

    prompt = f"""
Eres un experto en modelado de amenazas STRIDE.

Este es un reporte generado por PyTM:

{report_text}

Devuelve solo este JSON válido:
{{
  "summary": {{
    "total_threats": <int>,
    "critical": <int>,
    "high": <int>,
    "medium": <int>,
    "low": <int>,
    "critical_found": true | false
  }},
  "threats": [
    {{
      "id": "T1",
      "title": "",
      "stride": [],
      "severity": "",
      "component": "",
      "description": "",
      "mitigation": ""
    }}
  ]
}}
"""

    body = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(AI_URL, json=body, headers=headers)
    response.raise_for_status()

    try:
        return json.loads(response.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print("ERROR: La IA no devolvió JSON válido.")
        print(response.text)
        sys.exit(1)

def main():
    report = load_report()
    result = call_ai(report)

    os.makedirs("tm", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    summary = result["summary"]
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if summary["critical_found"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
