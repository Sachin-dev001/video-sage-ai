import streamlit as st
from dotenv import load_dotenv

from utils.youtube_loader import (get_transcript_documents, extract_video_id)
from utils.text_cleaner import clean_transcript
from utils.chunker import create_chunks

from vectorstore.qdrant_store import get_vector_store

from services.llm_service import get_chat_model

from retrieval.retriever import retrieve_context

from prompts.rag_prompt import rag_prompt

load_dotenv()

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="VideoSage AI",
    page_icon="🎥",
    layout="wide"
)

# =========================================
# LOAD CSS
# =========================================

with open("styles/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =========================================
# SESSION STATE
# =========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "full_transcript" not in st.session_state:
    st.session_state.full_transcript = ""

if "video_processed" not in st.session_state:
    st.session_state.video_processed = False

# =========================================
# SIDEBAR
# =========================================
with st.sidebar:

    st.markdown("# 🚀 VideoSage AI")

    st.markdown("---")

    st.markdown("""
### 👨‍💻 Developer

**Sachin Sharma**

AI Engineer focused on retrieval systems, LLM applications, and real-time AI experiences.
""")

    st.markdown("---")

    st.markdown("""
### 🧠 Core Features

• Chat with YouTube videos in natural language  
• Timestamp-aware video understanding  
• AI-generated summaries and insights  
• Semantic search across video transcripts  
• Real-time streaming AI responses  
• Multilingual transcript support
""")

    st.markdown("---")

    st.markdown("""
### ⚙️ Tech Stack

• Gemini 2.5 Flash  
• LangChain  
• Qdrant Vector Database  
• HuggingFace Embeddings  
• RAG-based Retrieval Pipeline  
• Streamlit  
• Semantic Search + Reranking
""")

    st.markdown("---")

    st.markdown("### 🌐 Connect With Me")
    
    # Styled links with matching emojis/icons
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/sachin-sharma-659ab53b6)")
    st.markdown("💻 [GitHub](https://github.com/Sachin-dev001)")

# =========================================
# VIDEO INPUT SECTION
# =========================================

st.markdown("""
<div class="upload-section">

<h1 class="main-title">
Analyze Any YouTube Video
</h1>

<p class="main-subtitle">
Paste a YouTube link to generate AI-powered summaries, timestamp insights, semantic search, and conversational analysis.
</p>

</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="
display:flex;
gap:14px;
justify-content:center;
flex-wrap:wrap;
margin-top:25px;
">

<div style="
padding:10px 18px;
border-radius:999px;
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.08);
">
⚡ AI Summaries
</div>

<div style="
padding:10px 18px;
border-radius:999px;
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.08);
">
🎯 Timestamp Insights
</div>

<div style="
padding:10px 18px;
border-radius:999px;
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.08);
">
🔍 Semantic Search
</div>

<div style="
padding:10px 18px;
border-radius:999px;
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.08);
">
💬 Conversational AI
</div>

</div>
""", unsafe_allow_html=True)
youtube_url = st.text_input(
    "",
    placeholder="Paste YouTube URL here..."
)

col1, col2, col3 = st.columns([1.5,2,1.5])

with col2:

    process_btn = st.button(
        "🚀 Process Video",
        use_container_width=True
    )

# =========================================
# PROCESS VIDEO
# =========================================

if process_btn:

    if youtube_url.strip() == "":

        st.warning("Please paste a YouTube URL")

        st.stop()

    with st.spinner("🔄 Processing Video..."):

        try:

            from utils.youtube_loader import (
                get_transcript_documents,
                extract_video_id
            )

            # GET TIMESTAMP-AWARE DOCUMENTS
            docs = get_transcript_documents(youtube_url)

            # SAVE FULL TRANSCRIPT
            st.session_state.full_transcript = "\n".join(
                [doc.page_content for doc in docs]
            )

            # CREATE CHUNKS
            chunks = create_chunks(docs)

            # GET VIDEO ID
            video_id = extract_video_id(youtube_url)

            # LOAD VECTOR STORE
            vector_store = get_vector_store(video_id)

            # ADD CHUNKS
            vector_store.add_documents(chunks)

            # SAVE VECTOR STORE
            st.session_state.vector_store = vector_store

            st.session_state.video_processed = True

            st.success("✅ Video Processed Successfully")

        except Exception as e:

            error_message = str(e)

            # NO TRANSCRIPT
            if "NoTranscriptFound" in error_message:

                st.warning("""
⚠️ No transcript found for this video.

Try:
• Another video
• Videos with captions enabled
• English subtitle videos
""")

            # SUBTITLE DISABLED
            elif "TranscriptsDisabled" in error_message:

                st.warning("""
⚠️ Captions are disabled for this video.
""")

            # GEMINI RATE LIMIT
            elif "429" in error_message:

                st.warning("""
⚠️ Gemini API quota exceeded.

Please wait or switch API key.
""")

            # GEMINI SERVER LOAD
            elif "503" in error_message:

                st.warning("""
⚠️ Gemini servers are under heavy load.

Please retry in a few moments.
""")

            else:

                st.error(
                    f"""
❌ Video Processing Failed

Reason:
{error_message}
"""
                )

# =========================================
# CHAT SECTION
# =========================================

st.markdown("""
<div class="chat-container">
""", unsafe_allow_html=True)

st.markdown("""
<div class="chat-heading">
💬 Conversational Video Assistant
</div>
""", unsafe_allow_html=True)

if not st.session_state.video_processed:

    st.info("Process a YouTube video to start chatting.")

else:

    # =========================================
    # SHOW CHAT HISTORY
    # =========================================

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # =========================================
    # USER INPUT
    # =========================================

    user_query = st.chat_input(
        "Ask anything about the video..."
    )

    if user_query:

        # SAVE USER MESSAGE

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_query
            }
        )

        with st.chat_message("user"):
            st.markdown(user_query)

# =========================================
# ASSISTANT RESPONSE
# =========================================

        with st.chat_message("assistant"):

            response_placeholder = st.empty()

            full_response = ""

            try:

                llm = get_chat_model()

# =========================================
# SUMMARY MODE
# =========================================

                if any(
                    keyword in user_query.lower()
                    for keyword in [
                        "summary",
                        "summarize",
                        "overview",
                        "explain video"
                    ]
                ):

                    prompt = f"""
                    You are an advanced AI video analyst.

                    Give a HIGH-QUALITY professional summary of the YouTube video.

                    Include:
                    1. Main topic
                    2. Key concepts
                    3. Important insights
                    4. Technologies/tools discussed
                    5. Final conclusion

                    Transcript:
                    {st.session_state.full_transcript}
                    """

# =========================================
# NORMAL RAG MODE
# =========================================

                else:

                    import re

                    timestamp_match = re.search(
                        r"(\d{1,2})[:.](\d{2})",
                        user_query
                    )

# =========================================
# TIMESTAMP RETRIEVAL
# =========================================

                    if timestamp_match:

                        minutes = int(
                            timestamp_match.group(1)
                        )

                        seconds = int(
                            timestamp_match.group(2)
                        )

                        target_total_seconds = (
                            minutes * 60
                        ) + seconds

                        all_docs = st.session_state.vector_store.similarity_search(
                            "",
                                 k=500
                                        )

                        docs = []

                        for doc in all_docs:

                            ts = doc.metadata.get(
                                "timestamp",
                                "00:00"
                            )

                            try:

                                ts_minutes, ts_seconds = map(
                                    int,
                                    ts.split(":")
                                )

                                doc_total_seconds = (
                                    ts_minutes * 60
                                ) + ts_seconds

                                # ±15 seconds
                                if abs(
                                    doc_total_seconds
                                    - target_total_seconds
                                ) <= 15:

                                    docs.append(doc)

                            except:

                                continue

# =========================================
# NORMAL RETRIEVAL
# =========================================

                    else:

                        docs = retrieve_context(
                            st.session_state.vector_store,
                            user_query
                        )

# =========================================
# FALLBACK
# =========================================

                    if len(docs) == 0:

                        docs = st.session_state.vector_store.similarity_search(
                            user_query,
                            k=8
                        )

# =========================================
# BUILD CONTEXT
# =========================================

                    context = "\n\n".join(
                        [
                            f"""
Timestamp: {doc.metadata.get('timestamp')}

Content:
{doc.page_content}
"""
                            for doc in docs
                        ]
                    )

# =========================================
# RAG PROMPT
# =========================================

                    prompt = rag_prompt.invoke(
                        {
                            "context": context,
                            "question": user_query
                        }
                    )

# =========================================
# STREAM RESPONSE
# =========================================

                for chunk in llm.stream(prompt):

                    if chunk.content:

                        full_response += chunk.content

                        response_placeholder.markdown(
                            full_response + "▌"
                        )

                response_placeholder.markdown(
                    full_response
                )

            except Exception as e:

                error_message = str(e)

# =========================================
# RATE LIMIT
# =========================================

                if "429" in error_message:

                    st.warning("""
⚠️ Gemini API quota exceeded.

Try:
• Wait a few minutes
• Use another API key
• Upgrade Gemini API plan
""")

# =========================================
# SERVER OVERLOAD
# =========================================

                elif "503" in error_message:

                    st.warning("""
⚠️ Gemini servers are under heavy load.

Please retry in a few moments.
""")

# =========================================
# TRANSCRIPT ISSUES
# =========================================

                elif "NoTranscriptFound" in error_message:

                    st.warning("""
⚠️ No transcript available for this video.
""")

                elif "Subtitles are disabled" in error_message:

                    st.warning("""
⚠️ This video has subtitles disabled.
""")

# =========================================
# UNKNOWN ERROR
# =========================================

                else:

                    st.error(
                        f"Unexpected Error: {error_message}"
                    )

                full_response = "Error occurred."

# =========================================
# SAVE CHAT HISTORY
# =========================================

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response
            }
        )

st.markdown("</div>", unsafe_allow_html=True)