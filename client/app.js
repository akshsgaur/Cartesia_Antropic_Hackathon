// RepoBuddy Client

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// --- State ---
let ws = null;
let audioCtx = null;
let micStream = null;
let micProcessor = null;
let isRecording = false;
let playbackQueue = [];
let isPlaying = false;

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

// --- WebSocket ---
function connect() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${proto}//${location.host}/ws`);

  ws.onopen = () => {
    statusDot.classList.add('connected');
    statusText.textContent = 'Connected';
  };

  ws.onclose = () => {
    statusDot.classList.remove('connected');
    statusText.textContent = 'Disconnected';
    setTimeout(connect, 2000);
  };

  ws.onerror = (e) => {
    console.error('WS error:', e);
  };

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    handleMessage(msg);
  };
}

function send(type, data = {}) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type, ...data }));
  }
}

// --- Message handler ---
function handleMessage(msg) {
  switch (msg.type) {
    case 'transcript':
      handleTranscript(msg);
      break;
    case 'response_text':
      handleResponse(msg);
      break;
    case 'audio_chunk':
      handleAudioChunk(msg);
      break;
    case 'audio_done':
      handleAudioDone(msg);
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
    case 'session_info':
      handleSessionInfo(msg);
      break;
    case 'mode_changed':
      handleModeChanged(msg);
      break;
    case 'curriculum':
      handleCurriculum(msg);
      break;
    case 'session_ended':
      // Server ended session (e.g. user said "goodbye")
      stopMic();
      addMessage('system', 'Session ended. Goodbye!');
      break;
    case 'error':
      console.error('Server error:', msg.message);
      addMessage('system', `Error: ${msg.message}`);
      break;
  }
}

function handleTranscript(msg) {
  if (msg.is_final) {
    interimTranscript.classList.add('hidden');
    interimTranscript.textContent = '';
    addMessage('user', msg.text);
  } else {
    interimTranscript.classList.remove('hidden');
    interimTranscript.textContent = msg.text;
  }
}

function handleResponse(msg) {
  const el = document.createElement('div');
  el.className = 'message assistant';

  let html = '';
  // Only show detailed_answer if it's meaningfully different from voice_answer
  const voice = msg.voice_answer || '';
  const detailed = msg.detailed_answer || '';
  const isDifferent = detailed && detailed.length > voice.length * 1.3;

  if (isDifferent) {
    // Show both: voice summary + detailed markdown
    html += `<div class="detailed">${renderMarkdown(detailed)}</div>`;
  } else if (voice) {
    html += `<div class="voice-answer">${escapeHtml(voice)}</div>`;
  } else if (detailed) {
    html += `<div class="detailed">${renderMarkdown(detailed)}</div>`;
  }
  el.innerHTML = html;
  messages.appendChild(el);
  scrollToBottom();
}

function handleAudioChunk(msg) {
  const raw = atob(msg.audio);
  const buf = new ArrayBuffer(raw.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < raw.length; i++) view[i] = raw.charCodeAt(i);
  playbackQueue.push(buf);
  if (!isPlaying) playNext();
}

function handleAudioDone(msg) {
  if (msg.interrupted) {
    playbackQueue = [];
    isPlaying = false;
  }
}

async function playNext() {
  if (playbackQueue.length === 0) {
    isPlaying = false;
    return;
  }
  isPlaying = true;
  const buf = playbackQueue.shift();

  if (!audioCtx) audioCtx = new AudioContext({ sampleRate: 24000 });

  // Convert PCM s16le to float32
  const int16 = new Int16Array(buf);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) {
    float32[i] = int16[i] / 32768;
  }

  const audioBuf = audioCtx.createBuffer(1, float32.length, 24000);
  audioBuf.getChannelData(0).set(float32);

  const source = audioCtx.createBufferSource();
  source.buffer = audioBuf;
  source.connect(audioCtx.destination);
  source.onended = () => playNext();
  source.start();
}

function handleEvidence(msg) {
  const ev = msg.evidence;
  if (!ev) return;

  evidenceContent.innerHTML = '';

  if (ev.snippets && ev.snippets.length > 0) {
    ev.snippets.forEach(s => {
      const item = document.createElement('div');
      item.className = 'evidence-item';
      item.innerHTML = `
        <div class="path">${escapeHtml(s.path)} (lines ${s.start}-${s.end})</div>
        <div class="snippet">${escapeHtml(s.text)}</div>
      `;
      evidenceContent.appendChild(item);
    });
  }

  if (ev.matches && ev.matches.length > 0) {
    ev.matches.slice(0, 10).forEach(m => {
      const item = document.createElement('div');
      item.className = 'evidence-item';
      item.innerHTML = `
        <div class="path">${escapeHtml(m.path)}:${m.line_number}</div>
        <div class="snippet">${escapeHtml(m.line_text)}</div>
      `;
      evidenceContent.appendChild(item);
    });
  }
}

function handleQuest(msg) {
  questPanel.classList.remove('hidden');
  const stars = '★'.repeat(msg.difficulty) + '☆'.repeat(3 - msg.difficulty);
  questContent.innerHTML = `
    <div class="quest-panel">
      <div class="quest-title">${escapeHtml(msg.title)}</div>
      <div class="quest-desc">${escapeHtml(msg.description)}</div>
      <div class="difficulty">${stars}</div>
    </div>
  `;
}

function handleQuestResult(msg) {
  const el = document.createElement('div');
  el.className = `quest-result ${msg.grade}`;
  el.innerHTML = `
    <strong>${msg.grade.toUpperCase()}</strong> (${msg.score}/100)<br>
    ${escapeHtml(msg.feedback)}
  `;
  questResultsList.appendChild(el);
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

function handleModeChanged(msg) {
  $$('.mode-toggle button').forEach(b => b.classList.remove('active'));
  if (msg.mode === 'practice') {
    practiceModeBtn.classList.add('active');
  } else {
    chatModeBtn.classList.add('active');
  }
}

function handleCurriculum(msg) {
  const c = msg.curriculum;
  if (!c) return;

  let html = `<div style="font-size: 14px; font-weight: 500; margin-bottom: 8px;">${escapeHtml(c.title)}</div>`;

  if (c.goals && c.goals.length) {
    c.goals.forEach(g => {
      html += `<div class="curriculum-goal">• ${escapeHtml(g)}</div>`;
    });
  }

  if (c.modules && c.modules.length) {
    html += '<div style="margin-top: 12px;">';
    c.modules.forEach(m => {
      html += `<div class="module-item">
        <div class="name">${escapeHtml(m.name)}</div>
        <div class="topics">${m.topics.map(t => escapeHtml(t)).join(', ')}</div>
      </div>`;
    });
    html += '</div>';
  }

  curriculumContent.innerHTML = html;
}

// --- UI helpers ---
function addMessage(role, text) {
  const el = document.createElement('div');
  el.className = `message ${role}`;
  el.textContent = text;
  messages.appendChild(el);
  scrollToBottom();
}

function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function renderMarkdown(text) {
  // Minimal markdown: code blocks, inline code, bold
  return escapeHtml(text)
    .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
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

    // Use ScriptProcessorNode (simpler than AudioWorklet for hackathon)
    const processor = captureCtx.createScriptProcessor(4096, 1, 1);
    processor.onaudioprocess = (e) => {
      if (!isRecording) return;
      const float32 = e.inputBuffer.getChannelData(0);

      // Simple VAD: compute RMS energy and skip silence
      let sum = 0;
      for (let i = 0; i < float32.length; i++) sum += float32[i] * float32[i];
      const rms = Math.sqrt(sum / float32.length);
      if (rms < 0.02) return; // below speech threshold — skip

      const int16 = new Int16Array(float32.length);
      for (let i = 0; i < float32.length; i++) {
        const s = Math.max(-1, Math.min(1, float32[i]));
        int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }
      const bytes = new Uint8Array(int16.buffer);
      const b64 = btoa(String.fromCharCode(...bytes));
      send('audio_in', { audio: b64 });
    };

    source.connect(processor);
    processor.connect(captureCtx.destination);
    micProcessor = { processor, source, ctx: captureCtx };
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

// --- Event listeners ---
startSessionBtn.addEventListener('click', () => {
  const repoPath = repoPathInput.value.trim();
  const curriculumId = curriculumIdInput.value.trim();
  if (!repoPath) {
    alert('Please enter a repo path');
    return;
  }
  send('start_session', {
    repo_path: repoPath,
    curriculum_page_id: curriculumId
  });
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
});

chatModeBtn.addEventListener('click', () => send('mode_switch', { mode: 'chat' }));
practiceModeBtn.addEventListener('click', () => send('mode_switch', { mode: 'practice' }));

// --- Init ---
connect();

// Disable microphone button until session starts
micBtn.disabled = true;
micBtn.style.opacity = '0.5';
