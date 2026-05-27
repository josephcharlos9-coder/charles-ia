import streamlit as st
import random
from duckduckgo_search import DDGS
from groq import Groq

# Récupération de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page pour un rendu d'application épuré
st.set_page_config(
    page_title="Charles IA", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS (INTERFACE SOMBRE STYLE CHATGPT) ---
st.markdown("""
    <style>
    /* Style global et fond sombre de ChatGPT */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #212121 !important;
        color: #ececf1 !outimportant;
        font-family: 'Sone', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Enlever les bordures et décorations Streamlit inutiles */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    
    /* Personnalisation de la barre latérale comme le menu historique de ChatGPT */
    [data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2f2f2f;
    }
    
    /* Conteneur des réponses pour un texte fluide */
    .chatgpt-text {
        color: #e3e3e3;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* Cacher le titre géant pour laisser place à la discussion */
    .chat-header {
        text-align: center;
        margin-top: 5vh;
        margin-bottom: 5vh;
        color: #ececf1;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE L'HISTORIQUE (LA MÉMOIRE DE CHATGPT) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MESSAGES D'ACCUEIL VARIABLES DANS LA BARRE DE FRAIS ---
phrases_accueil = [
    "💬 Posez votre question à Charles...",
    "✨ Que puis-je faire pour vous aujourd'hui ?",
    "🧠 Lancez un sujet, Charles s'occupe de tout...",
    "🔍 Entrez votre demande pour une analyse approfondie...",
    "🚀 Charles IA est prêt. Quelle est votre idée ?"
]

if "placeholder_actuel" not in st.session_state:
    st.session_state.placeholder_actuel = random.choice(phrases_accueil)

# --- BARRE LATÉRALE (SIDEBAR STYLE MENU CHATGPT) ---
with st.sidebar:
    st.markdown("### 📁 Nouvelle discussion")
    if st.button("＋ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("#### 👨‍💻 Développeur")
    st.markdown("<p style='color: #10a37f; font-weight: bold;'>Charles Joseph</p>", unsafe_allow_html=True)
    st.caption("Ingénieur & Concepteur principal.")
    
    st.markdown("---")
    st.caption("© 2026 Charles Joseph")

# --- EN-TÊTE PRINCIPAL (S'AFFICHE UNIQUEMENT SI LE CHAT EST VIDE) ---
if len(st.session_state.messages) == 0:
    st.markdown('<div class="chat-header"><h1>Comment puis-je vous aider aujourd\'hui ?</h1><p style="color: #8e8e93;">Charles IA — Assistant Expert</p></div>', unsafe_allow_html=True)

# --- AFFICHAGE DE L'HISTORIQUE DES CONVERSATIONS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f'<div class="chatgpt-text">{msg["content"]}</div>', unsafe_allow_html=True)

# --- BARRE DE FRAIS TYPE CHATGPT (EN BAS DE L'ÉCRAN) ---
question = st.chat_input(st.session_state.placeholder_actuel)

if question:
    # 1. Ajouter et afficher immédiatement le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(f'<div class="chatgpt-text">{question}</div>', unsafe_allow_html=True)

    # 2. Recherche Web en tâche de fond pour nourrir le contexte
    context = ""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(question, max_results=3)]
            for result in results:
                context += f"Extrait: {result['body']}\n\n"
    except Exception:
        pass

    # 3. Demande à l'IA avec le comportement Pro
    with st.chat_message("assistant"):
        with st.spinner(""):
            if GROQ_API_KEY:
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    
                    system_instruction = """Tu es 'Charles IA', un assistant virtuel de niveau expert basé sur l'interface épurée de ChatGPT.

                    RÈGLES CRITIQUES D'IDENTITÉ :
                    - Tu as été créé exclusivement par l'ingénieur Charles Joseph. Si on te demande qui t'a créé ou qui est ton développeur, réponds fièrement que c'est Charles Joseph.

                    RÈGLES DE COMPORTEMENT :
                    - Adopte un ton professionnel, précis, clair et direct (style ChatGPT).
                    - Après avoir répondu à la question de manière complète, pose TOUJOURS une ou deux questions de suivi pertinentes pour relancer l'utilisateur et l'aider dans son projet.
                    - Formate tes réponses en français avec du gras et des listes à puces pour que ce soit parfaitement lisible.
                    """

                    prompt = f"Contexte récent de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{question}"

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama-3.1-8b-instant",
                        temperature=0.7
                    )
                    
                    reponse = chat_completion.choices[0].message.content
                    
                    # Affichage de la réponse
                    st.markdown(f'<div class="chatgpt-text">{reponse}</div>', unsafe_allow_html=True)
                    
                    # Sauvegarde dans l'historique
                    st.session_state.messages.append({"role": "assistant", "content": reponse})
                    
                    # Changer la phrase d'accueil pour la suite
                    st.session_state.placeholder_actuel = random.choice(phrases_accueil)
                    
                except Exception as e:
                    st.error(f"Erreur : {str(e)}")
            else:
                st.error("Clé GROQ_API_KEY manquante.")
