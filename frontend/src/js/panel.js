// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeChatbotEvents);

function initializeChatbotEvents() {
  // Event delegation for all buttons
  document.addEventListener('click', (e) => {
    const target = e.target.closest('button');
    if (!target) return;

    switch(target.id) {
      case 'priority-btn':
        console.log('Priority Inbox clicked');
        break;
      case 'digest-btn':
        console.log('Daily Digest clicked');
        break;
      case 'chat-btn':
        toggleChatbot();
        break;
      case 'close-chatbot':
        toggleChatbot(false);
        break;
      case 'send-message':
        sendMessage();
        break;
    }
  });

  // Handle Enter key in chat input
  document.addEventListener('keydown', (e) => {
    if (e.target.id === 'chat-input' && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  document.addEventListener('input', (e) => {
    if (e.target.id === 'chat-input') {
      e.target.style.height = 'auto';
      e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
    }
  });
}

function toggleChatbot(show = null) {
  const chatbot = document.getElementById('chatbot-container');
  if (!chatbot) {
    console.error('Chatbot container not found');
    return;
  }

  if (show === null) {
    chatbot.classList.toggle('hidden');
  } else {
    chatbot.classList.toggle('hidden', !show);
  }

  if (!chatbot.classList.contains('hidden')) {
    setTimeout(() => {
      const input = document.getElementById('chat-input');
      if (input) {
        input.focus();
        input.style.height = 'auto';
      }
    }, 100);
  }
}

async function sendMessage() {
  const input = document.getElementById('chat-input');
  if (!input || !input.value.trim()) return;

  const message = input.value.trim();
  input.value = '';
  input.style.height = 'auto';

  addMessage(message, 'user');
  showTypingIndicator();

  try {
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Request failed');
    }

    const data = await response.json();
    removeTypingIndicator();
    addMessage(data.response, 'bot');

  } catch (error) {
    console.error('API Error:', error);
    removeTypingIndicator();
    addMessage(`Error: ${error.message}`, 'bot');
  }
}

function addMessage(text, sender) {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;

  const messageElement = document.createElement('div');
  messageElement.classList.add('message', `${sender}-message`);
  messageElement.textContent = text;
  messagesContainer.appendChild(messageElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;

  const typingElement = document.createElement('div');
  typingElement.classList.add('message', 'bot-message', 'typing-indicator');
  typingElement.id = 'typing-indicator';
  typingElement.innerHTML = '<span></span><span></span><span></span>';
  messagesContainer.appendChild(typingElement);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
  const typingElement = document.getElementById('typing-indicator');
  if (typingElement) typingElement.remove();
}