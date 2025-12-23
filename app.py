import openai
import os
import streamlit as st
from pytube import YouTube
from PIL import Image
import re
from gtts import gTTS
import time

MAX_RETRIES = 3

# Set up OpenAI API credentials using Streamlit Secrets
# You will enter this key in the Streamlit Cloud dashboard
openai.api_key = st.secrets["OPENAI_KEY"]

def video_to_audio(video_URL:str, destination:str)-> None:
    '''Downloads the audio of the input URL and saves it into a .mp3 audio file'''   
    video = YouTube(video_URL)
    
    # Convert video to Audio
    audio = video.streams.filter(only_audio=True).first()
    output = audio.download(output_path = destination)  
    _, ext = os.path.splitext(output)
    new_file = "Target_audio.mp3"
    
    if os.path.exists(new_file):
        os.remove(new_file)
    os.rename(output, new_file)

def audio_to_text_with_retry() -> str:
    '''Converts Target_audio.mp3 into text using whisper-1 model with retry logic'''  
    for attempt in range(MAX_RETRIES):
        try:
            with open("Target_audio.mp3", "rb") as audio_file:
                transcript = openai.Audio.translate("whisper-1", audio_file)
                return transcript['text']
        except openai.error.RateLimitError as e:
            if attempt < MAX_RETRIES - 1:
                st.warning(f"Rate limit error. Retrying in 5s (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(5)
            else:
                st.error("Max retries reached. Unable to process request.")
                raise e 

def audio_to_text() -> str:
    return audio_to_text_with_retry()

def markdown_to_voice(text:str)-> None: 
    '''Converts markdown into plain text and saves as audio'''
    output_file = "notes_voice.mp3"
    # Clean markdown characters for better speech synthesis
    cleaned_text = text.replace('#', ' ').replace('-', ' ').replace('*', ' ').replace('`', ' ')
    speech = gTTS(text = cleaned_text)
    speech.save(output_file)
    
import google.generativeai as genai

# Setup Gemini API Key
genai.configure(api_key=st.secrets["GEMINI_KEY"])

def generate_notes(text:str)-> str:
    '''Generates ADHD/Dyslexia friendly notes using Google Gemini'''
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""You are a teacher helping students with learning disabilities such as Dyslexia and ADHD. 
               Summarize the following text into these sections:
               1) Title, 2) Summary, 3) Key Takeaways, 4) Mnemonics, 5) Quiz Yourself!
               
               Text to summarize: {text}"""

    # Generate response
    response = model.generate_content(prompt)
    return response.text

def display_sidebar_and_content(text: str) -> None:
    '''Displays table of contents in sidebar and main markdown content'''
    pattern = r'##\s+(.*?)(?=:)' 
    headers = re.findall(pattern, text)

    st.sidebar.markdown('## Table of Contents')
    for header in headers:
        st.sidebar.markdown(f'- [{header}](#{header.lower().replace(" ", "-")})')

    st.markdown(text, unsafe_allow_html=True)

# Main App Execution
def main():
    st.set_page_config(page_title="MINDMATE", page_icon="🧠", layout="wide")

    # 2. Custom CSS for a cleaner look
    st.markdown("""
        <style>
        .main { background-color: #f0f2f6; }
        .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4A90E2; color: white; }
        .stTextInput>div>div>input { border-radius: 20px; }
        </style>
    """, unsafe_allow_html=True)

    # 3. Sidebar UI
    with st.sidebar:
        try:
            image_logo = Image.open("assets/images/mm.jpeg")
            st.image(image_logo, use_container_width=True)
        except:
            st.title("🧠 MINDMATE")
        
        st.header("Summarization Assistant")
        st.info("Tailored for Neurodiverse Learners (ADHD & Dyslexia).")
        st.divider()

    # 4. Main Header
    try:
        header_img = Image.open("assets/images/bg.jpg")
        st.image(header_img, use_container_width=True)
    except:
        pass

    st.title("MINDMATE 📝")
    st.subheader("Transforming YouTube Content into Interactive Learning Experiences!")
    st.divider()

    # 5. Input Section in a centered column
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        video_URL = st.text_input("🔗 Paste the YouTube video URL here:", placeholder="https://youtube.com/watch?v=...")
        generate_btn = st.button("Generate Notes ✨")

    if generate_btn:
        if video_URL:
            # (Keep your existing processing logic here...)
            st.success("Notes generated successfully!")
        else:
            st.warning("Please enter a valid URL.")

if __name__ == '__main__':
    main()
