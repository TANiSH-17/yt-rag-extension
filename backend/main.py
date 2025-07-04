import os
import re
from typing import Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

# Load env
load_dotenv()

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing. Please set it in .env")

# Initialize once
print("🔗 Initializing Google Gemini components...")
llm_translation = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, google_api_key=GOOGLE_API_KEY)
llm_rag = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.7, google_api_key=GOOGLE_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

print("✅ Components initialized.")


def extract_video_id(youtube_url: str) -> Optional[str]:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None


def fetch_transcript(video_id: str) -> str:
    print(f"🎯 Fetching transcript for video ID: {video_id}")
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        # Priority: English manual > English generated > any manual > any
        candidates = []
        for t in transcripts:
            candidates.append((t.language_code, not t.is_generated, t))

        # sort by our priority
        candidates.sort(key=lambda x: (x[0] != 'en', not x[1]))

        best_transcript = candidates[0][2] if candidates else None
        if not best_transcript:
            raise NoTranscriptFound(video_id)

        raw_data = best_transcript.fetch()
        text = " ".join(item.text for item in raw_data)

        if best_transcript.language_code != "en":
            print(f"🔄 Translating transcript from {best_transcript.language} ({best_transcript.language_code})...")
            translation = llm_translation.invoke(
                f"Translate the following to English while preserving meaning:\n\n{text}"
            )
            return translation.content

        print("✅ English transcript found.")
        return text

    except NoTranscriptFound:
        raise ValueError("No transcript available for this video.")
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except VideoUnavailable:
        raise ValueError("Video is unavailable (private, deleted, or restricted).")


def rag_query(transcript: str, query: str, video_id: str) -> str:
    doc = Document(page_content=transcript, metadata={"source": video_id})
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents([doc])

    vectorstore = FAISS.from_documents(chunks, embeddings)

    qa = RetrievalQA.from_chain_type(
        llm=llm_rag,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )

    print(f"🤖 Answering query: {query}")
    response = qa.invoke({"query": query})
    return response.get("result", "No answer found.")


@app.route("/ask-youtube", methods=["POST"])
def ask_youtube():
    data = request.json or {}
    youtube_url = data.get("youtube_url")
    query = data.get("query")

    if not youtube_url or not query:
        return jsonify({"error": "Missing 'youtube_url' or 'query'."}), 400

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Could not extract video ID from URL."}), 400

    try:
        transcript = fetch_transcript(video_id)
        answer = rag_query(transcript, query, video_id)
        return jsonify({"answer": answer}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({"error": f"Internal server error: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
