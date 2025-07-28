import streamlit as st
import google.generativeai as genai
from streamlit_webrtc import webrtc_streamer
import av
import io
import speech_recognition as sr
import numpy as np

# Configure the page
st.set_page_config(
    page_title="AI Mental Health Chatbot",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.mentalhealth.gov/',
        'Report a bug': "https://www.example.com/reportbug", # Replace with a relevant URL
        'About': "# AI Mental Health Chatbot. This is a prototype."
    }
)

# Custom CSS for additional styling (optional)
st.markdown("""
<style>
    /* Add your custom CSS here */
    .stTextInput > div > div > input {
        color: #4F8BF9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
st.title("AI Mental Health Chatbot")

# Audio Processor class to handle audio frames
class AudioProcessor:
    def __init__(self) -> None:
        self.sound_chunk = io.BytesIO()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        sound_bytes = frame.to_ndarray().tobytes()
        self.sound_chunk.write(sound_bytes)
        return frame

# Video Processor class to handle video frames and capture images
class VideoProcessor:
    def __init__(self) -> None:
        self.captured_frame = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        # Store the latest frame
        self.captured_frame = frame
        return frame

st.title("AI Mental Health Chatbot")


# Configure the Gemini API key
# Replace "YOUR_API_KEY" with your actual Gemini API key
genai.configure(api_key="AIzaSyCq4BPePiFRB24NKJ4mEjRGO0ZSvgdmU-8")

# Personalized Greeting
if 'username' not in st.session_state:
    st.session_state.username = st.text_input("What's your name?")
    if st.session_state.username:
        st.write(f"Hello, {st.session_state.username}! How are you feeling today?")
elif st.session_state.username:
    st.write(f"Welcome back, {st.session_state.username}!")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Voice input
webrtc_ctx_audio = webrtc_streamer(
    key="speech-to-text",
    mode="sendonly",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

if webrtc_ctx_audio.audio_processor:
    st.write("Recording...")
    if st.button("Stop Recording"):
        sound_chunk = webrtc_ctx_audio.audio_processor.sound_chunk
        if len(sound_chunk.getvalue()) > 0:
            recognizer = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(sound_chunk.getvalue())) as source:
                audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                st.session_state.user_input = text
            except sr.UnknownValueError:
                st.write("Could not understand audio")
            except sr.RequestError as e:
                st.write(f"Could not request results from Google Speech Recognition service; {e}")
        webrtc_ctx_audio.audio_processor.sound_chunk = io.BytesIO() # Reset buffer

# Image capture
webrtc_ctx_video = webrtc_streamer(
    key="video-capture",
    mode="sendonly",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

if webrtc_ctx_video.video_processor:
    if st.button("Capture Image"):
        if webrtc_ctx_video.video_processor.captured_frame:
            # Convert the captured frame to a NumPy array and then display it as an image
            img_array = webrtc_ctx_video.video_processor.captured_frame.to_ndarray(format="rgb24")
            st.image(img_array, caption="Captured Image")
            # Optionally, you can add the image to the chat history
            # st.session_state.messages.append({"role": "user", "content": "Captured an image:", "image": img_array})


# Accept user input
if user_input := st.chat_input("Type your message here...", key="user_input_text"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # Create a Gemini model instance
        model = genai.GenerativeModel('gemini-1.5-flash') # You can choose a different model if needed
        # Generate bot response using Gemini
        response = model.generate_content(user_input)
        bot_response = response.text
        # Apply basic markdown formatting (example: bolding the first sentence)
        sentences = bot_response.split('. ')
        if sentences:
            bot_response = f"**{sentences[0]}**" + ('. ' + '. '.join(sentences[1:]) if len(sentences) > 1 else '')

    except Exception as e:
        bot_response = f"An error occurred: {e}" # Basic error handling

    # Display bot response in chat message container
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
