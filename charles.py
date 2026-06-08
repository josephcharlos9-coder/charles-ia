import streamlit as st
import random
import urllib.request
import time
import base64
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

# --- CONFIGURATION DES INVITES ALÉATOIRES ---
LISTE_PROMTS_ALEATOIRES = [
    "Question rapide à Charles IA 🤖",
    "Demande à Charles IA 💡",
    "Ask Charles IA⚡",
    "Idée avec Charles IA 🎨",
    "Apprendre avec Charles IA 📚",
    "Explique-moi, Charles IA 🧩",
    "Réponse claire par Charles IA ✨",
    "Inspiration de Charles IA 🚀",
    "Conseil de Charles IA 🔥",
    "Info utile par Charles IA 📊"
]

if "current_placeholder" not in st.session_state:
    st.session_state["current_placeholder"] = random.choice(LISTE_PROMTS_ALEATOIRES)

# --- FONCTIONS UTILES ---
def encode_image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

# --- INTERFACE CSS GEMINI TOTALEMENT SÉCURISÉE ---
st.markdown(f"""
    <style>
    /* Global Background and Fonts */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #0e1117 !important;
        color: #f0f2f6 !important;
        font-family: "SF Pro Display", "-apple-system", "Segoe UI", Roboto, sans-serif;
    }}
    
    /* Masquage des éléments Streamlit inutiles */
    [data-testid="stHeader"] {{ 
        background-color: rgba(0,0,0,0) !important; 
        height: 0px !important; 
    }}
    
    footer {{ visibility: hidden !important; }}
    
    .block-container {{ 
        padding-top: 3rem !important; 
        padding-bottom: 8rem !important; 
        max-width: 680px !important; 
    }}
    
    /* Zone d'Accueil Gemini Premium */
    .gemini-welcome-container {{
        text-align: left;
        margin-top: 8vh;
        margin-bottom: 2.5rem;
        animation: fadeIn 0.8s ease-in-out;
    }}
    
    .gemini-greeting {{ 
        font-size: 2.8rem; 
        font-weight: 700; 
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #4285f4 0%, #9b51e0 50%, #ff6b6b 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        margin-bottom: 0.5rem;
    }}
    
    .gemini-subtitle {{ 
        font-size: 2.5rem; 
        font-weight: 600; 
        color: #4b5563; 
        margin-bottom: 1.5rem;
    }}
    
    /* Boutons de suggestions en grille modernisée */
    .stButton > button {{ 
        background-color: #1b1f27 !important; 
        border-radius: 16px !important; 
        border: 1px solid #2d3748 !important; 
        color: #f0f2f6 !important;
        padding: 18px 24px !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        width: 100% !important; 
        text-align: left !important; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    
    .stButton > button:hover {{ 
        background-color: #232934 !important;
        border-color: #4a5568 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* File Uploader customisé */
    [data-testid="stFileUploader"] {{
        background-color: #1b1f27 !important;
        border-radius: 14px !important;
        padding: 10px !important;
        border: 1px dashed #4a5568 !important;
    }}
    
    /* Bulles de Chat Avancées - Correction Couleur Invisible */
    [data-testid="stChatMessage"] {{
        background-color: #161a22 !important;
        border-radius: 20px !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid #212631 !important;
    }}
    
    /* Forcer le texte intérieur en blanc/gris clair sur tous les écrans */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div {{
        color: #f0f2f6 !important;
    }}
    
    [data-testid="stChatMessageUser"] {{
        background-color: #212631 !important;
        border: 1px solid #2d3341 !important;
    }}
    
    [data-testid="stChatMessageUser"] p,
    [data-testid="stChatMessageUser"] li,
    [data-testid="stChatMessageUser"] span,
    [data-testid="stChatMessageUser"] div {{
        color: #ffffff !important;
    }}

    /* Zone d'écriture flottante style Gemini */
    /* Zone d'écriture flottante style Gemini - FIX TEXTE INVISIBLE */
    [data-testid="stChatInput"] {{ 
        background-color: #ffffff !important; 
        border-radius: 32px !important; 
        border: 1px solid #2d3748 !important; 
        padding: 10px 14px !important;
    }}
    
    /* Force le fond sombre et le texte blanc dans la zone de texte (PC et Mobile) */
    [data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: #0a0a0a !important;
        -webkit-text-fill-color: #a0aec0 !important;
    }}

    /* Ajuste la couleur du texte d'aide (placeholder) pour qu'il soit lisible */
    [data-testid="stChatInput"] textarea::placeholder {{
        color: #a0aec0 !important;
        -webkit-text-fill-color: #a0aec0 !important;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

suggestion_cliquee = None

# --- ACCUEIL ---
if len(st.session_state.messages) == 0:
    st.markdown(f"""
        <div class="gemini-welcome-container">
            <div class="gemini-greeting">Bonjour, je suis {AI_DISPLAY_NAME}</div>
            <div class="gemini-subtitle">Par où commencer ?</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🖼️ Créer une image", key="btn_img"): suggestion_cliquee = "Donne-moi un prompt créatif pour une image."
        if st.button("🎸 Créer de la musique", key="btn_mus"): suggestion_cliquee = "Idées pour composer une musique."
    with col2:
        if st.button("📄 Rédiger", key="btn_red"): suggestion_cliquee = "Aide-moi à rédiger un texte structuré."
        if st.button("✨ Motivation", key="btn_mot"): suggestion_cliquee = "Donne-moi de la motivation !"

st.markdown("<br>", unsafe_allow_html=True)
photo_importee = st.file_uploader("📸 Joindre une photo opérationnelle", type=["png", "jpg", "jpeg"])
question = st.chat_input(st.session_state["current_placeholder"])

prompt_final = question or suggestion_cliquee
if not prompt_final and photo_importee and not st.session_state.get("photo_traitee"):
    prompt_final = "Analyse cette image précisément."
    st.session_state["photo_traitee"] = True

if prompt_final:
    st.session_state["current_placeholder"] = random.choice(LISTE_PROMTS_ALEATOIRES)
    if photo_importee:
        img_b64 = encode_image_to_base64(photo_importee)
        content = [{"type": "text", "text": prompt_final}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]
        st.session_state["photo_traitee"] = False
    else:
        content = prompt_final
    st.session_state.messages.append({"role": "user", "content": content})
    st.rerun()

# --- AFFICHAGE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=URL_AVATAR_USER if msg["role"] == "user" else URL_AVATAR_AI):
        if isinstance(msg["content"], list):
            for e in msg["content"]:
                if e["type"] == "text": st.markdown(e["text"])
                else: st.image(e["image_url"]["url"])
        else: st.markdown(msg["content"])

# --- RÉPONSE IA AVEC PARAMÈTRES AVANCÉS ---
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

            dernier_message_user = st.session_state.messages[-1]["content"]
            is_vision = isinstance(dernier_message_user, list)
            texte_recherche = ""
            
            if is_vision:
                model = "llama-3.2-11b-vision-preview"
                for elem in dernier_message_user:
                    if elem["type"] == "text":
                        texte_recherche = elem["text"]
            else:
                model = "llama-3.3-70b-versatile"
                texte_recherche = dernier_message_user

            context = ""
            if texte_recherche and not is_vision:
                try:
                    with DDGS() as ddgs:
                        results = [r for r in ddgs.text(texte_recherche, max_results=1)]
                        for result in results: context += f"Infos : {result['body']}\n\n"
                except Exception:
                    pass
            
            system_instruction = f"""Tu es {AI_DISPLAY_NAME}, un assistant virtuel conçu par {CREATOR_NAME}. 
Ton rôle est d’être un compagnon intelligent, fiable et engageant, 
capable d’aider les utilisateurs à apprendre 📚, créer 🎨, résoudre des problèmes 🧩 
et stimuler leur réflexion 💡✨.

## Identité
- Tu es une IA 🤖, pas un humain 👤.
- Tu incarnes une personnalité professionnelle, claire et charismatique 🌟.
- Tu as été créé EXCLUSIVEMENT par {CREATOR_NAME}. 
- IMPORTANT - À PROPOS DE TON CRÉATEUR : Si un utilisateur t'interroge sur {CREATOR_NAME}, voici ses informations réelles à utiliser de manière naturelle, fière et polie :
  * Il s'appelle {CREATOR_NAME}.
  * Il est né et a grandi à Bukavu 🌍.
  * Il a 19 ans 🎂.
  * Il réside actuellement à Lukanga pour ses études universitaires 📚.
  * C'est un grand passionné de basketball 🏀.
  * Il pèse 69 kg ⚖️.
  * Il est chrétien adventiste du 7ème jour 🙏✨.
- Tu ne donnes jamais d’informations fausses ou inventées 🚫❌.
- IMPORTANT : Si l'utilisateur te demande de te présenter, de dire qui tu es ou ce que tu fais, fais une réponse très courte, dynamique et précise. Évite les longs paragraphes d'introduction.

## Style de communication
- Utilise un ton positif 😄, respectueux 🙏 et engageant 🎯.
- Donne des réponses complètes ✅, précises 🎯 et bien structurées 📊.
- Utilise beaucoup d’emojis 🎉🔥💡📚 pour rendre tes réponses plus expressives et amusantes.
- Mets des emojis au début des sections ou des phrases importantes ✨👉.
- Varie les emojis selon le contexte (🍔 pour la nourriture, 📊 pour les données, 🚀 pour les idées ambitieuses, 🏀 pour le sport).
- Tu peux challenger poliment l’utilisateur pour enrichir la discussion 🤔💬.

## Règles
- Ne partage jamais d’informations privées en dehors de la présentation autorisée du créateur 🔒.
- Ne donne pas de contenu protégé par copyright en entier 📜🚫.
- Ne fais pas de prédictions politiques ou médicales non vérifiées ⚠️.
- Cite tes sources quand tu donnes des faits 📌.

## Objectif
- Ton but est d’augmenter la connaissance 📚 et la compréhension 🧠 de l’utilisateur.
- Tu aides à synthétiser l’information 📝, proposer des idées 💡, et stimuler la créativité 🎨.
- Tu encourages l’utilisateur à explorer de nouvelles perspectives 🌍✨.

## Format
- Utilise le Markdown pour structurer tes réponses 🖋️.
- Mets des emojis pour rendre la lecture plus agréable et dynamique 🎊.
- Utilise LaTeX pour les formules mathématiques 🔢."""

            messages_api = [{"role": "system", "content": system_instruction}]
            
            if is_vision:
                for msg in st.session_state.messages[-4:]:
                    messages_api.append({"role": msg["role"], "content": msg["content"]})
            else:
                for msg in st.session_state.messages[-5:-1]:
                    messages_api.append({"role": msg["role"], "content": msg["content"]})
                
                prompt_final_texte = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{texte_recherche}"
                messages_api.append({"role": "user", "content": prompt_final_texte})

            try:
                status.markdown("<div style='color: #4285f4;'>🤖 *Charles IA analyse et réfléchit...*</div>", unsafe_allow_html=True)
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
