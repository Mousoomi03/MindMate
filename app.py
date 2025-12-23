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
    
def generate_notes(text:str)-> str:
    '''Generates ADHD/Dyslexia friendly notes using GPT-3.5-turbo'''
    prompt = """You are a teacher helping students with learning disabilities such as Dyslexia and ADHD. 
               The answer must include: 1) Title, 2) Summary, 3) Key Takeaways, 4) Mnemonics, 5) Quiz Yourself!
               Optional sections: Formulae, Code, Trivia, Jargons.
               Use Markdown formatting, simple language, and a compassionate tone."""

    messages = [
        {"role": "system", "content": prompt}, 
        {"role": "user", "content": text}
    ]

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages, 
        temperature=1.2
    )
    
    return chat.choices[0].message.content

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
    st.set_page_config(page_title="MINDMATE", page_icon="🧠")  
    
    # Sidebar Logo and Branding
    try:
        image_sidebar = Image.open("assets/images/mm.jpeg")
        st.sidebar.image(image_sidebar)
    except FileNotFoundError:
        st.sidebar.title("MINDMATE")

    st.sidebar.header("Intelligent Summarization Assistant")
    st.sidebar.write("_For Neurodiverse Learners._")

    # Header Image
    try:
        image_header = Image.open("assets/images/bg.jpg")
        st.image(image_header)
    except FileNotFoundError:
        pass

    st.title("MINDMATE 📑")
    st.subheader("Transforming YouTube Content into Interactive Learning Experiences!")

    video_URL = st.text_input("Paste the YouTube video URL here:")

    if st.button("Generate Notes"):
        if video_URL:
            try:
                with st.spinner('Simplifying content for you... 📖'):
                    # Process Video
                    video_to_audio(video_URL, ".")
                    transcript_text = audio_to_text()
                    
                    # Cleanup audio to save space
                    if os.path.exists('Target_audio.mp3'):
                        os.remove('Target_audio.mp3')
                    
                    # Generate Notes
                    notes_output = generate_notes(transcript_text)
                    
                    # Display Results
                    st.video(video_URL)
                    st.divider()
                    st.write("### 🎧 Listen to your customized notes")
                    markdown_to_voice(notes_output)
                    st.audio('notes_voice.mp3')
                    
                    display_sidebar_and_content(notes_output)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please provide a valid YouTube URL.")

if __name__ == '__main__':
    main()
