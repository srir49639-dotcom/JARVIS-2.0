// Time update
function updateTime() {
    const now = new Date();
    document.getElementById('time-display').innerText = now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();

// Pywebview API interaction
let isRunning = false;

window.addEventListener('pywebviewready', function() {
    // Tell python backend that JS is ready
    if(window.pywebview && window.pywebview.api) {
        window.pywebview.api.ui_ready();
    }
});

function toggleJarvis() {
    if(window.pywebview && window.pywebview.api) {
        window.pywebview.api.toggle_jarvis();
    }
}

function closeJarvis() {
    if(window.pywebview && window.pywebview.api) {
        window.pywebview.api.close_jarvis();
    }
}

// Commands from input
document.getElementById('cmd-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const cmd = this.value;
        if(cmd && window.pywebview && window.pywebview.api) {
            window.pywebview.api.process_manual_command(cmd);
            this.value = '';
        }
    }
});

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
