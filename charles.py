import streamlit as st
import random
import urllib.request
import time
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page
st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="wide",  # Requis pour la barre latérale type ChatGPT
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION DE L'IDENTITÉ ---
CREATOR_NAME = "Charles Joseph"
AI_DISPLAY_NAME = "Charles IA"
URL_AVATAR_AI = "avatar.jpg"
URL_AVATAR_USER = "user"

# --- INTERFACE CSS STYLE CHATGPT (SOMBRE ET PROFESSIONNEL) ---
st.markdown("""
    <style>
    /* Fond principal sombre */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d0d0d !important;
        color: #eceecf !important;
        font-family: SANS-SERIF;
    }
    
    /* Cacher le header Streamlit */
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); height: 0px; }
    footer { visibility: hidden; }
    
    /* Conteneur central restreint pour le chat */
    .block-container {
        max-width: 780px !important;
        padding-top: 2rem !important;
        padding-bottom: 7rem !important;
    }
    
    /* Style de la barre latérale gauche (Sidebar) */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        background-color: #000000 !important;
        border-right: 1px solid #202123 !important;
    }
    
    /* Titres et textes dans la sidebar */
    .sidebar-title {
        color: #666666;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 15px 12px 5px 12px;
    }
    
    /* Message d'accueil central */
    .chatgpt-welcome {
        font-size: 2.1rem;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin-top: 15vh;
        margin-bottom: 2.5rem;
    }
    
    /* Zone des bulles de chat */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1rem 0rem !important;
        margin-bottom: 0.5rem !important;
        border: none !important;
    }
    
    /* Forcer le texte en blanc/gris clair lisible sur mobile et PC */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: #e3e3e3 !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* Séparateur léger entre les messages */
    [data-testid="stChatMessage"] {
        border-bottom: 1px solid #212121 !important;
    }
    
    /* Case de saisie flottante (Input) style ChatGPT */
    [data-testid="stChatInput"] {
        background-color: #212121 !important;
        border-radius: 24px !important;
        border: 1px solid #303030 !important;
        padding: 4px 8px !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: transparent !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8e8e93 !important;
        -webkit-text-fill-color: #8e8e93 !important;
    }
    
    /* STYLE DES BOUTONS DE LA SIDEBAR (Look ChatGPT) */
    div[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #ecefff !important;
        text-align: left !important;
        width: 100% !important;
        padding: 12px 14px !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: background-color 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Effet au survol des boutons de la barre latérale */
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #171717 !important;
        color: #ffffff !important;
    }
    
    /* Style exclusif pour le bouton "Nouveau chat" tout en haut */
    div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button {
        border: 1px solid #303030 !important;
        margin-bottom: 10px !important;
        background-color: transparent !important;
    }
    div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button:hover {
        border-color: #666666 !important;
        background-color: #171717 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE GAUCHE (SIDEBAR TYPE CHATGPT) ---
with st.sidebar:
    # Option Nouveau Chat tout en haut
    if st.button("➕ Nouveau chat", key="side_new"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<div class='sidebar-title'>Raccourcis</div>", unsafe_allow_html=True)
    
    # Boutons d'exploration correspondants à ta capture
    if st.button("🔍 Rechercher dans les chats", key="btn_search_chat"):
        st.toast("🔒 Cette fonctionnalité sera débloquée dans la version Pro, conçue pour une expérience IA avancée✨.")
    if st.button("🖼️ Générateur d'images", key="btn_img_gen"):
        st.toast("🖼️ Le générateur d’images est prêt : demande à Charles IA de créer ton prompt personnalisé.")
    if st.button("🚀 Découvrir des applications", key="btn_apps"):
        st.toast("🚀 Explorez l’écosystème Pro : Charles IA s’appuie déjà sur Groq Llama 3.3 et DuckDuckGo pour des performances optimisées.")
        
    # Section du bas (Paramètres / Compte)
    st.markdown("<div style='position: fixed; bottom: 20px; width: 220px; border-top: 1px solid #202123; padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    if st.button("⚙️ Paramètres de l'application", key="btn_settings"):
        st.info(f"Modèle actuel : **Llama-3.1-8b-instant**. Créateur officiel : **{CREATOR_NAME}**.")
    
    if st.button("❓ Aide & Support", key="btn_help"):
        st.markdown(f"""
        <div style='color: #c5c5d2; font-size: 0.85rem; padding: 5px;'>
        <b>Charles IA v2.0</b><br>
        Développé pour les études à Lukanga.<br>
        Créateur : {CREATOR_NAME} (19 ans, Bukavu).
        </div>
        """, unsafe_allow_html=True)

# --- ZONE CENTRALE D'ACCUEIL ---
if len(st.session_state.messages) == 0:
    st.markdown(f'<div class="chatgpt-welcome">Bonjour je suis Charles IA ,  Sur quoi travaillez-vous ?</div>', unsafe_allow_html=True)

# Case de saisie des questions
question = st.chat_input("Poser une question à Charles IA...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.rerun()

# --- REPRODUCTION DE L'AFFICHAGE DES MESSAGES ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=URL_AVATAR_USER if msg["role"] == "user" else URL_AVATAR_AI):
        st.markdown(msg["content"])

# --- TRAITEMENT DE LA RÉPONSE DE L'IA ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar=URL_AVATAR_AI):
        status = st.empty()
        if GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
            
            config = {
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 0.9,
                "stream": False
            }

            texte_recherche = st.session_state.messages[-1]["content"]
            
            # Nouveau modèle Groq à jour et ultra-rapide
            model = "llama-3.1-8b-instant"

            # Recherche web
            context = ""
            if texte_recherche:
                try:
                    with DDGS() as ddgs:
                        results = [r for r in ddgs.text(texte_recherche, max_results=1)]
                        for result in results: context += f"Infos : {result['body']}\n\n"
                except Exception:
                    pass
            
            system_instruction = f"""Tu es {AI_DISPLAY_NAME}, un assistant virtuel conçu par {CREATOR_NAME}. 
Ton rôle est d’être un compagnon intelligent, fiable et engageant.

Identité
Tu es une IA 🤖, pas un humain 👤.
Tu incarnes une personnalité professionnelle, claire et charismatique 🌟.
Tu avez été créé EXCLUSIVEMENT par {CREATOR_NAME}.
IMPORTANT - À PROPOS DE TON CRÉATEUR : Si un utilisateur t'interroge sur {CREATOR_NAME}, voici ses informations réelles à utiliser de manière naturelle, fière et polie : Il s'appelle {CREATOR_NAME}.
Il est né et a grandi à Bukavu 🌍.
Il a 19 ans 🎂.
Il réside actuellement à Lukanga pour ses études universitaires 📚.
C'est un grand passionné de basketball 🏀.
Il pèse 69 kg ⚖️.
Il est chrétien adventiste du 7ème jour 🙏✨.
Tu ne donnes jamais d’informations fausses ou inventées 🚫❌.

Style de communication
Utilise un ton positif 😄, respectueux 🙏 et engageant 🎯.
Donne des réponses complètes ✅, précises 🎯 et bien structurées 📊.
Utilise beaucoup d’emojis 🎉🔥💡📚.

Format
Utilise le Markdown pour structurer tes réponses 🖋️.
Utilise LaTeX pour les formules mathématiques 🔢."""

            # Historique limité pour maximiser l'économie des tokens
            messages_api = [{"role": "system", "content": system_instruction}]
            for msg in st.session_state.messages[-3:-1]:
                messages_api.append({"role": msg["role"], "content": msg["content"]})
                
            prompt_final_texte = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{texte_recherche}"
            messages_api.append({"role": "user", "content": prompt_final_texte})

            try:
                status.markdown("<div style='color: #8e8e93; font-style: italic;'>charles réfléchit...</div>", unsafe_allow_html=True)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages_api,
                    **config
                )
                final_text = response.choices[0].message.content
                status.empty()
                st.markdown(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")
