// Time update
function updateTime() {
    const now = new Date();
    document.getElementById('time-display').innerText = now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();

// Pywebview or hosted API interaction
let isRunning = false;
const hasPywebview = () => window.pywebview && window.pywebview.api;

window.addEventListener('pywebviewready', function() {
    // Tell python backend that JS is ready
    if(hasPywebview()) {
        window.pywebview.api.ui_ready();
    }
});

function toggleJarvis() {
    if(hasPywebview()) {
        window.pywebview.api.toggle_jarvis();
        return;
    }
    const shouldActivate = !isRunning;
    window.setAssistantState(shouldActivate ? 'ACTIVE' : 'IDLE');
    window.addLogEntry(shouldActivate ? 'Web core initialized' : 'Web core paused');
}

function closeJarvis() {
    if(hasPywebview()) {
        window.pywebview.api.close_jarvis();
        return;
    }
    window.setAssistantState('IDLE');
    window.addLogEntry('Web core idle');
}

// Commands from input
document.getElementById('cmd-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const cmd = this.value;
        if(cmd && hasPywebview()) {
            window.pywebview.api.process_manual_command(cmd);
            this.value = '';
        } else if (cmd) {
            processHostedCommand(cmd);
            this.value = '';
        }
    }
});

async function processHostedCommand(cmd) {
    window.addLogEntry(cmd, 'user');
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });
        const data = await response.json();
        window.addLogEntry(data.reply || 'No response');
        if (Array.isArray(data.actions)) {
            data.actions.forEach(action => {
                if (action.type === 'open' && action.url) {
                    window.open(action.url, '_blank', 'noopener');
                }
            });
        }
    } catch (error) {
        const data = processStaticCommand(cmd);
        window.addLogEntry(data.reply || 'Static web core ready');
        if (Array.isArray(data.actions)) {
            data.actions.forEach(action => {
                if (action.type === 'open' && action.url) {
                    window.open(action.url, '_blank', 'noopener');
                }
            });
        }
    }
}

function processStaticCommand(command) {
    const original = command.trim();
    const cmd = original.toLowerCase();
    const now = new Date();

    if (!cmd) {
        return { reply: 'Enter a command.', actions: [] };
    }
    if (cmd.includes('hello') || cmd.includes('hi') || cmd.includes('hey jarvis')) {
        return { reply: 'Hello. Jarvis web core is online.', actions: [] };
    }
    if (cmd.includes('help') || cmd.includes('what can you do')) {
        return { reply: 'Try time, date, joke, search cats, or youtube lo-fi.', actions: [] };
    }
    if (cmd.includes('time')) {
        return { reply: 'The time is ' + now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + '.', actions: [] };
    }
    if (cmd.includes('date') || cmd.includes('today') || cmd.includes('day')) {
        return { reply: 'Today is ' + now.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) + '.', actions: [] };
    }
    if (cmd.includes('joke') || cmd.includes('funny')) {
        const jokes = [
            'Why do programmers prefer dark mode? Because light attracts bugs.',
            'Why do Java developers wear glasses? Because they do not C sharp.',
            'A SQL query walks into a bar and asks: Can I join you?'
        ];
        return { reply: jokes[Math.floor(Math.random() * jokes.length)], actions: [] };
    }

    const youtubePrefixes = ['search youtube for ', 'youtube search ', 'play on youtube ', 'youtube '];
    for (const prefix of youtubePrefixes) {
        if (cmd.startsWith(prefix)) {
            const query = original.slice(prefix.length).trim();
            return {
                reply: 'Opening YouTube results for ' + query + '.',
                actions: [{ type: 'open', url: 'https://www.youtube.com/results?search_query=' + encodeURIComponent(query) }]
            };
        }
    }

    const searchPrefixes = ['search for ', 'search ', 'google search ', 'google for ', 'look up ', 'find '];
    for (const prefix of searchPrefixes) {
        if (cmd.startsWith(prefix)) {
            const query = original.slice(prefix.length).trim();
            return {
                reply: 'Opening Google results for ' + query + '.',
                actions: [{ type: 'open', url: 'https://www.google.com/search?q=' + encodeURIComponent(query) }]
            };
        }
    }

    return { reply: 'Static web core can handle time, date, jokes, Google search, and YouTube search.', actions: [] };
}

async function refreshHostedStats() {
    if (hasPywebview()) return;
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        window.updateSystemStats(data.cpu || 0, data.ram || 0, data.battery, data.plugged);
    } catch (error) {
        window.updateSystemStats(0, 0, null, false);
    }
}

// Functions exposed to Python backend via window object
window.updateSystemStats = function(cpu, ram, battery, plugged) {
    document.getElementById('cpu-val').innerText = Math.round(cpu) + '%';
    document.getElementById('cpu-bar').style.width = cpu + '%';
    
    document.getElementById('ram-val').innerText = Math.round(ram) + '%';
    document.getElementById('ram-bar').style.width = ram + '%';
    
    if(battery !== null) {
        document.getElementById('bat-val').innerText = (plugged ? '⚡ ' : '') + Math.round(battery) + '%';
        document.getElementById('bat-bar').style.width = battery + '%';
    }
};

setInterval(refreshHostedStats, 5000);
refreshHostedStats();

window.addLogEntry = function(text, type='system') {
    const container = document.getElementById('log-container');
    const div = document.createElement('div');
    div.className = 'log-entry ' + type;
    div.innerText = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    
    // Keep max 50 entries
    while(container.children.length > 50) {
        container.removeChild(container.firstChild);
    }
};

window.setAssistantState = function(state) {
    const btn = document.getElementById('toggle-btn');
    const statusInd = document.getElementById('system-status');
    const core = document.getElementById('voice-core');
    const statusText = document.querySelector('.glitch-text');
    
    if (state === 'LISTENING' || state === 'ACTIVE') {
        isRunning = true;
        btn.innerText = 'PAUSE CORE';
        btn.classList.add('active');
        statusInd.classList.add('listening');
        core.classList.add('active');
        statusText.setAttribute('data-text', 'LISTENING...');
        statusText.innerText = 'LISTENING...';
    } else if (state === 'PAUSED' || state === 'IDLE') {
        isRunning = false;
        btn.innerText = 'INITIALIZE';
        btn.classList.remove('active');
        statusInd.classList.remove('listening');
        core.classList.remove('active');
        statusText.setAttribute('data-text', 'SYSTEM STANDBY');
        statusText.innerText = 'SYSTEM STANDBY';
    }
};
