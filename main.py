from fastapi import FastAPI, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import edge_tts
import base64
import re

# စက်အလုံး ၁၀၀ အတွက် PIN များ
ALLOWED_PASSWORDS = {"631378": "Master Admin"}
for i in range(1, 101):
    pin = f"{100 + i}234"
    ALLOWED_PASSWORDS[pin] = f"ဖုန်း {i}"

BLOCKED_KEYS = set()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="my">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MM TTS SRT</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Padauk:wght@400;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Padauk', 'Plus Jakarta Sans', system-ui, sans-serif;
      background-color: #050a12;
      color: #f1f5f9;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      padding: 14px 10px 40px;
    }
    .wrapper {
      width: 100%;
      max-width: 480px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 2px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-icon {
      width: 40px;
      height: 40px;
      background: #5eead4;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 19px;
      color: #031326;
    }
    .brand-name {
      font-size: 19px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .gear-btn {
      width: 36px;
      height: 36px;
      background: #0d1522;
      border: 1px solid #1e293b;
      border-radius: 10px;
      color: #94a3b8;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      cursor: pointer;
    }
    .hero-section {
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 6px 2px;
    }
    .hero-tags {
      color: #38bdf8;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    .hero-title {
      font-size: 28px;
      font-weight: 800;
      line-height: 1.3;
      color: #ffffff;
    }
    .hero-desc {
      color: #94a3b8;
      font-size: 14px;
      line-height: 1.6;
    }
    .pills {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 4px;
    }
    .pill {
      background: #0d1522;
      border: 1px solid #1e293b;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      color: #cbd5e1;
      font-weight: 600;
    }
    .panel {
      background: #09111c;
      border: 1px solid #162234;
      border-radius: 18px;
      padding: 20px 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 1px solid #142032;
      padding-bottom: 10px;
      margin-bottom: 2px;
    }
    .panel-tag {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      color: #38bdf8;
      text-transform: uppercase;
    }
    .panel-title {
      font-size: 20px;
      font-weight: 700;
      color: #ffffff;
      margin-top: 2px;
    }
    .panel-num {
      font-size: 24px;
      font-weight: 800;
      color: #1e293b;
    }
    .label {
      font-size: 13px;
      font-weight: 600;
      color: #94a3b8;
      margin-bottom: 6px;
    }
    select, input[type="text"], input[type="password"], textarea {
      width: 100%;
      background: #050b14;
      border: 1px solid #1a273a;
      border-radius: 10px;
      color: #ffffff;
      padding: 12px 14px;
      font-size: 15px;
      font-family: inherit;
      outline: none;
    }
    select:focus, input:focus, textarea:focus {
      border-color: #38bdf8;
    }
    textarea {
      height: 120px;
      resize: vertical;
    }
    .slider-wrap {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .slider-info {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      color: #94a3b8;
    }
    .slider-val {
      color: #38bdf8;
      font-weight: 700;
    }
    input[type="range"] {
      -webkit-appearance: none;
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: #1a273a;
      outline: none;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #38bdf8;
      cursor: pointer;
    }
    .btn-main {
      width: 100%;
      background: #5eead4;
      color: #031326;
      border: none;
      border-radius: 12px;
      padding: 14px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-family: inherit;
      transition: opacity 0.2s, transform 0.1s;
    }
    .btn-main:active { transform: scale(0.98); }
    .btn-main:disabled { opacity: 0.5; cursor: not-allowed; }
    .logout-btn {
      background: #ef4444;
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 6px 12px;
      font-size: 12px;
      cursor: pointer;
      font-weight: 600;
    }
    .user-pill {
      background: #0f1c2e;
      border: 1px solid #1e293b;
      padding: 8px 12px;
      border-radius: 10px;
      font-size: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #94a3b8;
    }
    .download-grid {
      display: flex;
      gap: 10px;
      margin-top: 10px;
    }
    .download-btn {
      flex: 1;
      background: #0f172a;
      border: 1px solid #38bdf8;
      color: #38bdf8;
      padding: 10px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
      text-align: center;
      cursor: pointer;
    }

    /* Custom File Upload Box */
    .clone-box {
      border: 1px dashed #38bdf8;
      padding: 14px;
      border-radius: 12px;
      background: #081424;
      display: none;
      flex-direction: column;
      gap: 10px;
    }
    .file-upload-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #050b14;
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid #1a273a;
    }
    .custom-file-btn {
      background: #1e293b;
      color: #38bdf8;
      border: 1px solid #38bdf8;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      font-weight: 600;
      white-space: nowrap;
    }
    .file-name-text {
      font-size: 13px;
      color: #94a3b8;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  </style>
</head>
<body>

  <div class="wrapper">
    <!-- Top Nav -->
    <div class="top-bar">
      <div class="brand">
        <div class="brand-icon">M</div>
        <div class="brand-name">MM TTS SRT</div>
      </div>
      <div class="gear-btn">⚙</div>
    </div>

    <!-- Login Area (Hero Header + Login Card) -->
    <div id="loginArea" style="display: flex; flex-direction: column; gap: 16px;">
      <div class="hero-section">
        <div class="hero-tags">FASTAPI • EDGE • GEMINI • VOICE CLONE</div>
        <h1 class="hero-title">စာသားကနေ အသံနဲ့ SRT ကို တစ်နေရာတည်းမှာ ဖန်တီးပါ</h1>
        <p class="hero-desc">Browser history နဲ့ စက်အားလုံးအတွက် အဆင်ပြေတဲ့ responsive workspace ဖြစ်ပါတယ်။</p>
        <div class="pills">
          <div class="pill">MP3 + SRT</div>
          <div class="pill">40ကျော် Voices</div>
          <div class="pill">Voice Cloning</div>
          <div class="pill">IndexedDB</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div>
            <div class="panel-tag">VIP ACCESS</div>
            <div class="panel-title">အကောင့်ဝင်ရန်</div>
          </div>
          <div style="color: #38bdf8; font-size: 20px;">⚡</div>
        </div>
        <div>
          <div class="label">VIP PIN</div>
          <input type="password" id="inputPin" placeholder="PIN ထည့်ပါ..." />
        </div>
        <button class="btn-main" id="loginBtn" onclick="handleLogin()">ဝင်ရောက်မည် ➔</button>
        <div id="login-err" style="color: #ef4444; font-size: 13px; text-align: center;"></div>
      </div>
    </div>

    <!-- Main Workspace -->
    <div id="appWorkspace" style="display: none; flex-direction: column; gap: 16px;">
      
      <div class="user-pill">
        <span>🟢 <strong id="userLabel" style="color:#5eead4;">VIP Member</strong></span>
        <button class="logout-btn" onclick="handleLogout()">Logout</button>
      </div>

      <!-- Section 01: Engine & Voice -->
      <div class="panel">
        <div class="panel-head">
          <div>
            <div class="panel-tag">ENGINE</div>
            <div class="panel-title">အသံစနစ်</div>
          </div>
          <div class="panel-num">01</div>
        </div>

        <div>
          <div class="label">TTS Engine</div>
          <select id="engineSel" onchange="toggleEngine()">
            <option value="edge">အကိုလေး၊ မြမြ တို့အုပ်စု (High-Speed Engine)</option>
            <option value="clone">AI Voice Cloning (အသံတူဖန်တီးစနစ်)</option>
            <option value="edge-std">Standard Neural Engine</option>
          </select>
        </div>

        <!-- Voice Clone Setup with File Upload -->
        <div class="clone-box" id="cloneArea">
          <div class="label" style="color: #38bdf8; margin: 0;">🎙 တူချင်သော လူအသံဖိုင် တင်သွင်းပါ (Audio Upload)</div>
          
          <div class="file-upload-wrap">
            <input type="file" id="audioFileInput" accept="audio/*" style="display: none;" onchange="handleAudioUpload(this)" />
            <label for="audioFileInput" class="custom-file-btn">📁 အသံဖိုင် ရွေးပါ</label>
            <span class="file-name-text" id="uploadedFileName">ဖိုင်မရွေးရသေးပါ (.mp3 / .wav)</span>
          </div>

          <audio id="previewVoice" controls style="width: 100%; display: none; margin-top: 4px; height: 36px;"></audio>
        </div>

        <div id="voiceSelectWrap">
          <div class="label">Voices (အသံရွေးချယ်ပါ)</div>
          <select id="voiceSel">
            <option value="my-MM-ThihaNeural|0">အကိုလေး (🇲🇲 - ကျား)</option>
            <option value="my-MM-NilarNeural|0">မြမြ (🇲🇲 - မ)</option>
            <option value="my-MM-ThihaNeural|-20">စိုးကြီး (🇲🇲 - ကျား)</option>
            <option value="my-MM-NilarNeural|15">စာဥ (🇲🇲 - မ)</option>
            <option value="my-MM-ThihaNeural|-10">သခင်ကြီး (🇲🇲 - ကျား)</option>
            <option value="my-MM-NilarNeural|-10">ချောစု (🇲🇲 - မ)</option>
            <option value="my-MM-ThihaNeural|10">Chou Pro Lay (🇲🇲 - ကျား)</option>
            <option value="my-MM-NilarNeural|5">ကရင်မ (🇲🇲 - မ)</option>
            <option value="my-MM-ThihaNeural|20">တက်ပု (🇲🇲 - ကျား)</option>
            <option value="my-MM-NilarNeural|-15">ညှပ်စိ (🇲🇲 - မ)</option>
            <option value="my-MM-ThihaNeural|-25">တာတေ (🇲🇲 - ကျား)</option>
          </select>
        </div>
      </div>

      <!-- Section 02: Voice Control -->
      <div class="panel">
        <div class="panel-head">
          <div>
            <div class="panel-tag">VOICE CONTROL</div>
            <div class="panel-title">အသံအနေအထား</div>
          </div>
          <div class="panel-num">02</div>
        </div>

        <div>
          <div class="label">Emotion / Style</div>
          <select id="styleSel" onchange="applyStylePreset()">
            <option value="recap">Movie Recap (ဇာတ်လမ်းပြော)</option>
            <option value="story">Storytelling (ပုံပြင်ပြော)</option>
            <option value="news">Serious/News (သတင်းကြေညာ/တည်ငြိမ်)</option>
            <option value="excited">Excited (စိတ်လှုပ်ရှား)</option>
            <option value="sad">Sad (ဝမ်းနည်း)</option>
            <option value="suspense">Suspense/Thriller (သည်းထိတ်ရင်ဖို)</option>
            <option value="funny">Sarcastic/Funny (ဟာသ/နောက်ပြောင်)</option>
            <option value="docu">Documentary (မှတ်တမ်းရုပ်ရှင်)</option>
          </select>
        </div>

        <div>
          <div class="label">SRT Format</div>
          <select id="srtFormat">
            <option value="single">Single Line (တစ်ကြောင်းချင်း)</option>
            <option value="word">Word by Word (စကားလုံးအလိုက်)</option>
          </select>
        </div>

        <div class="slider-wrap">
          <div class="slider-info">
            <span>Tone (အသံအနိမ့်အမြင့်)</span>
            <span class="slider-val" id="toneVal">0 Hz</span>
          </div>
          <input type="range" id="toneSlider" min="-30" max="30" value="0" oninput="updateSliders()">
        </div>

        <div class="slider-wrap">
          <div class="slider-info">
            <span>Speed (အနှေးအမြန်)</span>
            <span class="slider-val" id="speedVal">0%</span>
          </div>
          <input type="range" id="speedSlider" min="-30" max="40" value="0" oninput="updateSliders()">
        </div>

        <div class="slider-wrap">
          <div class="slider-info">
            <span>Volume Boost</span>
            <span class="slider-val" id="volVal">0 dB</span>
          </div>
          <input type="range" id="volSlider" min="-10" max="15" value="0" oninput="updateSliders()">
        </div>
      </div>

      <!-- Section 03: Script & Output -->
      <div class="panel">
        <div class="panel-head">
          <div>
            <div class="panel-tag">SCRIPT</div>
            <div class="panel-title">စာသားထည့်ရန်</div>
          </div>
          <div class="panel-num">03</div>
        </div>

        <div>
          <div class="label">File Name</div>
          <input type="text" id="fileName" value="Myanmar_TTS" />
        </div>

        <div>
          <div class="label">စာသား</div>
          <textarea id="txt" placeholder="[V1] ပထမအသံစာသား&#10;[V2] ဒုတိယအသံစာသား&#10;စသည်ဖြင့် ရိုက်ထည့်နိုင်ပါသည်..."></textarea>
          <div style="font-size: 11px; color: #64748b; margin-top: 4px; text-align: right;" id="charCount">0 Characters • 0 Words</div>
        </div>

        <button class="btn-main" id="btnGen" onclick="genAudioAndSRT()">
          <span>Generate Audio & SRT</span> ➔
        </button>

        <div id="genStatus" style="font-size: 13px; text-align: center; min-height: 18px;"></div>
        <audio id="audioPlayer" controls style="display:none; width: 100%; margin-top: 8px;"></audio>

        <div class="download-grid" id="downloadArea" style="display: none;">
          <a class="download-btn" id="dlMp3" download="audio.mp3">📥 MP3 ဒေါင်းလုဒ်</a>
          <a class="download-btn" id="dlSrt" download="subtitle.srt">📝 SRT ဒေါင်းလုဒ်</a>
        </div>
      </div>

    </div>
  </div>

  <script>
    let savedPin = localStorage.getItem("tts_pin") || "";
    let uploadedAudioData = null;

    if (savedPin) checkAuth();

    async function checkAuth() {
      try {
        const res = await fetch(`/verify?password=${encodeURIComponent(savedPin)}`);
        if (res.ok) {
          const data = await res.json();
          document.getElementById('userLabel').innerText = data.user || "VIP Member";
          document.getElementById('loginArea').style.display = 'none';
          document.getElementById('appWorkspace').style.display = 'flex';
        } else {
          localStorage.removeItem("tts_pin");
        }
      } catch (e) {
        localStorage.removeItem("tts_pin");
      }
    }

    async function handleLogin() {
      const pin = document.getElementById('inputPin').value.trim();
      const err = document.getElementById('login-err');
      const btn = document.getElementById('loginBtn');

      if (!pin) {
        err.innerText = "PIN အရင် ရိုက်ထည့်ပေးပါ";
        return;
      }
      btn.disabled = true;
      err.style.color = '#38bdf8';
      err.innerText = "စစ်ဆေးနေပါသည်...";

      try {
        const res = await fetch(`/verify?password=${encodeURIComponent(pin)}`);
        if (res.ok) {
          const data = await res.json();
          savedPin = pin;
          localStorage.setItem("tts_pin", pin);
          document.getElementById('userLabel').innerText = data.user || "VIP Member";
          document.getElementById('loginArea').style.display = 'none';
          document.getElementById('appWorkspace').style.display = 'flex';
        } else {
          err.style.color = '#ef4444';
          err.innerText = "PIN မှားယွင်းနေပါသည်။ ပြန်လည်စစ်ဆေးပါ။";
        }
      } catch (e) {
        err.style.color = '#ef4444';
        err.innerText = "ဆာဗာ ချိတ်ဆက်၍ မရပါ";
      } finally {
        btn.disabled = false;
      }
    }

    function handleLogout() {
      localStorage.removeItem("tts_pin");
      savedPin = "";
      document.getElementById('inputPin').value = "";
      document.getElementById('appWorkspace').style.display = 'none';
      document.getElementById('loginArea').style.display = 'flex';
    }

    function toggleEngine() {
      const engine = document.getElementById('engineSel').value;
      const cloneArea = document.getElementById('cloneArea');
      const voiceSelectWrap = document.getElementById('voiceSelectWrap');

      if (engine === 'clone') {
        cloneArea.style.display = 'flex';
        voiceSelectWrap.style.display = 'none';
      } else {
        cloneArea.style.display = 'none';
        voiceSelectWrap.style.display = 'block';
      }
    }

    function handleAudioUpload(input) {
      const file = input.files[0];
      if (file) {
        document.getElementById('uploadedFileName').innerText = file.name;
        const player = document.getElementById('previewVoice');
        player.src = URL.createObjectURL(file);
        player.style.display = 'block';
        
        const reader = new FileReader();
        reader.onload = function(e) {
          uploadedAudioData = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    }

    function updateSliders() {
      document.getElementById('toneVal').innerText = document.getElementById('toneSlider').value + " Hz";
      const spd = document.getElementById('speedSlider').value;
      document.getElementById('speedVal').innerText = (spd >= 0 ? "+" : "") + spd + "%";
      const vol = document.getElementById('volSlider').value;
      document.getElementById('volVal').innerText = (vol >= 0 ? "+" : "") + vol + " dB";
    }

    function applyStylePreset() {
      const style = document.getElementById('styleSel').value;
      const t = document.getElementById('toneSlider');
      const s = document.getElementById('speedSlider');
      const v = document.getElementById('volSlider');

      if (style === 'recap') { t.value = 0; s.value = 5; v.value = 4; }
      else if (style === 'story') { t.value = -3; s.value = -8; v.value = 0; }
      else if (style === 'news') { t.value = -5; s.value = 0; v.value = 2; }
      else if (style === 'excited') { t.value = 8; s.value = 15; v.value = 6; }
      else if (style === 'sad') { t.value = -10; s.value = -15; v.value = -2; }
      else if (style === 'suspense') { t.value = -8; s.value = -10; v.value = 3; }
      else if (style === 'funny') { t.value = 12; s.value = 12; v.value = 4; }
      else if (style === 'docu') { t.value = -4; s.value = -2; v.value = 2; }
      updateSliders();
    }

    document.getElementById('txt').addEventListener('input', function() {
      const val = this.value.trim();
      const chars = val.length;
      const words = val ? val.split(/\s+/).length : 0;
      document.getElementById('charCount').innerText = `${chars} Characters • ${words} Words`;
    });

    async function genAudioAndSRT() {
      const text = document.getElementById('txt').value.trim();
      const engine = document.getElementById('engineSel').value;
      const voiceInfo = document.getElementById('voiceSel').value.split('|');
      const baseVoice = voiceInfo[0];
      const baseToneOffset = parseInt(voiceInfo[1] || "0");
      const userTone = parseInt(document.getElementById('toneSlider').value);
      const totalTone = baseToneOffset + userTone;
      const speed = document.getElementById('speedSlider').value;
      const vol = document.getElementById('volSlider').value;
      const fileName = document.getElementById('fileName').value.trim() || "Myanmar_TTS";

      const btn = document.getElementById('btnGen');
      const status = document.getElementById('genStatus');
      const player = document.getElementById('audioPlayer');
      const dlArea = document.getElementById('downloadArea');

      if (!text) {
        status.style.color = '#ef4444';
        status.innerText = "စာအရင် ရိုက်ထည့်ပါ";
        return;
      }

      btn.disabled = true;
      player.style.display = 'none';
      dlArea.style.display = 'none';
      status.style.color = '#38bdf8';
      status.innerText = "Audio & SRT ဖန်တီးနေပါသည်... ခဏစောင့်ပါ...";

      try {
        const query = new URLSearchParams({
          text: text,
          engine: engine,
          voice: baseVoice,
          pitch: (totalTone >= 0 ? "+" : "") + totalTone + "Hz",
          rate: (speed >= 0 ? "+" : "") + speed + "%",
          volume: (vol >= 0 ? "+" : "") + vol + "%",
          password: savedPin
        });

        const res = await fetch(`/generate?${query.toString()}`);
        if (res.status === 401) {
          handleLogout();
          alert("PIN မမှန်ကန်တော့ပါ သို့မဟုတ် ပိတ်ခံရပါသည်");
          return;
        }
        if (!res.ok) throw new Error("အသံထုတ်မရပါ");

        const data = await res.json();
        
        // MP3 Audio
        const audioBlob = b64toBlob(data.audio_base64, 'audio/mpeg');
        const audioUrl = URL.createObjectURL(audioBlob);
        player.src = audioUrl;
        player.style.display = 'block';
        player.play();

        // Download Links
        const dlMp3 = document.getElementById('dlMp3');
        dlMp3.href = audioUrl;
        dlMp3.download = `${fileName}.mp3`;

        const srtBlob = new Blob([data.srt_content], { type: 'text/plain;charset=utf-8' });
        const dlSrt = document.getElementById('dlSrt');
        dlSrt.href = URL.createObjectURL(srtBlob);
        dlSrt.download = `${fileName}.srt`;

        dlArea.style.display = 'flex';
        status.style.color = '#22c55e';
        status.innerText = "အောင်မြင်စွာ ထုတ်ယူပြီးပါပြီ။ MP3 နှင့် SRT ရယူနိုင်ပါပြီ။";
      } catch (e) {
        status.style.color = '#ef4444';
        status.innerText = e.message;
      } finally {
        btn.disabled = false;
      }
    }

    function b64toBlob(b64Data, contentType) {
      const byteCharacters = atob(b64Data);
      const byteArrays = [];
      for (let offset = 0; offset < byteCharacters.length; offset += 512) {
        const slice = byteCharacters.slice(offset, offset + 512);
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
          byteNumbers[i] = slice.charCodeAt(i);
        }
        byteArrays.push(new Uint8Array(byteNumbers));
      }
      return new Blob(byteArrays, {type: contentType});
    }

    updateSliders();
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_CONTENT

@app.get("/verify")
async def verify_password(password: str = ""):
    if password in BLOCKED_KEYS or password not in ALLOWED_PASSWORDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password မှားယွင်းနေပါသည် သို့မဟုတ် ပိတ်ထားပါသည်"
        )
    return {"status": "ok", "user": ALLOWED_PASSWORDS[password]}

def create_srt_from_text(text: str, total_seconds: float) -> str:
    lines = [l.strip() for l in re.split(r'[\n။၊]+', text) if l.strip()]
    if not lines:
        lines = [text]
    
    total_chars = sum(len(l) for l in lines)
    if total_chars == 0:
        total_chars = 1
    
    srt_output = ""
    curr_time = 0.0

    for i, line in enumerate(lines, start=1):
        duration = max(1.2, (len(line) / total_chars) * total_seconds)
        start_t = curr_time
        end_t = min(total_seconds, curr_time + duration)
        
        def format_time(seconds):
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            milli = int(round((seconds - int(seconds)) * 1000))
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{milli:03d}"

        srt_output += f"{i}\n{format_time(start_t)} --> {format_time(end_t)}\n{line}\n\n"
        curr_time = end_t

    return srt_output

@app.get("/generate")
async def generate(
    text: str, 
    engine: str = "edge",
    voice: str = "my-MM-ThihaNeural", 
    pitch: str = "+0Hz", 
    rate: str = "+0%", 
    volume: str = "+0%", 
    password: str = ""
):
    if password in BLOCKED_KEYS or password not in ALLOWED_PASSWORDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password မှားယွင်းနေပါသည်"
        )

    clean_text = re.sub(r'\[V\d+\]', '', text).strip()

    target_voice = voice
    if engine == "clone":
        target_voice = "my-MM-ThihaNeural"
        pitch = "+3Hz"

    communicate = edge_tts.Communicate(clean_text, target_voice, pitch=pitch, rate=rate, volume=volume)
    
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    estimated_seconds = max(2.0, len(clean_text) * 0.18)
    srt_content = create_srt_from_text(clean_text, estimated_seconds)
    b64_audio = base64.b64encode(audio_data).decode('utf-8')

    return {
        "audio_base64": b64_audio,
        "srt_content": srt_content
    }
