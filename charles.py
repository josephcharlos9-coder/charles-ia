import streamlit as st
import random
import urllib.request
import time
import base64
from PIL import Image
import io
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

# --- FONCTION POUR ENCODER L'IMAGE ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- STYLE CSS (INTERFACE GEMINI) ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #f8fafd !important;
        color: #1f1f1f !important;
        font-family: "Google Sans", sans-serif;
    }}
    [data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); height: 0px; }}
    .gemini-greeting {{
        font-size: 2.3rem; font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .stButton > button {{
        background-color: #ffffff !important; border-radius: 16px !important;
        border: 1px solid #e3e3e3 !important; width: 100% !important; text-align: left !important;
    }}
    [data-testid="stChatInput"] {{ background-color: #f0f4f9 !important; border-radius: 32px !important; border: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- BARRE LATÉRALE POUR LES PHOTOS ---
with st.sidebar:
    st.title("📷 Options Image")
    uploaded_file = st.file_uploader("Ajouter ou capturer une photo", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Image prête à l'envoi", use_container_width=True)

# --- INITIALISATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ÉCRAN D'ACCUEIL ---
if len(st.session_state.messages) == 0:
    st.markdown(f'<div style="margin-top:12vh;"><div class="gemini-greeting">Bonjour, je suis {AI_DISPLAY_NAME}</div><div style="font-size:2.3rem; color:#c4c7c5; font-weight:500;">Par où commencer ?</div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🖼️ Analyser une photo"):
            st.info("Utilisez le menu à gauche (flèche en haut à gauche) pour envoyer votre photo !")
    with col2:
        if st.button("📄 Rédiger un texte"):
            st.session_state.messages.append({"role": "user", "content": "Aide-moi à rédiger un texte bien structuré."})
            st.rerun()

# --- ZONE DE SAISIE ---
question = st.chat_input("Demandez à Charles IA ou commentez la photo...")

if question or (uploaded_file and st.button("Envoyer la photo 🚀")):
    user_content = []
    if question:
        user_content.append({"type": "text", "text": question})
    if uploaded_file:
        base64_image = encode_image(uploaded_file)
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
    
    st.session_state.messages.append({"role": "user", "content": user_content if uploaded_file else question})
    st.rerun()

# --- RENDU DE LA DISCUSSION ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=URL_AVATAR_USER if msg["role"]=="user" else URL_AVATAR_AI):
        if isinstance(msg["content"], list):
            for item in msg["content"]:
                if item["type"] == "text": st.write(item["text"])
                if item["type"] == "image_url": st.image(uploaded_file, width=300)
        else:
            st.write(msg["content"])

# --- RÉPONSE IA ---
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar=URL_AVATAR_AI):
        status = st.empty()
        if GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
            
            # Si c'est une image, on utilise le modèle VISION
            model_to_use = "llama-3.2-11b-vision-preview" if uploaded_file else "llama-3.1-8b-instant"
            
            try:
                status.markdown(f"🤖 {AI_DISPLAY_NAME} analyse...")
                
                # Préparation du message pour Groq
                messages_api = [{"role": "system", "content": f"Tu es {AI_DISPLAY_NAME}, créé par {CREATOR_NAME}. Analyse les textes et les images avec précision."}]
                
                # Historique simplifié pour la vision
                for m in st.session_state.messages[-3:]: # Garde les 3 derniers pour le contexte
                    messages_api.append(m)

                completion = client.chat.completions.create(
                    model=model_to_use,
                    messages=messages_api,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                reponse = completion.choices[0].message.content
                status.empty()
                st.write(reponse)
                st.session_state.messages.append({"role": "assistant", "content": reponse})
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
