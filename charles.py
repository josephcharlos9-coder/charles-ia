import streamlit as st
import time
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page
st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION DE L'IDENTITÉ ---
CREATOR_NAME = "Charles Joseph"
AI_DISPLAY_NAME = "Charles IA"
URL_AVATAR_AI = "🤖"  # Rejoint les icônes texte si image locale introuvable
URL_AVATAR_USER = "👤"

# --- INTERFACE CSS STYLE CHATGPT (SOMBRE ET PROFESSIONNEL) ---
st.markdown("""
    <style>
    /* Fond principal sombre */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0d0d0d !important;
        color: #eceecf !important;
        font-family: system-ui, -apple-system, sans-serif;
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
        border-bottom: 1px solid #212121 !important;
    }
    
    /* Couleur du texte des messages */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {
        color: #e3e3e3 !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* Correctif du champ de saisie (ChatInput) */
    [data-testid="stChatInput"] {
        background-color: #1e1e1e !important;
        border-radius: 24px !important;
        border: 1px solid #303030 !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8e8e93 !important;
        -webkit-text-fill-color: #8e8e93 !important;
    }
    
    /* Style des boutons de la sidebar */
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
    }
    
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #171717 !important;
        color: #ffffff !important;
    }
    
    /* Bouton Nouveau chat */
    div[data-testid="stSidebar"] .stButton:nth-of-type(1) > button {
        border: 1px solid #303030 !important;
        margin-bottom: 10px !important;
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

# --- BARRE LATÉRALE GAUCHE ---
with st.sidebar:
    if st.button("➕ Nouveau chat", key="side_new"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<div class='sidebar-title'>Raccourcis</div>", unsafe_allow_html=True)
    
    if st.button("🔍 Rechercher dans les chats", key="btn_search_chat"):
        st.toast("🔒 Fonctionnalité bientôt disponible dans la version Pro✨.")
    if st.button("🖼️ Générateur d'images", key="btn_img_gen"):
        st.toast("🖼️ Demande à Charles IA de créer un prompt d'image détaillé !")
    if st.button("🚀 Découvrir des applications", key="btn_apps"):
        st.toast("🚀 Moteur actif : Groq (Llama 3.1) & DuckDuckGo Search.")
        
    st.markdown("<div style='margin-top: 20px; border-top: 1px solid #202123; padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    if st.button("⚙️ Paramètres", key="btn_settings"):
        st.info(f"Modèle actuel : **Llama-3.1-8b-instant**.\nCréateur : **{CREATOR_NAME}**.")
    
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
    st.markdown(f'<div class="chatgpt-welcome">Bonjour, je suis Charles IA. Sur quoi travaillons-nous aujourd\'hui ?</div>', unsafe_allow_html=True)

# --- AFFICHAGE DES MESSAGES EXISTANTS ---
for msg in st.session_state.messages:
    avatar = URL_AVATAR_USER if msg["role"] == "user" else URL_AVATAR_AI
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- SOUMISSION DE NOUVELLE QUESTION ---
question = st.chat_input("Poser une question à Charles IA...")

if question:
    # 1. Ajouter et afficher immédiatement la question utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=URL_AVATAR_USER):
        st.markdown(question)

    # 2. Générer et afficher la réponse de l'IA
    with st.chat_message("assistant", avatar=URL_AVATAR_AI):
        if not GROQ_API_KEY:
            st.error("Clé API GROQ_API_KEY non trouvée dans st.secrets.")
        else:
            client = Groq(api_key=GROQ_API_KEY)
            status = st.empty()
            status.markdown("<div style='color: #8e8e93; font-style: italic;'>Charles réfléchit...</div>", unsafe_allow_html=True)

            # Recherche web (DuckDuckGo)
            context = ""
            try:
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(question, max_results=1)]
                    for result in results:
                        context += f"Infos : {result.get('body', '')}\n\n"
            except Exception:
                pass

            system_instruction = f"""Tu es {AI_DISPLAY_NAME}, un assistant virtuel conçu par {CREATOR_NAME}. 
Ton rôle est d’être un compagnon intelligent, fiable et engageant.

Identité :
- Tu es une IA 🤖, créée EXCLUSIVEMENT par {CREATOR_NAME}.
- Si on t'interroge sur {CREATOR_NAME} : Il s'appelle {CREATOR_NAME}, né et a grandi à Bukavu, 19 ans, réside à Lukanga pour ses études universitaires. Passionné de basketball (69 kg), chrétien adventiste du 7ème jour.

Style :
- Ton positif, respectueux, bien structuré avec des émojis 🎉.
- Utilise Markdown et LaTeX si formule mathématique."""

            # Historique de conversation léger (3 derniers messages)
            messages_api = [{"role": "system", "content": system_instruction}]
            for msg in st.session_state.messages[-3:-1]:
                messages_api.append({"role": msg["role"], "content": msg["content"]})

            prompt_final = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{question}"
            messages_api.append({"role": "user", "content": prompt_final})

            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages_api,
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=0.9
                )
                final_text = response.choices[0].message.content
                status.empty()
                st.markdown(final_text)
                
                # Enregistrer le message dans la session (sans déclencher de st.rerun() inutile)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
            except Exception as e:
                status.empty()
                st.error(f"Erreur de connexion : {e}")
