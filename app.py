import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from llm_wrapper import OpenVinoLangChainLLM
from rag_utils import (
    load_vectorstore,
    load_uploaded_documents,
    create_temp_vectorstore,
)
from chat_utils import (
    list_chat_sessions,
    load_chat,
    save_chat,
    generate_new_session_name,
)


st.set_page_config(page_title="OpenVINO Chatbot", layout="centered")
st.title("Query Resolution App (Powered By OpenVINO)")


@st.cache_resource
def load_chain_and_db():
    llm = OpenVinoLangChainLLM()
    memory = ConversationBufferMemory(return_messages=True)
    chain = ConversationChain(llm=llm, memory=memory, verbose=False)
    vectordb = load_vectorstore()
    return chain, vectordb

chain, vectordb = load_chain_and_db()

# Sidebar Session Picker 
session_list = ["Start new chat"] + list_chat_sessions()
selected_session = st.sidebar.selectbox("Select a chat session", session_list)

# Detect session change
session_changed = (
    "session_name" not in st.session_state or
    selected_session != st.session_state.session_name
)

# Load selected session or start new
if session_changed:
    if selected_session == "Start new chat":
        st.session_state.session_name = generate_new_session_name()
        st.session_state.chat_history = []
    else:
        st.session_state.session_name = selected_session
        st.session_state.chat_history = load_chat(selected_session)

    # Sync LangChain memory
    chain.memory.clear()
    for role, msg in st.session_state.chat_history:
        if role == "user":
            chain.memory.chat_memory.add_user_message(msg)
        elif role == "assistant":
            chain.memory.chat_memory.add_ai_message(msg)

    st.session_state.memory_synced = True
    st.rerun()  # Refresh UI

# File uploading
uploaded_files = st.file_uploader("Upload additional PDFs", type="pdf", accept_multiple_files=True)
temp_db = None

if uploaded_files:
    uploaded_docs = load_uploaded_documents(uploaded_files)
    if uploaded_docs:
        temp_db = create_temp_vectorstore(uploaded_docs)


def build_rag_prompt(query: str) -> str:
    docs = vectordb.similarity_search(query, k=3)
    if temp_db:
        extra_docs = temp_db.similarity_search(query, k=2)
        docs.extend(extra_docs)

    context = "\n".join([doc.page_content for doc in docs])
    return f"""Use the following context to answer the question:

{context}

Question: {query}
Answer:"""

# Chat Input and Response Logic
user_input = st.chat_input("Ask something...")

if user_input:
    rag_prompt = build_rag_prompt(user_input)
    response = chain.run(rag_prompt)

    # Save to chat history
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("assistant", response))

    # Save to file
    save_chat(st.session_state.session_name, st.session_state.chat_history)

# Displaying the chat
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

#  Reset Chat Button
if st.button("Reset Chat"):
    st.session_state.session_name = generate_new_session_name()
    st.session_state.chat_history = []
    st.session_state.memory_synced = False
    chain.memory.clear()
    st.rerun()
