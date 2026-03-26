# 📄 PDF Studio — Editor & Conversor

Una app completa para editar, convertir y procesar documentos PDF con IA integrada.

## ✨ Funcionalidades

- **✏️ Editor de PDF** — Extrae texto, edita, buscar & reemplazar, exporta como PDF/TXT/Word
- **🔄 Conversor** — PDF↔TXT, PDF↔JPG, PDF↔Word, TXT↔Word, JPG→PDF
- **✦ Asistente IA** — Claude para corregir, resumir, traducir y reescribir documentos

---

## 🚀 Desplegar en Streamlit Cloud (GRATIS)

### Paso 1 — Subir a GitHub

1. Crea una cuenta en [github.com](https://github.com) si no tienes
2. Crea un **repositorio nuevo** (puede ser privado)
3. Sube estos dos archivos:
   - `app.py`
   - `requirements.txt`

```bash
# O desde terminal:
git init
git add app.py requirements.txt README.md
git commit -m "PDF Studio app"
git remote add origin https://github.com/TU_USUARIO/pdf-studio.git
git push -u origin main
```

### Paso 2 — Deployar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en **"New app"**
4. Selecciona tu repositorio y la rama `main`
5. En **"Main file path"** escribe: `app.py`
6. Haz clic en **"Deploy!"**

✅ En ~2 minutos tendrás tu URL pública tipo:
`https://tu-usuario-pdf-studio-app-xxxxx.streamlit.app`

---

## 🔑 Usar el Asistente IA

Para usar la función de IA necesitas una clave API de Anthropic:
1. Regístrate en [console.anthropic.com](https://console.anthropic.com)
2. Crea una API key
3. En la app, ve a "✦ Asistente IA" → "Configuración API" e ingresa tu clave

**Opcional:** Para no escribir la clave cada vez, en Streamlit Cloud puedes configurarla como **secret**:
- En Streamlit Cloud → tu app → **Settings → Secrets**
- Añade: `ANTHROPIC_API_KEY = "sk-ant-..."`

---

## 📦 Dependencias

| Paquete | Uso |
|---------|-----|
| `streamlit` | Framework web |
| `pypdf` | Leer PDFs |
| `reportlab` | Generar PDFs |
| `python-docx` | Leer/escribir Word |
| `Pillow` | Procesar imágenes |
| `anthropic` | API de Claude IA |
| `PyMuPDF` | PDF → JPG de alta calidad |
