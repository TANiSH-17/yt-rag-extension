import os
import re
import functions_framework

from dotenv import load_dotenv
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

load_dotenv()

llm_for_translation = None
llm_for_rag = None
embeddings = None
google_api_key = os.getenv("GOOGLE_API_KEY")


def initialize_global_components():
    global llm_for_translation, llm_for_rag, embeddings, google_api_key

    if not google_api_key:
        print("⚠️  GOOGLE_API_KEY environment variable not set. LLM/Embeddings will not initialize.")
        return

    if llm_for_translation is None:
        try:
            llm_for_translation = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", temperature=0.3, google_api_key=google_api_key)
            llm_for_rag = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro", temperature=0.7, google_api_key=google_api_key)
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", google_api_key=google_api_key)
            print("✅ Google Gemini LLM and Embeddings initialized globally.")
        except Exception as e:
            print(f"❌ Error initializing global LLM/Embeddings: {e}")
            llm_for_translation, llm_for_rag, embeddings = None, None, None


def extract_video_id(youtube_url: str) -> str | None:
    pattern = (
        r'(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)'
        r'(?:/(?:watch\?v=|embed/|v/|e/|live/|shorts/|playlist\?list=.*&v=|'
        r'user/.*/|channel/.*/|c/.*/|@.*/videos/))([^"&?/]{11})'
    )
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    return None


def _process_rag_request(youtube_url: str, query: str) -> str:
    global llm_for_translation, llm_for_rag, embeddings, google_api_key

    if llm_for_translation is None or llm_for_rag is None or embeddings is None:
        initialize_global_components()
        if llm_for_translation is None or llm_for_rag is None or embeddings is None:
            return "Error: LLM/Embeddings components could not be initialized. Check API key and logs."

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return f"Error: Could not extract video ID from the provided URL: {youtube_url}. Please ensure it's a valid YouTube video URL."

    transcript_text = ""
    try:
        print(f"🎯 Extracted video ID: {video_id} from URL: {youtube_url}")
        print(f"📄 Attempting to fetch transcript for video ID: {video_id}...")

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        selected_transcript = None
        for transcript in transcript_list:
            manual = not transcript.is_generated
            if transcript.language_code == "en":
                selected_transcript = transcript
                print(f"✅ Found English transcript (language: {transcript.language}, code: {transcript.language_code}, generated: {transcript.is_generated}, manual: {manual}).")
                break
            elif selected_transcript is None:
                selected_transcript = transcript
                print(f"ℹ️ No English transcript found yet. Found transcript in {transcript.language} (code: {transcript.language_code}, generated: {transcript.is_generated}, manual: {manual}).")

        if selected_transcript:
            raw_transcript_data = selected_transcript.fetch()
            # 🔥 FIXED: use `.text` instead of `['text']`
            raw_text = " ".join([item.text for item in raw_transcript_data])

            if selected_transcript.language_code != 'en':
                print(f"🔄 Translating transcript from {selected_transcript.language} ({selected_transcript.language_code}) to English using Gemini...")
                translation_prompt = (
                    f"Translate the following text from {selected_transcript.language} ({selected_transcript.language_code}) to English. "
                    f"Maintain the original meaning and context. Text:\n\n{raw_text}"
                )
                translated_response = llm_for_translation.invoke(translation_prompt)
                transcript_text = translated_response.content
                print("✅ Translation complete.")
            else:
                transcript_text = raw_text
                print("✅ Using English transcript directly.")

            if not transcript_text.strip():
                return f"Error: Transcript (or translated transcript) for video ID '{video_id}' was empty after processing."
        else:
            return (f"Error: No retrievable transcripts found for video ID '{video_id}' using youtube-transcript-api. "
                    f"This typically means there are no manually uploaded or YouTube-generated captions in any language. "
                    f"Auto-translated captions in the YouTube player are not accessible via this API. "
                    f"Please try a different video that is known to have captions.")

    except NoTranscriptFound:
        return (f"Error: No transcript found for video ID '{video_id}'. "
                f"This usually means there are no manually uploaded or YouTube-generated captions for this video. "
                f"Auto-translated captions in the YouTube player are not accessible via this API. "
                f"Please try a different video that is known to have captions.")
    except TranscriptsDisabled:
        return f"Error: Transcripts are disabled for video ID '{video_id}' by the video creator."
    except VideoUnavailable:
        return f"Error: Video ID '{video_id}' is unavailable (e.g., private, deleted, or region-restricted)."
    except Exception as e:
        return f"An unexpected error occurred during transcript handling for video ID '{video_id}': {str(e)}"

    try:
        documents = [Document(page_content=transcript_text, metadata={"source": f"youtube_video_{video_id}"})]

        print("📄 Splitting transcript into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        print(f"✅ Split into {len(docs)} chunks.")

        print("📦 Creating FAISS vector store from chunks...")
        vectorstore = FAISS.from_documents(docs, embeddings)
        print("✅ FAISS vector store created.")

        print("🔗 Creating RetrievalQA chain...")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_for_rag,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        print("✅ RetrievalQA chain created.")

        print(f"🤖 Getting answer for query: '{query}'...")
        response = qa_chain.invoke({"query": query})
        answer = response.get("result", "Could not find an answer.")
        print("✅ Answer received.")

        return answer

    except Exception as e:
        return f"An unexpected error occurred during RAG processing: {str(e)}"


if __name__ == "__main__":
    print("\n--- 🧪 Running YouTube RAG Application Locally (for testing) ---")
    print("This block is for local development and will not run on Google Cloud Functions.")
    print("------------------------------------------------------------")

    initialize_global_components()
    if llm_for_translation is None:
        print("❌ Local LLM/Embeddings initialization failed due to missing API key. Cannot proceed with RAG.")
    else:
        while True:
            user_url = input("\nEnter YouTube Video URL (or type 'quit' to exit'): ")
            if user_url.lower() == 'quit':
                break

            user_query = input("Enter your query about the video: ")

            print("\n⚙️ Processing your request locally...")
            rag_answer = _process_rag_request(user_url, user_query)

            print("\n--- 🎯 RAG Answer ---")
            print(rag_answer)
            print("\n--------------------\n")

    print("👋 Exiting local application. Goodbye!")
