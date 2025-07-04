# 🎥 YouTube RAG Extension

> 🔍 Retrieval-Augmented Generation (RAG) powered Chrome extension for querying YouTube video content with context-aware answers, using LangChain, Gemini, FAISS & Flask.

---

## 🚀 Overview

This project implements a **Chrome extension** that allows users to ask questions about a YouTube video and receive accurate, context-aware answers by leveraging the video's transcript and a Retrieval-Augmented Generation (RAG) pipeline.

When the user queries something, the system:
- Fetches the video’s transcript.
- Splits it into chunks.
- Embeds the chunks using Gemini Embeddings.
- Stores them in a **FAISS vector database**.
- Uses similarity search to retrieve relevant chunks.
- Passes the context + question to Gemini via LangChain to generate a precise answer.

---

## 📂 Project Structure

