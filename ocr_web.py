import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz
from docx import Document
from io import BytesIO
import pandas as pd
from pptx import Presentation

# --- Page Setup ---
st.set_page_config(page_title="AI Scanner Ultimate", layout="wide")
st.title("🚀 AI Scanner (Word, Excel, PPT, JPG)")

# --- Sidebar ---
langs = st.sidebar.multiselect("Zaban (Languages):", ["en", "ur", "ar"], default=["en", "ur"])
zoom = st.sidebar.slider("Quality:", 1.0, 3.0, 2.0)

@st.cache_resource
def get_reader(l):
    return easyocr.Reader(l, gpu=False)

up_file = st.file_uploader("File select karein", type=["pdf", "png", "jpg", "jpeg"])

if up_file:
    reader = get_reader(langs)
    text_list = []
    images_data = []

    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI processing ho rahi hai..."):
            try:
                if up_file.type == "application/pdf":
                    doc = fitz.open(stream=up_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        images_data.append(img)
                        res = reader.readtext(np.array(img), detail=0)
                        text_list.extend(res)
                else:
                    img = Image.open(up_file)
                    images_data.append(img)
                    res = reader.readtext(np.array(img), detail=0)
                    text_list = res

                full_text = "\n".join(text_list)
                st.success("Scanning Mukammal!")

                # --- Buttons Row ---
                col1, col2, col3, col4 = st.columns(4)

                # 1. WORD
                doc_file = Document()
                for line in text_list:
                    p = doc_file.add_paragraph(line)
                    if any(ord(c) > 1200 for c in line): p.paragraph_format.alignment = 2
                w_buf = BytesIO()
                doc_file.save(w_buf)
                col1.download_button("📥 Word", w_buf.getvalue(), "result.docx")

                # 2. EXCEL
                df = pd.DataFrame(text_list, columns=["Scanned Text"])
                e_buf = BytesIO()
                with pd.ExcelWriter(e_buf, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                col2.download_button("📊 Excel", e_buf.getvalue(), "result.xlsx")

                # 3. PPT
                ppt = Presentation()
                slide = ppt.slides.add_slide(ppt.slide_layouts[1])
                slide.shapes.title.text = "Scanned Data"
                slide.placeholders[1].text = full_text[:500]
                p_buf = BytesIO()
                ppt.save(p_buf)
                col3.download_button("📽️ PPT", p_buf.getvalue(), "result.pptx")

                # 4. JPG
                if images_data:
                    j_buf = BytesIO()
                    images_data[0].save(j_buf, format="JPEG")
                    col4.download_button("🖼️ JPG", j_buf.getvalue(), "page1.jpg")

                st.text_area("Preview", full_text, height=300)

            except Exception as e:
                st.error(f"Error: {e}")
