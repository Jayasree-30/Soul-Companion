import streamlit as st
import google.generativeai as genai

# Configure the Gemini API key
# Replace "YOUR_API_KEY" with your actual Gemini API key
genai.configure(api_key="AIzaSyCq4BPePiFRB24NKJ4mEjRGO0ZSvgdmU-8")

st.title("AI Mental Health Chatbot")

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

# Mood tracking and resource recommendations - these can be integrated with Gemini or kept separate
# For now, we'll keep them as they are, but Gemini can be used to generate more nuanced responses
responses = {
    "sad": [
        "I'm sorry to hear that. Remember, you can find helpful resources at https://www.mentalhealth.gov/",
        "It sounds like you're going through a tough time. Talking to someone can help. Check out https://www.betterhelp.com/",
        "I'm here for you. If you need immediate support, the National Suicide Prevention Lifeline is available at 988."
    ],
    "happy": [
        "That's great to hear! Keep that positive energy going.",
        "I'm happy for you! What's making you feel so good?",
        "Awesome! It's wonderful to hear that you're in a good mood."
    ],
    "help": [
        "Of course. Here are some resources that might be helpful: \n- Crisis Text Line: Text HOME to 741741\n- The Trevor Project: 1-866-488-7386\n- National Alliance on Mental Illness (NAMI): 1-800-950-NAMI (6264)",
        "Here are some recommended resources: \n- BetterHelp: https://www.betterhelp.com/ \n- Talkspace: https://www.talkspace.com/ \n- Headspace: https://www.headspace.com/",
    ],
    "default": [
        "I'm not sure I understand. Could you please rephrase that?",
        "Tell me more about that.",
        "How does that make you feel?",
        "That's interesting. Can you elaborate?"
    ]
}


# Accept user input
if user_input := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # Create a Gemini model instance
        model = genai.GenerativeModel('gemini-pro') # You can choose a different model if needed
        # Generate bot response using Gemini
        response = model.generate_content(user_input)
        bot_response = response.text
    except Exception as e:
        bot_response = f"An error occurred: {e}" # Basic error handling

    # Display bot response in chat message container
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
