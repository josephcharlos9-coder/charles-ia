import base64
import json
import requests
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Charles IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Style pour masquer l'interface Streamlit par défaut
st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #000000 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stHeader"], footer, .viewerBadge_container__1QSob, 
        [data-testid="stStatusWidget"], #stDecoration, [data-testid="stDecoration"] { 
            display: none !important; 
        }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        iframe { display: block; border: none !important; }
    </style>
""",
    unsafe_allow_html=True,
)


def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""


logo_b64 = get_base64_image("iconcharlesia.jpg")

# Récupération de la clé API Groq depuis les secrets Streamlit
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

html_code = """
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
  <!-- Parser Markdown -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

  <style>
    :root {
      --bg-app: #000000;
      --card-bg: #121212;
      --input-bg: #1f1f1f;
      --text-main: #FFFFFF;
      --text-muted: #8e8e93;
      --border-color: #2a2a2a;
      --radius-lg: 24px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    html, body { background: var(--bg-app); height: 100vh; width: 100vw; overflow: hidden; color: var(--text-main); }
    .app-container { display: flex; flex-direction: column; height: 100vh; width: 100vw; background-color: var(--bg-app); }
    .app-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; }
    .brand-logo { font-weight: 600; font-size: 1.05rem; color: var(--text-main); display: flex; align-items: center; gap: 8px; cursor: pointer; }
    .header-btn { background: none; border: none; color: var(--text-main); cursor: pointer; padding: 6px; border-radius: 50%; }
    .chat-body { flex: 1; overflow-y: auto; display: flex; flex-direction: column; align-items: center; padding: 20px; }
    .welcome-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: auto; text-align: center; gap: 24px; max-width: 600px; width: 100%; }
    .welcome-logo { width: 130px; height: 130px; object-fit: contain; border-radius: 20px; }
    .welcome-title { font-size: 2rem; font-weight: 600; }
    .input-container-wrapper { width: 100%; max-width: 720px; margin: 0 auto; padding: 16px; padding-bottom: 35px; }
    .chat-form { background-color: var(--input-bg); border-radius: var(--radius-lg); padding: 12px 16px; border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 12px; }
    .input-field { border: none; outline: none; background: transparent; font-size: 1rem; color: var(--text-main); width: 100%; resize: none; max-height: 150px; }
    .form-actions { display: flex; align-items: center; justify-content: space-between; }
    .actions-left, .actions-right { display: flex; align-items: center; gap: 8px; }
    .icon-action-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 6px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: all 0.2s; }
    .send-btn { background-color: var(--text-main); color: #000; width: 32px; height: 32px; border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; }
    .suggestions-grid { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
    .suggestion-chip { background-color: var(--card-bg); border: 1px solid var(--border-color); padding: 10px 16px; border-radius: 16px; font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px; }
    .message-list { width: 100%; max-width: 720px; display: flex; flex-direction: column; gap: 16px; margin: 0 auto; padding-bottom: 20px; }
    
    /* Styles Prévisualisation Fichier */
    .file-preview-container { display: none; align-items: center; gap: 10px; background: #2a2a2a; padding: 8px 12px; border-radius: 12px; width: fit-content; margin-bottom: 4px; }
    .file-preview-thumb { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; display: none; }
    .file-preview-name { font-size: 0.85rem; color: #fff; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .remove-file-btn { background: none; border: none; color: #8e8e93; cursor: pointer; font-size: 1rem; padding: 2px 6px; }

    /* Styles Markdown */
    .message-bubble { max-width: 85%; padding: 14px 18px; border-radius: 16px; font-size: 0.95rem; line-height: 1.6; word-break: break-word; }
    .message-user { align-self: flex-end; background-color: #212121; color: #FFFFFF; border-bottom-right-radius: 4px; }
    .message-assistant { align-self: flex-start; background-color: transparent; color: #FFFFFF; padding-left: 0; }
    .message-assistant p { margin-bottom: 8px; }
    .message-assistant ul, .message-assistant ol { margin-left: 20px; margin-bottom: 8px; }
    .message-assistant h1, .message-assistant h2, .message-assistant h3 { margin-top: 12px; margin-bottom: 6px; font-weight: 600; }
    .message-assistant code { background: #2a2a2a; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.85em; }
    .message-assistant pre { background: #1a1a1a; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 8px 0; }
    .message-assistant pre code { background: transparent; padding: 0; }
    .message-media-img { max-width: 100%; max-height: 250px; border-radius: 12px; margin-bottom: 8px; display: block; }

    .bottom-banner { max-width: 600px; margin: 0 auto 12px auto; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; width: calc(100% - 32px); }
    .banner-info { display: flex; align-items: center; gap: 12px; }
    .banner-icon-box { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #9333ea); display: flex; align-items: center; justify-content: center; color: #fff; }
    .voice-launch-btn { background-color: #262626; color: var(--text-main); border: 1px solid var(--border-color); padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; cursor: pointer; }

    .thinking-loader { display: inline-flex; align-items: center; justify-content: center; padding: 4px 0; }
    .thinking-flower { width: 28px; height: 28px; fill: #4c6ef5; animation: spinPulse 2s linear infinite; }
    @keyframes spinPulse {
      0% { transform: rotate(0deg) scale(0.85); opacity: 0.6; }
      50% { transform: rotate(180deg) scale(1.1); opacity: 1; }
      100% { transform: rotate(360deg) scale(0.85); opacity: 0.6; }
    }

    .mic-active {
      color: #ef4444 !important;
      animation: pulseMic 1.2s infinite;
    }
    @keyframes pulseMic {
      0% { transform: scale(1); }
      50% { transform: scale(1.15); }
      100% { transform: scale(1); }
    }
  </style>
</head>
<body>
  <div class="app-container">
    <header class="app-header">
      <div class="brand-logo" onclick="resetChat()">
        <span>Charles IA</span>
        <i data-lucide="chevron-down" style="width: 16px; height: 16px;"></i>
      </div>
      <button class="header-btn" title="Nouvelle discussion" onclick="resetChat()">
        <i data-lucide="square-pen" style="width: 20px; height: 20px;"></i>
      </button>
    </header>

    <main class="chat-body" id="chatBody">
      <div class="welcome-screen" id="welcomeScreen">
        <img src="data:image/jpeg;base64,__LOGO_B64__" alt="Logo Charles IA" class="welcome-logo" />
        <h1 class="welcome-title">Comment puis-je vous aider ?</h1>
        <div class="suggestions-grid">
          <div class="suggestion-chip" onclick="selectPrompt('Créer une image')">
            <i data-lucide="image" style="width: 18px; height: 18px; color: #3b82f6;"></i>
            <span>Créer une image</span>
          </div>
          <div class="suggestion-chip" onclick="selectPrompt('Écrire ou modifier du code')">
            <i data-lucide="pen-tool" style="width: 18px; height: 18px; color: #10b981;"></i>
            <span>Écrire ou modifier</span>
          </div>
          <div class="suggestion-chip" onclick="selectPrompt('Faire une recherche')">
            <i data-lucide="globe" style="width: 18px; height: 18px; color: #f59e0b;"></i>
            <span>Faire une recherche</span>
          </div>
        </div>
      </div>
      <div class="message-list" id="messageList"></div>
    </main>

    <div class="bottom-banner" id="bottomBanner">
      <div class="banner-info">
        <div class="banner-icon-box"><i data-lucide="headphones" style="width: 18px; height: 18px;"></i></div>
        <div>
          <h4 style="font-size:0.85rem;">Découvrez la nouvelle Voix</h4>
          <p style="font-size:0.75rem; color:var(--text-muted);">Conversations dynamiques avec Charles IA</p>
        </div>
      </div>
      <button class="voice-launch-btn" onclick="toggleVoiceInput()">Lancer Voix</button>
    </div>

    <div class="input-container-wrapper">
      <form class="chat-form" id="chatForm">
        <div class="file-preview-container" id="filePreviewContainer">
          <img id="filePreviewThumb" class="file-preview-thumb" src="" alt="Aperçu" />
          <span id="filePreviewName" class="file-preview-name"></span>
          <button type="button" class="remove-file-btn" onclick="clearSelectedFile()">✕</button>
        </div>
        <textarea class="input-field" id="userInput" rows="1" placeholder="Poser une question à Charles IA..."></textarea>
        <div class="form-actions">
          <div class="actions-left">
            <input type="file" id="fileInput" accept="image/*" style="display: none;" onchange="handleFileSelect(event)">
            <button type="button" class="icon-action-btn" onclick="document.getElementById('fileInput').click()"><i data-lucide="plus" style="width: 20px; height: 20px;"></i></button>
            <button type="button" class="icon-action-btn"><i data-lucide="sliders-horizontal" style="width: 18px; height: 18px;"></i></button>
            <button type="button" class="icon-action-btn"><i data-lucide="search" style="width: 18px; height: 18px;"></i></button>
          </div>
          <div class="actions-right">
            <button type="button" class="icon-action-btn" id="micBtn" onclick="toggleVoiceInput()" title="Parler à Charles IA">
              <i data-lucide="mic" id="micIcon" style="width: 18px; height: 18px;"></i>
            </button>
            <button type="submit" class="send-btn"><i data-lucide="arrow-up" style="width: 18px; height: 18px;"></i></button>
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
    const bottomBanner = document.getElementById('bottomBanner');
    const chatBody = document.getElementById('chatBody');
    const fileInput = document.getElementById('fileInput');
    const filePreviewContainer = document.getElementById('filePreviewContainer');
    const filePreviewThumb = document.getElementById('filePreviewThumb');
    const filePreviewName = document.getElementById('filePreviewName');
    const micBtn = document.getElementById('micBtn');

    let currentFile = null;

    const placeholders = [
      "Poser une question à Charles IA...",
      "Demandez-moi d'écrire ou corriger du code 💻",
      "Générez des idées créatives ✨",
      "Posez une question sur n'importe quel sujet 🌐",
      "Besoin d’un coup de main en Python ?",
      "Libère ta créativité avec Charles IA 🎨",
      "Explore le monde avec Charles IA 🌍",
      "Transformons tes idées en algorithmes 🔢"
    ];

    let placeholderIndex = 0;
    setInterval(() => {
      placeholderIndex = (placeholderIndex + 1) % placeholders.length;
      userInput.setAttribute('placeholder', placeholders[placeholderIndex]);
    }, 4000);

    const apiKey = "__GROQ_API_KEY__";

    const systemPrompt = "Tu es Charles IA, un assistant virtuel intelligent, professionnel et charismatique. Tu t'adresses de manière universelle, polie et neutre à tous tes utilisateurs sans présumer de leur nom. Utilise régulièrement des emojis 🤖✨ pour rendre tes réponses vivantes et dynamiques. SEULEMENT si un utilisateur te pose une question directe sur ton créateur, réponds en présentant ton créateur avec ces détails précis : 'Mon créateur est Charles Joseph 🤖✨\\nC'est un jeune passionné de technologie et de basketball de 19 ans (68 kg) 🏀💻 Il a grandi à Bukavu et habite actuellement à Lukanga pour ses études universitaires à l'UNILUK 🎓📍\\nEn tant que développeur, il maîtrise la programmation (notamment avec Python, PySide6, PyQt6, HTML, CSS et JavaScript) ainsi que le montage vidéo et le graphisme 👨‍💻🎨 Côté cœur, il est épanoui et en couple 💑❤️ Et lorsqu'il n'est pas en train de coder ou de concevoir des projets tech, c'est sur un terrain de basket qu'il trouve son véritable équilibre et sa paix intérieure 🏀🔥'";

    let contentsHistory = [];

    const loaderHTML = `
      <div class="thinking-loader">
        <svg class="thinking-flower" viewBox="0 0 24 24">
          <path d="M12 2C12.55 2 13 2.45 13 3V5.07C14.73 5.43 16.2 6.42 17.15 7.85L18.62 6.38C19.01 5.99 19.64 5.99 20.03 6.38C20.42 6.77 20.42 7.4 20.03 7.79L18.56 9.26C19.58 10.21 20.57 11.68 20.93 13.41H23C23.55 13.41 24 13.86 24 14.41C24 14.96 23.55 15.41 23 15.41H20.93C20.57 17.14 19.58 18.61 18.56 19.56L20.03 21.03C20.42 21.42 20.42 22.05 20.03 22.44C19.64 22.83 19.01 22.83 18.62 22.44L17.15 20.97C16.2 21.9 14.73 22.89 13 23.25V25.32C13 25.87 12.55 26.32 12 26.32C11.45 26.32 11 25.87 11 25.32V23.25C9.27 22.89 7.8 21.9 6.85 20.97L5.38 22.44C4.99 22.83 4.36 22.83 3.97 22.44C3.58 22.05 3.58 21.42 3.97 21.03L5.44 19.56C4.42 18.61 3.43 17.14 3.07 15.41H1C0.45 15.41 0 14.96 0 14.41C0 13.86 0.45 13.41 1 13.41H3.07C3.43 11.68 4.42 10.21 5.44 9.26L3.97 7.79C3.58 7.4 3.58 6.77 3.97 6.38C4.36 5.99 4.99 5.99 5.38 6.38L6.85 7.85C7.8 6.42 9.27 5.43 11 5.07V3C11 2.45 11.45 2 12 2Z" />
        </svg>
      </div>
    `;

    // Reconnaissance Vocale
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.lang = 'fr-FR';
      recognition.interimResults = true;

      recognition.onstart = function() {
        isListening = true;
        if (micBtn) micBtn.classList.add('mic-active');
      };

      recognition.onresult = function(event) {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        userInput.value = transcript;
      };

      recognition.onerror = function() { stopVoiceInput(); };
      recognition.onend = function() {
        stopVoiceInput();
        if (userInput.value.trim().length > 0) {
          chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
      };
    }

    function toggleVoiceInput() {
      if (!recognition) {
        alert("La reconnaissance vocale n'est pas supportée par votre navigateur.");
        return;
      }
      isListening ? recognition.stop() : (userInput.value = '', recognition.start());
    }

    function stopVoiceInput() {
      isListening = false;
      if (micBtn) micBtn.classList.remove('mic-active');
    }

    function handleFileSelect(event) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = function(e) {
        currentFile = {
          dataUrl: e.target.result,
          name: file.name
        };
        filePreviewName.textContent = file.name;
        filePreviewThumb.src = e.target.result;
        filePreviewThumb.style.display = 'block';
        filePreviewContainer.style.display = 'flex';
      };
      reader.readAsDataURL(file);
    }

    function clearSelectedFile() {
      currentFile = null;
      fileInput.value = '';
      filePreviewContainer.style.display = 'none';
      filePreviewThumb.src = '';
      filePreviewName.textContent = '';
    }

    function selectPrompt(text) {
      userInput.value = text;
      userInput.focus();
    }

    function resetChat() {
      messageList.innerHTML = '';
      welcomeScreen.style.display = 'flex';
      bottomBanner.style.display = 'flex';
      contentsHistory = [];
      clearSelectedFile();
    }

    function appendMessage(content, sender, isHTML = false, fileObj = null) {
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('message-bubble', sender === 'user' ? 'message-user' : 'message-assistant');
      
      let htmlContent = '';
      if (fileObj) {
        htmlContent += `<img src="${fileObj.dataUrl}" class="message-media-img" alt="Media envoyé" />`;
      }

      if (isHTML) {
        htmlContent += content;
        msgDiv.innerHTML = htmlContent;
      } else {
        if (sender === 'assistant') {
          htmlContent += marked.parse(content);
          msgDiv.innerHTML = htmlContent;
        } else {
          if (content) {
            const textNode = document.createElement('div');
            textNode.textContent = content;
            htmlContent += textNode.innerHTML;
          }
          msgDiv.innerHTML = htmlContent;
        }
      }

      messageList.appendChild(msgDiv);
      chatBody.scrollTop = chatBody.scrollHeight;
      return msgDiv;
    }

    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = userInput.value.trim();
      if (!text && !currentFile) return;

      if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
        bottomBanner.style.display = 'none';
      }

      const attachedFile = currentFile;
      appendMessage(text, 'user', false, attachedFile);
      
      userInput.value = '';
      clearSelectedFile();

      contentsHistory.push({ role: "user", content: text || "[Image jointe]" });

      const loadingMsg = appendMessage(loaderHTML, 'assistant', true);

      if (!apiKey) {
        loadingMsg.innerHTML = "Erreur : La clé GROQ_API_KEY est absente dans st.secrets. ⚠️";
        return;
      }

      try {
        const groqUrl = "https://api.groq.com/openai/v1/chat/completions";

        const messagesToSend = [
          { role: "system", content: systemPrompt },
          ...contentsHistory.slice(-10)
        ];

        const response = await fetch(groqUrl, {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + apiKey,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "llama-3.3-70b-versatile",
            messages: messagesToSend,
            temperature: 0.7,
            max_tokens: 1024
          })
        });

        const data = await response.json();

        if (response.ok && data.choices && data.choices[0].message.content) {
          const assistantReply = data.choices[0].message.content;
          
          loadingMsg.innerHTML = marked.parse(assistantReply);
          
          contentsHistory.push({
            role: "assistant",
            content: assistantReply
          });
        } else {
          loadingMsg.innerHTML = "Erreur Groq (" + response.status + ") : " + (data.error?.message || "Erreur lors de la génération");
        }
      } catch (err) {
        loadingMsg.innerHTML = "Erreur de connexion avec l'API Groq. ⚠️";
      }
    });
  </script>
</body>
</html>
""".replace("__LOGO_B64__", logo_b64).replace("__GROQ_API_KEY__", GROQ_API_KEY)

# Intégration dans Streamlit
st.components.v1.html(
    html_code,
    height=900,
)
