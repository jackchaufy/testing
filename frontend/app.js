const toolList = document.getElementById("tool-list");
const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

const history = [];

async function fetchTools() {
  const response = await fetch("/api/tools");
  const data = await response.json();
  renderTools(data.tools || []);
}

async function toggleTool(name) {
  await fetch(`/api/tools/${name}/toggle`, { method: "POST" });
  await fetchTools();
}

function renderTools(tools) {
  toolList.innerHTML = "";
  tools.forEach((tool) => {
    const item = document.createElement("div");
    item.className = "tool-item";

    const title = document.createElement("h3");
    title.textContent = tool.name;

    const description = document.createElement("p");
    description.textContent = tool.description;

    const statusRow = document.createElement("div");
    statusRow.className = "tool-status";

    const statusText = document.createElement("span");
    statusText.textContent = tool.enabled ? "Active" : "Inactive";

    const toggleButton = document.createElement("button");
    toggleButton.className = `toggle-button ${
      tool.enabled ? "enabled" : "disabled"
    }`;
    toggleButton.textContent = tool.enabled ? "Disable" : "Enable";
    toggleButton.addEventListener("click", () => toggleTool(tool.name));

    statusRow.append(statusText, toggleButton);
    item.append(title, description, statusRow);
    toolList.appendChild(item);
  });
}

function appendMessage(role, content, toolUsage = []) {
  const bubble = document.createElement("div");
  bubble.className = `message ${role}`;

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = role === "user" ? "You" : "Agent";

  const text = document.createElement("div");
  text.textContent = content;

  bubble.append(meta, text);

  if (toolUsage.length) {
    const usage = document.createElement("div");
    usage.className = "tool-usage";
    usage.textContent = `Tools used: ${toolUsage.join(", ")}`;
    bubble.appendChild(usage);
  }

  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(event) {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  history.push({ role: "user", content: message });
  chatInput.value = "";

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });

  const data = await response.json();
  const reply = data.reply || "(no response)";
  appendMessage("assistant", reply, data.tool_usage || []);
  history.push({ role: "assistant", content: reply });
}

chatForm.addEventListener("submit", sendMessage);
fetchTools();
