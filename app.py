import os
import streamlit as st
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from PIL import Image
import re
from gtts import gTTS
import google.generativeai as genai

# API CONFIGURATION

genai.configure(api_key=st.secrets["GEMINI_KEY"])

# LOGIC FUNCTIONS

def get_video_transcript(video_url):
    '''Extracts transcript from YouTube video ID for free'''
    try:
        # Improved Video ID extraction
        video_id = None
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            st.error("Could not find a valid Video ID in the URL.")
            return None

        # Fetching the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([i['text'] for i in transcript_list])
        return full_transcript
        
    except Exception as e:
        st.error(f"Transcript Error: {e}. Please ensure the video has English Closed Captions (CC) enabled.")
        return None

def generate_notes(text: str) -> str:
    '''Generates ADHD/Dyslexia friendly notes using Google Gemini'''
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # This prompt is tailored to your specific project requirements
    prompt = f"""You are a specialized teacher for neurodiverse learners (ADHD/Dyslexia). 
    Generate structured notes from the following text. 
    Format the answer in Markdown with these EXACT sections:
    
    ## 📌 Title: [A clear, catchy title]
    
    ## 📝 Summary: [A creative and intuitive explanation]
    
    ## 💡 Key Takeaways: [Important points to remember]
    
    ## 🧠 Mnemonics: [Acronyms or associations to help remember facts]
    
    ## ❓ Quiz Yourself!: [3-5 Multiple choice questions with HIDDEN answers]
    
    Use simple, compassionate language. 
    
    Text: {text}"""

    response = model.generate_content(prompt)
    return response.text

def markdown_to_voice(text: str) -> None: 
    '''Converts markdown text into a clean audio file'''
    output_file = "notes_voice.mp3"
    # Remove markdown symbols so the voice doesn't read "hashtag hashtag"
    cleaned_text = re.sub(r'[#*`\-]', '', text)
    speech = gTTS(text=cleaned_text, lang='en')
    speech.save(output_file)

# STREAMLIT UI

def main():
    st.set_page_config(page_title="MINDMATE", page_icon="🧠", layout="wide")

    # Custom Styling
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4A90E2; color: white; border: none; }
        .stTextInput>div>div>input { border-radius: 20px; }
        .reportview-container { background: #f0f2f6; }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        try:
            image_logo = Image.open("assets/images/mm.jpeg")
            st.image(image_logo, use_container_width=True)
        except:
            st.title("🧠 MINDMATE")
        
        st.header("Summarization Assistant")
        st.info("Tailored for Neurodiverse Learners (ADHD & Dyslexia).")
        st.divider()
        st.write("Created with ❤️ for inclusive learning.")

    # Main Header
    try:
        header_img = Image.open("assets/images/bg.jpg")
        st.image(header_img, use_container_width=True)
    except:
        st.write("---")

    st.title("MINDMATE 📝")
    st.subheader("Transforming YouTube Content into Interactive Learning Experiences!")
    st.divider()

    # Input Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        video_URL = st.text_input("🔗 Paste the YouTube video URL here:", placeholder="https://youtube.com/watch?v=...")
        generate_btn = st.button("Generate Notes ✨")

    # App Logic
    if generate_btn:
        if video_URL:
            with st.spinner('🚀 Analyzing the video and simplifying content...'):
                # 1. Get Transcript (Free)
                transcript = get_video_transcript(video_URL)
                
                if transcript:
                    # 2. Generate Notes (Gemini Free)
                    output_notes = generate_notes(transcript)
                    
                    # 3. Show Video and Results
                    st.video(video_URL)
                    st.divider()
                    
                    st.write("### 🎧 Listen to your customized notes")
                    markdown_to_voice(output_notes)
                    st.audio('notes_voice.mp3')
                    
                    st.divider()
                    st.markdown(output_notes)
                    st.balloons()
        else:
            st.warning("Please enter a valid YouTube URL first!")

if __name__ == '__main__':
    main()
