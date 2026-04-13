// ==============================================
// Chatbot logic powered by Qwen API via backend proxy
// ==============================================

const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-chat-btn');
const messagesDiv = document.getElementById('chat-messages');

let conversationHistory = [];
let isSending = false;

function appendMessageBubble(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-animation flex items-start space-x-2 ${sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`;

    const iconWrapper = document.createElement('div');
    iconWrapper.className = sender === 'user'
        ? 'w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0'
        : 'w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0';

    const icon = document.createElement('i');
    icon.className = sender === 'user'
        ? 'fas fa-user text-white text-sm'
        : 'fas fa-robot text-indigo-600 text-sm';
    iconWrapper.appendChild(icon);

    const bubble = document.createElement('div');
    bubble.className = sender === 'user'
        ? 'flex-1 bg-green-500 text-white rounded-lg p-3'
        : 'flex-1 bg-gray-100 rounded-lg p-3';

    const paragraph = document.createElement('p');
    paragraph.className = 'text-sm whitespace-pre-wrap';
    paragraph.textContent = text;
    bubble.appendChild(paragraph);

    messageDiv.appendChild(iconWrapper);
    messageDiv.appendChild(bubble);

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

window.addChatbotMessage = function(text, sender) {
    appendMessageBubble(text, sender);
};

function addTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'flex items-start space-x-2';
    indicator.innerHTML = `
        <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
            <i class="fas fa-robot text-indigo-600 text-sm"></i>
        </div>
        <div class="bg-gray-100 rounded-lg p-3">
            <div class="flex space-x-1">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesDiv.appendChild(indicator);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function getCrmContext() {
    return {
        deals: window.dealsData || [],
        accounts: window.accountsData || [],
        targets: window.targetsData || []
    };
}

async function requestAIReply(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message,
            history: conversationHistory.slice(-8),
            crmContext: getCrmContext()
        })
    });

    let payload = {};
    try {
        payload = await response.json();
    } catch (error) {
        throw new Error('Server returned an invalid response.');
    }

    if (!response.ok) {
        throw new Error(payload.error || 'Failed to get AI response.');
    }

    return payload.reply;
}

window.sendMessage = async function() {
    const message = chatInput.value.trim();
    if (!message || isSending) {
        return;
    }

    isSending = true;
    sendBtn.disabled = true;
    sendBtn.classList.add('opacity-60', 'cursor-not-allowed');

    window.addChatbotMessage(message, 'user');
    conversationHistory.push({ role: 'user', content: message });
    chatInput.value = '';

    addTypingIndicator();

    try {
        const aiReply = await requestAIReply(message);
        removeTypingIndicator();
        window.addChatbotMessage(aiReply, 'ai');
        conversationHistory.push({ role: 'assistant', content: aiReply });
    } catch (error) {
        removeTypingIndicator();
        const fallbackMessage = `Unable to reach Qwen right now: ${error.message}`;
        window.addChatbotMessage(fallbackMessage, 'ai');
        conversationHistory.push({ role: 'assistant', content: fallbackMessage });
    } finally {
        isSending = false;
        sendBtn.disabled = false;
        sendBtn.classList.remove('opacity-60', 'cursor-not-allowed');
        chatInput.focus();
    }
};

function quickQuestion(question) {
    chatInput.value = question;
    window.sendMessage();
}

window.quickQuestion = quickQuestion;

sendBtn.addEventListener('click', window.sendMessage);
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        window.sendMessage();
    }
});

document.querySelectorAll('[data-quick]').forEach((button) => {
    button.addEventListener('click', () => {
        quickQuestion(button.getAttribute('data-quick'));
    });
});

window.addEventListener('load', () => {
    messagesDiv.innerHTML = '';
    const welcomeMessage =
        "Hello! I'm your CRM assistant powered by Qwen. " +
        "Ask about sales, deals, accounts, target progress, or request a short business summary.";
    window.addChatbotMessage(welcomeMessage, 'ai');
    conversationHistory.push({ role: 'assistant', content: welcomeMessage });
});
