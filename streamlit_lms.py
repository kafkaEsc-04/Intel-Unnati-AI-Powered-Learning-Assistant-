import streamlit as st
import os
import base64
import fitz  # PyMuPDF
import datetime
import plotly.figure_factory as ff
from streamlit_extras.card import card
import ollama
import re

# Flashcard making logic
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def generate_flashcards(pdf_text):
    flashcard_prompt = """You are a helpful study assistant. Create flashcards from the provided text.\nYOU MUST FOLLOW THIS FORMAT EXACTLY:\nEach flashcard must start with 'Q: ' on a new line.\nThe answer must start with 'A: ' on the line immediately following the question.\nProvide at least 5 flashcards.\n\nExample:\nQ: What is a process?\nA: A program in execution.\n\nHere is the text:"""
    try:
        response = ollama.chat(
            model='phi3:mini',
            messages=[
                {'role': 'system', 'content': flashcard_prompt},
                {'role': 'user', 'content': pdf_text[:12000]},
            ])
        return response['message']['content']
    except Exception as e:
        st.error(f"An error occurred with Ollama: {e}")
        st.info("Please ensure the Ollama application is running and the model has been pulled.")
        return None

def parse_flashcards(flashcards_str):
    matches = re.findall(r"^Q:\s*(.*?)\nA:\s*(.*?)(?=\n^Q:|$)", flashcards_str, re.MULTILINE | re.DOTALL)
    flashcards = [(q.strip(), a.strip()) for q, a in matches]
    return flashcards



st.set_page_config(page_title="AI Course Companion", page_icon="🧠", layout="wide")


if 'progress' not in st.session_state:
    st.session_state['progress'] = {}
if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = {}

# --- PATHS ---
COURSE_MATERIAL_PATH = os.path.join(os.path.dirname(__file__), 'Course Material')


@st.cache_data
def get_courses():
    if not os.path.exists(COURSE_MATERIAL_PATH):
        return []
    return [d for d in os.listdir(COURSE_MATERIAL_PATH) if os.path.isdir(os.path.join(COURSE_MATERIAL_PATH, d))]

@st.cache_data
def get_chapters(course_name):
    course_path = os.path.join(COURSE_MATERIAL_PATH, course_name)
    if not os.path.exists(course_path):
        return []
    return sorted([d for d in os.listdir(course_path) if os.path.isdir(os.path.join(course_path, d))])

@st.cache_data
def get_chapter_parts(course_name, chapter_name):
    chapter_path = os.path.join(COURSE_MATERIAL_PATH, course_name, chapter_name)
    if not os.path.exists(chapter_path):
        return []
    return sorted([f for f in os.listdir(chapter_path) if f.lower().endswith('.pdf')])

def display_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")

def calculate_progress(course_name):
    chapters = get_chapters(course_name)
    if not chapters:
        return 0
    completed_chapters = [ch for ch in chapters if st.session_state.progress.get(course_name, {}).get(ch, {}).get('completed')]
    return int((len(completed_chapters) / len(chapters)) * 100)

@st.cache_data
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

@st.cache_data
def generate_with_llm(_prompt, text_content):
    try:
        response = ollama.chat(
            model='phi3:mini',
            messages=[
                {'role': 'system', 'content': _prompt},
                {'role': 'user', 'content': text_content},
            ])
        return response['message']['content']
    except Exception as e:
        st.error(f"An error occurred with Ollama: {e}")
        st.info("Please ensure the Ollama application is running and the model has been pulled.")
        return None

# --- UI PAGES ---
def main_page():
    st.title("Course Selector")
    st.write("Welcome! Please select a course to begin.")
    courses = get_courses()
    if not courses:
        st.warning("No courses found.")
        return
    cols = st.columns(3)
    for i, course_name in enumerate(courses):
        with cols[i % 3]:
            card(
                title=course_name,
                text=f"Progress: {calculate_progress(course_name)}%",
                on_click=lambda name=course_name: set_page('course_page', course=name)
            )

def course_page():
    course_name = st.session_state['selected_course']
    st.title(f"Course: {course_name}")
    st.progress(calculate_progress(course_name))
    if st.button("<- Back to Courses"):
        set_page('main_page')
    st.header("Chapters")
    chapters = get_chapters(course_name)
    if not chapters:
        st.warning("No chapters found for this course.")
        return
    cols = st.columns(4)
    for i, chapter_name in enumerate(chapters):
        is_completed = st.session_state.progress.get(course_name, {}).get(chapter_name, {}).get('completed', False)
        with cols[i % 4]:
            card(
                title=f"{chapter_name} {'✅' if is_completed else ''}",
                text="Completed" if is_completed else "Not Started",
                on_click=lambda ch=chapter_name: set_page('chapter_page', chapter=ch)
            )
    st.header("Revision Plan Timeline")
    create_revision_timeline(course_name)

def chapter_page():
    course_name = st.session_state['selected_course']
    chapter_name = st.session_state['selected_chapter']
    st.title(f"{course_name} - {chapter_name}")
    if st.button("<- Back to Chapters"):
        set_page('course_page')
    chapter_parts = get_chapter_parts(course_name, chapter_name)
    if not chapter_parts:
        st.warning("No parts found for this chapter.")
        return
    selected_part = st.selectbox("Select a part to view:", chapter_parts)
    pdf_path = os.path.join(COURSE_MATERIAL_PATH, course_name, chapter_name, selected_part)
    display_pdf(pdf_path)
    
    # Generating flashcards and summary
    st.markdown("---    ")
    st.header("AI-Powered Study Aids")
    # Session state for flashcards and flip state
    if 'chapter_flashcards' not in st.session_state:
        st.session_state['chapter_flashcards'] = {}
    if 'chapter_flashcard_flip' not in st.session_state:
        st.session_state['chapter_flashcard_flip'] = {}
    if st.button("Generate Summary & Flashcards", key=f"generate_{pdf_path}"):
        with st.spinner("Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(pdf_path)
        if pdf_text:
            with st.spinner("Generating summary..."):
                summary_prompt = "You are an expert in this subject. Based on the following text from a course document, provide a comprehensive summary for a university student. Feel free to expand on the key concepts and definitions using your own knowledge to provide a richer explanation. The goal is to clarify the material, not just repeat it."
                summary = generate_with_llm(summary_prompt, pdf_text[:12000]) # Limit context to avoid token limits
                st.session_state.generated_content[pdf_path] = st.session_state.generated_content.get(pdf_path, {})
                st.session_state.generated_content[pdf_path]['summary'] = summary
            with st.spinner("Generating flashcards..."):
                flashcards_str = generate_flashcards(pdf_text)
                flashcards = parse_flashcards(flashcards_str)
                st.session_state['chapter_flashcards'][pdf_path] = flashcards
                st.session_state['chapter_flashcard_flip'][pdf_path] = {i: False for i in range(len(flashcards))}

    # Display generated content
    if pdf_path in st.session_state.generated_content:
        if 'summary' in st.session_state.generated_content[pdf_path]:
            st.subheader("Summary")
            st.markdown(st.session_state.generated_content[pdf_path]['summary'])
    # Display flashcards as tiles with flip buttons
    if pdf_path in st.session_state['chapter_flashcards'] and st.session_state['chapter_flashcards'][pdf_path]:
        st.subheader("Flashcards")
        flashcards = st.session_state['chapter_flashcards'][pdf_path]
        flip_state = st.session_state['chapter_flashcard_flip'][pdf_path]
        cols = st.columns(3)
        for i, (q, a) in enumerate(flashcards):
            col = cols[i % 3]
            with col:
                if i not in flip_state:
                    flip_state[i] = False
                st.markdown(f"**Q{i+1}:**" if not flip_state[i] else f"**Answer {i+1}:**", unsafe_allow_html=True)
                st.markdown(f"{q}" if not flip_state[i] else f"{a}")
                if st.button("Show Answer" if not flip_state[i] else "Show Question", key=f"btn_{pdf_path}_{i}"):
                    flip_state[i] = not flip_state[i]
        st.info("Click the button below each card to flip between Question and Answer.")
    elif pdf_path in st.session_state.generated_content and 'flashcards' in st.session_state.generated_content[pdf_path]:
        st.warning("Could not parse flashcards from the model's response. The raw response is shown below.")
        st.text(st.session_state.generated_content[pdf_path]['flashcards'])

    st.sidebar.header("Progress")
    is_completed = st.session_state.progress.get(course_name, {}).get(chapter_name, {}).get('completed', False)
    def on_checkbox_change():
        if st.session_state[f"{course_name}_{chapter_name}_progress"]:
            if course_name not in st.session_state.progress: st.session_state.progress[course_name] = {}
            st.session_state.progress[course_name][chapter_name] = {'completed': True, 'completion_date': datetime.date.today().isoformat()}
        else:
            if course_name in st.session_state.progress and chapter_name in st.session_state.progress[course_name]:
                st.session_state.progress[course_name][chapter_name] = {'completed': False, 'completion_date': None}
    st.sidebar.checkbox("Mark as Completed", value=is_completed, key=f"{course_name}_{chapter_name}_progress", on_change=on_checkbox_change)

def create_revision_timeline(course_name):
    df = []
    revision_intervals = [1, 3, 7, 14, 30]
    completed_chapters = st.session_state.progress.get(course_name, {})
    for chapter, data in completed_chapters.items():
        if data.get('completed') and data.get('completion_date'):
            start_date = datetime.date.fromisoformat(data['completion_date'])
            for i, days in enumerate(revision_intervals):
                df.append(dict(Task=chapter, Start=start_date + datetime.timedelta(days=days), Finish=start_date + datetime.timedelta(days=days + 1), Resource=f"Revision {i+1}"))
    if not df:
        st.info("Complete some chapters to see your revision timeline.")
        return
    fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True, title="Chapter Revision Schedule")
    st.plotly_chart(fig, use_container_width=True)


def set_page(page, course=None, chapter=None):
    st.session_state['page'] = page
    if course: st.session_state['selected_course'] = course
    if chapter: st.session_state['selected_chapter'] = chapter
    st.rerun()

if 'page' not in st.session_state: st.session_state['page'] = 'main_page'

if st.session_state['page'] == 'main_page': main_page()
elif st.session_state['page'] == 'course_page': course_page()
elif st.session_state['page'] == 'chapter_page': chapter_page()
