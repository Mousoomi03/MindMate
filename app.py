import os
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import re
from gtts import gTTS
import google.generativeai as genai

# 1. API CONFIGURATION
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# 2. LOGIC FUNCTIONS
def get_video_transcript(video_url):
    try:
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        else: return None
        # Static method call on Class
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        return " ".join([i['text'] for i in transcript_list])
    except Exception: return None

def generate_notes(text: str) -> str:
    # Adding 'models/' prefix for better compatibility with the API
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    prompt = f"Summarize this for a neurodiverse learner: {text}"
    response = model.generate_content(prompt)
    return response.text

def markdown_to_voice(text: str):
    output_file = "notes_voice.mp3"
    cleaned_text = re.sub(r'[#*`\-]', '', text)
    speech = gTTS(text=cleaned_text, lang='en')
    speech.save(output_file)

# 3. MAIN APP UI & LOGIC
def main():
    st.set_page_config(page_title="MINDMATE", page_icon="🧠", layout="wide")
    
    # Initialize session state for persistent data
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None

    with st.sidebar:
        try: st.image("assets/images/mm.jpeg", use_container_width=True)
        except: st.title("🧠 MINDMATE")
        st.info("Tailored for Neurodiverse Learners.")

    try: st.image("assets/images/bg.jpg", use_container_width=True)
    except: st.write("---")

    st.title("MINDMATE 📝")
    video_URL = st.text_input("🔗 Paste YouTube URL here:")
    generate_btn = st.button("Generate Notes ✨")

    # ALL interactive logic must be inside main()
    if generate_btn:
        if video_URL:
            st.session_state.transcript = get_video_transcript(video_URL)
            if not st.session_state.transcript:
                st.error("⚠️ YouTube blocked the automated fetch (Bot Detection).")
        else:
            st.warning("Please enter a URL.")

    # Show Fallback UI if auto-fetch failed
    if video_URL and not st.session_state.transcript:
        st.info("💡 **Solution:** Copy the transcript from YouTube and paste it below.")
        pasted_text = st.text_area("Paste Transcript Text Here:", height=200)
        if st.button("Process Pasted Text"):
            st.session_state.transcript = pasted_text

    # Final execution block
    if st.session_state.transcript and st.session_state.transcript.strip():
        with st.spinner('🚀 Simplifying content...'):
            try:
                output_notes = generate_notes(st.session_state.transcript)
                # ... rest of your display code ...
            except Exception as e:
                st.error(f"Gemini API Error: {e}")

if __name__ == '__main__':
    main()
