import streamlit as st
import fitz  # PyMuPDF
import io
from docx import Document
import google.generativeai as genai

# 1. ຕັ້ງຄ່າໜ້າຕາເວັບ Streamlit
st.set_page_config(page_title="AI PDF to Word (Lao)", page_icon="📝", layout="centered")

st.title("📝 AI ປ່ຽນ PDF ເປັນ Word ພາສາລາວ")
st.write("ແອັບພລິເຄຊັນສໍາລັບແປງຟາຍ PDF ພາສາລາວ ໃຫ້ກາຍເປັນ Word ດ້ວຍ AI ເພື່ອຫຼຸດຜ່ອນບັນຫາສະຫຼະໂດດ ຫຼື ໂຕໜັງສືບໍ່ຖືກຕ້ອງ.")
st.write("#ພັດທະນາໂດຍ: ອາຈານ ສຸກປະເສີດ ບັນຈົງ ພາກວິຊາວິທະຍາສາດຄອມພີວເຕີ ຄວທ, ມຊ.#")
# 2. ສ້າງແຖບດ້ານຂ້າງສໍາລັບໃສ່ API Key
#st.sidebar.header("🔑 ການຕັ້ງຄ່າ AI")
#api_key = st.sidebar.text_input("ໃສ່ Gemini API Key ຂອງທ່ານ:", type="password")
api_key = "AIzaSyD94KVzbEc0Wdz7O9WU4l9zLE8Jsp5RrNE"  # ແທນທີ່ເປັນ Key ຂອງທ່ານ
# 3. ສ່ວນອັບໂຫຼດໄຟລ໌ PDF
uploaded_file = st.file_uploader("ເລືອກຟາຍ PDF ທີ່ຕ້ອງການແປງ", type=["pdf"])

if uploaded_file:
    if not api_key:
        st.warning("⚠️ ກະລຸນາໃສ່ Gemini API Key ຢູ່ແຖບດ້ານຂ້າງ (Sidebar) ກ່ອນເລີ່ມໃຊ້ງານ.")
    else:
        # ກວດສອບຄວາມພ້ອມກ່ອນກົດປຸ່ມ
        if st.button("🚀 ເລີ່ມແປງຟາຍດ້ວຍ AI"):
            # ຕັ້ງຄ່າ Gemini API
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # ອ່ານໄຟລ໌ PDF ດ້ວຍ PyMuPDF
                pdf_data = uploaded_file.read()
                pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
                total_pages = len(pdf_doc)
                
                # ສ້າງ Document ຂອງ Word ໃໝ່
                word_doc = Document()
                
                # ສ້າງຕົວແປເກັບຂໍ້ຄວາມທັງໝົດ
                extracted_text = ""
                
                # ວົນລູບປະມວນຜົນເທື່ອລະໜ້າ
                for page_num in range(total_pages):
                    status_text.text(f"⏳ ກໍາລັງປະມວນຜົນໜ້າທີ {page_num + 1} ຈາກທັງໝົດ {total_pages} ໜ້າ...")
                    
                    # ແປງໜ້າ PDF ເປັນຮູບພາບ (JPEG)
                    page = pdf_doc[page_num]
                    pix = page.get_pixmap(dpi=150)  # ກໍານົດຄວາມຄົມຊັດ 150 DPI
                    img_bytes = pix.tobytes("jpeg")
                    
                    # ກໍານົດຄໍາສັ່ງ (Prompt) ໃຫ້ AI ດຶງຂໍ້ຄວາມພາສາລາວ
                    prompt = (
                        "Extract all the text from this image perfectly. Maintain the original paragraphs and structure. "
                        "The text is in Lao language. Be extremely careful with Lao vowels (ິ, ີ, ຶ, ື, ຸ, ູ), "
                        "tone marks (່, ້, ໊, ໋), and special signs (ຯ, ໆ). Ensure they are placed correctly on the consonants. "
                        "Do not add any preamble or explanation, just return the exact extracted text."
                    )
                    
                    # ສົ່ງຮູບພາບ ແລະ ຄໍາສັ່ງໃຫ້ Gemini Vision
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "image/jpeg", "data": img_bytes}
                    ])
                    
                    # ເອົາຂໍ້ຄວາມທີ່ໄດ້ໄປເພີ່ມໃສ່ Word
                    page_text = response.text
                    word_doc.add_paragraph(page_text)
                    
                    # ຖ້າມີໜ້າຖັດໄປ ໃຫ້ເພີ່ມ Page Break ໃນ Word
                    if page_num < total_pages - 1:
                        word_doc.add_page_break()
                    
                    # ອັບເດດ Progress bar
                    progress_bar.progress((page_num + 1) / total_pages)
                
                status_text.text("🎉 ປະມວນຜົນສໍາເລັດແລ້ວ!")
                
                # ບັນທຶກ Word ໄວ້ໃນ Memory (BytesIO) ເພື່ອໃຫ້ກຽມດາວໂຫຼດ
                word_io = io.BytesIO()
                word_doc.save(word_io)
                word_io.seek(0)
                
                # ສະແດງປຸ່ມດາວໂຫຼດ
                st.success("✨ ແປງຟາຍສໍາເລັດຮຽບຮ້ອຍແລ້ວ! ທ່ານສາມາດດາວໂຫຼດຟາຍໄດ້ຢູ່ລຸ່ມນີ້:")
                st.download_button(
                    label="📥 ດາວໂຫຼດຟາຍ Word (.docx)",
                    data=word_io,
                    file_name=f"Converted_{uploaded_file.name.rsplit('.', 1)[0]}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"❌ ເກີດຂໍ້ຜິດພາດໃນການປະມວນຜົນ: {str(e)}")
