// RepoBuddy Client - Calls API + Data WebSocket

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// --- State ---
let ws = null;           // Data WebSocket to our server
let callsWs = null;       // Calls API WebSocket for audio
let audioCtx = null;
let micStream = null;
let micProcessor = null;
let isRecording = false;
let playbackQueue = [];
let isPlaying = false;
let agentId = null;
let accessToken = null;

// --- DOM refs ---
const statusDot = $('#statusDot');
const statusText = $('#statusText');
const sessionSetup = $('#sessionSetup');
const chatArea = $('#chatArea');
const messages = $('#messages');
const interimTranscript = $('#interimTranscript');
const controls = $('#controls');
const micBtn = $('#micBtn');
const stopBtn = $('#stopBtn');
const startSessionBtn = $('#startSessionBtn');
const repoPathInput = $('#repoPathInput');
const curriculumIdInput = $('#curriculumIdInput');
const chatModeBtn = $('#chatModeBtn');
const practiceModeBtn = $('#practiceModeBtn');
const curriculumContent = $('#curriculumContent');
const trailLink = $('#trailLink');
const repoInfo = $('#repoInfo');
const evidenceContent = $('#evidenceContent');
const questPanel = $('#questPanel');
const questContent = $('#questContent');
const questResultsList = $('#questResultsList');

// --- Data WebSocket (to our server) ---
function connectDataWs() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${proto}//${location.host}/ws`);

  ws.onopen = () => {
    statusDot.classList.add('connected');
    statusText.textContent = 'Connected';
  };

  ws.onclose = () => {
    statusDot.classList.remove('connected');
    statusText.textContent = 'Disconnected';
    setTimeout(connectDataWs, 3000);
  };

  ws.onerror = (err) => {
    console.error('WebSocket error:', err);
    statusText.textContent = 'Connection error';
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleMessage(msg);
  };
}

// --- Calls API WebSocket (for audio) ---
async function connectCallsWs() {
  try {
    // Get access token from our server
    const tokenResp = await fetch('/api/token');
    const tokenData = await tokenResp.json();
    accessToken = tokenData.access_token;
    agentId = tokenData.agent_id;

    if (!accessToken || !agentId) {
      throw new Error('Failed to get Calls API credentials');
    }

    // Connect to Calls API
    callsWs = new WebSocket(`wss://api.cartesia.ai/agents/stream/${agentId}`);

    callsWs.onopen = () => {
      console.log('Calls API connected');
      
      // Send start event
      callsWs.send(JSON.stringify({
        event: "start",
        config: { 
          input_format: "pcm_16000",
          output_format: "pcm_24000"
        },
        agent: {
          introduction: "Hey! I'm RepoBuddy. I'm here to help you explore and understand this codebase. What would you like to know?"
        },
        metadata: { 
          server_url: location.origin,
          repo_path: repoPathInput.value,
          curriculum_page_id: curriculumIdInput.value
        }
      }));
    };

    callsWs.onclose = () => {
      console.log('Calls API disconnected');
      callsWs = null;
    };

    callsWs.onerror = (err) => {
      console.error('Calls API error:', err);
    };

    callsWs.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      handleCallsMessage(msg);
    };

  } catch (err) {
    console.error('Failed to connect Calls API:', err);
    addMessage('error', `🎤 Audio Error: ${err.message}`);
  }
}

// --- Message handlers ---
function handleMessage(msg) {
  switch (msg.type) {
    case 'session_info':
      handleSessionInfo(msg);
      break;
    case 'transcript':
      handleTranscript(msg);
      break;
    case 'response_text':
      handleResponseText(msg);
      break;
    case 'evidence':
      handleEvidence(msg);
      break;
    case 'quest':
      handleQuest(msg);
      break;
    case 'quest_result':
      handleQuestResult(msg);
      break;
    case 'curriculum':
      handleCurriculum(msg);
      break;
    case 'mode_changed':
      handleModeChanged(msg);
      break;
    case 'error':
      addMessage('error', `❌ ${msg.message}`);
      break;
  }
}

function handleCallsMessage(msg) {
  switch (msg.event) {
    case 'media_output':
      handleAudioChunk(msg);
      break;
    case 'clear':
      // Barge-in - clear playback queue
      playbackQueue = [];
      isPlaying = false;
      break;
    case 'transcript':
      // Show interim transcript
      if (msg.text) {
        interimTranscript.textContent = msg.text;
      }
      break;
    case 'error':
      console.error('Calls API error:', msg);
      break;
  }
}

function handleAudioChunk(msg) {
  const raw = atob(msg.data);
  const buf = new ArrayBuffer(raw.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < raw.length; i++) view[i] = raw.charCodeAt(i);
  playbackQueue.push(buf);
  if (!isPlaying) playNext();
}

async function playNext() {
  if (playbackQueue.length === 0) {
    isPlaying = false;
    return;
  }

  isPlaying = true;
  const buf = playbackQueue.shift();

  if (!audioCtx) audioCtx = new AudioContext({ sampleRate: 24000 });

  const audioBuffer = audioCtx.createBuffer(1, buf.byteLength / 2, 24000);
  const channelData = audioBuffer.getChannelData(0);
  
  const dataView = new DataView(buf);
  for (let i = 0; i < channelData.length; i++) {
    channelData[i] = dataView.getInt16(i * 2, true) / 32768;
  }

  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioCtx.destination);
  source.onended = () => playNext();
  source.start();
}

// --- UI Message handling ---
function addMessage(type, content) {
  const el = document.createElement('div');
  el.className = `message ${type}`;
  
  if (type === 'user') {
    el.innerHTML = `<div class="user-text">${escapeHtml(content)}</div>`;
  } else if (type === 'assistant') {
    el.innerHTML = `<div class="assistant-text">${renderMarkdown(content)}</div>`;
  } else if (type === 'system') {
    el.innerHTML = `<div class="system-text">${content}</div>`;
  } else if (type === 'error') {
    el.innerHTML = `<div class="error-text">${content}</div>`;
  }
  
  messages.appendChild(el);
  scrollToBottom();
}

function handleSessionInfo(msg) {
  sessionSetup.classList.add('hidden');
  chatArea.classList.remove('hidden');
  controls.classList.remove('hidden');
  
  // Enable microphone button now that session is active
  micBtn.disabled = false;
  micBtn.style.opacity = '1';

  if (msg.trail_url) {
    trailLink.innerHTML = `<a class="trail-link" href="${msg.trail_url}" target="_blank">Open Onboarding Trail</a>`;
  }
  if (msg.repo_summary) {
    repoInfo.innerHTML = `<pre style="font-size: 11px; color: var(--text-muted); white-space: pre-wrap;">${escapeHtml(msg.repo_summary)}</pre>`;
  }

  addMessage('system', `🚀 Session started! Repo: ${msg.repo_path || 'none'}`);
  addMessage('system', '🎤 Ready to listen! Click the microphone button and speak your questions.');
}

function handleResponseText(msg) {
  interimTranscript.textContent = '';
  addMessage('assistant', msg.detailed_answer || msg.voice_answer);
}

function handleEvidence(msg) {
  if (!msg.evidence) return;
  
  const evidence = msg.evidence;
  let html = '<div class="evidence-header">📄 Code Evidence</div>';
  
  if (evidence.matches && evidence.matches.length > 0) {
    html += '<div class="evidence-section">';
    html += '<div class="evidence-title">Search Results</div>';
    evidence.matches.forEach(match => {
      html += `<div class="evidence-item">
        <div class="path">${match.path}:${match.line_number}</div>
        <div class="snippet">${escapeHtml(match.line_text)}</div>
      </div>`;
    });
    html += '</div>';
  }
  
  evidenceContent.innerHTML = html;
}

function handleQuest(msg) {
  questPanel.classList.remove('hidden');
  questContent.innerHTML = `
    <div class="quest-item">
      <div class="quest-title">${msg.title}</div>
      <div class="quest-description">${msg.description}</div>
      <div class="quest-difficulty">Difficulty: ${msg.difficulty}</div>
    </div>
  `;
}

function handleQuestResult(msg) {
  const el = document.createElement('div');
  el.className = 'quest-result';
  el.innerHTML = `
    <div class="quest-grade ${msg.grade}">Grade: ${msg.grade.toUpperCase()}</div>
    <div class="quest-score">Score: ${msg.score}%</div>
    <div class="quest-feedback">${msg.feedback}</div>
  `;
  questResultsList.appendChild(el);
}

function handleCurriculum(msg) {
  if (!msg.curriculum) return;
  
  const curriculum = msg.curriculum;
  let html = '<div class="curriculum-header">📚 Learning Curriculum</div>';
  
  if (curriculum.weeks) {
    curriculum.weeks.forEach(week => {
      html += `<div class="curriculum-week">
        <div class="week-title">Week ${week.number}: ${week.title}</div>
        <div class="week-description">${week.description}</div>
      </div>`;
    });
  }
  
  curriculumContent.innerHTML = html;
}

function handleModeChanged(msg) {
  $$('.mode-toggle button').forEach(b => b.classList.remove('active'));
  if (msg.mode === 'practice') {
    practiceModeBtn.classList.add('active');
  } else {
    chatModeBtn.classList.add('active');
  }
}

// --- Audio capture (toggle mode) ---
function toggleMic() {
  if (isRecording) {
    stopMic();
  } else {
    // Add immediate visual feedback
    micBtn.classList.add('recording');
    micBtn.style.transform = 'scale(1.1)';
    setTimeout(() => {
      micBtn.style.transform = 'scale(1)';
    }, 200);
    
    // Show immediate message to user
    addMessage('system', '🎤 Listening... Speak now!');
    
    startMic();
  }
}

async function startMic() {
  if (isRecording) return;
  isRecording = true;
  micBtn.classList.add('recording');
  micBtn.title = 'Click to stop listening';

  try {
    // Check if mediaDevices is available
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Microphone access not available. Please use a modern browser and access over HTTPS.');
    }

    micStream = await navigator.mediaDevices.getUserMedia({
      audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true, noiseSuppression: true }
    });

    if (!audioCtx) audioCtx = new AudioContext({ sampleRate: 24000 });

    // Create a separate context for capture at 16kHz
    const captureCtx = new AudioContext({ sampleRate: 16000 });
    const source = captureCtx.createMediaStreamSource(micStream);
    const processor = captureCtx.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0);
      const output = new Int16Array(input.length);
      
      for (let i = 0; i < input.length; i++) {
        output[i] = Math.max(-1, Math.min(1, input[i])) * 32767;
      }
      
      // Send to Calls API as media_input
      if (callsWs && callsWs.readyState === WebSocket.OPEN) {
        const base64 = btoa(String.fromCharCode.apply(null, new Uint8Array(output.buffer)));
        callsWs.send(JSON.stringify({
          event: "media_input",
          data: base64
        }));
      }
    };

    source.connect(processor);
    processor.connect(captureCtx.destination);

    micProcessor = { ctx: captureCtx, source, processor };

  } catch (err) {
    console.error('Mic error:', err);
    isRecording = false;
    micBtn.classList.remove('recording');

    // Show user-friendly error message
    const errorMsg = err.message || 'Microphone access denied';
    addMessage('error', `🎤 Microphone Error: ${errorMsg}`);
  }
}

function stopMic() {
  isRecording = false;
  micBtn.classList.remove('recording');
  micBtn.title = 'Click to start listening';
  
  // Add visual feedback when stopping
  micBtn.style.transform = 'scale(0.95)';
  setTimeout(() => {
    micBtn.style.transform = 'scale(1)';
  }, 150);
  
  // Show processing message
  addMessage('system', '🔊 Processing your speech...');

  if (micProcessor) {
    micProcessor.processor.disconnect();
    micProcessor.source.disconnect();
    micProcessor.ctx.close();
    micProcessor = null;
  }
  if (micStream) {
    micStream.getTracks().forEach(t => t.stop());
    micStream = null;
  }
}

// --- Utility functions ---
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function renderMarkdown(text) {
  return text
    .replace(/### (.*)/g, '<h3>$1</h3>')
    .replace(/## (.*)/g, '<h2>$1</h2>')
    .replace(/# (.*)/g, '<h1>$1</h1>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function send(type, data = {}) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    const payload = { type, ...data };
    ws.send(JSON.stringify(payload));
  }
}

// --- Event listeners ---
startSessionBtn.addEventListener('click', async () => {
  const repoPath = repoPathInput.value.trim();
  const curriculumId = curriculumIdInput.value.trim();
  
  send('start_session', {
    repo_path: repoPath,
    curriculum_page_id: curriculumId
  });
  
  // Connect Calls API after session starts
  await connectCallsWs();
});

// Toggle mic on click (not hold)
micBtn.addEventListener('click', () => toggleMic());

stopBtn.addEventListener('click', () => {
  stopMic();
  send('stop_session');
  sessionSetup.classList.remove('hidden');
  chatArea.classList.add('hidden');
  controls.classList.add('hidden');
  messages.innerHTML = '';
  
  // Disable microphone button when session ends
  micBtn.disabled = true;
  micBtn.style.opacity = '0.5';
  
  // Close Calls API
  if (callsWs) {
    callsWs.close();
    callsWs = null;
  }
});

chatModeBtn.addEventListener('click', () => send('mode_switch', { mode: 'chat' }));
practiceModeBtn.addEventListener('click', () => send('mode_switch', { mode: 'practice' }));

// --- Init ---
connectDataWs();

// Disable microphone button until session starts
micBtn.disabled = true;
micBtn.style.opacity = '0.5';
