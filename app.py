import streamlit as st
import io
import zipfile
from pathlib import Path

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDF Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&display=swap');
html, body, [class*="css"] { font-family: 'DM Mono', monospace !important; }
.stApp { background-color: #f5f0e8; }
.hdr { background:#0f0e0c; color:#f5f0e8; padding:20px 32px; border-radius:6px; margin-bottom:20px; }
.hdr h1 { font-family:'Fraunces',serif; font-size:1.8rem; font-weight:300; font-style:italic; margin:0; color:#f5f0e8; }
.hdr p  { font-size:0.68rem; letter-spacing:0.12em; text-transform:uppercase; color:#c8cfd8; margin:4px 0 0 0; }
.badge  { background:#d4822a; color:white; font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; padding:4px 10px; border-radius:2px; float:right; margin-top:-36px; }
.sec-title { font-family:'Fraunces',serif !important; font-size:1.4rem; font-weight:300; font-style:italic; color:#0f0e0c; }
.sec-sub   { font-size:0.67rem; letter-spacing:0.1em; text-transform:uppercase; color:#3d4a5c; margin-bottom:18px; }
.info-bar  { background:#ede7d9; border:1px solid rgba(15,14,12,0.1); border-radius:3px; padding:10px 14px;
             font-size:0.71rem; color:#3d4a5c; letter-spacing:0.05em; margin-bottom:12px; }
.ok-box    { background:#eaf4ea; border-left:3px solid #2d5a27; padding:10px 14px; border-radius:0 3px 3px 0;
             font-size:0.75rem; color:#2d5a27; margin-bottom:10px; }
.err-box   { background:#faeaea; border-left:3px solid #b84c2e; padding:10px 14px; border-radius:0 3px 3px 0;
             font-size:0.75rem; color:#b84c2e; margin-bottom:10px; }
.warn-box  { background:#fdf6e3; border-left:3px solid #d4822a; padding:10px 14px; border-radius:0 3px 3px 0;
             font-size:0.75rem; color:#7a4a15; margin-bottom:10px; }
.stButton>button { font-family:'DM Mono',monospace !important; font-size:0.7rem !important;
  letter-spacing:0.1em !important; text-transform:uppercase !important; border-radius:2px !important;
  border:1.5px solid #0f0e0c !important; background:#0f0e0c !important; color:#f5f0e8 !important; }
.stButton>button:hover { background:#3d4a5c !important; border-color:#3d4a5c !important; }
.stDownloadButton>button { font-family:'DM Mono',monospace !important; font-size:0.7rem !important;
  letter-spacing:0.1em !important; text-transform:uppercase !important; border-radius:2px !important;
  background:#d4822a !important; color:white !important; border:none !important; }
.stTextArea textarea { font-family:'DM Mono',monospace !important; font-size:0.82rem !important;
  background:#fdfaf5 !important; border:1.5px solid rgba(15,14,12,0.2) !important;
  border-radius:2px !important; line-height:1.8 !important; }
.stTabs [data-baseweb="tab-list"] { background:#ede7d9; border-bottom:1.5px solid #0f0e0c; gap:0; }
.stTabs [data-baseweb="tab"] { font-family:'DM Mono',monospace !important; font-size:0.7rem !important;
  letter-spacing:0.1em !important; text-transform:uppercase !important; color:#3d4a5c !important;
  border-right:1px solid rgba(15,14,12,0.12) !important; padding:13px 22px !important; }
.stTabs [aria-selected="true"] { background:#fdfaf5 !important; color:#0f0e0c !important;
  border-bottom:2.5px solid #d4822a !important; }
div[data-testid="stFileUploader"] { border:2px dashed #3d4a5c; border-radius:4px;
  background:#fdfaf5; padding:8px; }
div[data-testid="stFileUploader"]:hover { border-color:#d4822a; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hdr">
  <h1>● PDF Studio</h1>
  <p>Editor & Conversor — PDF · JPG · TXT · Word</p>
  <span class="badge">✦ IA Integrada</span>
</div>
""", unsafe_allow_html=True)

# ─── SESSION STATE INIT ────────────────────────────────────────────────────────
for key, default in {
    "extracted_text": "",
    "edited_text": "",
    "editor_filename": "",
    "editor_file_bytes": None,
    "ai_result": "",
    "api_key": "",
    "conv_result_files": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def extract_pdf_text(file_bytes: bytes) -> tuple[str, int, list[str]]:
    """Extract text from PDF. Returns (full_text, num_pages, errors)."""
    errors = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for i, page in enumerate(reader.pages):
            raw = page.extract_text() or ""
            pages.append(f"{'─── Página ' + str(i+1) + ' ───' if i > 0 else '─── Página 1 ───'}\n{raw}")
        return "\n\n".join(pages), len(reader.pages), errors
    except Exception as e:
        errors.append(str(e))
        return "", 0, errors


def text_to_pdf_bytes(text: str) -> bytes:
    """Convert plain text to PDF bytes using reportlab."""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontName = "Helvetica"
    normal.fontSize = 10
    normal.leading = 15

    story = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 6))
            continue
        safe = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if stripped.startswith("─── Página"):
            h_style = styles["Heading2"]
            story.append(Paragraph(safe, h_style))
        else:
            story.append(Paragraph(safe, normal))
        story.append(Spacer(1, 2))
    doc.build(story)
    return buf.getvalue()


def text_to_docx_bytes(text: str, title: str = "Documento") -> bytes:
    """Convert plain text to DOCX bytes."""
    from docx import Document as DocxDoc
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = DocxDoc()
    # Margins
    for section in doc.sections:
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)

    doc.add_heading(title, level=0)
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            doc.add_paragraph("")
            continue
        if stripped.startswith("─── Página"):
            doc.add_heading(stripped.replace("─── ", "").replace(" ───", ""), level=2)
        else:
            p = doc.add_paragraph(stripped)
            p.style.font.size = Pt(10.5)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def validate_file_size(file, max_mb: int = 50) -> bool:
    return file.size <= max_mb * 1024 * 1024


def safe_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_editor, tab_converter, tab_ai = st.tabs([
    "✏️  Editar PDF",
    "🔄  Convertir Archivos",
    "✦  Asistente IA",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EDITOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_editor:
    st.markdown('<p class="sec-title">Editor de PDF</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Sube un PDF, edita el texto y descarga el resultado</p>', unsafe_allow_html=True)

    # ── Upload ──
    uploaded = st.file_uploader(
        "📄 Arrastra tu PDF aquí o haz clic para seleccionar (máx. 50MB)",
        type=["pdf"],
        key="editor_upload",
    )

    # ── Process upload ──
    if uploaded is not None:
        # Validate
        if not validate_file_size(uploaded):
            st.markdown('<div class="err-box">❌ El archivo supera los 50MB permitidos.</div>', unsafe_allow_html=True)
        elif uploaded.name != st.session_state.get("editor_filename"):
            # New file → extract
            with st.spinner("Extrayendo texto del PDF..."):
                raw_bytes = uploaded.read()
                text, n_pages, errs = extract_pdf_text(raw_bytes)
            if errs:
                st.markdown(f'<div class="err-box">❌ Error al leer el PDF: {errs[0]}</div>', unsafe_allow_html=True)
            else:
                st.session_state["extracted_text"]   = text
                st.session_state["edited_text"]      = text
                st.session_state["editor_filename"]  = uploaded.name
                st.session_state["editor_file_bytes"] = raw_bytes
                st.markdown(f'<div class="ok-box">✓ PDF cargado: <strong>{uploaded.name}</strong> · {n_pages} página(s) · {uploaded.size/1024:.1f} KB</div>', unsafe_allow_html=True)

    # ── Show editor if text loaded ──
    if st.session_state["extracted_text"]:
        st.markdown(f'<div class="info-bar">📄 Editando: <strong>{st.session_state["editor_filename"]}</strong></div>', unsafe_allow_html=True)

        col_edit, col_tools = st.columns([3, 1])

        with col_tools:
            # ── Stats ──
            words = len(st.session_state["edited_text"].split())
            chars = len(st.session_state["edited_text"])
            st.metric("Palabras", f"{words:,}")
            st.metric("Caracteres", f"{chars:,}")

            st.markdown("---")

            # ── Find & Replace ──
            st.markdown("**🔍 Buscar y Reemplazar**")
            find_str    = st.text_input("Buscar",        placeholder="Texto a buscar...",    key="find_input")
            replace_str = st.text_input("Reemplazar con", placeholder="Texto nuevo...",      key="replace_input")
            match_case  = st.checkbox("Distinguir mayúsculas", key="match_case")

            col_r1, col_r2 = st.columns(2)
            do_replace = col_r1.button("Reemplazar", key="btn_replace", use_container_width=True)
            do_reset   = col_r2.button("Restaurar",  key="btn_reset",   use_container_width=True)

            if do_replace:
                if not find_str.strip():
                    st.markdown('<div class="warn-box">Escribe el texto a buscar.</div>', unsafe_allow_html=True)
                else:
                    src = st.session_state["edited_text"]
                    if match_case:
                        count = src.count(find_str)
                        new_text = src.replace(find_str, replace_str)
                    else:
                        import re
                        count = len(re.findall(re.escape(find_str), src, re.IGNORECASE))
                        new_text = re.sub(re.escape(find_str), replace_str, src, flags=re.IGNORECASE)
                    st.session_state["edited_text"] = new_text
                    if count:
                        st.markdown(f'<div class="ok-box">✓ {count} reemplazos realizados.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="warn-box">No se encontró el texto.</div>', unsafe_allow_html=True)
                    st.rerun()

            if do_reset:
                st.session_state["edited_text"] = st.session_state["extracted_text"]
                st.markdown('<div class="ok-box">✓ Texto restaurado al original.</div>', unsafe_allow_html=True)
                st.rerun()

            st.markdown("---")

            # ── Downloads ──
            st.markdown("**📥 Descargar**")

            # TXT
            st.download_button(
                "📄 Descargar TXT",
                data=st.session_state["edited_text"].encode("utf-8"),
                file_name=st.session_state["editor_filename"].replace(".pdf", "_editado.txt"),
                mime="text/plain",
                use_container_width=True,
                key="dl_txt_editor",
            )

            # PDF
            try:
                pdf_bytes = text_to_pdf_bytes(st.session_state["edited_text"])
                st.download_button(
                    "📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name=st.session_state["editor_filename"].replace(".pdf", "_editado.pdf"),
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf_editor",
                )
            except Exception as e:
                st.markdown(f'<div class="err-box">PDF export error: {e}</div>', unsafe_allow_html=True)

            # DOCX
            try:
                docx_bytes = text_to_docx_bytes(
                    st.session_state["edited_text"],
                    title=st.session_state["editor_filename"].replace(".pdf", "")
                )
                st.download_button(
                    "📝 Descargar Word",
                    data=docx_bytes,
                    file_name=st.session_state["editor_filename"].replace(".pdf", "_editado.docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="dl_docx_editor",
                )
            except Exception as e:
                st.markdown(f'<div class="err-box">Word export error: {e}</div>', unsafe_allow_html=True)

        with col_edit:
            st.markdown("**Contenido editable** — modifica libremente el texto:")
            new_text = st.text_area(
                label="editor_area",
                value=st.session_state["edited_text"],
                height=560,
                label_visibility="collapsed",
                key="editor_textarea_widget",
            )
            # Persist edits
            if new_text != st.session_state["edited_text"]:
                st.session_state["edited_text"] = new_text

    else:
        st.markdown("""
        <div style="border:2px dashed #3d4a5c;border-radius:4px;padding:70px 36px;
                    text-align:center;background:#fdfaf5;margin-top:16px;">
          <div style="font-size:3.5rem;margin-bottom:14px;">📄</div>
          <div style="font-family:'Fraunces',serif;font-size:1.2rem;font-weight:300;color:#0f0e0c;">
            Sube un PDF para comenzar
          </div>
          <div style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;
                      color:#3d4a5c;margin-top:8px;">
            Se extraerá el texto automáticamente · Edita · Descarga como PDF, TXT o Word
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_converter:
    st.markdown('<p class="sec-title">Conversor de Formatos</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Convierte entre PDF · JPG · TXT · Word en ambas direcciones</p>', unsafe_allow_html=True)

    # ── Supported conversions table ──
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;">
      <div style="background:#fdfaf5;border:1.5px solid #0f0e0c;border-radius:4px;padding:14px;text-align:center;">
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#d4822a;">PDF</div>
        <div style="font-size:0.8rem;color:#3d4a5c;">↕</div>
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;">TXT</div>
        <div style="font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#3d4a5c;margin-top:4px;">texto plano</div>
      </div>
      <div style="background:#fdfaf5;border:1.5px solid #0f0e0c;border-radius:4px;padding:14px;text-align:center;">
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#d4822a;">PDF</div>
        <div style="font-size:0.8rem;color:#3d4a5c;">↓</div>
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;">JPG</div>
        <div style="font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#3d4a5c;margin-top:4px;">cada página</div>
      </div>
      <div style="background:#fdfaf5;border:1.5px solid #0f0e0c;border-radius:4px;padding:14px;text-align:center;">
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#d4822a;">PDF</div>
        <div style="font-size:0.8rem;color:#3d4a5c;">↕</div>
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;">Word</div>
        <div style="font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#3d4a5c;margin-top:4px;">editable</div>
      </div>
      <div style="background:#fdfaf5;border:1.5px solid #0f0e0c;border-radius:4px;padding:14px;text-align:center;">
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;color:#d4822a;">JPG/PNG</div>
        <div style="font-size:0.8rem;color:#3d4a5c;">↑</div>
        <div style="font-family:'Fraunces',serif;font-size:1.2rem;">PDF</div>
        <div style="font-size:0.6rem;letter-spacing:0.1em;text-transform:uppercase;color:#3d4a5c;margin-top:4px;">imagen → doc</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_up, col_fmt = st.columns([1, 1])

    with col_up:
        conv_file = st.file_uploader(
            "📁 Sube el archivo a convertir",
            type=["pdf", "jpg", "jpeg", "png", "txt", "docx"],
            key="conv_upload",
        )
        if conv_file:
            if not validate_file_size(conv_file, max_mb=100):
                st.markdown('<div class="err-box">❌ El archivo supera los 100MB.</div>', unsafe_allow_html=True)
                conv_file = None
            else:
                ext = Path(conv_file.name).suffix.lower().lstrip(".")
                icons = {"pdf":"📄","jpg":"🖼️","jpeg":"🖼️","png":"🖼️","txt":"📝","docx":"📋"}
                st.markdown(
                    f'<div class="info-bar">{icons.get(ext,"📁")} '
                    f'<strong>{conv_file.name}</strong> · {conv_file.size/1024:.1f} KB · {ext.upper()}</div>',
                    unsafe_allow_html=True
                )

    with col_fmt:
        if conv_file:
            ext = Path(conv_file.name).suffix.lower().lstrip(".")
            options_map = {
                "pdf":  ["TXT — Texto plano", "JPG — Imagen por página", "Word — DOCX editable"],
                "jpg":  ["PDF — Documento"],
                "jpeg": ["PDF — Documento"],
                "png":  ["PDF — Documento", "JPG — Convertir formato"],
                "txt":  ["PDF — Documento", "Word — DOCX editable"],
                "docx": ["PDF — Documento", "TXT — Texto plano"],
            }
            available = options_map.get(ext, ["TXT — Texto plano"])
            target = st.selectbox("Convertir a →", available, key="conv_target")
            btn_convert = st.button("🔄 Convertir ahora", key="btn_conv", use_container_width=True)

            if btn_convert:
                file_bytes = conv_file.read()
                base_name  = Path(conv_file.name).stem
                result_files = []

                with st.spinner("Procesando conversión..."):
                    try:
                        # ── PDF → TXT ──
                        if ext == "pdf" and "TXT" in target:
                            text, _, errs = extract_pdf_text(file_bytes)
                            if errs:
                                st.markdown(f'<div class="err-box">❌ {errs[0]}</div>', unsafe_allow_html=True)
                            else:
                                result_files.append((text.encode("utf-8"), f"{base_name}.txt", "text/plain"))

                        # ── PDF → JPG ──
                        elif ext == "pdf" and "JPG" in target:
                            try:
                                import fitz
                                pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
                                for i, page in enumerate(pdf_doc):
                                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                                    result_files.append((
                                        pix.tobytes("jpeg"),
                                        f"{base_name}_p{i+1}.jpg",
                                        "image/jpeg"
                                    ))
                            except ImportError:
                                st.markdown('<div class="err-box">❌ PyMuPDF no está instalado. Verifica requirements.txt.</div>', unsafe_allow_html=True)

                        # ── PDF → DOCX ──
                        elif ext == "pdf" and "Word" in target:
                            text, _, errs = extract_pdf_text(file_bytes)
                            if errs:
                                st.markdown(f'<div class="err-box">❌ {errs[0]}</div>', unsafe_allow_html=True)
                            else:
                                docx_bytes = text_to_docx_bytes(text, base_name)
                                result_files.append((
                                    docx_bytes, f"{base_name}.docx",
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                ))

                        # ── JPG/PNG → PDF ──
                        elif ext in ("jpg", "jpeg", "png") and "PDF" in target:
                            from reportlab.pdfgen import canvas as rl_canvas
                            from reportlab.lib.utils import ImageReader
                            from PIL import Image as PILImage
                            img = PILImage.open(io.BytesIO(file_bytes))
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            w, h = img.size
                            img_buf = io.BytesIO()
                            img.save(img_buf, format="JPEG", quality=95)
                            img_buf.seek(0)
                            buf = io.BytesIO()
                            c = rl_canvas.Canvas(buf, pagesize=(w, h))
                            c.drawImage(ImageReader(img_buf), 0, 0, w, h)
                            c.save()
                            result_files.append((buf.getvalue(), f"{base_name}.pdf", "application/pdf"))

                        # ── PNG → JPG ──
                        elif ext == "png" and "JPG" in target:
                            from PIL import Image as PILImage
                            img = PILImage.open(io.BytesIO(file_bytes)).convert("RGB")
                            buf = io.BytesIO()
                            img.save(buf, format="JPEG", quality=92)
                            result_files.append((buf.getvalue(), f"{base_name}.jpg", "image/jpeg"))

                        # ── TXT → PDF ──
                        elif ext == "txt" and "PDF" in target:
                            text = file_bytes.decode("utf-8", errors="replace")
                            pdf_b = text_to_pdf_bytes(text)
                            result_files.append((pdf_b, f"{base_name}.pdf", "application/pdf"))

                        # ── TXT → DOCX ──
                        elif ext == "txt" and "Word" in target:
                            text = file_bytes.decode("utf-8", errors="replace")
                            result_files.append((
                                text_to_docx_bytes(text, base_name),
                                f"{base_name}.docx",
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            ))

                        # ── DOCX → PDF ──
                        elif ext == "docx" and "PDF" in target:
                            from docx import Document as DocxDoc
                            doc_w = DocxDoc(io.BytesIO(file_bytes))
                            text  = "\n".join(p.text for p in doc_w.paragraphs if p.text.strip())
                            result_files.append((text_to_pdf_bytes(text), f"{base_name}.pdf", "application/pdf"))

                        # ── DOCX → TXT ──
                        elif ext == "docx" and "TXT" in target:
                            from docx import Document as DocxDoc
                            doc_w = DocxDoc(io.BytesIO(file_bytes))
                            text  = "\n".join(p.text for p in doc_w.paragraphs)
                            result_files.append((text.encode("utf-8"), f"{base_name}.txt", "text/plain"))

                        st.session_state["conv_result_files"] = result_files

                    except Exception as e:
                        st.markdown(f'<div class="err-box">❌ Error en conversión: {e}</div>', unsafe_allow_html=True)

        else:
            st.info("Sube un archivo a la izquierda para ver las opciones.")

    # ── Download results ──
    results = st.session_state.get("conv_result_files", [])
    if results:
        st.markdown("---")
        st.markdown(f'<div class="ok-box">✓ Conversión completada — {len(results)} archivo(s) listo(s)</div>', unsafe_allow_html=True)

        if len(results) == 1:
            data, fname, mime = results[0]
            st.download_button(
                f"📥 Descargar {fname}",
                data=data, file_name=fname, mime=mime,
                use_container_width=True, key="dl_conv_single",
            )
        else:
            # Multiple files → zip
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for data, fname, _ in results:
                    zf.writestr(fname, data)
            st.download_button(
                f"📦 Descargar todos ({len(results)} archivos) como ZIP",
                data=zip_buf.getvalue(),
                file_name="convertidos.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_conv_zip",
            )
            st.caption("También puedes descargarlos individualmente:")
            for i, (data, fname, mime) in enumerate(results):
                st.download_button(
                    f"  └─ {fname}",
                    data=data, file_name=fname, mime=mime,
                    key=f"dl_conv_{i}", use_container_width=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
with tab_ai:
    st.markdown('<p class="sec-title">Asistente IA</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-sub">Claude procesa, corrige, resume y transforma tu documento</p>', unsafe_allow_html=True)

    # ── API Key ──
    with st.expander("⚙️ Configuración — Clave API de Anthropic", expanded=not bool(st.session_state["api_key"])):
        api_input = st.text_input(
            "Clave API (sk-ant-...)",
            type="password",
            value=st.session_state["api_key"],
            placeholder="sk-ant-api03-...",
            key="api_key_input",
        )
        if api_input != st.session_state["api_key"]:
            st.session_state["api_key"] = api_input

        if st.session_state["api_key"]:
            st.markdown('<div class="ok-box">✓ Clave API configurada</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warn-box">
              ⚠️ Necesitas una clave API de Anthropic.<br>
              Obtén la tuya gratis en <strong>console.anthropic.com</strong> → API Keys
            </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    with col_l:
        # ── Option: use already-loaded PDF or paste text ──
        source_mode = st.radio(
            "Fuente del texto",
            ["Pegar texto manualmente", "Usar PDF del editor"],
            horizontal=True,
            key="ai_source_mode",
        )

        if source_mode == "Usar PDF del editor" and st.session_state["edited_text"]:
            ai_text = st.session_state["edited_text"]
            st.markdown(
                f'<div class="info-bar">📄 Usando: <strong>{st.session_state["editor_filename"]}</strong> '
                f'({len(ai_text):,} chars)</div>', unsafe_allow_html=True
            )
            st.text_area("Vista previa", value=ai_text[:800] + ("..." if len(ai_text) > 800 else ""),
                         height=180, disabled=True, key="ai_preview")
        elif source_mode == "Usar PDF del editor" and not st.session_state["edited_text"]:
            st.markdown('<div class="warn-box">⚠️ No hay PDF cargado en el editor. Ve a la pestaña "Editar PDF" primero.</div>', unsafe_allow_html=True)
            ai_text = ""
        else:
            ai_text = st.text_area(
                "Pega el texto de tu documento aquí",
                height=240,
                placeholder="Pega aquí el contenido del PDF o cualquier texto...",
                key="ai_manual_text",
                label_visibility="visible",
            )

        st.markdown("---")

        # ── Quick prompts ──
        st.markdown("**Instrucciones rápidas:**")
        quick = {
            "✓ Corregir ortografía":   "Corrige todos los errores ortográficos y gramaticales sin cambiar el contenido ni el formato.",
            "📝 Resumir (5 puntos)":   "Resume este documento en exactamente 5 puntos clave, en español.",
            "💼 Tono formal":           "Reescribe este texto con un tono más profesional y formal, manteniendo toda la información.",
            "😊 Tono amigable":         "Reescribe este texto con un tono más amigable y cercano al lector.",
            "🌐 Traducir → inglés":    "Traduce este texto al inglés de manera natural, manteniendo el formato y la estructura.",
            "🌐 Traducir → español":   "Traduce este texto al español de manera natural, manteniendo el formato y la estructura.",
            "📋 Extraer puntos clave": "Extrae los puntos más importantes del texto como lista numerada.",
            "✏️ Ampliar contenido":    "Amplía y enriquece este texto agregando detalles relevantes, manteniendo el tema original.",
        }
        cols = st.columns(2)
        for i, (lbl, prompt_text) in enumerate(quick.items()):
            if cols[i % 2].button(lbl, key=f"qp_{i}", use_container_width=True):
                st.session_state["ai_prompt_val"] = prompt_text
                st.rerun()

        ai_prompt = st.text_area(
            "O escribe tu propia instrucción:",
            value=st.session_state.get("ai_prompt_val", ""),
            height=100,
            placeholder='Ej: "Cambia todos los precios de dólares a euros" · "Elimina la sección de introducción"',
            key="ai_prompt_widget",
        )
        if ai_prompt != st.session_state.get("ai_prompt_val", ""):
            st.session_state["ai_prompt_val"] = ai_prompt

        btn_run = st.button("✦ Procesar con Claude IA", key="btn_ai_run", use_container_width=True)

    with col_r:
        st.markdown("**Resultado:**")

        # ── Run AI ──
        if btn_run:
            final_text = ai_text if source_mode == "Pegar texto manualmente" else st.session_state["edited_text"]

            # Validations
            if not st.session_state["api_key"].strip():
                st.markdown('<div class="err-box">❌ Configura tu clave API de Anthropic arriba.</div>', unsafe_allow_html=True)
            elif not final_text.strip():
                st.markdown('<div class="err-box">❌ No hay texto para procesar.</div>', unsafe_allow_html=True)
            elif not ai_prompt.strip():
                st.markdown('<div class="err-box">❌ Escribe o selecciona una instrucción.</div>', unsafe_allow_html=True)
            elif len(final_text) > 100_000:
                st.markdown('<div class="warn-box">⚠️ El texto es muy largo. Se usarán los primeros 100.000 caracteres.</div>', unsafe_allow_html=True)
                final_text = final_text[:100_000]
            else:
                with st.spinner("✦ Claude está procesando tu documento..."):
                    try:
                        import anthropic
                        client = anthropic.Anthropic(api_key=st.session_state["api_key"].strip())
                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=4096,
                            messages=[{
                                "role": "user",
                                "content": (
                                    f"Instrucción del usuario: {ai_prompt}\n\n"
                                    f"---\nDocumento:\n\n{final_text}"
                                )
                            }]
                        )
                        st.session_state["ai_result"] = message.content[0].text
                        st.markdown('<div class="ok-box">✓ Procesado correctamente.</div>', unsafe_allow_html=True)
                    except Exception as e:
                        err_msg = str(e)
                        if "authentication" in err_msg.lower() or "401" in err_msg:
                            st.markdown('<div class="err-box">❌ Clave API inválida. Revisa tu clave en console.anthropic.com</div>', unsafe_allow_html=True)
                        elif "rate" in err_msg.lower() or "429" in err_msg:
                            st.markdown('<div class="err-box">❌ Límite de velocidad alcanzado. Espera unos segundos y vuelve a intentar.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="err-box">❌ Error: {err_msg}</div>', unsafe_allow_html=True)

        # ── Show result ──
        result = st.session_state.get("ai_result", "")
        if result:
            st.text_area(
                "Resultado editable",
                value=result,
                height=380,
                key="ai_result_area",
                label_visibility="collapsed",
            )

            # Update result if user edits it
            edited_result = st.session_state.get("ai_result_area", result)

            st.markdown("**Exportar resultado:**")
            ec1, ec2, ec3, ec4 = st.columns(4)

            # TXT
            ec1.download_button("📄 TXT",
                data=result.encode("utf-8"),
                file_name="resultado_ia.txt", mime="text/plain",
                key="dl_ai_txt", use_container_width=True)

            # PDF
            try:
                ec2.download_button("📥 PDF",
                    data=text_to_pdf_bytes(result),
                    file_name="resultado_ia.pdf", mime="application/pdf",
                    key="dl_ai_pdf", use_container_width=True)
            except Exception:
                pass

            # DOCX
            try:
                ec3.download_button("📝 Word",
                    data=text_to_docx_bytes(result, "Resultado IA"),
                    file_name="resultado_ia.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="dl_ai_docx", use_container_width=True)
            except Exception:
                pass

            # Send to editor
            if ec4.button("✏️ Al editor", key="btn_to_editor", use_container_width=True):
                st.session_state["edited_text"] = result
                st.session_state["extracted_text"] = result
                if not st.session_state["editor_filename"]:
                    st.session_state["editor_filename"] = "documento_ia.pdf"
                st.markdown('<div class="ok-box">✓ Texto enviado al editor. Ve a la pestaña "Editar PDF".</div>', unsafe_allow_html=True)

            if st.button("🗑 Limpiar resultado", key="btn_clear_ai"):
                st.session_state["ai_result"] = ""
                st.rerun()
        else:
            st.markdown("""
            <div style="border:1px dashed #c8cfd8;border-radius:3px;padding:80px 24px;
                        text-align:center;color:#3d4a5c;font-size:0.75rem;letter-spacing:0.08em;">
              ✦ El resultado de Claude aparecerá aquí
            </div>
            """, unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.62rem;letter-spacing:0.1em;
            text-transform:uppercase;color:#3d4a5c;padding:8px 0;">
  PDF Studio · Streamlit · IA por Claude — Anthropic
</div>
""", unsafe_allow_html=True)
