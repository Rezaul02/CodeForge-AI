const API_URL = 'http://localhost:5006/api/ask';

const sendBtn = document.getElementById('sendBtn');
const sendBtnBottom = document.getElementById('sendBtnBottom');
const newChatBtn = document.querySelector('.new-chat-btn');
const clearChatBtn = document.getElementById('clearChatBtn');

const heroSection = document.getElementById('heroSection');
const chatSection = document.getElementById('chatSection');
const chatMessages = document.getElementById('chatMessages');
const historyList = document.getElementById('historyList');

let currentChatId = null;
let chatStore = loadChatStore();
clearChatBtn.addEventListener('click', clearAllHistory);
sendBtn.addEventListener('click', () => startWorkflow('userInput'));
sendBtnBottom.addEventListener('click', () => startWorkflow('userInputBottom'));
newChatBtn.addEventListener('click', createNewChat);

document.getElementById('userInput').addEventListener('keydown', handleEnterToSend);
document.getElementById('userInputBottom').addEventListener('keydown', handleEnterToSend);

initApp();

function clearAllHistory() {
    const confirmDelete = confirm("Are you sure you want to delete all chat history?");
    if (!confirmDelete) return;

    localStorage.removeItem('multiAgentChatStore');
    chatStore = {};
    currentChatId = null;
    clearChatUI();
    resetStatusMenu();
    renderHistoryList();

    heroSection.classList.remove('hidden');
    chatSection.classList.add('hidden');
}

/* =========================
   APP INIT
========================= */
function initApp() {
    renderHistoryList();

    const validChats = getValidChats();
    if (validChats.length > 0) {
        currentChatId = validChats[0].id;
        loadChat(currentChatId);
    } else {
        createNewChat(true);
    }
}

function handleEnterToSend(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        startWorkflow(e.target.id);
    }
}

/* =========================
   STORAGE
========================= */
function loadChatStore() {
    try {
        return JSON.parse(localStorage.getItem('multiAgentChatStore')) || {};
    } catch {
        return {};
    }
}

function saveChatStore() {
    localStorage.setItem('multiAgentChatStore', JSON.stringify(chatStore));
}

function getValidChats() {
    return Object.values(chatStore)
        .filter(chat => chat.messages && chat.messages.length > 0)
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}
/*Type writer effect for system messages*/

function typeWriterEffect(el, text, speed = 8) {
    return new Promise(resolve => {
        let i = 0;
        el.textContent = '';
        function type() {
            if (i < text.length) {
                el.textContent += text.charAt(i);
                i++;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }
        type();
    });
}

/* =========================
   NEW CHAT
========================= */
function createNewChat(skipRender = false) {
    // গুরুত্বপূর্ণ: এখানে আর localStorage-এ empty chat save করা হবে না
    currentChatId = null;
    clearChatUI();
    resetStatusMenu();

    if (!skipRender) {
        heroSection.classList.remove('hidden');
        chatSection.classList.add('hidden');
    }

    renderHistoryList();
}

function ensureCurrentChat(promptText = 'New Chat') {
    if (currentChatId && chatStore[currentChatId]) return;

    currentChatId = 'chat_' + Date.now();
    chatStore[currentChatId] = {
        id: currentChatId,
        title: truncateText(promptText, 30),
        createdAt: new Date().toISOString(),
        messages: []
    };

    saveChatStore();
    renderHistoryList();
}

/* =========================
   CHAT LOAD / HISTORY
========================= */
function loadChat(chatId) {
    const chat = chatStore[chatId];
    if (!chat) return;

    currentChatId = chatId;
    clearChatUI();
    renderHistoryList();

    if (!chat.messages || chat.messages.length === 0) {
        heroSection.classList.remove('hidden');
        chatSection.classList.add('hidden');
        return;
    }

    heroSection.classList.add('hidden');
    chatSection.classList.remove('hidden');

    chat.messages.forEach(msg => {
        if (msg.type === 'html') {
            appendHTMLMessage(msg.html, msg.className, false);
        } else {
            appendMessage(msg.text, msg.className, false);
        }
    });

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function clearChatUI() {
    chatMessages.innerHTML = '';
    document.getElementById('userInput').value = '';
    document.getElementById('userInputBottom').value = '';
}

function renderHistoryList() {
    if (!historyList) return;

    historyList.innerHTML = '';

    const chats = getValidChats();

    if (chats.length === 0) {
        historyList.innerHTML = `<div style="color:#9aa0a6;font-size:13px;padding:6px;">No chats yet</div>`;
        return;
    }

    chats.forEach(chat => {
        const item = document.createElement('div');
        item.className = 'history-item' + (chat.id === currentChatId ? ' active' : '');
        item.innerText = chat.title || 'Untitled Chat';
        item.title = chat.title || 'Untitled Chat';

        item.addEventListener('click', () => loadChat(chat.id));
        historyList.appendChild(item);
    });
}

function saveMessageToCurrentChat(messageObj) {
    if (!currentChatId || !chatStore[currentChatId]) return;

    chatStore[currentChatId].messages.push(messageObj);

    // title update only from first user message
    if (
        messageObj.className === 'user-message' &&
        chatStore[currentChatId].messages.filter(m => m.className === 'user-message').length === 1
    ) {
        chatStore[currentChatId].title = truncateText(messageObj.text, 30);
    }

    saveChatStore();
    renderHistoryList();
}

/* =========================
   MAIN WORKFLOW
========================= */
async function startWorkflow(inputId) {
    const inputElement = document.getElementById(inputId);
    const prompt = inputElement.value.trim();
    if (!prompt) return;

    // chat create হবে প্রথম prompt পাঠানোর সময়
    ensureCurrentChat(prompt);

    heroSection.classList.add('hidden');
    chatSection.classList.remove('hidden');

    document.getElementById('userInput').value = '';
    document.getElementById('userInputBottom').value = '';

    appendMessage(prompt, 'user-message', true);
    resetStatusMenu();

    const aiMessageDiv = appendMessage("🤖 Agents are processing your request...", 'system-message', true);

    let latestCode = '';
    let reviewerFeedback = '';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) throw new Error("Backend server error");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let partialData = '';

        aiMessageDiv.innerHTML = '⚡ <b>Multi-agent workflow started:</b><br>';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            partialData += decoder.decode(value, { stream: true });
            const lines = partialData.split('\n\n');
            partialData = lines.pop();

            for (const line of lines) {
                if (!line.trim().startsWith('data: ')) continue;

                try {
                    const cleanLine = line.replace('data: ', '').trim();
                    if (!cleanLine) continue;

                    const jsonData = JSON.parse(cleanLine);

                    if (jsonData.node === "ERROR" || jsonData.error_message) {
                        appendMessage(
                            `Backend error: ${jsonData.error_message || jsonData.error}`,
                            'system-message',
                            true
                        );
                        return;
                    }

                    if (jsonData.code) latestCode = jsonData.code;
                    if (jsonData.node === "REVIEWER" && jsonData.review_comments) {
                        reviewerFeedback = jsonData.review_comments;
                    }

                    updateUIWithAgentEvent(jsonData);
                } catch (err) {
                    console.error("JSON parse error:", err);
                }
            }
        }

        // ✅ Stream শেষ — এখন শুধু typing effect দিয়ে final code দেখানো
        if (latestCode) {
            await showFinalCodeWithTyping(aiMessageDiv, latestCode);
        } else {
            aiMessageDiv.innerHTML = `<div style="color:#f28b82;">⚠ কোনো কোড generate হয়নি।</div>`;
        }

    } catch (error) {
        console.error(error);
        appendMessage("❌ Backend connection failed.", 'system-message', true);
    }
}
async function showFinalCodeWithTyping(aiMessageDiv, code) {
    // পুরনো "processing" প্লেসহোল্ডারকে ছোট status মেসেজে বদলে দিই
    aiMessageDiv.innerHTML = `
        <div style="color:#81c995;font-weight:700;">✅ Workflow completed! Final code নিচে দেখুন 👇</div>
    `;

    // নতুন final-code বক্স সবসময় চ্যাটের একদম শেষে বসাই, যাতে scroll করলে visible হয়
    const finalDiv = document.createElement('div');
    finalDiv.className = 'message system-message';
    finalDiv.innerHTML = `
        <div class="agent-output-box coder-box">
            <div class="agent-title" style="display:flex;justify-content:space-between;align-items:center;">
                <span>🎯 FINAL GENERATED CODE</span>
                <button class="copy-btn">📋 Copy</button>
            </div>
            <pre class="code-block"><code></code></pre>
        </div>
    `;
    chatMessages.appendChild(finalDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // ✅ document.getElementById নয় — এই নির্দিষ্ট finalDiv এর ভিতর থেকেই খুঁজি
    const codeEl = finalDiv.querySelector('code');
    await typeWriterEffect(codeEl, code, 6);

    const copyBtn = finalDiv.querySelector('.copy-btn');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(code);
        copyBtn.innerText = '✅ Copied';
        setTimeout(() => (copyBtn.innerText = '📋 Copy'), 1500);
    });

    // চ্যাট history তে দুইটা মেসেজই ঠিকভাবে সেভ করি
    replaceLastSystemMessageWithHTML(
        `<div style="color:#81c995;font-weight:700;">✅ Workflow completed! Final code নিচে দেখুন 👇</div>`
    );

    saveMessageToCurrentChat({
        type: 'html',
        html: finalDiv.innerHTML,
        className: 'system-message'
    });
}

/* =========================
   AGENT EVENT UI
========================= */
function updateUIWithAgentEvent(data) {
    if (!data.node) return;

    const nodeLower = data.node.toLowerCase();
    const statusElement = document.getElementById(`status-${nodeLower}`);

    if (statusElement) {
        statusElement.className = 'status-item active';
        statusElement.innerText = `⚙ ${data.node} working...`;
    }

    if (data.node === "PLANNER") {
        if (statusElement) {
            statusElement.className = 'status-item completed';
            statusElement.innerText = '✓ Planner done';
        }

        if (data.plan) {
            const html = `
                <div class="agent-output-box planner-box">
                    <div class="agent-title">🧠 Planner Output</div>
                    <div>${formatPlainText(data.plan)}</div>
                </div>
            `;
            appendHTMLMessage(html, 'system-message', true);
        }
    }

    if (data.node === "CODER") {
        if (statusElement) {
            statusElement.className = 'status-item completed';
            statusElement.innerText = '✓ Coder done';
        }

        if (data.code) {
            const html = `
                <div class="agent-output-box coder-box">
                    <div class="agent-title">💻 Coder Output</div>
                    <pre class="code-block"><code>${escapeHtml(data.code)}</code></pre>
                </div>
            `;
            appendHTMLMessage(html, 'system-message', true);
        }
    }

    if (data.node === "TESTER") {
        if (statusElement) {
            statusElement.className = 'status-item completed';
            statusElement.innerText = '✓ Tester done';
        }

        if (data.test_results) {
            const testText = typeof data.test_results === 'string'
                ? data.test_results
                : JSON.stringify(data.test_results, null, 2);

            const html = `
                <div class="agent-output-box tester-box">
                    <div class="agent-title">🧪 Tester Output</div>
                    <pre class="code-block"><code>${escapeHtml(testText)}</code></pre>
                </div>
            `;
            appendHTMLMessage(html, 'system-message', true);
        }
    }

    if (data.node === "REVIEWER") {
        if (statusElement) {
            statusElement.className = 'status-item completed';
            statusElement.innerText = '✓ Reviewer done';
        }

        if (data.review_comments) {
            const html = `
                <div class="agent-output-box reviewer-box">
                    <div class="agent-title">📝 Reviewer Feedback</div>
                    <div>${formatPlainText(data.review_comments)}</div>
                </div>
            `;
            appendHTMLMessage(html, 'system-message', true);
        }
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* =========================
   MESSAGE HELPERS
========================= */
function appendMessage(text, className, shouldSave = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerText = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (shouldSave) {
        saveMessageToCurrentChat({
            type: 'text',
            text,
            className
        });
    }

    return messageDiv;
}

function appendHTMLMessage(html, className, shouldSave = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (shouldSave) {
        saveMessageToCurrentChat({
            type: 'html',
            html,
            className
        });
    }

    return messageDiv;
}

function replaceLastSystemMessageWithHTML(html) {
    if (!currentChatId || !chatStore[currentChatId]) return;

    const messages = chatStore[currentChatId].messages;
    for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].className === 'system-message') {
            messages[i] = {
                type: 'html',
                html,
                className: 'system-message'
            };
            break;
        }
    }

    saveChatStore();
}

/* =========================
   STATUS RESET
========================= */
function resetStatusMenu() {
    ['planner', 'coder', 'tester', 'reviewer'].forEach(node => {
        const el = document.getElementById(`status-${node}`);
        if (el) {
            el.className = 'status-item';
            el.innerText = node.charAt(0).toUpperCase() + node.slice(1);
        }
    });
}

/* =========================
   UTILITIES
========================= */
function truncateText(text, maxLength = 30) {
    if (!text) return 'Untitled Chat';
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
}

function formatPlainText(text) {
    if (!text) return '';
    return escapeHtml(String(text)).replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}