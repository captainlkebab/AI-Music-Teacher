# AI Music Teacher 🎹

**AI Music Teacher** is a web-based application built with Flask that helps piano learners interactively explore audio, sheet music, and learning plans using modern AI tools and music processing libraries.

---

## ✅ Core Features

- 🎧 **MP3 to MIDI Visualization**  
  Upload MP3 files to extract pitch and rhythm features and visualize them (using Librosa).

- 🎼 **Direct MIDI Visualization**  
  Upload MIDI files and display their structure directly in the browser.

- 💬 **Chatbot (RAG-based)**  
  Ask questions related to piano learning, theory, and technique. The chatbot uses Retrieval-Augmented Generation for contextual answers.

- 🧭 **Learning Plan Generator (RAG-based)**  
  Generate step-by-step learning plans tailored to user goals and knowledge.

- 📚 **Sheet Music Library**  
  Browse and search a database of curated sheet music in PDF format.

---

## 🛠️ TODO / Roadmap

| Feature | Status |
|--------|--------|
| 🔄 Implement `basic-pitch` for accurate audio-to-MIDI conversion | Planned |
| 🔄 Finalize RAG-based learning plan system | In Progress |
| 📂 Add support for uploading MP3, MIDI, and PDF files in one interface | Planned |
| 🧾 Direct MIDI upload workflow (no MP3 required) | Planned |
| 📘 OEMER integration for pedagogical content | Planned |
| 📱 Android app with minimal UI | Planned |
| 💅 Flask UI redesign to full website experience | Planned |
| 📖 Expand RAG knowledge base with more books | Planned |
| 🔁 Use both `librosa` and `basic-pitch` for conversion comparison | Planned |
| 🧪 Evaluation module for quality of MIDI conversion | Planned |
| 🎹 Improve MIDI visualization (e.g., note timing, pitch accuracy) | Planned |
| 🎙️ Audio Transcriber (melody/rhythm extraction from audio) | Planned |
| 👩‍🏫 Lesson Assistant (suggests exercises, monitors progress) | Planned |

---

## ⚙️ Tech Stack

| Area           | Technology           |
|----------------|----------------------|
| Backend        | Flask (Python)       |
| Audio Analysis | `librosa`, planned: `basic-pitch` |
| Embeddings / RAG | FAISS, Custom Embedding Models |
| Database       | SQLite (dev), PostgreSQL (future) |
| UI             | HTML, Jinja2 Templates |
| Deployment     | Localhost / Gunicorn (planned) |

---

## 📁 Project Structure

ai-music-teacher/
├── app/                     # Main application package
│   ├── audio/               # Audio processing (e.g., MP3 to MIDI, librosa, basic-pitch)
│   ├── rag/                 # Retrieval-Augmented Generation logic (chatbot, learning plan)
│   ├── database/            # Sheet music database logic and models
│   ├── static/              # Frontend assets (CSS, JS, images)
│   ├── templates/           # HTML templates rendered by Flask
│   └── routes/              # Flask route definitions
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point to run the Flask app
└── README.md                # Project documentation



## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/yourusername/ai-music-teacher.git
cd ai-music-teacher

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
flask run


MIT Licence