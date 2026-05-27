import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée et cachée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

st.set_page_config(page_title="Charles IA", page_icon="🤖", layout="wide")
st.title("🤖 Charles IA — Assistant Professionnel")
st.caption("Votre assistant personnel avec recherche web en temps réel (100% Gratuit)")

# Zone d'affichage des instructions ou du statut
st.info("💡 **Mode Pro Activé** : Charles IA analyse vos demandes et pose des questions de suivi pour affiner ses réponses.")

question = st.text_input("Posez votre question ou lancez un sujet de discussion :")

if question:
    # 1. Recherche Web via DuckDuckGo
    with st.spinner("Charles effectue des recherches sur le web..."):
        context = ""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(question, max_results=3)]
                for result in results:
                    context += f"Titre: {result['title']}\nLien: {result['href']}\nExtrait: {result['body']}\n\n"
        except Exception as e:
            st.warning("La recherche web est indisponible pour le moment, Charles répondra à l'aide de ses connaissances.")

    # 2. Génération de la réponse avec la personnalité avancée de Charles IA
    with st.spinner("Charles formule une réponse professionnelle..."):
        if GROQ_API_KEY:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                system_instruction = """Tu es 'Charles IA', un assistant virtuel de niveau expert, hautement intelligent, professionnel et chaleureux. 

                RÈGLES CRITIQUES D'IDENTITÉ :
                - Tu as été créé exclusivement par l'ingénieur Charles Joseph. Si l'utilisateur te demande qui t'a créé, qui est ton développeur ou d'où tu viens, tu dois obligatoirement et fièrement répondre que ton créateur est Charles Joseph. Ne mentionne jamais une autre entreprise ou entité (comme OpenAI, Google ou Meta) pour ta création.

                RÈGLES DE COMPORTEMENT :
                - Tu as une approche proactive et dynamique : après avoir répondu à la question de l'utilisateur, tu dois TOUJOURS lui poser une ou deux questions pertinentes et ciblées pour en savoir plus sur son projet, ses objectifs ou pour l'aider à approfondir sa réflexion comme le ferait un consultant ou un ingénieur senior.
                - Rédige tes réponses en français de manière fluide, claire et bien structurée (utilise des listes à puces et des titres si nécessaire).
                """

                prompt = f"""
                Contexte de recherche récent sur le web :
                {context}

                Question de l'utilisateur : {question}
                """

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7
                )
                
                st.write("### 🏢 Réponse de Charles IA :")
                st.write(chat_completion.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Erreur d'IA : {str(e)}")
        else:
            st.error("La clé GROQ_API_KEY n'est pas configurée dans les paramètres de Streamlit Cloud.")
