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


![Screenshot 2025-07-04 at 5 27 00 PM](https://github.com/user-attachments/assets/aeb432e7-ae4b-45d5-94c4-cb08e1651665)

![Screenshot 2025-07-04 at 5 27 04 PM](https://github.com/user-attachments/assets/612bb05a-7206-4ebd-8854-e5931d2f41b6)
![Screenshot 2025-07-04 at 5 27 34 PM](https://github.com/user-attachments/assets/30c03481-246f-4be4-ad6c-2bb7a8b45e7b)
![Screenshot 2025-07-04 at 5 26 12 PM](https://github.com/user-attachments/assets/54555924-7837-4da8-8f27-2e7a89aff14d)
![Screenshot 2025-07-04 at 5 27 59 PM](https://github.com/user-attachments/assets/b1c2ab27-9156-46ff-a77c-f9f14ff8eb7f)







---

\🔗 Usage
1️⃣ Navigate to a YouTube video page.

2️⃣ Click on the extension icon.

3️⃣ Type your question about the video.

4️⃣ The extension sends the video URL & question to the backend.

5️⃣ The backend fetches transcript, processes it, and sends the answer back.


<img width="836" alt="image" src="https://github.com/user-attachments/assets/2dfff342-2e85-44e3-85db-84542461f6ac" />

🔍 How it works

✅ Step 1: Get transcript → using youtube-transcript-api.

✅ Step 2: Split transcript → using RecursiveCharacterTextSplitter.

✅ Step 3: Embed chunks → using GoogleGenerativeAIEmbeddings.

✅ Step 4: Store & retrieve → using FAISS.

✅ Step 5: Compose answer → using ChatGoogleGenerativeAI.


💻 Dependencies

Python (backend)

Flask


Flask-CORS


dotenv


youtube-transcript-api


langchain


langchain-google-genai


faiss-cpu (or faiss)

Chrome Extension (frontend)

Standard Chrome Extension APIs


Vanilla JS/HTML/CSS


📋 To-Do / Improvements
 Add support for multi-lingual transcripts.

 Better error handling when transcripts are disabled.

 Cache embeddings for previously processed videos.

 Add tests & CI/CD pipeline.

 Deploy backend to cloud (e.g., GCP, AWS, or Railway).

 UI polish and responsiveness.

 📝 License
This project is licensed under the MIT License. See the LICENSE file for details.

👨‍💻 Author
👋 Developed by Tanish

If you like this project, please ⭐️ the repository and share it!

📣 Contributing
Pull requests are welcome!
For major changes, please open an issue first to discuss what you would like to change.
Don’t forget to update tests as appropriate.

🌟 Support
If you find this project helpful, consider giving it a ⭐️ on GitHub and sharing it with others!



