(function () {
  // Determine API URL from script attribute or current origin
  const currentScript = document.currentScript;
  const API_URL = (currentScript && currentScript.getAttribute("data-api-url")) || "http://localhost:8000";
  const TITLE = (currentScript && currentScript.getAttribute("data-title")) || "GitHub Assistant";
  const SUBTITLE = (currentScript && currentScript.getAttribute("data-subtitle")) || "Powered by MyRag";
  const STARTER_PROMPTS = [
    "What projects are featured?",
    "Who is Sacha?",
    "What technologies are used?",
  ];

  // Create UI Elements
  function createWidget() {
    if (document.getElementById("myrag-container")) return;

    // Launcher Button
    const launcher = document.createElement("button");
    launcher.id = "myrag-launcher";
    launcher.setAttribute("aria-label", "Open Chat");
    launcher.innerHTML = `
      <svg id="myrag-open-icon" viewBox="0 0 24 24">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
      <svg id="myrag-close-icon" viewBox="0 0 24 24" style="display:none;">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>
    `;

    // Chat Window
    const container = document.createElement("div");
    container.id = "myrag-container";
    container.innerHTML = `
      <div class="myrag-header">
        <div class="myrag-header-left">
          <span class="myrag-status-dot"></span>
          <div>
            <div class="myrag-header-title">${TITLE}</div>
            <div class="myrag-header-subtitle">${SUBTITLE}</div>
          </div>
        </div>
        <div class="myrag-header-actions">
          <button id="myrag-reset-btn" title="Clear Chat">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
            </svg>
          </button>
          <button id="myrag-close-btn" title="Close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
      <div class="myrag-messages" id="myrag-messages"></div>
      <div class="myrag-input-container">
        <input type="text" class="myrag-input" id="myrag-input" placeholder="Ask anything about my projects..." />
        <button class="myrag-send-btn" id="myrag-send-btn">
          <svg viewBox="0 0 24 24">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
      <div class="myrag-footer">MyRag • Local & Gemini RAG</div>
    `;

    document.body.appendChild(launcher);
    document.body.appendChild(container);

    setupEvents(launcher, container);
    renderInitialMessage();
  }

  function setupEvents(launcher, container) {
    const openIcon = document.getElementById("myrag-open-icon");
    const closeIcon = document.getElementById("myrag-close-icon");
    const closeBtn = document.getElementById("myrag-close-btn");
    const resetBtn = document.getElementById("myrag-reset-btn");
    const input = document.getElementById("myrag-input");
    const sendBtn = document.getElementById("myrag-send-btn");

    function toggleChat() {
      const isOpen = container.classList.toggle("open");
      openIcon.style.display = isOpen ? "none" : "block";
      closeIcon.style.display = isOpen ? "block" : "none";
      if (isOpen) {
        setTimeout(() => input.focus(), 200);
      }
    }

    launcher.addEventListener("click", toggleChat);
    closeBtn.addEventListener("click", toggleChat);

    resetBtn.addEventListener("click", () => {
      const messagesContainer = document.getElementById("myrag-messages");
      messagesContainer.innerHTML = "";
      renderInitialMessage();
    });

    sendBtn.addEventListener("click", () => handleSendMessage());
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });
  }

  function renderInitialMessage() {
    const messagesContainer = document.getElementById("myrag-messages");
    const welcomeHtml = `
      <p>Hi there! 👋 I am an AI assistant trained on this GitHub Page and repositories.</p>
      <p>Ask me questions or try these quick suggestions:</p>
      <div class="myrag-starters">
        ${STARTER_PROMPTS.map(
          (p) => `<button class="myrag-starter-btn" data-prompt="${p}">${p}</button>`
        ).join("")}
      </div>
    `;
    appendMessage("bot", welcomeHtml, false);

    // Attach listeners to starter buttons
    messagesContainer.querySelectorAll(".myrag-starter-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const prompt = btn.getAttribute("data-prompt");
        const input = document.getElementById("myrag-input");
        input.value = prompt;
        handleSendMessage();
      });
    });
  }

  function appendMessage(sender, text, isMarkdown = true) {
    const messagesContainer = document.getElementById("myrag-messages");
    const msg = document.createElement("div");
    msg.className = `myrag-msg ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "myrag-bubble";
    bubble.innerHTML = isMarkdown ? parseMarkdown(text) : text;

    msg.appendChild(bubble);
    messagesContainer.appendChild(msg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return { msg, bubble };
  }

  async function handleSendMessage() {
    const input = document.getElementById("myrag-input");
    const query = input.value.trim();
    if (!query) return;

    input.value = "";
    input.disabled = true;
    document.getElementById("myrag-send-btn").disabled = true;

    // Append user message
    appendMessage("user", query, false);

    // Show typing dots
    const messagesContainer = document.getElementById("myrag-messages");
    const typingMsg = document.createElement("div");
    typingMsg.className = "myrag-msg bot";
    typingMsg.id = "myrag-typing-indicator";
    typingMsg.innerHTML = `
      <div class="myrag-bubble">
        <div class="myrag-typing">
          <div class="myrag-dot"></div>
          <div class="myrag-dot"></div>
          <div class="myrag-dot"></div>
        </div>
      </div>
    `;
    messagesContainer.appendChild(typingMsg);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      // Attempt streaming endpoint first
      const streamUrl = `${API_URL.replace(/\/$/, "")}/api/chat/stream`;
      const response = await fetch(streamUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      // Remove typing indicator
      typingMsg.remove();

      if (response.ok && response.body) {
        // Stream reading
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";
        let sources = [];

        const { msg, bubble } = appendMessage("bot", "", true);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const payload = JSON.parse(line.substring(6));
                if (payload.token) {
                  fullText += payload.token;
                  bubble.innerHTML = parseMarkdown(fullText);
                  messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
                if (payload.done && payload.sources) {
                  sources = payload.sources;
                }
              } catch (e) {
                // partial json chunk, ignore
              }
            }
          }
        }

        // Render sources if available
        if (sources && sources.length > 0) {
          renderSources(msg, sources);
        }
      } else {
        // Fallback to standard /api/chat
        const fallbackUrl = `${API_URL.replace(/\/$/, "")}/api/chat`;
        const res = await fetch(fallbackUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        });
        const data = await res.json();
        const { msg, bubble } = appendMessage("bot", data.answer || "No response received.", true);
        if (data.sources) {
          renderSources(msg, data.sources);
        }
      }
    } catch (err) {
      if (document.getElementById("myrag-typing-indicator")) {
        typingMsg.remove();
      }
      appendMessage("bot", `⚠️ Could not reach RAG server at \`${API_URL}\`. Please ensure the backend is running.`, true);
      console.error("MyRag Error:", err);
    } finally {
      input.disabled = false;
      document.getElementById("myrag-send-btn").disabled = false;
      input.focus();
    }
  }

  function renderSources(msgNode, sources) {
    if (!sources || sources.length === 0) return;
    const sourcesDiv = document.createElement("div");
    sourcesDiv.className = "myrag-sources";

    sources.forEach((s) => {
      const chip = document.createElement("span");
      chip.className = "myrag-source-chip";
      chip.title = `${s.source} (Relevance: ${Math.round(s.score * 100)}%)\n\nPreview:\n${s.preview}`;
      chip.textContent = `📄 ${s.title} (${Math.round(s.score * 100)}%)`;
      sourcesDiv.appendChild(chip);
    });

    msgNode.appendChild(sourcesDiv);
  }

  // Simple Markdown Parser (Zero dependencies)
  function parseMarkdown(md) {
    if (!md) return "";
    let html = md
      // Code blocks
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      // Inline code
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      // Blockquotes
      .replace(/^>\s*(.+)$/gm, "<blockquote>$1</blockquote>")
      // Headers
      .replace(/^### (.*$)/gm, "<strong>$1</strong><br/>")
      .replace(/^## (.*$)/gm, "<strong>$1</strong><br/>")
      .replace(/^# (.*$)/gm, "<strong>$1</strong><br/>")
      // Bold
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      // Italic
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      // Unordered lists
      .replace(/^\s*-\s+(.+)$/gm, "<li>$1</li>")
      // Line breaks
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br/>");

    return `<p>${html}</p>`;
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createWidget);
  } else {
    createWidget();
  }
})();
