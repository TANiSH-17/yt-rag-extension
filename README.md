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
<img width="727" alt="image" src="https://github.com/user-attachments/assets/d6f549bb-9e2a-48cc-b1dd-1005861e6da4" />


---

## 🌟 Features

✅ Query any **YouTube video** directly from a Chrome popup.  
✅ Retrieves transcript automatically (if available).  
✅ Splits and embeds transcript into semantic chunks.  
✅ Stores embeddings in **FAISS** vector database.  
✅ Uses **similarity search + Gemini (Google Generative AI)** to generate answers.  
✅ Lightweight Flask backend with REST API.  
✅ Clean and user-friendly Chrome extension UI.  

---

## 📸 Demo!
[Screenshot 2025-07-04 at 5 27 00 PM](https://github.com/user-attachments/assets/781dd51c-8fff-4bc0-8790-3626a766e4d4)

![Screenshot 2025-07-04 at 5 27 04 PM](https://github.com/user-attachments/assets/612bb05a-7206-4ebd-8854-e5931d2f41b6)
![Screenshot 2025-07-04 at 5 27 34 PM](https://github.com/user-attachments/assets/30c03481-246f-4be4-ad6c-2bb7a8b45e7b)
![Screenshot 2025-07-04 at 5 26 12 PM](https://github.com/user-attachments/assets/54555924-7837-4da8-8f27-2e7a89aff14d)
![Screenshot 2025-07-04 at 5 27 59 PM](https://github.com/user-attachments/assets/b1c2ab27-9156-46ff-a77c-f9f14ff8eb7f)







---

## 🔧 Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/TANiSH-17/yt-rag-extension.git
cd yt-rag-extension



