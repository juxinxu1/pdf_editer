import streamlit as st
import io
import os
import base64
from pathlib import Path

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDF Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace !important; }

:root {
    --ink: #0f0e0c;
    --paper: #f5f0e8;
    --cream: #ede7d9;
    --amber: #d4822a;
    --rust: #b84c2e;
    --slate: #3d4a5c;
    --white: #fdfaf5;
}

.stApp { background-color: #f5f0e8; }

.main-header {
    background: #0f0e0c;
    color: #f5f0e8;
    padding: 22px 40px;
    border-radius: 6px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.main-header h1 {
    font-family: 'Fraunces', serif !important;
    font-size: 2rem;
    font-weight: 300;
    font-style: italic;
    margin: 0;
    color: #f5f0e8;
}
.main-header p {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c8cfd8;
    margin: 4px 0 0 0;
}
.badge {
    background: #d4822a;
    color: white;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 2px;
}
.section-title {
    font-family: 'Fraunces', serif !important;
    font-size: 1.5rem;
    font-weight: 300;
    font-style: italic;
    color: #0f0e0c;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3d4a5c;
    margin-bottom: 20px;
}
.card {
    background: #fdfaf5;
    border: 1.5px solid #0f0e0c;
    border-radius: 4px;
    padding: 20px;
    margin-bottom: 16px;
}
.card-title {
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #3d4a5c;
    border-bottom: 1px solid rgba(15,14,12,0.1);
    padding-bottom: 10px;
    margin-bottom: 14px;
}
.conv-pair {
    background: #fdfaf5;
    border: 1.5px solid #0f0e0c;
    border-radius: 4px;
    padding: 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}
.conv-pair:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(15,14,12,0.15); }
.fmt-from { font-family: 'Fraunces', serif; font-size: 1.3rem; font-weight: 600; color: #d4822a; }
.fmt-to   { font-family: 'Fraunces', serif; font-size: 1.3rem; font-weight: 600; color: #0f0e0c; }
.fmt-arrow { font-size: 1rem; color: #3d4a5c; }
.fmt-desc  { font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; color: #3d4a5c; margin-top: 6px; }

/* Streamlit widget overrides */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    border: 1.5px solid #0f0e0c !important;
    background: #0f0e0c !important;
    color: #f5f0e8 !important;
    padding: 8px 18px !important;
    transition: all 0.18s !important;
}
.stButton > button:hover { background: #3d4a5c !important; border-color: #3d4a5c !important; }
.stDownloadButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    background: #d4822a !important;
    color: white !important;
    border: none !important;
    padding: 8px 18px !important;
}
.stTextArea textarea {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    background: #f5f0e8 !important;
    border: 1.5px solid rgba(15,14,12,0.2) !important;
    border-radius: 2px !important;
    line-height: 1.8 !important;
}
.stSelectbox select, .stSelectbox > div > div {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 2px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #ede7d9;
    border-bottom: 1.5px solid #0f0e0c;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #3d4a5c !important;
    border-right: 1px solid rgba(15,14,12,0.12) !important;
    padding: 14px 24px !important;
}
.stTabs [aria-selected="true"] {
    background: #fdfaf5 !important;
    color: #0f0e0c !important;
    border-bottom: 2.5px solid #d4822a !important;
}
.stFileUploader > label { font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important; }
.result-box {
    background: #fdfaf5;
    border: 1px solid rgba(15,14,12,0.15);
    border-radius: 3px;
    padding: 18px;
    font-size: 0.82rem;
    line-height: 1.8;
    white-space: pre-wrap;
    color: #0f0e0c;
    max-height: 500px;
    overflow-y: auto;
    font-family: 'DM Mono', monospace;
}
.info-bar {
    background: #ede7d9;
    border: 1px solid rgba(15,14,12,0.1);
    border-radius: 3px;
    padding: 10px 16px;
    font-size: 0.72rem;
    color: #3d4a5c;
    letter-spacing: 0.06em;
    margin-bottom: 12px;
}
hr { border-top: 1px solid rgba(15,14,12,0.12) !important; margin: 16px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div>
    <h1>● PDF Studio</h1>
    <p>Editor & Conversor de Documentos — PDF · JPG · TXT · Word</p>
  </div>
  <span class="badge">✦ IA Integrada</span>
</div>
""", unsafe_allow_html=True)

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab_editor, tab_converter, tab_ai = st.tabs(["✏️  Editar PDF", "🔄  Convertir Archivos", "✦  Asistente IA"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EDITOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_editor:
    st.markdown('<p class="section-title">Editor de Contenido</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Modifica el texto de tu PDF manteniendo el formato</p>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader(
        "Arrastra tu PDF aquí o haz clic para seleccionar",
        type=["pdf"],
        key="editor_upload",
        help="Archivos PDF hasta 50MB"
    )

    if uploaded_pdf:
        st.markdown(f'<div class="info-bar">📄 <strong>{uploaded_pdf.name}</strong> · {uploaded_pdf.size / 1024:.1f} KB</div>', unsafe_allow_html=True)

        # Extract text
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(uploaded_pdf.read()))
            pages_text = []
            for i, page in enumerate(reader.pages):
                pages_text.append(f"{'— Página ' + str(i+1) + ' —' if i > 0 else ''}\n{page.extract_text() or ''}")
            full_text = "\n\n".join(pages_text)
            st.success(f"✓ PDF cargado · {len(reader.pages)} página(s)")
        except Exception as e:
            st.error(f"Error al leer PDF: {e}")
            full_text = ""

        col_edit, col_actions = st.columns([3, 1])

        with col_edit:
            st.markdown('<div class="card-title">Contenido del documento</div>', unsafe_allow_html=True)
            edited_text = st.text_area(
                label="texto",
                value=full_text,
                height=520,
                label_visibility="collapsed",
                key="editor_textarea"
            )
            words = len(edited_text.split()) if edited_text else 0
            st.caption(f"{words:,} palabras · {len(edited_text):,} caracteres")

        with col_actions:
            st.markdown('<div class="card-title">Buscar & Reemplazar</div>', unsafe_allow_html=True)
            find_str = st.text_input("Buscar", placeholder="Texto a buscar...")
            replace_str = st.text_input("Reemplazar con", placeholder="Texto nuevo...")
            if st.button("🔍 Reemplazar todo", key="replace_btn"):
                if find_str:
                    count = edited_text.count(find_str)
                    new_text = edited_text.replace(find_str, replace_str)
                    st.session_state["editor_textarea"] = new_text
                    st.success(f"✓ {count} reemplazos")
                    st.rerun()

            st.markdown("---")
            st.markdown('<div class="card-title">Exportar</div>', unsafe_allow_html=True)

            # Download as TXT
            st.download_button(
                "📄 Descargar TXT",
                data=edited_text.encode("utf-8"),
                file_name=uploaded_pdf.name.replace(".pdf", "_editado.txt"),
                mime="text/plain",
                use_container_width=True,
            )

            # Download as PDF
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas as rl_canvas
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.units import cm

                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=A4,
                                        leftMargin=2*cm, rightMargin=2*cm,
                                        topMargin=2*cm, bottomMargin=2*cm)
                styles = getSampleStyleSheet()
                story = []
                for para in edited_text.split("\n"):
                    if para.strip():
                        story.append(Paragraph(para.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"), styles["Normal"]))
                        story.append(Spacer(1, 4))
                doc.build(story)
                pdf_bytes = pdf_buffer.getvalue()

                st.download_button(
                    "📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name=uploaded_pdf.name.replace(".pdf", "_editado.pdf"),
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"PDF export: {e}")

            # Download as Word (DOCX)
            try:
                from docx import Document as DocxDocument
                docx_buffer = io.BytesIO()
                doc_word = DocxDocument()
                doc_word.add_heading("Documento editado", 0)
                for line in edited_text.split("\n"):
                    if line.strip():
                        doc_word.add_paragraph(line)
                doc_word.save(docx_buffer)
                docx_bytes = docx_buffer.getvalue()

                st.download_button(
                    "📝 Descargar Word",
                    data=docx_bytes,
                    file_name=uploaded_pdf.name.replace(".pdf", "_editado.docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"Word export: {e}")

    else:
        st.markdown("""
        <div style="border:2px dashed #3d4a5c;border-radius:4px;padding:60px 36px;text-align:center;background:#fdfaf5;margin-top:12px;">
          <div style="font-size:3rem;margin-bottom:12px;">📄</div>
          <div style="font-family:'Fraunces',serif;font-size:1.2rem;font-weight:300;color:#0f0e0c;">
            Sube un PDF para comenzar a editar
          </div>
          <div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:#3d4a5c;margin-top:8px;">
            PDF · hasta 50MB · extracción de texto automática
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_converter:
    st.markdown('<p class="section-title">Conversor de Formatos</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Transforma entre PDF, JPG, TXT y Word en ambas direcciones</p>', unsafe_allow_html=True)

    # Conversion pairs visual
    st.markdown("**Conversiones disponibles:**")
    pairs_html = """
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px;">
    """
    pairs = [
        ("PDF","TXT","texto plano"),
        ("PDF","JPG","cada página"),
        ("PDF","Word","editable"),
        ("JPG","PDF","imagen→doc"),
        ("TXT","PDF","texto→doc"),
        ("Word","PDF","word→doc"),
        ("TXT","Word","texto→word"),
        ("Word","TXT","extraer texto"),
    ]
    for frm, to, desc in pairs:
        pairs_html += f"""
        <div class="conv-pair">
          <div class="fmt-from">{frm}</div>
          <div class="fmt-arrow">↕</div>
          <div class="fmt-to">{to}</div>
          <div class="fmt-desc">{desc}</div>
        </div>"""
    pairs_html += "</div>"
    st.markdown(pairs_html, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="card-title">1. Selecciona tu archivo</div>', unsafe_allow_html=True)
        conv_file = st.file_uploader(
            "Sube el archivo a convertir",
            type=["pdf", "jpg", "jpeg", "png", "txt", "docx"],
            key="conv_upload",
            label_visibility="collapsed"
        )
        if conv_file:
            ext = Path(conv_file.name).suffix.lower().lstrip(".")
            icon_map = {"pdf": "📄", "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️", "txt": "📝", "docx": "📋"}
            st.markdown(f'<div class="info-bar">{icon_map.get(ext,"📁")} <strong>{conv_file.name}</strong> · {conv_file.size / 1024:.1f} KB · {ext.upper()}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-title">2. Elige el formato de salida</div>', unsafe_allow_html=True)
        if conv_file:
            ext = Path(conv_file.name).suffix.lower().lstrip(".")
            format_options = {
                "pdf":  ["TXT", "JPG (imágenes)", "Word (DOCX)"],
                "jpg":  ["PDF"],
                "jpeg": ["PDF"],
                "png":  ["PDF", "JPG"],
                "txt":  ["PDF", "Word (DOCX)"],
                "docx": ["PDF", "TXT"],
            }
            available = format_options.get(ext, ["TXT"])
            target_fmt = st.selectbox("Convertir a", available, key="target_fmt")
            convert_btn = st.button("🔄 Convertir ahora", key="conv_btn", use_container_width=True)
        else:
            st.info("Sube un archivo primero para ver las opciones de conversión")
            convert_btn = False

    # ── CONVERSION LOGIC ──
    if conv_file and convert_btn:
        ext = Path(conv_file.name).suffix.lower().lstrip(".")
        base_name = Path(conv_file.name).stem
        file_bytes = conv_file.read()

        with st.spinner("Convirtiendo..."):
            result_files = []  # list of (bytes, filename, mime)

            try:
                # ── PDF → TXT ──
                if ext == "pdf" and "TXT" in target_fmt:
                    from pypdf import PdfReader
                    reader = PdfReader(io.BytesIO(file_bytes))
                    txt = ""
                    for i, page in enumerate(reader.pages):
                        txt += f"\n\n— Página {i+1} —\n\n{page.extract_text() or ''}"
                    result_files.append((txt.encode("utf-8"), f"{base_name}.txt", "text/plain"))

                # ── PDF → JPG ──
                elif ext == "pdf" and "JPG" in target_fmt:
                    try:
                        import fitz  # PyMuPDF
                        pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
                        for i, page in enumerate(pdf_doc):
                            mat = fitz.Matrix(2, 2)
                            pix = page.get_pixmap(matrix=mat)
                            img_bytes = pix.tobytes("jpeg")
                            result_files.append((img_bytes, f"{base_name}_pagina{i+1}.jpg", "image/jpeg"))
                    except ImportError:
                        # Fallback con pdf2image si PyMuPDF no está disponible
                        st.warning("Instala PyMuPDF para conversión PDF→JPG: pip install PyMuPDF")
                        result_files = []

                # ── PDF → DOCX ──
                elif ext == "pdf" and "Word" in target_fmt:
                    from pypdf import PdfReader
                    from docx import Document as DocxDocument
                    reader = PdfReader(io.BytesIO(file_bytes))
                    doc_word = DocxDocument()
                    doc_word.add_heading(base_name, 0)
                    for i, page in enumerate(reader.pages):
                        doc_word.add_heading(f"Página {i+1}", level=2)
                        text = page.extract_text() or ""
                        for line in text.split("\n"):
                            if line.strip():
                                doc_word.add_paragraph(line)
                    buf = io.BytesIO()
                    doc_word.save(buf)
                    result_files.append((buf.getvalue(), f"{base_name}.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))

                # ── JPG/PNG → PDF ──
                elif ext in ("jpg", "jpeg", "png") and "PDF" in target_fmt:
                    from reportlab.pdfgen import canvas as rl_canvas
                    from reportlab.lib.utils import ImageReader
                    from PIL import Image as PILImage
                    img = PILImage.open(io.BytesIO(file_bytes))
                    w, h = img.size
                    buf = io.BytesIO()
                    c = rl_canvas.Canvas(buf, pagesize=(w, h))
                    c.drawImage(ImageReader(io.BytesIO(file_bytes)), 0, 0, w, h)
                    c.save()
                    result_files.append((buf.getvalue(), f"{base_name}.pdf", "application/pdf"))

                # ── PNG → JPG ──
                elif ext == "png" and "JPG" in target_fmt:
                    from PIL import Image as PILImage
                    img = PILImage.open(io.BytesIO(file_bytes)).convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=92)
                    result_files.append((buf.getvalue(), f"{base_name}.jpg", "image/jpeg"))

                # ── TXT → PDF ──
                elif ext == "txt" and "PDF" in target_fmt:
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import cm
                    text = file_bytes.decode("utf-8", errors="replace")
                    buf = io.BytesIO()
                    doc = SimpleDocTemplate(buf, pagesize=A4,
                                            leftMargin=2*cm, rightMargin=2*cm,
                                            topMargin=2*cm, bottomMargin=2*cm)
                    styles = getSampleStyleSheet()
                    story = []
                    for para in text.split("\n"):
                        if para.strip():
                            safe = para.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                            story.append(Paragraph(safe, styles["Normal"]))
                            story.append(Spacer(1, 4))
                    doc.build(story)
                    result_files.append((buf.getvalue(), f"{base_name}.pdf", "application/pdf"))

                # ── TXT → DOCX ──
                elif ext == "txt" and "Word" in target_fmt:
                    from docx import Document as DocxDocument
                    text = file_bytes.decode("utf-8", errors="replace")
                    doc_word = DocxDocument()
                    for line in text.split("\n"):
                        if line.strip():
                            doc_word.add_paragraph(line)
                    buf = io.BytesIO()
                    doc_word.save(buf)
                    result_files.append((buf.getvalue(), f"{base_name}.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))

                # ── DOCX → PDF ──
                elif ext == "docx" and "PDF" in target_fmt:
                    from docx import Document as DocxDocument
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import cm
                    doc_word = DocxDocument(io.BytesIO(file_bytes))
                    text = "\n".join(p.text for p in doc_word.paragraphs)
                    buf = io.BytesIO()
                    doc_rl = SimpleDocTemplate(buf, pagesize=A4,
                                              leftMargin=2*cm, rightMargin=2*cm,
                                              topMargin=2*cm, bottomMargin=2*cm)
                    styles = getSampleStyleSheet()
                    story = []
                    for para in text.split("\n"):
                        if para.strip():
                            safe = para.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                            story.append(Paragraph(safe, styles["Normal"]))
                            story.append(Spacer(1, 4))
                    doc_rl.build(story)
                    result_files.append((buf.getvalue(), f"{base_name}.pdf", "application/pdf"))

                # ── DOCX → TXT ──
                elif ext == "docx" and "TXT" in target_fmt:
                    from docx import Document as DocxDocument
                    doc_word = DocxDocument(io.BytesIO(file_bytes))
                    text = "\n".join(p.text for p in doc_word.paragraphs)
                    result_files.append((text.encode("utf-8"), f"{base_name}.txt", "text/plain"))

            except Exception as e:
                st.error(f"❌ Error en conversión: {e}")
                result_files = []

        # ── SHOW DOWNLOAD BUTTONS ──
        if result_files:
            st.success(f"✓ Conversión completada — {len(result_files)} archivo(s) listo(s)")
            for data, fname, mime in result_files:
                st.download_button(
                    f"📥 Descargar {fname}",
                    data=data,
                    file_name=fname,
                    mime=mime,
                    key=f"dl_{fname}",
                    use_container_width=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
with tab_ai:
    st.markdown('<p class="section-title">Asistente IA</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Usa Claude para mejorar, resumir y reescribir tu documento</p>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="card-title">Texto del documento</div>', unsafe_allow_html=True)
        ai_input = st.text_area(
            "Pega o escribe el contenido",
            height=260,
            placeholder="Pega aquí el texto de tu PDF o documento...",
            label_visibility="collapsed",
            key="ai_input"
        )

        st.markdown('<div class="card-title" style="margin-top:12px;">Instrucción rápida</div>', unsafe_allow_html=True)
        quick_prompts = {
            "✓ Corregir ortografía": "Corrige todos los errores ortográficos y gramaticales sin cambiar el contenido.",
            "📝 Resumir": "Resume este documento en máximo 5 oraciones clave.",
            "💼 Tono formal": "Reescribe este texto con un tono más profesional y formal.",
            "😊 Tono amigable": "Reescribe este texto con un tono más amigable y cercano.",
            "🌐 Traducir a inglés": "Traduce este texto al inglés manteniendo el formato y estructura.",
            "📋 Puntos clave": "Extrae los puntos más importantes como lista numerada.",
        }
        cols_q = st.columns(3)
        for i, (label, prompt_text) in enumerate(quick_prompts.items()):
            if cols_q[i % 3].button(label, key=f"qp_{i}", use_container_width=True):
                st.session_state["ai_prompt_val"] = prompt_text

        ai_prompt = st.text_area(
            "O escribe tu propia instrucción",
            value=st.session_state.get("ai_prompt_val", ""),
            height=100,
            placeholder="Ejemplo: Cambia el nombre Juan por Carlos en todo el documento...",
            key="ai_prompt"
        )

        # API Key
        with st.expander("⚙️ Configuración API de Anthropic"):
            api_key_input = st.text_input(
                "Clave API",
                type="password",
                placeholder="sk-ant-...",
                value=st.session_state.get("api_key", ""),
                key="api_key_field"
            )
            if api_key_input:
                st.session_state["api_key"] = api_key_input
            st.caption("Obtén tu clave en console.anthropic.com · Se guarda solo en esta sesión")

        run_ai = st.button("✦ Procesar con IA", key="ai_run", use_container_width=True)

    with col_right:
        st.markdown('<div class="card-title">Resultado de la IA</div>', unsafe_allow_html=True)

        if run_ai:
            if not ai_input.strip():
                st.warning("Escribe o pega el texto del documento")
            elif not ai_prompt.strip():
                st.warning("Escribe una instrucción para la IA")
            elif not st.session_state.get("api_key"):
                st.warning("Ingresa tu clave API de Anthropic en la sección de configuración")
            else:
                with st.spinner("✦ Claude está procesando tu documento..."):
                    try:
                        import anthropic
                        client = anthropic.Anthropic(api_key=st.session_state["api_key"])
                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=4096,
                            messages=[{
                                "role": "user",
                                "content": f"Instrucción: {ai_prompt}\n\nDocumento:\n\n{ai_input}"
                            }]
                        )
                        result_text = message.content[0].text
                        st.session_state["ai_result"] = result_text
                        st.success("✓ Procesado correctamente")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.session_state["ai_result"] = ""

        ai_result = st.session_state.get("ai_result", "")

        if ai_result:
            st.markdown(f'<div class="result-box">{ai_result}</div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("**Exportar resultado:**")
            c1, c2, c3 = st.columns(3)

            c1.download_button("📄 TXT",
                data=ai_result.encode("utf-8"),
                file_name="resultado_ia.txt", mime="text/plain",
                use_container_width=True)

            # PDF export
            try:
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.units import cm
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4,
                                        leftMargin=2*cm, rightMargin=2*cm,
                                        topMargin=2*cm, bottomMargin=2*cm)
                styles = getSampleStyleSheet()
                story = []
                for para in ai_result.split("\n"):
                    if para.strip():
                        safe = para.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        story.append(Paragraph(safe, styles["Normal"]))
                        story.append(Spacer(1, 4))
                doc.build(story)
                c2.download_button("📥 PDF",
                    data=buf.getvalue(),
                    file_name="resultado_ia.pdf", mime="application/pdf",
                    use_container_width=True)
            except Exception:
                pass

            # DOCX export
            try:
                from docx import Document as DocxDocument
                doc_word = DocxDocument()
                doc_word.add_heading("Resultado IA", 0)
                for line in ai_result.split("\n"):
                    if line.strip():
                        doc_word.add_paragraph(line)
                buf = io.BytesIO()
                doc_word.save(buf)
                c3.download_button("📝 Word",
                    data=buf.getvalue(),
                    file_name="resultado_ia.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            except Exception:
                pass

            if st.button("✏️ Enviar al editor", key="send_to_editor"):
                st.session_state["editor_text_from_ai"] = ai_result
                st.info("Texto guardado. Ve a la pestaña 'Editar PDF' y pégalo manualmente.")
        else:
            st.markdown("""
            <div style="border:1px dashed #c8cfd8;border-radius:3px;padding:60px 24px;text-align:center;color:#3d4a5c;font-size:0.75rem;letter-spacing:0.08em;">
              El resultado de la IA aparecerá aquí
            </div>
            """, unsafe_allow_html=True)


# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:#3d4a5c;padding:10px 0;">
  PDF Studio · Construido con Streamlit · IA por Claude (Anthropic)
</div>
""", unsafe_allow_html=True)
