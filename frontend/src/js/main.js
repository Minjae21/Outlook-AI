const initExtension = async () => {
  // Create toggle button
  const toggleBtn = document.createElement("button");
  toggleBtn.id = "assistant-toggle-btn";
  toggleBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="white" stroke-width="2"/>
      <path d="M12 16V16.01M12 8V12" stroke="white" stroke-width="2" stroke-linecap="round"/>
    </svg>`;
  document.body.appendChild(toggleBtn);

  // Load panel HTML
  const panelHTML = await fetch(chrome.runtime.getURL('src/html/panel.html')).then(r => r.text());

  const panelWrapper = document.createElement('div');
  panelWrapper.innerHTML = panelHTML;
  document.body.appendChild(panelWrapper);

  // Now initialize chatbot event handlers
  initializeChatbotEvents();

  // Toggle panel visibility
  toggleBtn.addEventListener("click", () => {
    const panel = document.getElementById("outlook-assistant-panel");
    if (panel) {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
  });
};

// Delay init until Outlook finishes loading
setTimeout(initExtension, 1500);
