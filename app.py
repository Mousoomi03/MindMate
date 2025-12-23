import os
import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
import google.generativeai as genai
from PIL import Image

# =====================================================
# 1. GEMINI API CONFIGURATION (FREE TIER)
# =====================================================

GEMINI_KEY = st.secrets.get("GEMINI_KEY") or os.getenv("GEMINI_KEY")

if not GEMINI_KEY:
    st.error("❌ Gemini API key not found. Add it to Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_KEY)

# =====================================================
# 2. LOGIC FUNCTIONS
# =====================================================

def get_video_transcript(video_url):
    """
    Fetch YouTube transcript (watch / youtu.be / shorts)
    """
    try:
        video_id = None

        if "watch?v=" in video_url:
            video_id = video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        elif "shorts/" in video_url:
            video_id = video_url.split("shorts/")[1].split("?")[0]

        if not video_id:
            return None

        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en"]
        )

        return " ".join(i["text"] for i in transcript)

    except Exception as e:
        print("Transcript error:", e)
        return None


def generate_notes(text: str) -> str:
    """
    Generate ADHD-friendly notes using Gemini (FREE)
    """
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    You are a supportive teacher for students with ADHD and Dyslexia.

    Create SIMPLE, CLEAR notes with:
    1. Title
    2. Short Summary
    3. Key Takeaways (bullets)
    4. Easy Mnemonics
    5. 5-question Quiz (MCQs)

    Use friendly language.

    TEXT:
    {text}
    """

    response = model.generate_content(prompt)

    if not response or not response.text:
        return "⚠️ No response generated."

    return response.text.strip()


def markdown_to_voice(text: str):
    """
    Convert notes to audio
    """
    output_file = "notes_voice.mp3"
    cleaned_text = re.sub(r"[#*`>-]", "", text)
    tts = gTTS(text=cleaned_text, lang="en")
    tts.save(output_file)
    return output_file


# =====================================================
# 3. STREAMLIT APP
# =====================================================

def main():
    st.set_page_config(
        page_title="MINDMATE",
        page_icon="🧠",
        layout="wide"
    )

    # Session state
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        try:
            st.image("assets/images/mm.jpeg", use_container_width=True)
        except:
            st.title("🧠 MINDMATE")

        st.info("Tailored for Neurodiverse Learners.")

    # ---------------- HEADER ----------------
    try:
        st.image("assets/images/bg.jpg", use_container_width=True)
    except:
        st.write("---")

    st.title("MINDMATE 📝")

    # ---------------- INPUT ----------------
    video_URL = st.text_input("🔗 Paste YouTube URL here:")
    generate_btn = st.button("✨ Generate Notes")

    # ---------------- AUTO TRANSCRIPT ----------------
    if generate_btn:
        st.session_state.clicked = True

        if video_URL:
            with st.spinner("📥 Fetching transcript..."):
                st.session_state.transcript = get_video_transcript(video_URL)

            if not st.session_state.transcript:
                st.error("⚠️ Automatic transcript unavailable for this video.")
        else:
            st.warning("Please enter a YouTube URL.")

    # ---------------- FALLBACK ----------------
    if (
        st.session_state.clicked
        and video_URL
        and not st.session_state.transcript
    ):
        st.info("💡 Copy the transcript from YouTube and paste it below.")
        pasted_text = st.text_area(
            "Paste Transcript Text Here:",
            height=220
        )

        if st.button("📄 Process Pasted Text"):
            st.session_state.transcript = pasted_text

    # ---------------- GENERATE NOTES ----------------
    if st.session_state.transcript and st.session_state.transcript.strip():
        with st.spinner("🚀 Simplifying content..."):
            try:
                notes = generate_notes(st.session_state.transcript)

                st.subheader("📘 Generated Notes")
                st.markdown(notes)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🔊 Generate Audio"):
                        audio_file = markdown_to_voice(notes)
                        st.audio(audio_file)

                with col2:
                    st.download_button(
                        "⬇️ Download Notes",
                        notes,
                        file_name="mindmate_notes.txt"
                    )

            except Exception as e:
                st.error(f"❌ Gemini Error: {e}")


# =====================================================
# 4. RUN
# =====================================================

if __name__ == "__main__":
    main()
