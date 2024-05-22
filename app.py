import os
import sys
import datetime
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# Import API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Function to check if the API key is set, either from .env or user input
def check_api_key():
    if 'OPENAI_API_KEY' in st.session_state:
        st.sidebar.success("API key is set.")
    else:
        if OPENAI_API_KEY:
            st.session_state.OPENAI_API_KEY = OPENAI_API_KEY
            st.sidebar.success("API key is set.")
        else:
            st.sidebar.warning("API key is not set. Please enter your API key.")
            api_key_input = st.sidebar.text_input("Enter OpenAI API Key", type="password")
            if api_key_input:
                st.session_state.OPENAI_API_KEY = api_key_input
                st.sidebar.success("API key has been updated.")
            else:
                st.error("API key is required to proceed.")
                st.stop()  # Stop the execution if API key is not provided

# Function to initialize and return the OpenAI client
def get_openai_client():
    if 'OPENAI_API_KEY' in st.session_state:
        return OpenAI(api_key=st.session_state.OPENAI_API_KEY)
    else:
        return None

# Initialize OpenAI client
client = get_openai_client()

# Function to save audio file with a timestamp
def save_audio_file(audio_bytes, file_extension):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_{timestamp}.{file_extension}"
    with open(file_name, "wb") as f:
        f.write(audio_bytes)
    return file_name

# Function to transcribe audio using OpenAI's Whisper model
def transcribe_audio(file_name):
    path = './' + file_name
    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    transcription_text = transcription.text if transcription else "No transcription available."
    return transcription_text

# Function to display transcript and provide a download button
def display_transcript(transcript_text):
    st.header("Transcript")
    st.write(transcript_text)
    save_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    text_file_name = f"text_{save_timestamp}.txt"
    with open(text_file_name, "w", encoding='utf-8') as text_file:
        text_file.write(transcript_text)
    with open(text_file_name, "rb") as file:
        st.download_button("Download File", file, text_file_name, 'text/plain')

# Main function to run the Streamlit app
def main():
    st.title("Whisper Transcription")
    
    # Check for API key
    check_api_key()
    
    # Initialize session state variables
    if 'audio_files' not in st.session_state:
        st.session_state.audio_files = {}
    if 'transcriptions' not in st.session_state:
        st.session_state.transcriptions = {}
    if 'recorded_audio_file' not in st.session_state:
        st.session_state.recorded_audio_file = None
    
    # Create tabs for recording and uploading audio
    tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])
    
    # Record Audio tab
    with tab1:
        audio_bytes = audio_recorder()
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            file_name = save_audio_file(audio_bytes, 'wav')
            st.session_state.recorded_audio_file = file_name
            st.session_state.audio_files[file_name] = audio_bytes

            if st.button("Transcribe from Recorded File", key="record_transcribe"):
                transcript_text = transcribe_audio(file_name)
                st.session_state.transcriptions[file_name] = transcript_text
                display_transcript(transcript_text)
    
    # Upload Audio tab
    with tab2:
        audio_file = st.file_uploader("Upload Audio", type=["mp3", "mp4", "wav", "m4a"])
        if audio_file:
            file_extension = audio_file.type.split('/')[1]
            if file_extension == 'x-m4a':
                file_extension = 'm4a'
            if 'uploaded_file' not in st.session_state:
                st.session_state.uploaded_file = {}
            if audio_file.name not in st.session_state.uploaded_file:
                file_name = save_audio_file(audio_file.read(), file_extension)
                st.session_state.uploaded_file[audio_file.name] = file_name
                st.session_state.audio_files[file_name] = audio_file.read()
            else:
                file_name = st.session_state.uploaded_file[audio_file.name]
            if st.button("Transcribe from Uploaded File", key="upload_transcribe"):
                transcript_text = transcribe_audio(file_name)
                st.session_state.transcriptions[file_name] = transcript_text
                display_transcript(transcript_text)
    
    # Display session data in the sidebar
    st.sidebar.header("Session Data")
    st.sidebar.write("Audio Files:", list(st.session_state.audio_files.keys()))
    st.sidebar.write("Transcriptions:", list(st.session_state.transcriptions.values()))

# Entry point of the program
if __name__ == "__main__":
    working_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(working_dir)
    main()
