import streamlit as st
import random
import urllib.request
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page pour une Web App mobile épurée
st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURATION DE L'IDENTITÉ ---
CREATOR_NAME = "Charles Joseph" # Le seul et unique créateur
AI_DISPLAY_NAME = "Charles IA"

# Configuration des profils visuels
URL_AVATAR_AI = "avatar.jpg"
URL_AVATAR_USER = "user"

# --- FONCTION DE VÉRIFICATION DE LA CONNEXION ---
def verifier_connexion():
    try:
        urllib.request.urlopen('https://www.google.com', timeout=3)
        return True
    except Exception:
        return False

# --- STYLE CSS APPLI MOBILE & AUTOMATISATION DU SCROLL ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #171717 !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        scroll-behavior: smooth;
    }}
    
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0);
        height: 0px;
    }}
    
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 7rem !important;
        max_width: 500px !important;
    }}
    
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        padding: 0.8rem 0.5rem !important;
        border-bottom: 1px solid #2d2d2d;
    }}
    
    [data-testid="stChatMessageAvatar"] {{
        background-color: transparent !important;
        border-radius: 50% !important;
    }}
    
    .message-author {{
        color: #b4b4b4 !important;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }}
    
    .chat-text, [data-testid="stChatMessage"] p {{
        color: #ffffff !important;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-top: 0px;
    }}
    
    /* --- CONFIGURATION DE LA BARRE DE SAISIE --- */
    [data-testid="stChatInput"] {{
        background-color: #2f2f2f !important;
        border-radius: 26px !important;
        border: 1px solid #424242 !important;
        padding: 8px !important;
        padding-right: 90px !important;
    }}
    [data-testid="stChatInput"] input {{
        color: #ffffff !important;
        font-size: 1rem !important;
    }}
    [data-testid="stChatInput"] button {{
        background-color: #ffffff !important;
        border-radius: 50% !important;
    }}

    /* Micro ancré discrètement à l'intérieur */
    .floating-mic-container {{
        position: fixed;
        bottom: 32px;
        left: 50%;
        transform: translateX(145px);
        z-index: 999999;
    }}
    </style>
""", unsafe_allow_html=True)

# --- INJECTION JAVASCRIPT POUR LE DEFILEMENT AUTOMATIQUE ---
st.components.v1.html("""
    <script>
    function scrollToBottom() {
        var mainContainer = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (mainContainer) {
            mainContainer.scrollTop = mainContainer.scrollHeight;
        }
    }
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 300);
    setTimeout(scrollToBottom, 500);
    </script>
""", height=0)

# --- INITIALISATION DE L'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TEXTES D'INVITE ALÉATOIRES ---
phrases_accueil = [
    f"Message {AI_DISPLAY_NAME}...",
    "Comment puis-je t'aider aujourd'hui ?",
    "Pose-moi une question...",
    "Dis-moi ce que tu as en tête..."
]
if "placeholder_actuel" not in st.session_state:
    st.session_state.placeholder_actuel = random.choice(phrases_accueil)

# --- BOUTONS D'EN-TÊTE ---
col_logo, col_clear = st.columns([8.5, 1.5])
with col_clear:
    if st.button("🗑️", help="Nouvelle discussion"):
        st.session_state.messages = []
        st.session_state.placeholder_actuel = random.choice(phrases_accueil)
        st.rerun()

# --- ÉCRAN D'ACCUEIL ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center;">
            <img src="app/static/{URL_AVATAR_AI}" width="90" style="border-radius: 50%; margin-bottom: 1rem; border: 2px solid #424242; object-fit: cover; height: 90px;">
            <div style="font-size: 2.2rem; color: #ffffff; font-weight: bold; margin-bottom: 0.2rem;">{AI_DISPLAY_NAME}</div>
            <p style="color: #8e8e93; font-size: 1rem;">Par {CREATOR_NAME}</p>
        </div>
    """, unsafe_allow_html=True)

# --- RENDU DE LA DISCUSSION ---
for msg in st.session_state.messages:
    author = "You" if msg["role"] == "user" else AI_DISPLAY_NAME
    avatar_img = URL_AVATAR_USER if msg["role"] == "user" else URL_AVATAR_AI
        
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(f'<div class="message-author">{author}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-text">{msg["content"]}</div>', unsafe_allow_html=True)

# --- LE BOUTON MICRO INJECTÉ DANS LA BARRE ---
st.markdown('<div class="floating-mic-container">', unsafe_allow_html=True)
if st.button("🎙️", key="inline_mic", help="Dictée vocale"):
    st.toast("ℹ️ Pour le moment, je ne suis pas disponible à parler.", icon="🎙️")
st.markdown('</div>', unsafe_allow_html=True)

# --- ZONE DE SAISIE EN BAS ---
question = st.chat_input(st.session_state.placeholder_actuel)

if question:
    if not verifier_connexion():
        st.error("⚠️ Connexion réseau instable ou indisponible. Impossible de joindre Charles IA pour le moment. Veuillez réessayer.")
    else:
        # 1. Enregistrement utilisateur
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar=URL_AVATAR_USER):
            st.markdown(f'<div class="message-author">You</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-text">{question}</div>', unsafe_allow_html=True)

        # 2. Recherche discrète
        context = ""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(question, max_results=2)]
                for result in results:
                    context += f"Infos : {result['body']}\n\n"
        except Exception:
            pass

        # 3. Génération IA
        with st.chat_message("assistant", avatar=URL_AVATAR_AI):
            st.markdown(f'<div class="message-author">{AI_DISPLAY_NAME}</div>', unsafe_allow_html=True)
            
            if GROQ_API_KEY:
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    # INSTRUCTIONS NETTOYÉES ET RESTRUCTURÉES
                    system_instruction = f"""Tu es '{AI_DISPLAY_NAME}', un assistant virtuel intelligent et poli de niveau expert. 
                    Tu as été entièrement conçu, programmé et développé par l'ingénieur {CREATOR_NAME}.
                    
                    CONSIGNES STRICTES :
                    1. Tu parles à un utilisateur général. Ne suppose jamais qu'il s'agit de ton créateur. Ne l'appelle pas Charles.
                    2. Si l'interlocuteur te salue (ex: "Salut", "Bonjour", "Jambo"), réponds simplement et chaleureusement en te présentant : "Bonjour ! Je suis {AI_DISPLAY_NAME}, un assistant virtuel. Comment puis-je vous aider aujourd'hui ?".
                    3. Si l'interlocuteur te demande explicitement qui t'a créé, qui t'a programmé, ou qui est ton créateur, donne immédiatement et fièrement toutes les informations : déclare ouvertement que tu as été créé et mis au point par le brillant ingénieur {CREATOR_NAME}.
                    4. Rédige toutes tes réponses en français. Sois clair, fluide, moderne et direct. 
                    5. Termine obligatoirement ta réponse par une ou deux questions de suivi pertinentes pour relancer l'utilisateur.
                    6. Utilise un formatage Markdown propre avec du gras. Pas d'émojis superflus.
                    """

                    prompt = f"Contexte de recherche disponible :\n{context}\n\nQuestion de l'utilisateur anonyme :\n{question}"

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama-3.1-8b-instant",
                        temperature=0.7
                    )
                    
                    reponse = chat_completion.choices[0].message.content
                    
                    st.markdown(f'<div class="chat-text">{reponse}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
                    st.session_state.placeholder_actuel = random.choice(phrases_accueil)
                    st.rerun()
                    
                except Exception as e:
                    st.error("⚠️ Le serveur de l'IA a mis trop de temps à répondre. Cela est dû à une baisse de débit de votre connexion.")
            else:
                st.error("L'application nécessite la clé GROQ_API_KEY.")
