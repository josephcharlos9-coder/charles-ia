import streamlit as st
import json

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #000000 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        iframe {
            display: block;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

html_code = f"""
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
      --bg-app: #000000;
      --card-bg: #121212;
      --input-bg: #1f1f1f;
      --text-main: #FFFFFF;
      --text-muted: #8e8e93;
      --border-color: #2a2a2a;
      --accent-color: #3b82f6;
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

    html, body {{
      background: var(--bg-app);
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      color: var(--text-main);
    }}

    .app-container {{
      display: flex;
      flex-direction: column;
      height: 100vh;
      width: 100vw;
      background-color: var(--bg-app);
      position: relative;
    }}

    .app-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      background: transparent;
      z-index: 10;
    }}

    .brand-logo {{
      font-weight: 600;
      font-size: 1.05rem;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .header-btn {{
      background: none;
      border: none;
      color: var(--text-main);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
      border-radius: 50%;
      transition: background 0.2s;
    }}

    .header-btn:hover {{
      background-color: rgba(255, 255, 255, 0.1);
    }}

    .chat-body {{
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      scroll-behavior: smooth;
    }}

    .welcome-screen {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin: auto;
      text-align: center;
      gap: 24px;
      max-width: 600px;
      width: 100%;
    }}

    .welcome-title {{
      font-size: 2rem;
      font-weight: 600;
      color: var(--text-main);
    }}

    .input-container-wrapper {{
      width: 100%;
      max-width: 720px;
      margin: 0 auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .chat-form {{
      background-color: var(--input-bg);
      border-radius: var(--radius-lg);
      padding: 12px 16px;
      border: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.5);
      transition: border-color 0.2s;
    }}

    .chat-form:focus-within {{
      border-color: #555;
    }}

    .input-field {{
      border: none;
      outline: none;
      background: transparent;
      font-size: 1rem;
      color: var(--text-main);
      width: 100%;
      resize: none;
      max-height: 150px;
      line-height: 1.4;
    }}

    .input-field::placeholder {{
      color: var(--text-muted);
    }}

    .form-actions {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .actions-left, .actions-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .icon-action-btn {{
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
      border-radius: 50%;
      transition: color 0.2s;
    }}

    .icon-action-btn:hover {{
      color: var(--text-main);
    }}

    .send-btn {{
      background-color: var(--text-main);
      color: #000;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.2s;
    }}

    .send-btn:hover {{
      transform: scale(1.05);
    }}

    .suggestions-grid {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      justify-content: center;
      margin-top: 4px;
    }}

    .suggestion-chip {{
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      padding: 10px 16px;
      border-radius: 16px;
      font-size: 0.9rem;
      color: var(--text-main);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s;
    }}

    .suggestion-chip:hover {{
      background-color: var(--input-bg);
    }}

    .message-list {{
      width: 100%;
      max-width: 720px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin: 0 auto;
      padding-bottom: 20px;
    }}

    .message-bubble {{
      max-width: 85%;
      padding: 14px 18px;
      border-radius: 16px;
      font-size: 0.95rem;
      line-height: 1.5;
      text-align: left;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    .message-user {{
      align-self: flex-end;
      background-color: #212121;
      color: #FFFFFF;
      border-bottom-right-radius: 4px;
    }}

    .message-assistant {{
      align-self: flex-start;
      background-color: transparent;
      color: #FFFFFF;
      padding-left: 0;
    }}

    .bottom-banner {{
      max-width: 600px;
      margin: 0 auto 12px auto;
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      width: calc(100% - 32px);
    }}

    .banner-info {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .banner-icon-box {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3b82f6, #9333ea);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }}

    .banner-text h4 {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-main);
    }}

    .banner-text p {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    .voice-launch-btn {{
      background-color: #262626;
      color: var(--text-main);
      border: 1px solid var(--border-color);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
    }}

    @media (max-width: 768px) {{
      .app-header {{
        padding: 12px 16px;
      }}
      .welcome-title {{
        font-size: 1.6rem;
      }}
      .suggestions-grid {{
        flex-direction: column;
        width: 100%;
      }}
      .suggestion-chip {{
        width: 100%;
        justify-content: flex-start;
      }}
    }}
  </style>
</head>
<body>

  <div class="app-container">
    <header class="app-header">
      <div class="brand-logo" id="resetBtn">
        <span>Charles IA</span>
        <i data-lucide="chevron-down" style="width: 16px; height: 16px;"></i>
      </div>
      <div class="header-actions">
        <button class="header-btn" title="Nouvelle discussion" onclick="resetChat()">
          <i data-lucide="square-pen" style="width: 20px; height: 20px;"></i>
        </button>
      </div>
    </header>

    <main class="chat-body" id="chatBody">
      <div class="welcome-screen" id="welcomeScreen">
        <h1 class="welcome-title">Comment puis-je vous aider ?</h1>
        
        <div class="suggestions-grid">
          <div class="suggestion-chip" onclick="selectPrompt('Générer une idée d\'image')">
            <i data-lucide="image" style="width: 18px; height: 18px; color: #3b82f6;"></i>
            <span>Créer une image</span>
          </div>
          <div class="suggestion-chip" onclick="selectPrompt('Aide-moi à écrire ou modifier du code')">
            <i data-lucide="pen-tool" style="width: 18px; height: 18px; color: #10b981;"></i>
            <span>Écrire ou modifier</span>
          </div>
          <div class="suggestion-chip" onclick="selectPrompt('Faire une recherche sur un sujet précis')">
            <i data-lucide="globe" style="width: 18px; height: 18px; color: #f59e0b;"></i>
            <span>Faire une recherche</span>
          </div>
        </div>
      </div>

      <div class="message-list" id="messageList"></div>
    </main>

    <div class="bottom-banner" id="bottomBanner">
      <div class="banner-info">
        <div class="banner-icon-box">
          <i data-lucide="headphones" style="width: 18px; height: 18px;"></i>
        </div>
        <div class="banner-text">
          <h4>Découvrez la nouvelle Voix</h4>
          <p>Des conversations dynamiques avec Charles IA</p>
        </div>
      </div>
      <button class="voice-launch-btn" onclick="alert('Module vocal actif ! 🎙️')">Lancer Voix</button>
    </div>

    <div class="input-container-wrapper">
      <form class="chat-form" id="chatForm">
        <textarea
          class="input-field"
          id="userInput"
          rows="1"
          placeholder="Poser une question à Charles IA..."
          autocomplete="off"
        ></textarea>
        <div class="form-actions">
          <div class="actions-left">
            <button type="button" class="icon-action-btn" title="Ajouter un fichier">
              <i data-lucide="plus" style="width: 20px; height: 20px;"></i>
            </button>
            <button type="button" class="icon-action-btn" title="Paramètres">
              <i data-lucide="sliders-horizontal" style="width: 18px; height: 18px;"></i>
            </button>
            <button type="button" class="icon-action-btn" title="Recherche Web">
              <i data-lucide="search" style="width: 18px; height: 18px;"></i>
            </button>
          </div>
          <div class="actions-right">
            <button type="button" class="icon-action-btn" title="Mode vocal">
              <i data-lucide="mic" style="width: 18px; height: 18px;"></i>
            </button>
            <button type="submit" class="send-btn" title="Envoyer">
              <i data-lucide="arrow-up" style="width: 18px; height: 18px;"></i>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <script>
    lucide.createIcons();

    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messageList = document.getElementById('messageList');
    const welcomeScreen = document.getElementById('welcomeScreen');
    const chatBody = document.getElementById('chatBody');
    const bottomBanner = document.getElementById('bottomBanner');

    const apiKey = "{GROQ_API_KEY}";

    userInput.addEventListener('input', function() {{
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    }});

    function selectPrompt(text) {{
      userInput.value = text;
      userInput.focus();
    }}

    function resetChat() {{
      messageList.innerHTML = '';
      welcomeScreen.style.display = 'flex';
      bottomBanner.style.display = 'flex';
    }}

    chatForm.addEventListener('submit', async (e) => {{
      e.preventDefault();
      const text = userInput.value.trim();
      if (!text) return;

      if (welcomeScreen.style.display !== 'none') {{
        welcomeScreen.style.display = 'none';
        bottomBanner.style.display = 'none';
      }}

      appendMessage(text, 'user');
      userInput.value = '';
      userInput.style.height = 'auto';

      const loadingMsg = appendMessage("Charles IA réfléchit...", 'assistant');

      try {{
        const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {{
          method: "POST",
          headers: {{
            "Authorization": "Bearer " + apiKey,
            "Content-Type": "application/json"
          }},
          body: JSON.stringify({{
            model: "llama-3.1-8b-instant",
            messages: [
              {{
                role: "system",
                content: "Tu es Charles IA, un assistant virtuel intelligent, professionnel et charismatique. Tu t'adresses de manière universelle, polie et neutre à chaque utilisateur (sans assumer qu'il s'appelle Charles Joseph). Utilise régulièrement des emojis 🤖✨ pour rendre tes réponses vivantes et dynamiques. Seulement si l'utilisateur te demande explicitement qui est ton créateur, réponds qu'il s'appelle Charles Joseph (résidant à Lukanga/Bukavu, 19 ans, passionné de basketball)."
              }},
              {{ role: "user", content: text }}
            ],
            temperature: 0.7
          }})
        }});

        const data = await response.json();
        if (data.choices && data.choices[0]) {{
          loadingMsg.textContent = data.choices[0].message.content;
        }} else {{
          loadingMsg.textContent = "Désolé, une erreur est survenue. 🤖";
        }}
      }} catch (err) {{
        loadingMsg.textContent = "Erreur de connexion. ⚠️";
      }}
    }});

    function appendMessage(text, sender) {{
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('message-bubble', sender === 'user' ? 'message-user' : 'message-assistant');
      msgDiv.textContent = text;
      
      messageList.appendChild(msgDiv);
      chatBody.scrollTop = chatBody.scrollHeight;
      return msgDiv;
    }}
  </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=900, scrolling=False)
