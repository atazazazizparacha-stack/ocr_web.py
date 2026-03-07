import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz
from docx import Document
from io import BytesIO

# --- Page Setup ---
st.set_page_config(page_title="AI Scanner Pro", layout="wide")
st.title("🚀 Smart AI Scanner")

# --- Optimized Sidebar ---
langs = st.sidebar.multiselect("Zaban (Languages):", ["en", "ur", "ar"], default=["en", "ur"])
zoom = st.sidebar.slider("Quality (2.0 is Best):", 1.0, 3.0, 2.0)

# Memory bachane ke liye model loading ko optimize kiya
@st.cache_resource
def get_reader(l):
    # gpu=False zaroori hai taake Streamlit Cloud crash na ho
    return easyocr.Reader(l, gpu=False)

up_file = st.file_uploader("PDF ya Image select karein", type=["pdf", "png", "jpg", "jpeg"])

if up_file:
    reader = get_reader(langs)
    text_data = ""

    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI parh raha hai..."):
            try:
                if up_file.type == "application/pdf":
                    doc = fitz.open(stream=up_file.read(), filetype="pdf")
                    for page in doc:
                        # Zoom ko control karne se memory kam kharch hogi
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        st.image(img, width=400)
                        res = reader.readtext(np.array(img), detail=0)
                        text_data += "\n".join(res) + "\n\n"
                else:
                    img = Image.open(up_file)
                    st.image(img, width=400)
                    res = reader.readtext(np.array(img), detail=0)
                    text_data = "\n".join(res)

                # --- Creating Word File with Correct Alignment ---
                doc_file = Document()
                for line in text_data.split('\n'):
                    if line.strip():
                        p = doc_file.add_paragraph(line)
                        # Urdu/Arabic check for Right Alignment (Unicode check)
                        if any(ord(c) > 1200 for c in line):
                            p.paragraph_format.alignment = 2 # Right
                        else:
                            p.paragraph_format.alignment = 0 # Left

                buf = BytesIO()
                doc_file.save(buf)
                
                st.success("Scanning Mukammal!")
                st.download_button("📥 Download Scanned Word", buf.getvalue(), "Final_AI_Result.docx")
                st.text_area("Live Preview", text_data, height=300)

            except Exception as e:
                st.error(f"App Error: {e}")
