// ==============================================
// CRM LOGIC - DATA, UI AND GRAPHICS
// ==============================================

// Current active section
let currentSection = 'dashboard';

// Set current date
//document.getElementById('current-date').innerText = new Date().toLocaleDateString('en-US');

// Mock data (in real app, this would come from backend)
let dealsData = [
    { id: 1, account: "TechCorp", amount: 50000, stage: "Proposal", date: "2026-04-01", owner: "John" },
    { id: 2, account: "DataFlow", amount: 75000, stage: "Negotiation", date: "2026-04-02", owner: "Maria" },
    { id: 3, account: "CloudNine", amount: 120000, stage: "Closed Won", date: "2026-03-28", owner: "John" },
    { id: 4, account: "InnoSoft", amount: 35000, stage: "Qualification", date: "2026-04-05", owner: "Peter" },
    { id: 5, account: "SecureNet", amount: 90000, stage: "Closed Won", date: "2026-03-30", owner: "Maria" }
];

let accountsData = [
    { id: 1, name: "TechCorp", segment: "Technology", industry: "Software", deals: 3, totalValue: 150000 },
    { id: 2, name: "DataFlow", segment: "Data", industry: "Analytics", deals: 2, totalValue: 95000 },
    { id: 3, name: "CloudNine", segment: "Cloud", industry: "Infra", deals: 4, totalValue: 280000 }
];

let targetsData = [
    { month: "January", target: 100000, achieved: 85000 },
    { month: "February", target: 120000, achieved: 110000 },
    { month: "March", target: 150000, achieved: 160000 },
    { month: "April", target: 180000, achieved: 95000 }
];

// Expose data for chatbot simulation (window object)
window.dealsData = dealsData;
window.accountsData = accountsData;
window.targetsData = targetsData;

// Show section
function showSection(section) {
    currentSection = section;
    document.getElementById('section-title').innerText = 
        section === 'dashboard' ? 'Dashboard' :
        section === 'deals' ? 'Deals' :
        section === 'accounts' ? 'Accounts' : 'Targets';
    
    if (section === 'dashboard') renderDashboard();
    else if (section === 'deals') renderDeals();
    else if (section === 'accounts') renderAccounts();
    else if (section === 'targets') renderTargets();
}
window.showSection = showSection; // Make global for inline buttons

// Render Dashboard
function renderDashboard() {
    const totalDeals = dealsData.reduce((sum, d) => sum + d.amount, 0);
    const closedWon = dealsData.filter(d => d.stage === 'Closed Won').reduce((sum, d) => sum + d.amount, 0);
    const activeDeals = dealsData.filter(d => d.stage !== 'Closed Won' && d.stage !== 'Closed Lost').length;
    
    const html = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Total Pipeline Value</p>
                        <p class="text-2xl font-bold text-gray-800">$${totalDeals.toLocaleString()}</p>
                    </div>
                    <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-dollar-sign text-blue-600 text-xl"></i>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Closed Won Deals</p>
                        <p class="text-2xl font-bold text-green-600">$${closedWon.toLocaleString()}</p>
                    </div>
                    <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-trophy text-green-600 text-xl"></i>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-500 text-sm">Active Deals</p>
                        <p class="text-2xl font-bold text-orange-600">${activeDeals}</p>
                    </div>
                    <div class="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                        <i class="fas fa-chart-line text-orange-600 text-xl"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold mb-4">Deals by Stage</h3>
                <canvas id="stageChart"></canvas>
            </div>
            
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold mb-4">Target vs Actual</h3>
                <canvas id="targetChart"></canvas>
            </div>
        </div>
        
        <div class="mt-6 bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">Recent Deals</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-2 text-left">Account</th>
                            <th class="px-4 py-2 text-left">Amount</th>
                            <th class="px-4 py-2 text-left">Stage</th>
                            <th class="px-4 py-2 text-left">Date</th>
                            <th class="px-4 py-2 text-left">Owner</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dealsData.slice(0, 5).map(deal => `
                            <tr class="border-t">
                                <td class="px-4 py-2">${deal.account}</td>
                                <td class="px-4 py-2">$${deal.amount.toLocaleString()}</td>
                                <td class="px-4 py-2">
                                    <span class="px-2 py-1 rounded-full text-xs 
                                        ${deal.stage === 'Closed Won' ? 'bg-green-100 text-green-700' : 
                                          deal.stage === 'Proposal' ? 'bg-blue-100 text-blue-700' : 
                                          'bg-yellow-100 text-yellow-700'}">
                                        ${deal.stage}
                                    </span>
                                </td>
                                <td class="px-4 py-2">${deal.date}</td>
                                <td class="px-4 py-2">${deal.owner}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    document.getElementById('content-area').innerHTML = html;
    
    setTimeout(() => {
        renderStageChart();
        renderTargetChart();
    }, 100);
}

function renderStageChart() {
    const stages = dealsData.reduce((acc, deal) => {
        acc[deal.stage] = (acc[deal.stage] || 0) + deal.amount;
        return acc;
    }, {});
    
    const ctx = document.getElementById('stageChart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(stages),
                datasets: [{
                    data: Object.values(stages),
                    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
                }]
            }
        });
    }
}

function renderTargetChart() {
    const ctx = document.getElementById('targetChart')?.getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: targetsData.map(t => t.month),
                datasets: [
                    {
                        label: 'Target',
                        data: targetsData.map(t => t.target),
                        backgroundColor: 'rgba(59, 130, 246, 0.5)'
                    },
                    {
                        label: 'Achieved',
                        data: targetsData.map(t => t.achieved),
                        backgroundColor: 'rgba(16, 185, 129, 0.5)'
                    }
                ]
            }
        });
    }
}

function renderDeals() {
    const html = `
        <div class="bg-white rounded-lg shadow">
            <div class="p-4 border-b flex justify-between items-center">
                <h3 class="text-lg font-semibold">All Deals</h3>
                <button onclick="showNewDealModal()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                    <i class="fas fa-plus"></i> New Deal
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stage</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        ${dealsData.map(deal => `
                            <tr>
                                <td class="px-6 py-4">${deal.account}</td>
                                <td class="px-6 py-4">$${deal.amount.toLocaleString()}</td>
                                <td class="px-6 py-4">Enterprise</td>
                                <td class="px-6 py-4">
                                    <select onchange="updateStage(${deal.id}, this.value)" class="text-sm border rounded px-2 py-1">
                                        <option ${deal.stage === 'Qualification' ? 'selected' : ''}>Qualification</option>
                                        <option ${deal.stage === 'Proposal' ? 'selected' : ''}>Proposal</option>
                                        <option ${deal.stage === 'Negotiation' ? 'selected' : ''}>Negotiation</option>
                                        <option ${deal.stage === 'Closed Won' ? 'selected' : ''}>Closed Won</option>
                                    </select>
                                </td>
                                <td class="px-6 py-4">${deal.date}</td>
                                <td class="px-6 py-4">
                                    <button onclick="deleteDeal(${deal.id})" class="text-red-600 hover:text-red-800">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    document.getElementById('content-area').innerHTML = html;
}
window.renderDeals = renderDeals;

function renderAccounts() {
    const html = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            ${accountsData.map(account => `
                <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
                    <div class="flex items-center justify-between mb-4">
                        <div class="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                            <i class="fas fa-building text-indigo-600 text-xl"></i>
                        </div>
                        <span class="text-xs bg-gray-100 px-2 py-1 rounded">${account.segment}</span>
                    </div>
                    <h3 class="text-lg font-semibold mb-2">${account.name}</h3>
                    <p class="text-sm text-gray-600 mb-2">${account.industry}</p>
                    <div class="border-t pt-3 mt-3">
                        <div class="flex justify-between text-sm">
                            <span class="text-gray-500">Total Deals:</span>
                            <span class="font-semibold">${account.deals}</span>
                        </div>
                        <div class="flex justify-between text-sm mt-1">
                            <span class="text-gray-500">Total Value:</span>
                            <span class="font-semibold">$${account.totalValue.toLocaleString()}</span>
                        </div>
                    </div>
                    <button class="mt-4 w-full bg-indigo-50 text-indigo-600 px-4 py-2 rounded hover:bg-indigo-100 transition">
                        View Details
                    </button>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('content-area').innerHTML = html;
}

function renderTargets() {
    const currentTarget = targetsData[targetsData.length - 1];
    const achievementPercent = (currentTarget.achieved / currentTarget.target * 100).toFixed(1);
    
    const html = `
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">Current Target</h3>
                <button class="text-indigo-600">Edit Target</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <p class="text-gray-500 text-sm">Monthly Target</p>
                    <p class="text-3xl font-bold text-gray-800">$${currentTarget.target.toLocaleString()}</p>
                    <p class="text-gray-500 text-sm mt-2">Achieved</p>
                    <p class="text-2xl font-semibold text-green-600">$${currentTarget.achieved.toLocaleString()}</p>
                </div>
                <div>
                    <div class="relative pt-1">
                        <div class="flex mb-2 items-center justify-between">
                            <div>
                                <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">
                                    Progress
                                </span>
                            </div>
                            <div class="text-right">
                                <span class="text-xs font-semibold inline-block text-indigo-600">
                                    ${achievementPercent}%
                                </span>
                            </div>
                        </div>
                        <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-200">
                            <div style="width:${achievementPercent}%" class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500"></div>
                        </div>
                    </div>
                    <p class="text-sm text-gray-600 mt-4">
                        ${achievementPercent >= 100 ? '🎉 Target achieved! Congratulations!' : 
                          `💰 Need $${(currentTarget.target - currentTarget.achieved).toLocaleString()} more to reach target`}
                    </p>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">Target History</h3>
            <canvas id="historyChart"></canvas>
        </div>
    `;
    document.getElementById('content-area').innerHTML = html;
    
    setTimeout(() => {
        const ctx = document.getElementById('historyChart')?.getContext('2d');
        if (ctx) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: targetsData.map(t => t.month),
                    datasets: [
                        {
                            label: 'Target',
                            data: targetsData.map(t => t.target),
                            borderColor: '#3B82F6',
                            tension: 0.4
                        },
                        {
                            label: 'Achieved',
                            data: targetsData.map(t => t.achieved),
                            borderColor: '#10B981',
                            tension: 0.4
                        }
                    ]
                }
            });
        }
    }, 100);
}

// CRUD Operations
function updateStage(dealId, newStage) {
    const deal = dealsData.find(d => d.id === dealId);
    if (deal) {
        deal.stage = newStage;
        renderDeals();
        // Feedback via Chatbot (using a global function from chatbot.js)
        if (window.addChatbotMessage) {
            window.addChatbotMessage(`Deal ${deal.account} updated to ${newStage}`, 'ai');
        }
    }
}
window.updateStage = updateStage;

function deleteDeal(dealId) {
    if (confirm('Are you sure you want to delete this deal?')) {
        dealsData = dealsData.filter(d => d.id !== dealId);
        renderDeals();
        if (window.addChatbotMessage) {
            window.addChatbotMessage(`Deal successfully removed`, 'ai');
        }
    }
}
window.deleteDeal = deleteDeal;

function showNewDealModal() {
    const account = prompt('Account name:');
    const amount = parseFloat(prompt('Deal amount:'));
    if (account && amount) {
        const newDeal = {
            id: dealsData.length + 1,
            account: account,
            amount: amount,
            stage: 'Qualification',
            date: new Date().toISOString().split('T')[0],
            owner: 'John'
        };
        dealsData.push(newDeal);
        renderDeals();
        if (window.addChatbotMessage) {
            window.addChatbotMessage(`New deal created for ${account} worth $${amount.toLocaleString()}`, 'ai');
        }
    }
}
window.showNewDealModal = showNewDealModal;

// Initialize dashboard
showSection('dashboard');