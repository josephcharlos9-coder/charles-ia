import streamlit as st
import json

# Récupération de la clé API depuis secrets.toml
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

st.set_page_config(
    page_title="Charles IA - Interface",
    page_icon="🤖",
    layout="wide"
)

# --- CODE HTML / CSS / JS ADAPTATIF (RESPONSIVE) ---
html_code = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Charles IA - Interface</title>
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

    /* --- MODE DESKTOP / PC --- */
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
      transition: all 0.3s ease;
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
      cursor: pointer;
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
      justify-content: center;
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
      white-space: pre-wrap;
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
    }}

    .input-field {{
      border: none;
      outline: none;
      background: transparent;
      font-size: 0.95rem;
      color: var(--text-main);
      width: 100%;
      resize: none;
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

    /* --- ADAPTATION MOBILE (ÉCRANS < 768px) --- */
    @media (max-width: 768px) {{
      body {{
        padding: 0;
        background: var(--bg-app);
      }}

      .hero-container {{
        justify-content: center;
      }}

      /* Cacher le grand titre du PC */
      .brand-section {{
        display: none;
      }}

      /* Le wrapper du téléphone prend tout l'écran mobile */
      .phone-wrapper {{
        max-width: 100vw;
        height: 100vh;
        border-radius: 0;
        padding: 0;
        border: none;
        box-shadow: none;
      }}

      /* Supprimer l'encoche fictive sur vrai téléphone */
      .dynamic-island {{
        display: none;
      }}

      .phone-screen {{
        border-radius: 0;
      }}

      .app-header {{
        padding-top: 20px; /* Réduction du haut de page */
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
          <button class="btn-header">
            <i data-lucide="chevron-left"></i>
            <span>Retour</span>
          </button>
          <div class="model-selector">
            <span>Llama 3.1 8B</span>
            <i data-lucide="chevron-down" style="width:16px; height:16px;"></i>
          </div>
          <button class="btn-header">
            <i data-lucide="square-pen" style="width:20px; height:20px;"></i>
          </button>
        </header>

        <main class="chat-body" id="chatBody">
          <div id="welcomeScreen" style="display: flex; flex-direction: column; align-items: center; gap: 16px;">
            <i data-lucide="bot" class="charles-logo"></i>
            <h2 class="greeting-text">Bonjour ! Sur quoi<br>travaillons-nous ?</h2>
          </div>
          <div class="message-list" id="messageList"></div>
        </main>

        <footer class="chat-footer">
          <form class="input-box" id="chatForm">
            <input
              type="text"
              class="input-field"
              id="userInput"
              placeholder="Poser une question à Charles IA..."
              autocomplete="off"
            />
            <div class="actions-bar">
              <div class="tools-left">
                <button type="button" class="icon-btn" title="Ajouter un fichier">
                  <i data-lucide="plus" style="width:20px; height:20px;"></i>
                </button>
                <button type="button" class="icon-btn" title="Paramètres">
                  <i data-lucide="sliders-horizontal" style="width:18px; height:18px;"></i>
                </button>
                <button type="button" class="icon-btn" title="Recherche Web">
                  <i data-lucide="search" style="width:18px; height:18px;"></i>
                </button>
              </div>
              <div style="display: flex; gap: 8px; align-items: center;">
                <button type="button" class="icon-btn" title="Entrée vocale">
                  <i data-lucide="mic" style="width:20px; height:20px;"></i>
                </button>
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

    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messageList = document.getElementById('messageList');
    const welcomeScreen = document.getElementById('welcomeScreen');
    const chatBody = document.getElementById('chatBody');

    const apiKey = "{GROQ_API_KEY}";

    chatForm.addEventListener('submit', async (e) => {{
      e.preventDefault();
      const text = userInput.value.trim();
      if (!text) return;

      if (welcomeScreen.style.display !== 'none') {{
        welcomeScreen.style.display = 'none';
        chatBody.style.justifyContent = 'flex-end';
      }}

      appendMessage(text, 'user');
      userInput.value = '';

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
                content: "Tu es Charles IA, créé par Charles Joseph. Tu es une IA 🤖 intelligente, dynamique et polie. Ton créateur a 19 ans, habite Bukavu/Lukanga, aime le basket. Réponds en français."
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
          loadingMsg.textContent = "Désolé, une erreur s'est produite lors du traitement de ta demande.";
        }}
      }} catch (err) {{
        loadingMsg.textContent = "Erreur de connexion. Vérifiez la clé API Groq.";
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

st.components.v1.html(html_code, height=850, scrolling=True)
