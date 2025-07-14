# Intel Unnati Industrial Training Program 2025

## Problem Statement 4: AI-Powered Interactive Learning Assistant for Classrooms

### Objective
Build a Multimodal AI assistant for classrooms to dynamically answer queries using text,
voice, and visuals while improving student engagement with personalized responses.

## Project Overview:

### This project consists of two components:

### 1.  MnemoCore Course Companion:   
  ### Features:
- **Course and Chapter Navigation:** Easily browse through your courses and their respective chapters.
- **PDF Viewer:** View chapter content directly in the app.
- **Progress Tracking:** Mark chapters as complete and visualize your study progress.
- **Revision Timeline:** Get a personalized revision schedule based on spaced repetition principles.
- **AI-Powered Flashcards:** Generate flashcards from your course material to aid in studying (requires an OpenAI API key).

### 2.  MnemoCore, an interactive chatbot:
  ### Features:

- **Multimodal Input Processing** - Unified interface for text, voice (WebM/MP3), PDF documents, and image OCR via Streamlit
- **Speech Recognition** - Faster-Whisper integration for real-time transcription with base64 audio handling
- **RAG Implementation** - Chroma vectorstore with sentence-transformers for semantic PDF document retrieval
- **OpenVINO Acceleration** - Local Phi-3 model inference with hardware optimization for privacy and performance
- **Session Architecture** - Persistent JSON chat history with session-specific vectorstores and context retention
- **Real-time Processing Pipeline** - Asynchronous multimodal input handling with dynamic context injection and response streaming

## Architecture Diagram 
![Architecture Diagram](./Assets/2_mnemocore_architecture.svg)


## Tech Stack
### MnemoCore Chatbot:

| Component           | Technology Used                          |
|---------------------|-------------------------------------------|
| UI Framework        | Streamlit                                 |
| Language Model      | OpenVINO-optimized LLM (Phi-3-Mini-128k) |
| RAG Framework       | LangChain + Chroma vectorstore            |
| PDF Processing      | PyMuPDF / PyPDFLoader                     |
| Image Understanding | Tesseract OCR via `pytesseract`           |
| Voice Input         | Whisper (via `faster-whisper`)            |
| File Handling       | `pdfplumber`, `Pillow`                    |
| Speech Transcription| Microphone + MP3 upload                   |
| State Management    | Streamlit session state + JSON logs       |
| Inference Runtime   | Intel OpenVINO for accelerated CPU use    | 

### MnemoCore Course Companion:

| Component          | Technology Used                                    |
| ------------------ | -------------------------------------------------- |
| UI Framework       | Streamlit                                          |
| Language Model     | Phi 3 Mini, Ollama                                 |
| PDF Processing     | PyMuPDF                                            |
| Data Visualization | Plotly                                             |
| State Management   | Streamlit Session State                            

---
## Screenshots:
### MnemoCore Chatbot
![Chatbot 1](./Assets/chatbot_ss_1.jpg)
----------------------------------------
![Chatbot 2](./Assets/chatbot_ss_2.jpg)
---------------------------------------
![Chatbot 3](./Assets/chatbot_ss_3.png)
---------------------------------------
![Chatbot 4](./Assets/chatbot_ss_4.png)
---------------------------------------
![Chatbot 5](./Assets/chatbot_ss_5.png)
---------------------------------------
### MnemoCore Course Companion
![Course Companion 1](./Assets/course_companion_ss_1.jpg)
---------------------------------------------------------
![Course Companion 2](./Assets/course_companion_ss_2.jpg)
---------------------------------------------------------
![Course Companion 3](./Assets/course_companion_ss_3.png)
---------------------------------------------------------
![Course Companion 4](./Assets/course_companion_ss_4.png)
---------------------------------------------------------

## Demo Videos:  
Note:
The inference times in the demo videos here are slow-**upwards of 2-3 minutes on average**. This is because the system I currently have with me for testing is a **7-year old laptop with 8GB of RAM and no GPU**, and as such is not very performant.  


### MnemoCore Course Companion:   https://youtu.be/sjx1kb9Jvbs    

### MnemoCore Assistant Part 1:   https://youtu.be/3Gyc1SHJx_w
### MnemoCore Assistant Part 2:   https://youtu.be/lPkAdUeulIs
### MnemoCore Assistant Part 3:   https://youtu.be/84NxpD5FUWw

## Setup and Installation

### Prerequisites:
1. Python ≥ 3.9
2. pip ≥ 22.0
3. Git
4. Tesseract OCR 
   > Install from: https://github.com/tesseract-ocr/tesseract
    Add to PATH or specify path in ocr_utils.py if needed
5.  FFmpeg (for audio decoding)
6. OpenVINO Runtime (installed automatically via optimum-intel)

### Create Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```
### Install Dependencies:
```bash 
pip install -r requirements.txt
```
### Clone the Repository

```bash
git clone https://github.com/kafkaEsc-04/Intel-Unnati-AI-Powered-Learning-Assistant-.git
```

### Expected Directory Setup for MnemoCore Chatbot
```pgsql
Your-Directory-/
├── app.py
├── llm_wrapper.py
├── rag_utils.py
├── voice_utils.py
├── voice_ui.py
├── ocr_utils.py
├── chat_utils.py
├── test_whisper_transcription.py
├── requirements.txt
├── vectorstore/
│   └── <chat_session_id>.json
├── chat_logs
└── README.md
```
### Expected Directory Setup for MnemoCore Course Companion
```pgsql
Your-Directory-/
├── Course Material/
│   └── [Your Course Name]/
│       └── [Your Chapter Name]/
│           └── [your_file].pdf
├── streamlit_lms.py
```
### Run the apps
#### For Chatbot
``` bash
streamlit run app.py
```
#### For Course Companion
``` bash
streamlit run streamlit_lms.py
```

## Credits
Built by Sai Rithvik Nama