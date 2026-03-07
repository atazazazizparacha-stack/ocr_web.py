import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AI Scanner", layout="wide")
st.title("🚀 Professional AI Scanner")

# Sidebar
langs = st.sidebar.multiselect("Languages", ["en", "ur", "ar"], default=["en", "ur"])
zoom = st.sidebar.slider("Quality", 1.0, 3.0, 2.0)

up_file = st.file_uploader("Upload File", type=["pdf", "png", "jpg", "jpeg"])

if up_file:
    # Model loading with cache
    @st.cache_resource
    def load_ocr_model(l):
        return easyocr.Reader(l)
    
    reader = load_ocr_model(langs)
    text_data = ""

    if st.button("Start Scan"):
        with st.spinner("AI is reading..."):
            try:
                # PDF Processing
                if up_file.type == "application/pdf":
                    pdf = fitz.open(stream=up_file.read(), filetype="pdf")
                    for page in pdf:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        st.image(img, width=400)
                        res = reader.readtext(np.array(img), detail=0)
                        text_data += "\n".join(res) + "\n\n"
                # Image Processing
                else:
                    img = Image.open(up_file)
                    st.image(img, width=400)
                    res = reader.readtext(np.array(img), detail=0)
                    text_data = "\n".join(res)

                st.success("Success!")

                # --- Creating Word File with RTL Support ---
                doc = Document()
                for line in text_data.split('\n'):
                    if line.strip():
                        p = doc.add_paragraph(line)
                        # Agar Urdu/Arabic character ho to Right-Align (2) karein
                        if any(ord(c) > 1200 for c in line):
                            p.paragraph_format.alignment = 2
                        else:
                            p.paragraph_format.alignment = 0

                buf = BytesIO()
                doc.save(buf)
                st.download_button("📥 Download Word File", buf.getvalue(), "final_result.docx")
                st.text_area("Live Preview", text_data, height=300)

            except Exception as e:
                st.error(f"App Error: {e}")
