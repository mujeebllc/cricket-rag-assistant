// API Base URL (FastAPI Backend)
const API_BASE_URL = "http://10.11.119.72:8000";

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const typingIndicator = document.getElementById("typingIndicator");
const apiStatusBadge = document.getElementById("apiStatusBadge");
const statusText = document.getElementById("statusText");
const welcomeCard = document.getElementById("welcomeCard");

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    setupEventListeners();
});

// Check Backend Health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/`, { method: "GET" });
        if (response.ok) {
            const data = await response.json();
            if (data.status === "ok") {
                apiStatusBadge.classList.add("online");
                apiStatusBadge.classList.remove("offline");
                statusText.textContent = "API Connected";
            }
        } else {
            setOfflineStatus();
        }
    } catch (error) {
        setOfflineStatus();
    }
}

function setOfflineStatus() {
    apiStatusBadge.classList.remove("online");
    apiStatusBadge.classList.add("offline");
    statusText.textContent = "API Offline";
}

// Event Listeners
function setupEventListeners() {
    userInput.addEventListener("input", handleInputResize);
    userInput.addEventListener("keydown", handleKeyDown);
    sendBtn.addEventListener("click", sendMessage);
    clearChatBtn.addEventListener("click", clearChat);

    // Delegate click for example chips
    document.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip-btn");
        if (chip) {
            const question = chip.getAttribute("data-question");
            if (question) {
                userInput.value = question;
                handleInputResize();
                sendMessage();
            }
        }
    });
}

// Auto-resize textarea
function handleInputResize() {
    userInput.style.height = "auto";
    userInput.style.height = `${Math.min(userInput.scrollHeight, 120)}px`;
    sendBtn.disabled = userInput.value.trim() === "";
}

// Handle Enter Key
function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (userInput.value.trim() !== "") {
            sendMessage();
        }
    }
}

// Clear Chat
function clearChat() {
    chatMessages.innerHTML = "";
    if (welcomeCard) {
        chatMessages.appendChild(welcomeCard);
        welcomeCard.style.display = "block";
    }
}

// Send Question to API
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    // Hide welcome card on first message
    if (welcomeCard) {
        welcomeCard.style.display = "none";
    }

    // Append User Message Bubble
    appendUserMessage(question);

    // Reset Input
    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.disabled = true;

    // Show Typing Indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        hideTypingIndicator();

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const detailMsg = errorData.detail || "Server returned an error.";
            appendAssistantError(`Error: ${detailMsg}`);
            return;
        }

        const data = await response.json();
        appendAssistantMessage(data);
        checkHealth(); // Update online badge
    } catch (error) {
        hideTypingIndicator();
        appendAssistantError("Could not connect to the backend server. Please verify that FastAPI is running on http://10.11.119.72:8000.");
        setOfflineStatus();
    }
}

// Append User Message to UI
function appendUserMessage(text) {
    const messageRow = document.createElement("div");
    messageRow.className = "message-row user";

    messageRow.innerHTML = `
        <div class="message-content-wrapper">
            <div class="message-bubble">
                ${escapeHtml(text)}
            </div>
        </div>
        <div class="avatar">
            <i class="fa-solid fa-user"></i>
        </div>
    `;

    chatMessages.appendChild(messageRow);
    scrollToBottom();
}

// Append Assistant Response to UI
function appendAssistantMessage(data) {
    const messageRow = document.createElement("div");
    messageRow.className = "message-row assistant";

    const answerText = data.answer || "No response received.";
    const langLabel = getLangLabel(data.language);

    let technicalDetailsHtml = "";
    if (data.sql || (data.columns && data.columns.length > 0)) {
        technicalDetailsHtml = buildTechnicalDetails(data);
    }

    messageRow.innerHTML = `
        <div class="avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-content-wrapper">
            <span class="lang-badge ${escapeHtml(data.language || 'english')}">${langLabel}</span>
            <div class="message-bubble">
                ${escapeHtml(answerText)}
            </div>
            ${technicalDetailsHtml}
        </div>
    `;

    chatMessages.appendChild(messageRow);
    scrollToBottom();
}

// Build Collapsible Technical Details (SQL + Table)
function buildTechnicalDetails(data) {
    let sqlBlock = "";
    if (data.sql) {
        sqlBlock = `
            <div>
                <strong>Generated MariaDB SQL:</strong>
                <pre class="sql-box"><code>${escapeHtml(data.sql)}</code></pre>
            </div>
        `;
    }

    let tableBlock = "";
    if (data.columns && data.columns.length > 0 && data.rows && data.rows.length > 0) {
        const headersHtml = data.columns.map(col => `<th>${escapeHtml(col)}</th>`).join("");
        const rowsHtml = data.rows.map(row => {
            const cells = row.map(cell => `<td>${escapeHtml(cell !== null ? String(cell) : "NULL")}</td>`).join("");
            return `<tr>${cells}</tr>`;
        }).join("");

        tableBlock = `
            <div>
                <strong>SQL Result Set (${data.rows.length} row${data.rows.length > 1 ? 's' : ''}):</strong>
                <div class="table-wrapper">
                    <table class="data-table">
                        <thead><tr>${headersHtml}</tr></thead>
                        <tbody>${rowsHtml}</tbody>
                    </table>
                </div>
            </div>
        `;
    }

    return `
        <details class="tech-accordion">
            <summary class="tech-accordion-summary">
                <span><i class="fa-solid fa-code"></i> Technical Details (SQL & Data)</span>
                <i class="fa-solid fa-chevron-down"></i>
            </summary>
            <div class="tech-accordion-details">
                ${sqlBlock}
                ${tableBlock}
            </div>
        </details>
    `;
}

// Append Error Message
function appendAssistantError(errorMsg) {
    const messageRow = document.createElement("div");
    messageRow.className = "message-row assistant";

    messageRow.innerHTML = `
        <div class="avatar" style="background: var(--danger);">
            <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div class="message-content-wrapper">
            <div class="message-bubble" style="border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.1); color: #fca5a5;">
                ${escapeHtml(errorMsg)}
            </div>
        </div>
    `;

    chatMessages.appendChild(messageRow);
    scrollToBottom();
}

// Helpers
function showTypingIndicator() {
    typingIndicator.classList.remove("hidden");
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.classList.add("hidden");
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getLangLabel(lang) {
    switch (lang) {
        case "roman_urdu": return "Roman Urdu";
        case "english":
        default: return "English";
    }
}

function escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
