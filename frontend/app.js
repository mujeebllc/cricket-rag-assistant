// Use the backend on the same host by default; the query string can override its URL.
const API_PROTOCOL = window.location.protocol === "https:" ? "https:" : "http:";
const API_HOST = window.location.hostname || "localhost";
const API_URL_OVERRIDE = new URLSearchParams(window.location.search).get("api");
const API_BASE_URL = window.CRICKET_API_BASE_URL || API_URL_OVERRIDE || `${API_PROTOCOL}//${API_HOST}:8000`;

// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const conversationList = document.getElementById("conversationList");
const typingIndicator = document.getElementById("typingIndicator");
const apiStatusBadge = document.getElementById("apiStatusBadge");
const statusText = document.getElementById("statusText");
const welcomeCard = document.getElementById("welcomeCard");
const ACTIVE_CONVERSATION_KEY = "cricket-active-conversation";
let activeConversationId = null;
let sendingMessage = false;

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    setupEventListeners();
    initializeConversationHistory();
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
    newChatBtn.addEventListener("click", async () => {
        try {
            await startNewConversation();
        } catch (error) {
            appendAssistantError(error.message);
        }
    });
    conversationList.addEventListener("click", event => {
        const deleteButton = event.target.closest("[data-delete-conversation]");
        if (deleteButton) {
            deleteConversation(deleteButton.dataset.deleteConversation).catch(error => {
                appendAssistantError(error.message);
            });
            return;
        }
        const conversationButton = event.target.closest("[data-conversation-id]");
        if (conversationButton && conversationButton.dataset.conversationId !== activeConversationId) {
            loadConversation(conversationButton.dataset.conversationId).catch(error => {
                appendAssistantError(error.message);
            });
        }
    });

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

function resetChatView() {
    chatMessages.innerHTML = "";
    if (welcomeCard) {
        chatMessages.appendChild(welcomeCard);
        welcomeCard.style.display = "block";
    }
    userInput.value = "";
    handleInputResize();
}

async function initializeConversationHistory() {
    try {
        const conversations = await fetchConversationList();
        const savedId = localStorage.getItem(ACTIVE_CONVERSATION_KEY);
        if (savedId && conversations.some(conversation => conversation.id === savedId)) {
            await loadConversation(savedId, false);
        } else {
            await startNewConversation(false);
        }
        await refreshConversationList();
    } catch (error) {
        showConversationListError(error.message);
        appendAssistantError(`Could not load conversation history: ${error.message}`);
    }
}

async function fetchConversationList() {
    const response = await fetch(`${API_BASE_URL}/api/conversations`);
    if (!response.ok) {
        throw new Error("The server could not list conversations.");
    }
    return response.json();
}

async function refreshConversationList() {
    const conversations = await fetchConversationList();
    conversationList.replaceChildren();
    if (conversations.length === 0) {
        const emptyState = document.createElement("div");
        emptyState.className = "conversation-list-status";
        emptyState.textContent = "Your conversations will appear here.";
        conversationList.appendChild(emptyState);
        return;
    }

    conversations.forEach(conversation => {
        const item = document.createElement("div");
        item.className = "conversation-item";
        if (conversation.id === activeConversationId) {
            item.classList.add("active");
        }

        const selectButton = document.createElement("button");
        selectButton.type = "button";
        selectButton.className = "conversation-select-btn";
        selectButton.dataset.conversationId = conversation.id;
        selectButton.textContent = conversation.title;
        selectButton.title = conversation.title;
        selectButton.setAttribute("aria-current", conversation.id === activeConversationId ? "page" : "false");

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "conversation-delete-btn";
        deleteButton.dataset.deleteConversation = conversation.id;
        deleteButton.title = "Delete conversation";
        deleteButton.setAttribute("aria-label", `Delete ${conversation.title}`);
        deleteButton.innerHTML = '<i class="fa-solid fa-trash-can" aria-hidden="true"></i>';

        item.append(selectButton, deleteButton);
        conversationList.appendChild(item);
    });
}

async function loadConversation(conversationId, refreshList = true) {
    const response = await fetch(`${API_BASE_URL}/api/conversations/${encodeURIComponent(conversationId)}`);
    if (!response.ok) {
        throw new Error("The selected conversation could not be loaded.");
    }
    const conversation = await response.json();
    activeConversationId = conversation.id;
    localStorage.setItem(ACTIVE_CONVERSATION_KEY, activeConversationId);
    resetChatView();
    if (conversation.messages.length > 0) {
        welcomeCard.style.display = "none";
        conversation.messages.forEach(message => {
            if (message.role === "user") {
                appendUserMessage(message.content);
            } else if (message.role === "assistant") {
                appendAssistantMessage({
                    ...(message.metadata || {}),
                    answer: message.content,
                });
            }
        });
    }
    if (refreshList) {
        await refreshConversationList();
    }
}

async function startNewConversation(refreshList = true) {
    const response = await fetch(`${API_BASE_URL}/api/conversations`, { method: "POST" });
    if (!response.ok) {
        throw new Error("The server could not create a conversation.");
    }
    const conversation = await response.json();
    activeConversationId = conversation.id;
    localStorage.setItem(ACTIVE_CONVERSATION_KEY, activeConversationId);
    resetChatView();
    if (refreshList) {
        await refreshConversationList();
    }
}

async function deleteConversation(conversationId) {
    if (!conversationId || !window.confirm("Delete this conversation and all its messages?")) {
        return;
    }
    setConversationControlsDisabled(true);
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/conversations/${encodeURIComponent(conversationId)}`,
            { method: "DELETE" }
        );
        if (!response.ok) {
            throw new Error("The conversation could not be deleted.");
        }
        if (conversationId === activeConversationId) {
            activeConversationId = null;
            localStorage.removeItem(ACTIVE_CONVERSATION_KEY);
            resetChatView();
            const remaining = await fetchConversationList();
            if (remaining.length > 0) {
                await loadConversation(remaining[0].id);
            } else {
                await startNewConversation();
            }
        } else {
            await refreshConversationList();
        }
    } catch (error) {
        appendAssistantError(error.message);
    } finally {
        setConversationControlsDisabled(false);
    }
}

function setConversationControlsDisabled(disabled) {
    newChatBtn.disabled = disabled;
    conversationList.querySelectorAll("button").forEach(button => {
        button.disabled = disabled;
    });
}

function showConversationListError(message) {
    conversationList.replaceChildren();
    const error = document.createElement("div");
    error.className = "conversation-list-status error";
    error.textContent = `Unable to load chats: ${message}`;
    conversationList.appendChild(error);
}

// Send Question to API
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question || sendingMessage) return;
    if (!activeConversationId) {
        appendAssistantError("Conversation history is not ready. Please try again.");
        return;
    }

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
    sendingMessage = true;
    setConversationControlsDisabled(true);

    // Show Typing Indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question, conversation_id: activeConversationId })
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
        try {
            await refreshConversationList();
        } catch (error) {
            showConversationListError(error.message);
        }
        checkHealth(); // Update online badge
    } catch (error) {
        hideTypingIndicator();
        appendAssistantError(`Could not connect to the backend server. Please verify that FastAPI is running on ${API_BASE_URL}.`);
        setOfflineStatus();
    } finally {
        sendingMessage = false;
        setConversationControlsDisabled(false);
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
    const sourcesHtml = data.sources && data.sources.length > 0
        ? `<div class="source-citations"><span>Sources:</span> ${data.sources.map(escapeHtml).join(", ")}</div>`
        : "";

    messageRow.innerHTML = `
        <div class="avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-content-wrapper">
            <span class="lang-badge ${escapeHtml(data.language || 'english')}">${langLabel}</span>
            <div class="message-bubble">
                ${escapeHtml(answerText)}
            </div>
            ${sourcesHtml}
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
