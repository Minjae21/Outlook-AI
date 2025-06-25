// Email tagging functionality
const injectEmailTags = () => {
    const emailRows = document.querySelectorAll('div[role="option"], div[role="row"][aria-rowindex]');

    emailRows.forEach(row => {
      if (row.querySelector('.email-tag')) return;

      const subject = row.querySelector('span[title], div[title]');
      if (!subject) return;

      const tag = document.createElement("span");
      tag.className = "email-tag";
      tag.innerText = "Email";
      subject.parentNode.insertBefore(tag, subject.nextSibling);
    });
  };

  const setupObserver = () => {
    const observer = new MutationObserver(injectEmailTags);
    const container = document.querySelector('[aria-label="Message list"]') ||
                     document.querySelector('div[role="main"]');
    if (container) observer.observe(container, { childList: true, subtree: true });
  };

  // Initialize tagging system
  setTimeout(() => {
    if (document.querySelector('div[role="option"]')) {
      injectEmailTags();
      setupObserver();
    }
  }, 2000);