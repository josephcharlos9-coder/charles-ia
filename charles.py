import streamlit as st
import random
from duckduckgo_search import DDGS
from groq import Groq

# Récupération de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page optimisée pour l'affichage mobile
st.set_page_config(
    page_title="ChatGPT", 
    page_icon="🤖", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- STYLE CSS APPLI MOBILE CHATGPT CORRIGÉ (TEXTE BLANC PUR) ---
st.markdown("""
    <style>
    /* Fond noir/anthracite officiel de ChatGPT mobile */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #1d1d1d !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Enlever les espaces blancs inutiles en haut sur téléphone */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
        height: 0px;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* Style des bulles de texte */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0.8rem 0.5rem !important;
        border-bottom: 1px solid #2d2d2d;
    }

    /* TEXTE DE RÉPONSE BLANC ET TRÈS LUMINEUX */
    .chatgpt-text, [data-testid="stChatMessage"] p, [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-size: 1.05rem;
        line-height: 1.5;
        font-weight: 400;
        text-shadow: 0 0 1px rgba(255,255,255,0.1); /* Donne un aspect encore plus net et blanc */
    }

    /* Écran d'accueil centralisé style appli */
    .mobile-welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 25vh;
        color: #b4b4b4;
    }
    
    .mobile-welcome h1 {
        font-size: 2rem;
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Personnalisation de la barre de frappe fixe en bas */
    [data-testid="stChatInput"] {
        background-color: #2f2f2f !important;
        border-radius: 24px !important;
        border: 1px solid #424242 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MÉMOIRE SANS COMPTE (STOCKAGE SESSION) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VARIATION DES PHRASES D'ACCUEIL ---
phrases_accueil = [
    "Message Charles IA...",
    "Comment puis-je t'aider aujourd'hui ?",
    "Pose-moi une question...",
    "Dis-moi ce que tu as en tête...",
    "Besoin d'idées ? Demande à Charles..."
]

if "placeholder_actuel" not in st.session_state:
    st.session_state.placeholder_actuel = random.choice(phrases_accueil)

# --- LOGO MENU EN HAUT (STYLE APPLI MOBILE) ---
col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🗑️", help="Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()

# --- ÉCRAN D'ACCUEIL MOBILE (SI AUCUN MESSAGE) ---
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="mobile-welcome">
            <h1>Charles IA</h1>
            <p>Posez vos questions librement, sans compte.</p>
        </div>
    """, unsafe_allow_html=True)

# --- AFFICHAGE DE L'HISTORIQUE DE CONVERSATION DÉROULANT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f'<div class="chatgpt-text">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ZONE DE FRAIS TECHNIQUE CHATGPT EN BAS ---
question = st.chat_input(st.session_state.placeholder_actuel)

if question:
    # 1. Enregistrement immédiat du message utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(f'<div class="chatgpt-text">{question}</div>', unsafe_allow_html=True)

    # 2. Recherche discrète en arrière-plan
    context = ""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(question, max_results=2)]
            for result in results:
                context += f"Extrait: {result['body']}\n\n"
    except Exception:
        pass

    # 3. Génération de la réponse d'expert par Charles IA
    with st.chat_message("assistant"):
        if GROQ_API_KEY:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                system_instruction = """Tu es 'Charles IA', un assistant virtuel de niveau expert, intégré dans une interface mobile épurée identique à ChatGPT.

                RÈGLES D'IDENTITÉ :
                - Tu as été créé à 100% par l'ingénieur Charles Joseph. Reste fidèle à ce créateur si on te pose la question.

                RÈGLES DE RÉPONSE :
                - Sois direct, intelligent et moderne dans tes explications.
                - Termine TOUJOYRS par une question ouverte ou une relance professionnelle pour poursuivre la discussion.
                - Utilise un formatage Markdown propre (listes, mots importants en gras).
                """

                prompt = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{question}"

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7
                )
                
                reponse = chat_completion.choices[0].message.content
                
                # Affichage direct de la réponse
                st.markdown(f'<div class="chatgpt-text">{reponse}</div>', unsafe_allow_html=True)
                
                # Enregistrement dans la mémoire
                st.session_state.messages.append({"role": "assistant", "content": reponse})
                
                st.session_state.placeholder_actuel = random.choice(phrases_accueil)
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
        else:
            st.error("Clé de connexion manquante.")
