let currentLang = 'en';
let chatHistory = [];

function changeLanguage() {
    currentLang = document.getElementById('lang-select').value;
    const input = document.getElementById('user-input');
    if (currentLang === 'hi') {
        input.placeholder = "Apne lakshan likhein (jaise: '2 din se tez bukhar hai', 'pet mein jalan')...";
    } else if (currentLang === 'bn') {
        input.placeholder = "আপনার লক্ষণগুলি লিখুন (যেমন: 'জ্বর এবং সর্দি')...";
    } else {
        input.placeholder = "Describe your symptoms in English (e.g., 'Fever and chills for 2 days')...";
    }
}

async function sendQuery(queryText) {
    if (!queryText.trim()) return;

    appendUserMessage(queryText);
    document.getElementById('user-input').value = '';

    // Show typing indicator
    const streamContainer = document.getElementById('chat-stream');
    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = "flex items-start gap-3 bg-slate-950/60 p-4 rounded-2xl border border-slate-800/50 mr-12 text-xs text-slate-400";
    loadingDiv.innerHTML = `
        <div class="w-8 h-8 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center shrink-0 font-bold">🌿</div>
        <div class="flex items-center gap-1.5 py-1">
            <span class="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></span>
            <span>Retrieving verified clinical guidelines...</span>
        </div>
    `;
    streamContainer.appendChild(loadingDiv);
    streamContainer.scrollTop = streamContainer.scrollHeight;

    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryText, language: currentLang })
        });

        const res = await resp.json();
        const loadElem = document.getElementById(loadingId);
        if (loadElem) loadElem.remove();

        if (res.status === 'success') {
            const data = res.data;
            chatHistory.push(data);
            appendBotMessage(data);
            updateTriageCard(data.triage);

            if (data.triage && data.triage.level === 'EMERGENCY') {
                document.getElementById('emergency-banner').classList.remove('hidden');
            }
        }
    } catch (err) {
        console.error("Chat Error:", err);
        const loadElem = document.getElementById(loadingId);
        if (loadElem) loadElem.remove();
        appendBotMessage({
            response: "I encountered an issue connecting to the clinical knowledge base. Please try again.",
            disclaimer: "System error.",
            citations: [],
            follow_up_questions: []
        });
    }
}

function appendUserMessage(text) {
    const stream = document.getElementById('chat-stream');
    const msgDiv = document.createElement('div');
    msgDiv.className = "flex items-start gap-3 bg-teal-950/40 p-4 rounded-2xl border border-teal-800/40 ml-12 text-xs";
    msgDiv.innerHTML = `
        <div class="w-8 h-8 rounded-xl bg-teal-500/20 text-teal-300 flex items-center justify-center shrink-0 font-bold">👤</div>
        <div class="space-y-1 text-slate-200">
            <span class="font-bold text-teal-400 block text-xs">Patient Query</span>
            <div>${escapeHtml(text)}</div>
        </div>
    `;
    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

function appendBotMessage(data) {
    const stream = document.getElementById('chat-stream');
    const msgDiv = document.createElement('div');
    msgDiv.className = "flex items-start gap-3 bg-slate-950/80 p-4 rounded-2xl border border-slate-800/80 mr-4 text-xs";

    const renderedMarkdown = marked.parse(data.response || '');
    let followUpPills = '';
    if (data.follow_up_questions && data.follow_up_questions.length > 0) {
        followUpPills = `
            <div class="pt-2 border-t border-slate-800/80 mt-3">
                <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block mb-1.5">Suggested Follow-ups:</span>
                <div class="flex flex-wrap gap-1.5">
                    ${data.follow_up_questions.map(q => `<button onclick="sendQuickQuery('${escapeHtml(q)}')" class="bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-teal-500/40 text-slate-300 px-2.5 py-1 rounded-lg text-[11px] transition-all text-left">💬 ${escapeHtml(q)}</button>`).join('')}
                </div>
            </div>
        `;
    }

    msgDiv.innerHTML = `
        <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-600 text-white flex items-center justify-center shrink-0 font-bold shadow-md shadow-teal-500/20">🌿</div>
        <div class="space-y-2 flex-1 text-slate-300">
            <div class="flex items-center justify-between">
                <span class="font-bold text-teal-400 text-xs">Nirmaya Clinical Guide</span>
                <span class="text-[10px] text-slate-500 font-mono">${data.latency_ms || 12}ms</span>
            </div>
            <div class="markdown-body leading-relaxed">${renderedMarkdown}</div>
            <div class="bg-amber-500/10 border border-amber-500/20 text-amber-300/90 p-2 rounded-lg text-[10px]">
                ${escapeHtml(data.disclaimer)}
            </div>
            ${followUpPills}
        </div>
    `;

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
    lucide.createIcons();
}

function updateTriageCard(triage) {
    if (!triage) return;
    const badge = document.getElementById('triage-badge');
    const advice = document.getElementById('triage-advice');

    badge.innerText = triage.badge;
    if (triage.level === 'EMERGENCY') {
        badge.className = "inline-block bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-bold px-3 py-1 rounded-full animate-pulse";
    } else if (triage.level === 'MODERATE') {
        badge.className = "inline-block bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-bold px-3 py-1 rounded-full";
    } else {
        badge.className = "inline-block bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold px-3 py-1 rounded-full";
    }
    advice.innerText = triage.action_advice || "Supportive home care and monitoring.";
}

function sendQuickQuery(text) {
    sendQuery(text);
}

function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('user-input');
    const query = input.value.trim();
    if (query) {
        sendQuery(query);
    }
}

function dismissEmergency() {
    document.getElementById('emergency-banner').classList.add('hidden');
}

async function exportConsultationNote() {
    if (chatHistory.length === 0) {
        alert("Please ask a symptom question first to generate a consultation summary.");
        return;
    }
    const resp = await fetch('/api/export-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_name: "Patient", query_history: chatHistory })
    });
    const html = await resp.text();
    const win = window.open("", "_blank");
    win.document.write(html);
    win.document.close();
}

function escapeHtml(string) {
    return String(string || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
