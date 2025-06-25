// Utility functions
function waitForElement(selector, maxAttempts = 10, interval = 500) {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      const checkElement = () => {
        attempts++;
        const element = document.querySelector(selector);
        if (element) {
          resolve(element);
        } else if (attempts < maxAttempts) {
          setTimeout(checkElement, interval);
        } else {
          reject(new Error(`Element ${selector} not found after ${maxAttempts} attempts`));
        }
      };
      checkElement();
    });
  }

  function injectHTML(url, target = document.body) {
    return new Promise((resolve, reject) => {
      fetch(chrome.runtime.getURL(url))
        .then(response => response.text())
        .then(html => {
          const container = document.createElement('div');
          container.innerHTML = html;
          target.appendChild(container);
          resolve(container);
        })
        .catch(reject);
    });
  }