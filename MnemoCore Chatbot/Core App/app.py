import streamlit as st
from llm_wrapper import OpenVinoLangChainLLM
from rag_utils import get_context_from_query
from chat_utils import (
    list_chat_sessions,
    generate_new_session_name,
    load_chat,
    save_chat,
)
from ocr_utils import extract_text_from_image
from voice_utils import transcribe_audio_base64, transcribe_uploaded_mp3
from voice_ui import record_audio_component

from PIL import Image
import base64

st.set_page_config(page_title="MnemoCore", layout="centered")
st.title("MnemoCore")

# --- Session Setup ---
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_new_session_name()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []
if "voice_input_data" not in st.session_state:
    st.session_state.voice_input_data = ""
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

# Load LLM
@st.cache_resource
def load_chain():
    return OpenVinoLangChainLLM()
llm = load_chain()

# Sidebar: Session selection
st.sidebar.subheader("Sessions")
sessions = list_chat_sessions()
selected = st.sidebar.selectbox("Chat sessions:", ["➕ Start new chat"] + sessions)

if selected == "➕ Start new chat":
    if st.sidebar.button("Start New Chat"):
        st.session_state.session_id = generate_new_session_name()
        st.session_state.chat_history = []
        st.session_state.uploaded_files = []
        st.session_state.uploaded_images = []
        st.session_state.voice_input_data = ""
        st.session_state.transcribed_text = ""
else:
    if selected != st.session_state.session_id:
        st.session_state.session_id = selected
        st.session_state.chat_history = load_chat(selected)
        st.session_state.uploaded_files = []
        st.session_state.uploaded_images = []
        st.session_state.voice_input_data = ""
        st.session_state.transcribed_text = ""

# --- Upload PDFs ---
st.markdown("### Upload PDF(s):")
pdfs = st.file_uploader("Drop PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
if pdfs:
    st.session_state.uploaded_files = pdfs

# --- Upload Images ---
st.markdown("### Upload image(s):")
images = st.file_uploader("Drop Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
if images:
    st.session_state.uploaded_images = images

# --- Upload MP3 file ---
st.markdown("### Upload audio file (Currently supports MP3):")
mp3_file = st.file_uploader("Drop an MP3 file to transcribe", type=["mp3"], label_visibility="collapsed")
if mp3_file:
    st.session_state.transcribed_text = transcribe_uploaded_mp3(mp3_file)
    st.success(f"MP3 Transcribed: {st.session_state.transcribed_text}")

# --- Mic Input ---
st.markdown("### Record Audio:")
record_audio_component()
st.text_area("hidden_voice", key="voice_input_data", label_visibility="collapsed")

# Transcribe mic input (base64 audio)
if st.session_state.voice_input_data:
    transcript = transcribe_audio_base64(st.session_state.voice_input_data)
    st.session_state.transcribed_text = transcript
    st.success(f"🗣️ Mic Transcribed: {transcript}")
    st.session_state.voice_input_data = ""  # reset after processing

# Chat history
for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(msg["user"])
    with st.chat_message("assistant"):
        st.markdown(msg["bot"])

# Chat input
user_input = st.chat_input("Type or use mic/upload to ask...")
if not user_input and st.session_state.transcribed_text:
    user_input = st.session_state.transcribed_text

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        # Creating context with OCR 
        image_context = ""
        if st.session_state.uploaded_images:
            extracted = [extract_text_from_image(img) for img in st.session_state.uploaded_images]
            image_context = "\n".join(extracted)

        # Creating context with PDFs
        file_context = get_context_from_query(
            query=user_input,
            session_id=st.session_state.session_id,
            uploaded_files=st.session_state.uploaded_files
        )

        combined_context = "\n".join(filter(None, [image_context.strip(), file_context.strip()]))

        # Use context only if present
        if combined_context:
            prompt = f"""You are a helpful assistant. Use the context only if it's relevant.

Context:
{combined_context}

{user_input}
"""
        else:
            prompt = f"{user_input}"

        response = llm(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.chat_history.append({"user": user_input, "bot": response})
    save_chat(st.session_state.session_id, st.session_state.chat_history)
    st.session_state.transcribed_text = ""  # clear for next turn
