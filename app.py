import os
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import re
from gtts import gTTS
import google.generativeai as genai

# 1. API CONFIGURATION
# Make sure GEMINI_KEY is in your Streamlit Cloud Secrets!
genai.configure(api_key=st.secrets["GEMINI_KEY"])

# 2. LOGIC FUNCTIONS
def get_video_transcript(video_url):
    try:
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        else:
            return None

        # Call on the Class directly, NOT an instance
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
        return " ".join([i['text'] for i in transcript_list])
    except Exception:
        return None

def generate_notes(text: str) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Summarize this for a neurodiverse learner with Title, Summary, Key Takeaways, Mnemonics, and a Quiz: {text}"
    response = model.generate_content(prompt)
    return response.text

def markdown_to_voice(text: str):
    output_file = "notes_voice.mp3"
    cleaned_text = re.sub(r'[#*`\-]', '', text)
    speech = gTTS(text=cleaned_text, lang='en')
    speech.save(output_file)

# 3. MAIN APP UI
def main():
    st.set_page_config(page_title="MINDMATE", page_icon="🧠", layout="wide")

    # Sidebar
    with st.sidebar:
        try:
            st.image("assets/images/mm.jpeg", use_container_width=True)
        except:
            st.title("🧠 MINDMATE")
        st.info("Tailored for ADHD & Dyslexia.")

    # Header Image
    try:
        st.image("assets/images/bg.jpg", use_container_width=True)
    except:
        st.write("---")

    st.title("MINDMATE 📝")
    video_URL = st.text_input("🔗 Paste YouTube URL here:")
    generate_btn = st.button("Generate Notes ✨")

    # ALL LOGIC MUST BE INSIDE main()
    if generate_btn:
        if video_URL:
            transcript = get_video_transcript(video_URL)
            
            # Manual Fallback UI if YouTube blocks the fetch
            if not transcript:
                st.error("⚠️ YouTube blocked the automated fetch.")
                st.info("Copy the transcript from YouTube and paste it below.")
                transcript = st.text_area("Paste Transcript Text Here:", height=200)
                # This sub-button processes the manually pasted text
                if st.button("Process Pasted Text"):
                    pass # The app will rerun and use the text in 'transcript'

            if transcript:
                with st.spinner('🚀 Simplifying content...'):
                    output_notes = generate_notes(transcript)
                    st.video(video_URL)
                    markdown_to_voice(output_notes)
                    st.audio('notes_voice.mp3')
                    st.markdown(output_notes)
                    st.balloons()
        else:
            st.warning("Please enter a URL.")

if __name__ == '__main__':
    main()
