# MindMate
AI-powered learning assistant designed to make educational content more accessible for neuro diverse learners.Individuals with ADHD and learning disabilities such as dyslexia often struggle to absorb information from lengthy videos and lectures. Traditional note taking methods can be challenging, leading to difficulties in retaining key information. This project aims to address these challenges by developing an AI-powered assistant that can summarize large educational videos/lectures, generate concise notes, and create quizzes to aid learning for individuals with ADHD and learning disabilities.

**Steps to run in terminal:**
1. pip install -r requirements
2. Paste OpenAI API key in secrets.toml
3. python -m streamlit run app.py

**📽️ What it does: **  

MindMate transforms YouTube educational videos into concise, interactive study materials, including:  
✍️ Simplified notes with summaries, key takeaways, mnemonics, and quizzes  
🧠 Audio playback of notes for multi-modal learning  
📄 Markdown formatting for clarity and structure  
🎯 Quiz-based self-assessment  

  
**🧩 Key Technologies Used: **  

**OpenAI Whisper** for speech-to-text conversion  
**GPT-3.5 Turbo** for intelligent summarization and note generation  
**gTTS** for text-to-speech conversion  
**Streamlit** for front-end deployment  
**PyTube** for YouTube audio extraction
