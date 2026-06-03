import streamlit as st
import random
import urllib.request
import time
import base64
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page
st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURATION DE L'IDENTITÉ ---
CREATOR_NAME = "Charles Joseph"
AI_DISPLAY_NAME = "Charles IA"
URL_AVATAR_AI = "avatar.jpg"
URL_AVATAR_USER = "user"

# --- CONFIGURATION DES INVITES ALÉATOIRES ---
LISTE_PROMTS_ALEATOIRES = [
    "Question rapide à Charles IA 🤖",
    "Demande à Charles IA 💡",
    "Astuce de Charles IA ⚡",
    "Idée avec Charles IA 🎨",
    "Apprendre avec Charles IA 📚",
    "Explique-moi, Charles IA 🧩",
    "Réponse claire par Charles IA ✨",
    "Inspiration de Charles IA 🚀",
    "Conseil de Charles IA 🔥",
    "Info utile par Charles IA 📊"
]

if "current_placeholder" not in st.session_state:
    st.session_state["current_placeholder"] = random.choice(LISTE_PROMTS_ALEATOIRES)

# --- FONCTIONS UTILES ---
def encode_image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

# --- INTERFACE CSS GEMINI ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: black !important;
        color: #1f1f1f !important;
        font-family: "Google Sans", sans-serif;
    }}
    [data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); height: 0px; }}
    .block-container {{ padding-top: 2.5rem !important; padding-bottom: 7rem !important; max-width: 560px !important; }}
    .gemini-greeting {{ font-size: 2.3rem; font-weight: 500; background: linear-gradient(90deg, #4285f4, #9b51e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .gemini-subtitle {{ font-size: 2.3rem; font-weight: 500; color: #c4c7c5; margin-bottom: 2rem; }}
    .stButton > button {{ background-color: #ffffff !important; border-radius: 16px !important; border: 1px solid #e3e3e3 !important; width: 100% !important; text-align: left !important; }}
    [data-testid="stChatInput"] {{ background-color: #f0f4f9 !important; border-radius: 32px !important; border: none !important; }}
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

suggestion_cliquee = None

# --- ACCUEIL ---
if len(st.session_state.messages) == 0:
    st.markdown(f'<div class="gemini-greeting">Bonjour, je suis {AI_DISPLAY_NAME}</div><div class="gemini-subtitle">Par où commencer ?</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🖼️ Créer une image", key="btn_img"): suggestion_cliquee = "Donne-moi un prompt créatif pour une image."
        if st.button("🎸 Créer de la musique", key="btn_mus"): suggestion_cliquee = "Idées pour composer une musique."
    with col2:
        if st.button("📄 Rédiger", key="btn_red"): suggestion_cliquee = "Aide-moi à rédiger un texte structuré."
        if st.button("✨ Motivation", key="btn_mot"): suggestion_cliquee = "Donne-moi de la motivation !"

photo_importee = st.file_uploader("📸 Joindre une photo", type=["png", "jpg", "jpeg"])
question = st.chat_input(st.session_state["current_placeholder"])

prompt_final = question or suggestion_cliquee
if not prompt_final and photo_importee and not st.session_state.get("photo_traitee"):
    prompt_final = "Analyse cette image précisément."
    st.session_state["photo_traitee"] = True

if prompt_final:
    st.session_state["current_placeholder"] = random.choice(LISTE_PROMTS_ALEATOIRES)
    if photo_importee:
        img_b64 = encode_image_to_base64(photo_importee)
        content = [{"type": "text", "text": prompt_final}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]
        st.session_state["photo_traitee"] = False
    else:
        content = prompt_final
    st.session_state.messages.append({"role": "user", "content": content})
    st.rerun()

# --- AFFICHAGE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=URL_AVATAR_USER if msg["role"] == "user" else URL_AVATAR_AI):
        if isinstance(msg["content"], list):
            for e in msg["content"]:
                if e["type"] == "text": st.markdown(e["text"])
                else: st.image(e["image_url"]["url"])
        else: st.markdown(msg["content"])

# --- RÉPONSE IA AVEC PARAMÈTRES AVANCÉS ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar=URL_AVATAR_AI):
        status = st.empty()
        if GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
            
            # Paramètres fonctionnels type Gemini
            config = {
                "temperature": 0.7,    # Équilibre entre créativité et précision
                "max_tokens": 4096,     # Longueur maximale de la réponse
                "top_p": 0.9,           # Diversité du vocabulaire
                "stream": False         # Désactivé pour la stabilité du rendu Markdown
            }

            is_vision = isinstance(st.session_state.messages[-1]["content"], list)
            model = "llama-3.2-11b-vision-preview" if is_vision else "llama-3.3-70b-versatile"
            
            # Préparation des messages
            messages_api = [{"role": "system", "content": "Tu es Charles IA... (Prompt Système de l'utilisateur)"}]
            for msg in st.session_state.messages[-5:]:
                messages_api.append({"role": msg["role"], "content": msg["content"]})

            try:
                status.markdown("🤖 *Charles IA réfléchit...*")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages_api,
                    **config # Application des paramètres
                )
                final_text = response.choices[0].message.content
                status.empty()
                st.markdown(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")
