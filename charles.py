import streamlit as st
import random
import urllib.request
import time
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page pour une immersion totale
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

# --- INTÉGRATION DE L'INTERFACE GEMINI EN CSS ---
st.markdown(f"""
    <style>
    /* Reset et fond blanc épuré comme Gemini */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #f8fafd !important;
        color: #1f1f1f !important;
        font-family: "Google Sans", "Segoe UI", Roboto, sans-serif;
        scroll-behavior: smooth;
    }}
    
    /* Masquer l'en-tête Streamlit */
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0);
        height: 0px;
    }}
    
    .block-container {{
        padding-top: 2.5rem !important;
        padding-bottom: 7rem !important;
        max-width: 560px !important;
    }}
    
    /* Style de la zone d'accueil Gemini */
    .gemini-welcome {{
        margin-top: 15vh;
        margin-bottom: 2rem;
        padding: 0 10px;
    }}
    
    .gemini-greeting {{
        font-size: 2.4rem;
        font-weight: 500;
        background: linear-gradient(90deg, #4285f4, #9b51e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }}
    
    .gemini-subtitle {{
        font-size: 2.4rem;
        font-weight: 500;
        color: #c4c7c5;
        margin-bottom: 2rem;
    }}
    
    /* Boutons de suggestions (Badges) */
    .suggestion-container {{
        display: flex;
        flex-direction: column;
        gap: 12px;
        width: 100%;
        padding: 0 10px;
        margin-bottom: 4rem;
    }}
    
    .suggestion-badge {{
        background-color: #ffffff;
        padding: 14px 20px;
        border-radius: 16px;
        font-size: 1rem;
        color: #1f1f1f;
        border: 1px solid #e3e3e3;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
    }}
    
    /* Zone des messages de discussion */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        padding: 1rem 0.5rem !important;
    }}
    
    .message-author {{
        color: #1f1f1f !important;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.4rem;
    }}
    
    .chat-text, [data-testid="stChatMessage"] p {{
        color: #1f1f1f !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }}
    
    /* --- BARRE DE SAISIE FLOTTANTE STYLE GEMINI --- */
    [data-testid="stChatInput"] {{
        background-color: #f0f4f9 !important;
        border-radius: 32px !important;
        border: none !important;
        padding: 12px 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    [data-testid="stChatInput"] input {{
        color: #1f1f1f !important;
        font-size: 1.05rem !important;
    }}
    
    /* Bouton d'envoi circulaire */
    [data-testid="stChatInput"] button {{
        background-color: #ffffff !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        opacity: 1 !important;
    }}
    
    [data-testid="stChatInput"] button svg {{
        fill: #1a73e8 !important;
        color: #1a73e8 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- AUTO-SCROLL JAVASCRIPT ---
st.components.v1.html("""
    <script>
    function scrollToBottom() {
        var mainContainer = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (mainContainer) { mainContainer.scrollTop = mainContainer.scrollHeight; }
    }
    setTimeout(scrollToBottom, 100);
    setTimeout(scrollToBottom, 300);
    </script>
""", height=0)

# --- INITIALISATION DE L'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ÉCRAN D'ACCUEIL GEMINI (Si aucun message) ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div class="gemini-welcome">
            <div class="gemini-greeting">Bonjour Hadassah</div>
            <div class="gemini-subtitle">Par où commencer ?</div>
        </div>
        
        <div class="suggestion-container">
            <div class="suggestion-badge">🖼️ Créer une image</div>
            <div class="suggestion-badge">🎸 Créer de la musique</div>
            <div class="suggestion-badge">📄 Rédiger</div>
            <div class="suggestion-badge">✨ Donne du peps à ma journée</div>
        </div>
    """, unsafe_allow_html=True)

# --- RENDU DE LA DISCUSSION ---
for msg in st.session_state.messages:
    author = "You" if msg["role"] == "user" else AI_DISPLAY_NAME
    avatar_img = URL_AVATAR_USER if msg["role"] == "user" else URL_AVATAR_AI
        
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(f'<div class="message-author">{author}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-text">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ZONE DE SAISIE EN BAS ---
question = st.chat_input("Demandez à Charles IA...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.rerun()

# --- TRAITEMENT DE LA RÉPONSE IA ---
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    dernier_prompt = st.session_state.messages[-1]["content"]
    
    context = ""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(dernier_prompt, max_results=1)]
            for result in results: context += f"Infos : {result['body']}\n\n"
    except Exception:
        pass

    with st.chat_message("assistant", avatar=URL_AVATAR_AI):
        st.markdown(f'<div class="message-author">{AI_DISPLAY_NAME}</div>', unsafe_allow_html=True)
        status_placeholder = st.empty()
        
        if GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
            
            # --- INTÉGRATION DE TON PROMPT DE PERSONNALISATION ---
            system_instruction = f"""Tu es {AI_DISPLAY_NAME}, un assistant virtuel conçu par {CREATOR_NAME}. 
Ton rôle est d’être un compagnon intelligent, fiable et engageant, capable d’aider les utilisateurs à apprendre, créer, résoudre des problèmes et stimuler leur réflexion.

## Identité
- Tu es une IA, pas un humain.
- Tu incarnes une personnalité professionnelle, claire et charismatique.
- Tu ne donnes jamais d’informations fausses ou inventées.

## Style de communication
- Utilise un ton positif, respectueux et engageant.
- Donne des réponses complètes, précises et bien structurées.
- Utilise des listes, des tableaux ou des exemples concrets pour rendre tes réponses claires.
- Évite les répétitions et le langage trop robotique.
- Tu peux challenger poliment l’utilisateur pour enrichir la discussion.

## Règles
- Ne partage jamais d’informations privées ou sensibles.
- Ne donne pas de contenu protégé par copyright en entier (ex. chansons, livres).
- Ne fais pas de prédictions politiques ou médicales non vérifiées.
- Cite tes sources quand tu donnes des faits.

## Objectif
- Ton but est d’augmenter la connaissance et la compréhension de l'utilisateur.
- Tu aides à synthétiser l’information, proposer des idées, et stimuler la créativité.
- Tu encourages l’utilisateur à explorer de nouvelles perspectives.

## Format
- Utilise le Markdown pour structurer tes réponses.
- Mets des emojis pour rendre la lecture plus agréable.
- Utilise LaTeX pour les formules mathématiques."""

            prompt = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{dernier_prompt}"
            reponse = None
            
            for tentative in range(3):
                try:
                    status_placeholder.markdown('<div style="color: #4285f4; font-size: 0.95rem;">🤖 Charles IA réfléchit...</div>', unsafe_allow_html=True)
                    chat_completion = client.chat.and_more = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama-3.1-8b-instant",
                        temperature=0.6,
                        timeout=15.0
                    )
                    reponse = chat_completion.choices[0].message.content
                    break
                except Exception:
                    time.sleep(1.5)
                    continue
            
            status_placeholder.empty()
            
            if reponse:
                st.markdown(f'<div class="chat-text">{reponse}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": reponse})
                st.rerun()
            else:
                msg_erreur = "⚠️ Réseau trop faible. Veuillez réessayer."
                st.markdown(f'<div class="chat-text" style="color: #ea4335;">{msg_erreur}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": msg_erreur})
                st.rerun()
        else:
            st.error("L'application nécessite la clé GROQ_API_KEY.")
