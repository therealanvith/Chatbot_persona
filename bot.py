import streamlit as st
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# =======================
# ENV / API KEY
# =======================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

st.title("💬 Chatbot")

# =======================
# PERSONAS
# =======================
persona_options = [
    "Normal", "RoastBot", "ShakespeareBot", "EmojiBot",
    "PirateBot", "Pokedex", "FlirtBot(desperate)", "FlirtBot(normal)"
]

persona = st.selectbox("🧠 Choose Your ChatBot Persona", persona_options)

personas = {
    "Normal": {
        "prompt": "You are a helpful assistant providing clear and concise answers.",
        "temperature": 0.5,
    },
    "RoastBot": {
        "prompt": "You are a ruthless, foul-mouthed roast bot. Be savage, dark, vulgar, hilarious. Max 4 lines.",
        "temperature": 1.5,
    },
    "ShakespeareBot": {
        "prompt": "Respond like William Shakespeare using poetic old English.",
        "temperature": 0.8,
    },
    "EmojiBot": {
        "prompt": "Only respond using emojis. No text.",
        "temperature": 0.7,
    },
    "PirateBot": {
        "prompt": "Respond like a pirate. Use arrr, matey, treasure talk.",
        "temperature": 0.85,
    },
    "Pokedex": {
        "prompt": "Give Pokémon descriptions exactly like a Pokédex.",
        "temperature": 1.0,
    },
    "FlirtBot(desperate)": {
        "prompt": "Extremely desperate, vulgar, cheesy flirting. Be inappropriate.",
        "temperature": 1.5,
    },
    "FlirtBot(normal)": {
        "prompt": "Light, funny, cheesy flirting. One paragraph.",
        "temperature": 1.0,
    }
}

settings = personas[persona]

# =======================
# SESSION STATE
# =======================
if "histories" not in st.session_state:
    st.session_state.histories = {}

if persona not in st.session_state.histories:
    st.session_state.histories[persona] = ChatMessageHistory()

# =======================
# MODEL
# =======================
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=settings["temperature"],
)

# =======================
# PROMPT
# =======================
prompt = ChatPromptTemplate.from_messages([
    ("system", settings["prompt"]),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

# =======================
# MEMORY WRAPPER
# =======================
def get_history(session_id: str):
    return st.session_state.histories[persona]

chat = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

# =======================
# DISPLAY HISTORY
# =======================
for msg in st.session_state.histories[persona].messages:
    role = "assistant" if msg.type == "ai" else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

# =======================
# CHAT INPUT
# =======================
if user_input := st.chat_input(f"Talk to {persona}..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": persona}}
            )
        st.markdown(response.content)

