import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq
import streamlit.components.v1 as components

# --- CONFIGURATION SÉCURISÉE DE LA PAGE ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Masquer complètement l'interface native Streamlit pour ne garder que notre maquette
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    iframe { display: block; border: none; width: 100vw; height: 100vh; }
    </style>
""", unsafe_allow_html=True)

# --- IDENTITÉ ET SESSIONS ---
CREATOR_NAME = "Charles Joseph"
AI_DISPLAY_NAME = "Charles IA"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TRAITEMENT DES NOUVEAUX MESSAGES VIA PARAMÈTRES D'URL ---
query_params = st.query_params
if "prompt" in query_params and query_params["prompt"].strip():
    user_prompt = query_params["prompt"].strip()
    
    # Nettoyer les paramètres pour éviter les boucles d'envoi
    st.query_params.clear()

    # 1. Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # 2. Générer la réponse avec DuckDuckGo + Groq
    context = ""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(user_prompt, max_results=1)]
            for result in results:
                context += f"Infos : {result.get('body', '')}\n\n"
    except Exception:
        pass

    system_instruction = f"""Tu es {AI_DISPLAY_NAME}, un assistant virtuel conçu par {CREATOR_NAME}. 
Ton rôle est d’être un compagnon intelligent, fiable et engageant.

Identité :
- Tu es une IA 🤖, créée EXCLUSIVEMENT par {CREATOR_NAME}.
- Si on t'interroge sur {CREATOR_NAME} : Il s'appelle {CREATOR_NAME}, né et a grandi à Bukavu, 19 ans, réside à Lukanga pour ses études universitaires. Passionné de basketball (69 kg), chrétien adventiste du 7ème jour.

Style :
- Ton positif, respectueux, bien structuré avec des émojis 🎉.
- Utilise Markdown et LaTeX si formule mathématique."""

    messages_api = [{"role": "system", "content": system_instruction}]
    for msg in st.session_state.messages[-3:-1]:
        messages_api.append({"role": msg["role"], "content": msg["content"]})

    prompt_final = f"Contexte de recherche :\n{context}\n\nQuestion de l'utilisateur :\n{user_prompt}"
    messages_api.append({"role": "user", "content": prompt_final})

    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages_api,
                temperature=0.7,
                max_tokens=4096,
                top_p=0.9
            )
            final_text = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": final_text})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Erreur : {e}"})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Clé API GROQ_API_KEY absente dans `st.secrets`."})

# --- GÉNÉRATION DU CODE HTML DYNAMIQUE ---
# Conversion des messages en HTML
messages_html = ""
for msg in st.session_state.messages:
    css_class = "message-user" if msg["role"] == "user" else "message-assistant"
    # Échappement sommaire des balises pour la sécurité d'affichage
    content_formatted = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    messages_html += f'<div class="message-bubble {css_class}">{content_formatted}</div>'

welcome_display = "display: flex;" if len(st.session_state.messages) == 0 else "display: none;"
chat_justify = "justify-content: flex-end;" if len(st.session_state.messages) > 0 else "justify-content: center;"

html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Charles IA</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>

  <style>
    :root {{
      --bg-gradient: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
      --bg-app: #0d0d0d;
      --card-bg: #171717;
      --text-main: #FFFFFF;
      --text-muted: #8e8e93;
      --border-color: #303030;
      --accent-color: #00D2FF;
      --accent-glow: rgba(0, 210, 255, 0.2);
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4);
      --shadow-md: 0 12px 32px rgba(0, 0, 0, 0.6);
      --radius-lg: 24px;
      --radius-full: 9999px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      -webkit-tap-highlight-color: transparent;
    }}

    body {{
      background: var(--bg-gradient);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      overflow-x: hidden;
      color: var(--text-main);
    }}

    .hero-container {{
      display: flex;
      width: 100%;
      max-width: 1200px;
      align-items: center;
      justify-content: space-between;
      gap: 40px;
    }}

    .brand-section {{
      color: #FFFFFF;
      display: flex;
      align-items: center;
      gap: 20px;
      flex: 1;
    }}

    .brand-logo-icon {{
      width: 64px;
      height: 64px;
      color: var(--accent-color);
      filter: drop-shadow(0 0 12px var(--accent-glow));
    }}

    .brand-title {{
      font-size: 4.5rem;
      font-weight: 700;
      letter-spacing: -1px;
      background: linear-gradient(180deg, #FFFFFF 0%, #8e8e93 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .phone-wrapper {{
      position: relative;
      width: 100%;
      max-width: 410px;
      height: 780px;
      background: #000000;
      border-radius: 48px;
      padding: 12px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 210, 255, 0.1);
      border: 2px solid rgba(255, 255, 255, 0.15);
    }}

    .dynamic-island {{
      position: absolute;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: 110px;
      height: 28px;
      background-color: #000;
      border-radius: 20px;
      z-index: 100;
    }}

    .phone-screen {{
      background-color: var(--bg-app);
      width: 100%;
      height: 100%;
      border-radius: 38px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
    }}

    .app-header {{
      padding: 50px 20px 15px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-color);
    }}

    .btn-header {{
      background: none;
      border: none;
      display: flex;
      align-items: center;
      gap: 4px;
      color: var(--text-main);
      font-size: 0.95rem;
      font-weight: 500;
      cursor: pointer;
    }}

    .model-selector {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 6px 12px;
      border-radius: var(--radius-full);
      background-color: #171717;
      border: 1px solid var(--border-color);
    }}

    .chat-body {{
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      {chat_justify}
      text-align: center;
      gap: 16px;
    }}

    .charles-logo {{
      color: var(--accent-color);
      width: 56px;
      height: 56px;
      animation: pulse 3s infinite ease-in-out;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(1); opacity: 0.9; }}
      50% {{ transform: scale(1.08); opacity: 1; }}
      100% {{ transform: scale(1); opacity: 0.9; }}
    }}

    .greeting-text {{
      font-size: 1.8rem;
      line-height: 1.25;
      color: var(--text-main);
      font-weight: 600;
    }}

    .message-list {{
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: auto;
    }}

    .message-bubble {{
      max-width: 85%;
      padding: 12px 16px;
      border-radius: 18px;
      font-size: 0.95rem;
      line-height: 1.4;
      text-align: left;
      animation: fadeIn 0.3s ease;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .message-user {{
      align-self: flex-end;
      background-color: #262626;
      color: #FFF;
      border-bottom-right-radius: 4px;
    }}

    .message-assistant {{
      align-self: flex-start;
      background-color: var(--card-bg);
      color: var(--text-main);
      border-bottom-left-radius: 4px;
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--border-color);
    }}

    .chat-footer {{
      padding: 12px 16px 20px;
      background-color: var(--bg-app);
    }}

    .input-box {{
      background: var(--card-bg);
      border-radius: var(--radius-lg);
      padding: 12px 16px;
      box-shadow: var(--shadow-md);
      border: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: border-color 0.2s;
    }}

    .input-box:focus-within {{
      border-color: var(--accent-color);
    }}

    .input-field {{
      border: none;
      outline: none;
      background: transparent;
      font-size: 0.95rem;
      color: var(--text-main);
      width: 100%;
    }}

    .input-field::placeholder {{
      color: var(--text-muted);
    }}

    .actions-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .tools-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .icon-btn {{
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
      border-radius: 50%;
    }}

    .audio-btn {{
      background-color: var(--text-main);
      color: #000;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }}

    /* RESPONSIVE IPAD & SMARTPHONE */
    @media (max-width: 850px) {{
      body {{
        padding: 0;
        align-items: flex-start;
      }}
      .brand-section {{
        display: none !important;
      }}
      .hero-container {{
        width: 100vw;
        height: 100vh;
      }}
      .phone-wrapper {{
        max-width: 100vw !important;
        height: 100vh !important;
        border-radius: 0 !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
      }}
      .dynamic-island {{
        display: none !important;
      }}
      .phone-screen {{
        border-radius: 0 !important;
        height: 100vh;
      }}
      .app-header {{
        padding: 20px 16px 12px !important;
      }}
      .chat-footer {{
        padding-bottom: 25px;
      }}
    }}
  </style>
</head>
<body>

  <div class="hero-container">
    <div class="brand-section">
      <i data-lucide="bot" class="brand-logo-icon"></i>
      <h1 class="brand-title">Charles IA</h1>
    </div>

    <div class="phone-wrapper">
      <div class="dynamic-island"></div>
      
      <div class="phone-screen">
        <header class="app-header">
          <button class="btn-header" onclick="window.top.location.href=window.location.pathname">
            <i data-lucide="rotate-ccw"></i>
            <span>Reset</span>
          </button>
          
          <div class="model-selector">
            <span>Llama 3.1 8B</span>
            <i data-lucide="zap" style="width:16px; height:16px; color:#00D2FF;"></i>
          </div>

          <button class="btn-header" onclick="window.top.location.href=window.location.pathname">
            <i data-lucide="square-pen" style="width:20px; height:20px;"></i>
          </button>
        </header>

        <main class="chat-body" id="chatBody">
          <div id="welcomeScreen" style="{welcome_display} flex-direction: column; align-items: center; gap: 16px;">
            <i data-lucide="bot" class="charles-logo"></i>
            <h2 class="greeting-text">Bonjour ! Sur quoi<br>travaillons-nous ?</h2>
          </div>

          <div class="message-list">
            {messages_html}
          </div>
        </main>

        <footer class="chat-footer">
          <form class="input-box" method="GET" action="" target="_top">
            <input 
              type="text" 
              name="prompt"
              class="input-field" 
              placeholder="Poser une question à Charles IA..."
              autocomplete="off"
              required
            />
            
            <div class="actions-bar">
              <div class="tools-left">
                <button type="button" class="icon-btn" title="Ajouter un fichier">
                  <i data-lucide="plus" style="width:20px; height:20px;"></i>
                </button>
                <button type="button" class="icon-btn" title="Paramètres">
                  <i data-lucide="sliders-horizontal" style="width:18px; height:18px;"></i>
                </button>
                <button type="button" class="icon-btn" title="Recherche Web active">
                  <i data-lucide="search" style="width:18px; height:18px;"></i>
                </button>
              </div>

              <div style="display: flex; gap: 8px; align-items: center;">
                <button type="submit" class="audio-btn" title="Envoyer">
                  <i data-lucide="send" style="width:18px; height:18px;"></i>
                </button>
              </div>
            </div>
          </form>
        </footer>

      </div>
    </div>
  </div>

  <script>
    lucide.createIcons();
    const chatBody = document.getElementById('chatBody');
    chatBody.scrollTop = chatBody.scrollHeight;
  </script>
</body>
</html>
"""

# Rend la maquette responsive avec la logique Python fonctionnelle
components.html(html_content, height=850, scrolling=True)
