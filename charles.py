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
USER_NAME = "Charles Joseph"
AI_DISPLAY_NAME = "Charles IA"

# --- FONCTION DE VÉRIFICATION DE LA CONNEXION ---
def verifier_connexion():
    """Retourne True si internet fonctionne, False si la connexion est mauvaise ou coupée."""
    try:
        # On tente de charger un site ultra-rapide avec un délai max de 3 secondes
        urllib.request.urlopen('https://www.google.com', timeout=3)
        return True
    except Exception:
        return False

# --- STYLE CSS (INTERFACE CHATGPT MOBILE) ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #171717 !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0);
        height: 0px;
    }}
    
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
        max_width: 500px !important;
    }}
    
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        padding: 0.8rem 0.5rem !important;
        border-bottom: 1px solid #2d2d2d;
        display: block !important;
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
    
    [data-testid="stChatInput"] {{
        background-color: #2f2f2f !important;
        border-radius: 26px !important;
        border: 1px solid #424242 !important;
        padding: 8px !important;
    }}
    [data-testid="stChatInput"] input {{
        color: #ffffff !important;
        font-size: 1rem !important;
    }}
    [data-testid="stChatInput"] button {{
        background-color: #ffffff !important;
        border-radius: 50% !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE L'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VARIATION DES TEXTES D'INVITE ---
phrases_accueil = [
    f"Message {AI_DISPLAY_NAME}...",
    "Comment puis-je t'aider aujourd'hui ?",
    "Pose-moi une question...",
    "Dis-moi ce que tu as en tête..."
]
if "placeholder_actuel" not in st.session_state:
    st.session_state.placeholder_actuel = random.choice(phrases_accueil)

# --- BOUTON POUR EFFACER LE CHAT ---
col_logo, col_clear = st.columns([8, 2])
with col_clear:
    if st.button("🗑️", help="Nouvelle discussion"):
        st.session_state.messages = []
        st.session_state.placeholder_actuel = random.choice(phrases_accueil)
        st.rerun()

# --- ÉCRAN D'ACCUEIL INITIAL ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 65vh; text-align: center;">
            <div style="font-size: 2.2rem; color: #ffffff; font-weight: bold; margin-bottom: 0.2rem;">{AI_DISPLAY_NAME}</div>
            <p style="color: #8e8e93; font-size: 1rem;">Par {USER_NAME}</p>
        </div>
    """, unsafe_allow_html=True)

# --- RENDU DE LA DISCUSSION ---
for msg in st.session_state.messages:
    author = USER_NAME if msg["role"] == "user" else AI_DISPLAY_NAME
    with st.chat_message(msg["role"]):
        st.markdown(f'<div class="message-author">{author}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-text">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ZONE DE SAISIE EN BAS ---
question = st.chat_input(st.session_state.placeholder_actuel)

if question:
    # TEST DE LA CONNEXION AVANT TOUTE CHOSE
    if not verifier_connexion():
        st.error("⚠️ Connexion réseau instable ou indisponible. Impossible de joindre Charles IA pour le moment. Veuillez réessayer.")
    else:
        # 1. Enregistrement et affichage du message de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(f'<div class="message-author">{USER_NAME}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-text">{question}</div>', unsafe_allow_html=True)

        # 2. Collecte de données discrète (Recherche)
        context = ""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(question, max_results=2)]
                for result in results:
                    context += f"Infos : {result['body']}\n\n"
        except Exception:
            pass

        # 3. Génération de la réponse pro par Charles IA
        with st.chat_message("assistant"):
            st.markdown(f'<div class="message-author">{AI_DISPLAY_NAME}</div>', unsafe_allow_html=True)
            
            if GROQ_API_KEY:
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    system_instruction = f"""Tu es '{AI_DISPLAY_NAME}', un assistant virtuel de niveau expert, conçu par l'ingénieur {USER_NAME}.
                    
                    CONSIGNES STRICTES :
                    - Si l'utilisateur te demande qui t'a créé ou qui t'a programmé, réponds fièrement que ton créateur est l'ingénieur Charles Joseph.
                    - Rédige tes réponses en français. Sois clair, fluide, moderne et direct.
                    - À la toute fin de ta réponse, pose TOUJOURS une ou deux questions de suivi intelligentes pour relancer l'utilisateur et approfondir son sujet.
                    - Utilise un formatage Markdown standard (mots clés importants en gras et listes à puces si nécessaire). Pas d'émojis superflus.
                    """

                    prompt = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur ({USER_NAME}) :\n{question}"

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
