import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
import pandas as pd
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(page_title="AI Multi-Lingual Pro Scanner", layout="wide")

st.title("🚀 Smart AI Scanner (Urdu, Arabic & English)")
st.write("PDF/Images ko scan karein. Word file ab RTL (Right-to-Left) support ke saath generate hogi.")

# --- Sidebar Settings ---
with st.sidebar:
    st.header("Settings")
    languages = st.multiselect("Zaban select karein (Languages):", ["en", "ur", "ar"], default=["en", "ur"])
    zoom = st.slider("Scan Quality (Higher is better/slower)", 1.0, 4.0, 2.5)
    st.info("Urdu/Arabic ke liye Quality ko 2.5 ya usse zyada rakhein.")

uploaded_file = st.file_uploader("File select karein (PDF, JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    @st.cache_resource
    def load_reader(langs):
        return easyocr.Reader(langs)
    
    reader = load_reader(languages)
    full_text = ""

    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI scan kar raha hai... is mein thora waqt lag sakta hai."):
            try:
                # --- PDF Processing ---
                if uploaded_file.type == "application/pdf":
                    doc_pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page_num in range(len(doc_pdf)):
                        page = doc_pdf.load_page(page_num)
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        
                        st.image(img, caption=f"Page {page_num + 1}", width=500)
                        
                        result = reader.readtext(np.array(img), detail=0)
                        page_text = "\n".join(result)
                        full_text += f"\n--- Page {page_num + 1} ---\n" + page_text
                
                # --- Image Processing ---
                else:
                    img = Image.open(uploaded_file)
                    st.image(img, width=500)
                    result = reader.readtext(np.array(img), detail=0)
                    full_text = "\n".join(result)

                st.success("Scanning Mukammal!")

                # --- WORD FILE GENERATION ---
                doc = Document()
                style = doc.styles['Normal']
                style.font.name = 'Arial'
                style.font.size = Pt(12)

                for line in full_text.split('\n'):
                    if line.strip():
                        p = doc.add_paragraph(line)
                        # Urdu/Arabic characters check (Unicode > 1200)
                        if any(ord(c) > 1200 for c in line):
                            p.paragraph_format.alignment = 2 # Right Align
                        else:
                            p.paragraph_format.alignment = 0 # Left Align

                word_buf = BytesIO()
                doc.save(word_buf)
                
                st.download_button(
                    label="📥 Download Fixed Word File",
                    data=word_buf.getvalue(),
                    file_name="ai_scanner_result.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

                st.subheader("Live Text Preview:")
                st.text_area("Scanned Content", full_text, height=400)

            except Exception as e:
                st.error(f"Scanning mein masla aaya hai: {e}")
