import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="AI Pro Scanner (RTL Support)", layout="wide")

st.title("🚀 Smart AI Scanner (Urdu & Arabic Optimized)")
st.write("PDF/Images ko scan karein. Word file ab khud-ba-khud Right-to-Left set ho jayegi.")

# Sidebar Settings
with st.sidebar:
    st.header("Settings")
    languages = st.multiselect("Zaban select karein:", ["en", "ur", "ar"], default=["en", "ur"])
    zoom = st.slider("Scan Quality (High = Slow)", 1.0, 4.0, 2.5)

uploaded_file = st.file_uploader("File select karein", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    @st.cache_resource
    def load_reader(langs):
        return easyocr.Reader(langs)
    
    reader = load_reader(languages)
    full_text = ""

    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI scan kar raha hai..."):
            if uploaded_file.type == "application/pdf":
                doc_pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page_num in range(len(doc_pdf)):
                    page = doc_pdf.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    st.image(img, caption=f"Page {page_num + 1}", width=400)
                    
                    result = reader.readtext(np.array(img), detail=0)
                    full_text += "\n".join(result) + "\n\n"
            else:
                img = Image.open(uploaded_file)
                st.image(img, width=400)
                result = reader.readtext(np.array(img), detail=0)
                full_text = "\n".join(result)

            st.success("Scanning Mukammal!")

            # --- WORD FILE WITH RTL SUPPORT ---
            doc = Document()
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Arial'
            font.size = Pt(12)

            for line in full_text.split('\n'):
                p = doc.add_paragraph(line)
                # Agar line mein Urdu/Arabic characters hon to Right-to-Left kar do
                if any(ord(c) > 1200 for c in line): 
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            word_buf = BytesIO()
            doc.save(word_buf)
            
            st.download_button("📥 Download Fixed Word File", data=word_buf.getvalue(), file_name="ai_scanner_fixed.docx")
            st.text_area("Live Preview", full_text, height=300)
