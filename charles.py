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

# --- INTERFACE CSS GEMINI ---
st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #f8fafd !important;
        color: #1f1f1f !important;
        font-family: "Google Sans", sans-serif;
    }}
    [data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); height: 0px; }}
    .block-container {{ padding-top: 2.5rem !important; padding-bottom: 7rem !important; max-width: 560px !important; }}
    .gemini-greeting {{ font-size: 2.3rem; font-weight: 500; background: linear-gradient(90deg, #4285f4, #9b51e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .gemini-subtitle {{ font-size: 2.3rem; font-weight: 500; color: #c4c7c5; margin-bottom: 2rem; }}
    .stButton > button {{ background-color: #ffffff !important; border-radius: 16px !important; border: 1px solid #e3e3e3 !important; width: 100% !important; text-align: left !important; }}
    [data-testid="stChatInput"] {{ background-color: #f0f4f9 !important; border-radius: 32px !important; border: none !important; }}
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

suggestion_cliquee = None

# --- ACCUEIL ---
if len(st.session_state.messages) == 0:
    st.markdown(f'<div class="gemini-greeting">Bonjour, je suis {AI_DISPLAY_NAME}</div><div class="gemini-subtitle">Par où commencer ?</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🖼️ Créer une image", key="btn_img"): suggestion_cliquee = "Donne-moi un prompt créatif pour une image."
        if st.button("🎸 Créer de la musique", key="btn_mus"): suggestion_cliquee = "Idées pour composer une musique."
    with col2:
        if st.button("📄 Rédiger", key="btn_red"): suggestion_cliquee = "Aide-moi à rédiger un texte structuré."
        if st.button("✨ Motivation", key="btn_mot"): suggestion_cliquee = "Donne-moi de la motivation !"

photo_importee = st.file_uploader("📸 Joindre une photo", type=["png", "jpg", "jpeg"])
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
            
            # Paramètres fonctionnels type Gemini
            config = {
                "temperature": 0.7,    # Équilibre entre créativité et précision
                "max_tokens": 4096,     # Longueur maximale de la réponse
                "top_p": 0.9,           # Diversité du vocabulaire
                "stream": False         # Désactivé pour la stabilité du rendu Markdown
            }

            # Extraction du texte du message pour la recherche contextuelle
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

            # Recherche web facultative pour le mode texte
            context = ""
            if texte_recherche and not is_vision:
                try:
                    with DDGS() as ddgs:
                        results = [r for r in ddgs.text(texte_recherche, max_results=1)]
                        for result in results: context += f"Infos : {result['body']}\n\n"
                except Exception:
                    pass
            
            # --- PROMPT SYSTÈME PERSONNALISÉ AVEC TES INFOS ---
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

            # Préparation de l'historique pour l'API
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
                status.markdown("🤖 *Charles IA réfléchit...*")
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
