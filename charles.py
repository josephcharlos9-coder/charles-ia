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
    page_title="Charles IA - Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION DE L'IDENTITÉ ---
CREATOR_NAME = "Charles Joseph"
AI_DISPLAY_NAME = "Charles IA"
URL_AVATAR_AI = "avatar.jpg"
URL_AVATAR_USER = "user"

# --- INTERFACE HTML & CSS MODERNE (HERO + SMARTPHONE) ---
st.markdown("""
  <!-- Google Fonts & Lucide Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>

  <style>
    /* Masquer les éléments natifs Streamlit inutiles pour une intégration fluide */
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); height: 0px; }
    footer { visibility: hidden; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

    :root {
      --bg-gradient: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
      --bg-app: #0d0d0d;
      --card-bg: #171717;
      --text-main: #FFFFFF;
      --text-muted: #8e8e93;
      --border-color: #303030;
      --accent-color: #00D2FF;
      --accent-glow: rgba(0, 210, 255, 0.2);
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4);
      --shadow-md: 0 12px 32px rgba(0, 0, 0, 0.6);
      --radius-lg: 24px;
      --radius-full: 9999px;
    }

    html, body, [data-testid="stAppViewContainer"] {
      background: var(--bg-gradient) !important;
      color: var(--text-main) !important;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Styles pour la bulle de chat personnalisée */
    [data-testid="stChatMessage"] {
      background-color: transparent !important;
      padding: 0.5rem 0rem !important;
      border: none !important;
    }

    [data-testid="stChatMessage"] p {
      color: #e3e3e3 !important;
      font-size: 0.95rem;
      line-height: 1.5;
    }

    /* Style du chat input */
    [data-testid="stChatInput"] {
      background-color: #171717 !important;
      border-radius: 24px !important;
      border: 1px solid #303030 !important;
    }

    [data-testid="stChatInput"] textarea {
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff !important;
    }

    /* Barre latérale sombre */
    [data-testid="stSidebar"] {
      background-color: #000000 !important;
      border-right: 1px solid #202123 !important;
    }

    .sidebar-title {
      color: #666666;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 15px 12px 5px 12px;
    }

    .chatgpt-welcome {
      font-size: 1.8rem;
      font-weight: 600;
      color: #ffffff;
      text-align: center;
      margin-top: 5vh;
      margin-bottom: 2rem;
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
        st.toast("🔒 Cette fonctionnalité sera débloquée dans la version Pro, conçue pour une expérience IA avancée✨.")
    if st.button("🖼️ Générateur d'images", key="btn_img_gen"):
        st.toast("🖼️ Le générateur d’images est prêt : demande à Charles IA de créer ton prompt personnalisé.")
    if st.button("🚀 Découvrir des applications", key="btn_apps"):
        st.toast("🚀 Explorez l’écosystème Pro : Charles IA s’appuie déjà sur Groq Llama 3.3 et DuckDuckGo pour des performances optimisées.")
        
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

# --- EN-TÊTE ET ACCUEIL DE L'INTERFACE ---
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: 20px; margin-bottom: 20px;">
            <span style="font-size: 3rem;">🤖</span>
            <h1 style="font-size: 3.5rem; font-weight: 700; background: linear-gradient(180deg, #FFFFFF 0%, #8e8e93 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">Charles IA</h1>
        </div>
        <div class="chatgpt-welcome">Bonjour ! Sur quoi travaillons-nous ?</div>
    """, unsafe_allow_html=True)

# Case de saisie des questions
question = st.chat_input("Poser une question à Charles IA...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.rerun()

# --- AFFICHAGE DES MESSAGES ---
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
Tu as été créé EXCLUSIVEMENT par {CREATOR_NAME}.
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
                status.empty()
                st.error(f"Erreur : {e}")
