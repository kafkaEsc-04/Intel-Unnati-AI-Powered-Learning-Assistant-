from PIL import Image
import pytesseract
import tempfile

def extract_text_from_image(uploaded_image):
    #This program extracts text from a Streamlit uploaded image using pytesseract.
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_image.getbuffer())
        tmp_path = tmp.name
    image = Image.open(tmp_path)
    text = pytesseract.image_to_string(image)
    return text.strip()
