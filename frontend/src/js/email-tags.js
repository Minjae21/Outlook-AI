// email-tags.js

let emailTagMap = {};

const TAG_COLORS = {
  "HR": "#D93F0B",
  "Finance": "#007A3E",
  "Personal": "#3B82F6",
  "Other": "#6B7280"
};

const extractSubjectText = (row) => {
  const spans = row.querySelectorAll('span, div');
  for (const el of spans) {
    const text = el.innerText?.trim();
    if (!text) continue;

    if (text.includes('@')) continue;
    if (text.length < 5) continue;

    const cleaned = text.toLowerCase();
    if (emailTagMap[cleaned]) {
      return { subject: cleaned, element: el };
    }
  }
  return null;
};

const injectEmailTags = () => {
  const emailRows = document.querySelectorAll('div[role="option"], div[role="row"][aria-rowindex]');

  emailRows.forEach(row => {
    if (row.querySelector('.email-tag')) return;

    const result = extractSubjectText(row);
    if (!result) return;

    const { subject, element } = result;

    const tagText = emailTagMap[subject] || "Other";
    const color = TAG_COLORS[tagText] || TAG_COLORS["Other"];

    console.log("UI Subject:", subject);
    console.log("Assigned tag:", tagText);


    const tag = document.createElement("span");
    tag.className = "email-tag";
    tag.innerText = tagText;
    tag.style.backgroundColor = color;

    element.parentNode.insertBefore(tag, element.nextSibling);
  });
};

const setupObserver = () => {
  const observer = new MutationObserver(injectEmailTags);
  const container = document.querySelector('[aria-label="Message list"]') ||
                   document.querySelector('div[role="main"]');
  if (container) observer.observe(container, { childList: true, subtree: true });
};

const loadEmailTagsFromBackend = async () => {
  try {
    const res = await fetch("http://localhost:8000/api/email/email-tags");
    const data = await res.json();

    emailTagMap = {};
    data.forEach(item => {
      if (item.subject && item.tag) {
        emailTagMap[item.subject.trim().toLowerCase()] = item.tag;
      }
    });

    injectEmailTags();
    setupObserver();
  } catch (err) {
    console.error("Failed to load email tags", err);
  }
};

setTimeout(() => {
  loadEmailTagsFromBackend();
}, 2000);
