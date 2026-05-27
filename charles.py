import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# Récupération sécurisée et cachée de la clé API
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

st.set_page_config(page_title="Charles IA", page_icon="🤖")
st.title("🤖 Charles IA")
st.caption("Votre assistant personnel avec recherche web en temps réel (100% Gratuit)")

question = st.text_input("Posez votre question à Charles :")

if question:
    # 1. Recherche Web Gratuite via DuckDuckGo
    with st.spinner("Charles cherche sur le web..."):
        context = ""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(question, max_results=3)]
                for result in results:
                    context += f"Titre: {result['title']}\nLien: {result['href']}\nExtrait: {result['body']}\n\n"
        except Exception as e:
            st.warning("La recherche web a rencontré un problème temporaire, Charles répondra avec ses connaissances.")

    # 2. Génération de la réponse avec l'identité de Charles
    with st.spinner("Charles rédige la réponse..."):
        if GROQ_API_KEY:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                prompt = f"""Tu es 'Charles IA', un assistant virtuel intelligent, poli et chaleureux. 
                Réponds à la question de l'utilisateur de manière exhaustive en utilisant les informations récentes du web fournies dans le contexte ci-dessous.
                Rédige une réponse claire, fluide et bien structurée en français.

                Contexte web :
                {context}

                Question: {question}
                """

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192", 
                )
                
                st.write("### Réponse de Charles IA :")
                st.write(chat_completion.choices[0].message.content)
            except Exception as e:
                st.error(f"Erreur d'IA : {str(e)}")
        else:
            st.error("La clé GROQ_API_KEY n'est pas configurée dans les paramètres Cloud.")
