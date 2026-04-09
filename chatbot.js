// ==============================================
// Chatbot simulation (replace with real API)
// ==============================================

// UI Elements
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-chat-btn');
const messagesDiv = document.getElementById('chat-messages');

// Public function for adding messages (will also be used by the CRM)
window.addChatbotMessage = function(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-animation flex items-start space-x-2 ${sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`;
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-user text-white text-sm"></i>
            </div>
            <div class="flex-1 bg-green-500 text-white rounded-lg p-3">
                <p class="text-sm">${text}</p>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-indigo-600 text-sm"></i>
            </div>
            <div class="flex-1 bg-gray-100 rounded-lg p-3">
                <p class="text-sm">${text}</p>
            </div>
        `;
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
};

// Function for typing indicator (mock)
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
    if (indicator) indicator.remove();
}

// Mock response logic
function generateMockAIResponse(question) {
    // Acessa os dados globais expostos pelo app.js
    const dealsData = window.dealsData || [];
    const accountsData = window.accountsData || [];
    
    const q = question.toLowerCase();
    
    if (q.includes('total') && (q.includes('sales') || q.includes('sale'))) {
        const total = dealsData.reduce((sum, d) => sum + d.amount, 0);
        const closedWon = dealsData.filter(d => d.stage === 'Closed Won').reduce((sum, d) => sum + d.amount, 0);
        return `💰 Total sales amount is $${total.toLocaleString()}. From this, $${closedWon.toLocaleString()} has been closed.`;
    }
    
    if (q.includes('top') && (q.includes('account') || q.includes('accounts'))) {
        if (accountsData.length > 0) {
            const topAccount = [...accountsData].sort((a,b) => b.totalValue - a.totalValue)[0];
            return `🏆 The top account by value is ${topAccount.name} with $${topAccount.totalValue.toLocaleString()} across ${topAccount.deals} deals.`;
        }
        return "No account data available.";
    }
    
    if (q.includes('stage') || q.includes('stages')) {
        const stages = dealsData.reduce((acc, d) => {
            acc[d.stage] = (acc[d.stage] || 0) + 1;
            return acc;
        }, {});
        return `📊 Distribution by stage:\n${Object.entries(stages).map(([k,v]) => `• ${k}: ${v} deal(s)`).join('\n')}`;
    }
    
    if (q.includes('rep') || q.includes('seller') || q.includes('owner')) {
        const byOwner = dealsData.reduce((acc, d) => {
            acc[d.owner] = (acc[d.owner] || 0) + d.amount;
            return acc;
        }, {});
        const topOwner = Object.entries(byOwner).sort((a,b) => b[1] - a[1])[0];
        if (topOwner) {
            return `👤 ${topOwner[0]} is the top performing sales rep with $${topOwner[1].toLocaleString()} in sales.`;
        }
    }
    
    return `I understand you're asking about "${question}". For a more precise answer, you could:\n\n• Be more specific about the time period\n• Mention specific stages (Proposal, Closed Won, etc.)\n• Ask about accounts, sales reps, or amounts\n\nExample: "What's the total closed won sales in March?"`;
}

// Main function for sending (called via button or quick question)
window.sendMessage = function() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    window.addChatbotMessage(message, 'user');
    chatInput.value = '';
    
    addTypingIndicator();
    
    // Response delay simulation (1 second)
    setTimeout(() => {
        removeTypingIndicator();
        const aiResponse = generateMockAIResponse(message);
        window.addChatbotMessage(aiResponse, 'ai');
    }, 1000);
};

// Quick Questions
function quickQuestion(question) {
    chatInput.value = question;
    window.sendMessage();
}
window.quickQuestion = quickQuestion;

// Event Listeners
sendBtn.addEventListener('click', window.sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        window.sendMessage();
    }
});

document.querySelectorAll('[data-quick]').forEach(btn => {
    btn.addEventListener('click', () => {
        quickQuestion(btn.getAttribute('data-quick'));
    });
});

// Initial welcome message
window.addEventListener('load', () => {
    // Clears default messages (if there is static HTML) and inserts the bot's message.
    messagesDiv.innerHTML = '';
    window.addChatbotMessage(
        "Hello! I'm your CRM assistant. I can help with:<br>" +
        "• 'What's the total sales this month?'<br>" +
        "• 'Show top 5 accounts by value'<br>" +
        "• 'How many deals are in negotiation?'<br>" +
        "• 'Which sales rep sold the most?'", 
        'ai'
    );
});