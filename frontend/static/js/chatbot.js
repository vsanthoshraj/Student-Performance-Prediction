// EduSense AI Chatbot Drawer Controller

document.addEventListener('DOMContentLoaded', () => {
  const trigger = document.getElementById('chatbotTrigger');
  const drawer = document.getElementById('chatbotDrawer');
  const closeBtn = document.getElementById('chatbotClose');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  const messagesContainer = document.getElementById('chatMessages');

  if (!trigger || !drawer) return;

  // Toggle drawer open/close
  trigger.addEventListener('click', () => {
    drawer.classList.toggle('active');
    if (drawer.classList.contains('active')) {
      chatInput.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => drawer.classList.remove('active'));
  }

  // Handle suggested query chip clicks
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      if (chatInput) {
        chatInput.value = chip.innerText;
        sendMessage();
      }
    });
  });

  // Send message on Enter key or button click
  if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
  }

  if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  }

  function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append user message bubble
    appendMessage(text, 'user');
    chatInput.value = '';

    // Append loading state bubble
    const loadingId = 'msg-loading-' + Date.now();
    appendLoadingMessage(loadingId);

    // Call API Endpoint
    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text })
    })
    .then(res => res.json())
    .then(data => {
      removeLoadingMessage(loadingId);
      const answer = data.answer || "Sorry, I couldn't process your request.";
      appendMessage(answer, 'ai');
    })
    .catch(err => {
      removeLoadingMessage(loadingId);
      appendMessage("Network error connecting to AI Assistant.", 'ai');
    });
  }

  function appendMessage(content, sender) {
    const bubble = document.createElement('div');
    bubble.className = `msg-bubble msg-${sender}`;
    
    if (sender === 'ai') {
      // Basic markdown conversion for AI responses
      let formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>')
        .replace(/• /g, '• ');
      bubble.innerHTML = formatted;
    } else {
      bubble.innerText = content;
    }

    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendLoadingMessage(id) {
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble msg-ai';
    bubble.id = id;
    bubble.innerHTML = `<span style="opacity:0.7;">Thinking...</span>`;
    messagesContainer.appendChild(bubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
});
