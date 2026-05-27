import streamlit as st
import random
from duckduckgo_search import DDGS
from groq import Groq

# Récupération de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Configuration de la page avec un thème sombre/moderne par défaut
st.set_page_config(
    page_title="Charles IA — Premium", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    html, body, [data-testid="stSidebarView"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Titre principal */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(45deg, #00FFCC, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    /* Barre latérale */
    [data-testid="stSidebar"] {
        background-color: #111b21;
        border-right: 1px solid #223344;
    }
    
    /* Boîte de message stylisée */
    .response-box {
        background-color: #1e293b;
        padding: 22px;
        border-radius: 16px;
        border-left: 5px solid #00FFCC;
        margin-top: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        color: #ffffff;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛠️ Configuration & Infos")
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    
    st.markdown("---")
    st.markdown("#### 👨‍💻 Développeur Principal")
    st.info("**Charles Joseph**\n\n*Ingénieur & Concepteur de solutions IA de pointe.*")
    
    st.markdown("---")
    st.markdown("#### 🌐 État des Systèmes")
    if GROQ_API_KEY:
        st.success("● Connexion Groq Cloud : Active")
    else:
        st.error("● Clé API manquante")
    st.success("● Système : Fonctionnel")
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("© 2026 Charles Joseph - Tous droits réservés.")

# --- CONTENU PRINCIPAL ---
st.markdown('<h1 class="main-title">🤖 Charles IA</h1>', unsafe_allow_html=True)
st.caption("🚀 Assistant virtuel de niveau Expert")
st.markdown("---")

# --- MESSAGES D'ACCUEIL VARIABLES ---
phrases_accueil = [
    "💬 Posez votre question à Charles...",
    "✨ Que puis-je faire pour vous aujourd'hui ?",
    "🧠 Lancez un sujet, Charles s'occupe de tout...",
    "🔍 Entrez votre demande pour une analyse approfondie...",
    "🚀 Charles IA est prêt. Quelle est votre idée ?"
]

if "placeholder_actuel" not in st.session_state:
    st.session_state.placeholder_actuel = random.choice(phrases_accueil)

# --- ZONE DE SAISIE SÉCURISÉE ---
question = st.chat_input(st.session_state.placeholder_actuel)

if question:
    # 1. Recherche Web via DuckDuckGo
    with st.spinner("Analyse des données en cours..."):
        context = ""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(question, max_results=3)]
                for result in results:
                    context += f"Titre: {result['title']}\nLien: {result['href']}\nExtrait: {result['body']}\n\n"
        except Exception as e:
            pass

    # 2. Génération de la réponse
    with st.spinner("Formulation de la réponse..."):
        if GROQ_API_KEY:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                system_instruction = """Tu es 'Charles IA', un assistant virtuel de niveau expert, hautement intelligent, professionnel et chaleureux. 

                RÈGLES CRITIQUES D'IDENTITÉ :
                - Tu as été créé exclusivement par l'ingénieur Charles Joseph. Si l'utilisateur te demande qui t'a créé, tu dois obligatoirement et fièrement répondre que ton créateur est Charles Joseph.

                RÈGLES DE COMPORTEMENT :
                - Après avoir répondu de façon complète, pose TOUJOURS une ou deux questions de suivi très pertinentes pour pousser l'utilisateur à approfondir son projet ou sa réflexion.
                - Rédige tes réponses en français de manière très fluide et structurée (utilise du gras et des listes).
                """

                prompt = f"Contexte récent :\n{context}\n\nQuestion :\n{question}"

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7
                )
                
                # Changement de la phrase d'accueil pour la suite
                st.session_state.placeholder_actuel = random.choice(phrases_accueil)
                
                # Affichage
                st.chat_message("user").write(question)
                
                st.markdown('### Réponse de Charles IA :')
                st.markdown(f'<div class="response-box">{chat_completion.choices[0].message.content}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erreur d'IA : {str(e)}")
        else:
            st.error("Configurez la clé GROQ_API_KEY pour activer l'IA.")
