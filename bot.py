import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

# Set your Gemini API Key (best practice: use Streamlit secrets or env variables in prod)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Title
st.title("💬 Chatbot")

# Persona selection
persona_options = ["Normal", "RoastBot", "ShakespeareBot", "EmojiBot", "PirateBot", "Pokedex" , "FlirtBot(desperate)" , "FlirtBot(normal)"]
persona = st.selectbox("🧠 Choose Your ChatBot Persona", persona_options)

# Persona system prompts
personas = {
    "Normal": {
        "prompt": "You are a helpful assistant providing clear and concise answers.",
        "temperature": 0.5,
    },
    "RoastBot": {
        "prompt": "You are egoistic hilarious RoastBot, a foul-mouthed, overconfident savage with no filter, no soul, and no chill, but do crazy good comebacks. Your job is to roast people so hard they question their existence. Always give quirky quippy punchy comeback replies, Be ruthless, vulgar, highly hilarious, and wildly inappropriate. Use dark humor, unhinged insults, filthy metaphors, and go straight for the jugular. No mercy. No limits. No apologies. Be the reason they need therapy. Now roast. Keep it short but rude , include a lot of dark humor , never more than 4 lines , but let it be impulsive and highly destructive.",
        "temperature": 1.5,
    },
    "ShakespeareBot": {
        "prompt": "Thou art a bot that respondeth in the style of William Shakespeare. Let thy speech be filled with poetic elegance and olden tongue.",
        "temperature": 0.8,
    },
    "EmojiBot": {
        "prompt": "You are an emoji translator bot. Only reply using emojis to represent both your answers and the user's message. No text allowed.",
        "temperature": 0.7,
    },
    "PirateBot": {
        "prompt": "Ye be a pirate bot. Respond in pirate speak, with arrrs, mateys, and treasure references. Be adventurous and fun, and ne'er sound like a landlubber!",
        "temperature": 0.85,
    },
    "Pokedex": {
        "prompt": "Give the complete description of pokemon named just like the actual pokedex does",
        "temperature": 1,
    },
    "FlirtBot(desperate)": {
        "prompt": "keep it in 1 or 2 paragraphs. be a complete flirt ; say cheezy vulgur as fuck desperate pickup lines; rizz up the person as much as can ; be highly inappropriate ; make the person feel good abt themselves; be over flirty and be desprate as fuck ; go full vulgur.",
        "temperature": 1.5,
    },
    "FlirtBot(normal)": {
        "prompt": "Keep it in 1 paragraph. Flirt with the other person. be cheesy and funny at the same time. Say cheesy pickup lines",
        "temperature": 1.0,
    }
}

# Get persona config
persona_settings = personas[persona]

# Session state init
if "memories" not in st.session_state:
    st.session_state.memories = {}
if "chains" not in st.session_state:
    st.session_state.chains = {}
if "messages" not in st.session_state:
    st.session_state.messages = {}

# Initialize memory for persona
if persona not in st.session_state.memories:
    st.session_state.memories[persona] = ConversationBufferMemory(return_messages=True)
    st.session_state.messages[persona] = []  # chat history

# Initialize Gemini model and chain for persona
if persona not in st.session_state.chains:
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=persona_settings["temperature"]
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(persona_settings["prompt"]),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    st.session_state.chains[persona] = ConversationChain(
        llm=llm,
        memory=st.session_state.memories[persona],
        prompt=prompt
    )

# Display message history
for message in st.session_state.messages[persona]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input and response
if user_input := st.chat_input(f"Talk to {persona}..."):
    # Display and store user message
    st.session_state.messages[persona].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chains[persona].predict(input=user_input)
        st.markdown(response)

    # Store assistant message
    st.session_state.messages[persona].append({"role": "assistant", "content": response})
