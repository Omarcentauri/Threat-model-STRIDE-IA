# Threat-model-STRIDE-IA

# 🛡️ Kultur Threat Modeling Demo  
### _Modelos que predicen amenazas desde el diseño (STRIDE + PyTM + IA + GitHub Actions)_

Este repositorio demuestra cómo realizar **modelado de amenazas automatizado** desde el diseño usando:

- **PyTM** (OWASP)  
- **IA** para clasificación y priorización (STRIDE)  
- **GitHub Actions** para ejecutar el análisis en cada Pull Request  

El objetivo de esta demo es mostrar cómo integrar **Threat Modeling as Code** y **AI-assisted risk analysis** dentro del ciclo de desarrollo.

---

## 📌 ¿Qué es esto?

Este repo **no contiene código de aplicación real**.  
Aquí modelamos el sistema únicamente desde el diseño, expresado como código Python usando PyTM.

Luego:

1. PyTM genera amenazas automáticamente basadas en reglas internas.  
2. Una IA clasifica esas amenazas según STRIDE, su severidad y mitigación recomendada.  
3. GitHub Actions decide si el Pull Request puede mergearse o debe bloquearse.

👉 Esto demuestra cómo llevar la seguridad **desde el diseño** directamente al pipeline de CI/CD.

---

## 🧱 Arquitectura del Repositorio

- .
- ├── tm_kultur.py # Modelo PyTM (Threat Model as Code)
- ├── threat_modeling/
- │ └── ai_enricher.py # IA para clasificación y priorización
- ├── docs/
- │ └── basic_template.md # Plantilla para el reporte de PyTM
- └── .github/
- └── workflows/
- └── threat_modeling.yml # Pipeline de GitHub Actions


---

## ⚙️ ¿Cómo funciona?

### 1️⃣ Modelo de amenazas como código — PyTM

El archivo `tm_kultur.py` describe:

- Actores  
- Componentes  
- Datastores  
- Flujos de datos  
- Boundaries  

PyTM usa esta definición para generar:

- `tm/threats.md` → Reporte técnico de amenazas  
- `tm/dfd.png` → Diagrama de flujo de datos  

> Estas amenazas NO están clasificadas bajo STRIDE aún.

---

### 2️⃣ Enriquecimiento con IA

El script `ai_enricher.py`:

- Lee `threats.md`  
- Clasifica cada amenaza bajo STRIDE  
- Asigna severidad (Low, Medium, High, Critical)  
- Genera mitigaciones  
- Produce un JSON final: `tm/threats_ai.json`  

Si existe al menos 1 amenaza crítica: 
critical_found = true
exit 1


➡️ Esto **bloquea el Pull Request**.

---

### 3️⃣ GitHub Actions — Pipeline automático

Cada Pull Request dispara el workflow:

1. **Generate PyTM Threat Report**  
2. **AI Threat Classification**

Artifacts disponibles:

- `pytm-output/` → threats.md + dfd.png  
- `ai-output/` → threats_ai.json  

Si la IA detecta amenazas críticas, el pipeline falla y el PR queda bloqueado.

---

## 🔧 Configuración requerida

### 1. Secrets en GitHub

Ir a:

**Settings → Secrets and Variables → Actions**

Crear:

| Secret Name      | Valor                         |
|------------------|--------------------------------|
| `AI_API_KEY`      | API key del proveedor de IA    |
| `AI_API_URL`      | Endpoint HTTP del modelo       |
| `AI_MODEL_NAME`   | (Opcional) Nombre del modelo   |

---

## 🧪 Probar localmente (opcional)

### 

pip install pytm graphviz
python tm_kultur.py --report docs/basic_template.md > tm/threats.md
python tm_kultur.py --dfd | dot -Tpng -o tm/dfd.png

IA
export AI_API_KEY="..."
export AI_API_URL="..."
python threat_modeling/ai_enricher.py

## 🚀 ¿Qué demuestra esta demo?

✔ Modelado de amenazas desde el diseño (Threat Modeling as Code).
✔ Automatización con PyTM.
✔ Clasificación STRIDE asistida por IA.
✔ Priorización de severidad.
✔ Pipeline obligatorio que bloquea merges con amenazas críticas.
✔ DevSecOps real: seguridad en cada Pull Request.

## ¿Cómo usar este repositorio?

1. Realiza un cambio en tm_kultur.py.
2. Abre un Pull Request.
3. Observa cómo:
4. PyTM genera amenazas
5. IA las clasifica
6. El PR queda aprobado o bloqueado según el riesgo
