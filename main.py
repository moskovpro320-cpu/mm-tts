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

# အသံတစ်မျိုးချင်းစီအတွက် သီးသန့် Preset ပရိုဖိုင်များ
VOICE_PROFILES = {
    "akolay": {"base": "my-MM-ThihaNeural", "pitch": "+0Hz", "rate": "+0%", "name": "အကိုလေး (🇲🇲 - ကျား)"},
    "myamya": {"base": "my-MM-NilarNeural", "pitch": "+0Hz", "rate": "+0%", "name": "မြမြ (🇲🇲 - မ)"},
    "soegyi": {"base": "my-MM-ThihaNeural", "pitch": "-18Hz", "rate": "-6%", "name": "စိုးကြီး (🇲🇲 - ကျား အသံဩဇာ)"},
    "sa_u": {"base": "my-MM-NilarNeural", "pitch": "+15Hz", "rate": "+6%", "name": "စာဥ (🇲🇲 - မ အသံကြည်)"},
    "thakingyi": {"base": "my-MM-ThihaNeural", "pitch": "-28Hz", "rate": "-12%", "name": "သခင်ကြီး (🇲🇲 - ကျား အသံနက်)"},
    "chawsu": {"base": "my-MM-NilarNeural", "pitch": "-6Hz", "rate": "-4%", "name": "ချောစု (🇲🇲 - မ အေးဆေး)"},
    "choupro": {"base": "my-MM-ThihaNeural", "pitch": "+8Hz", "rate": "+12%", "name": "Chou Pro Lay (🇲🇲 - ကျား အသံမြန်)"},
    "kayinma": {"base": "my-MM-NilarNeural", "pitch": "+8Hz", "rate": "-2%", "name": "ကရင်မ (🇲🇲 - မ သွက်လက်)"},
    "tetpu": {"base": "my-MM-ThihaNeural", "pitch": "+22Hz", "rate": "+8%", "name": "တက်ပု (🇲🇲 - ကျား အသံစူး)"},
    "nyapsi": {"base": "my-MM-NilarNeural", "pitch": "-14Hz", "rate": "-8%", "name": "ညှပ်စိ (🇲🇲 - မ အသံနက်)"},
    "tatei": {"base": "my-MM-ThihaNeural", "pitch": "-35Hz", "rate": "-15%", "name": "တာတေ (🇲🇲 - ကျား သည်းထိတ်ရင်ဖို)"},
    "james": {"base": "en-US-GuyNeural", "pitch": "+0Hz", "rate": "+0%", "name": "ဂျိမ်း (🇺🇸 - ကျား)"},
    "sophia": {"base": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "+0%", "name": "ဆိုဖီယာ (🇺🇸 - မ)"},
    "michael": {"base": "en-GB-RyanNeural", "pitch": "+0Hz", "rate": "+0%", "name": "မိုက်ကယ် (🇬🇧 - ကျား)"},
    "emma": {"base": "en-GB-SoniaNeural", "pitch": "+0Hz", "rate": "+0%", "name": "ဂျနီဖာ (🇬🇧 - မ)"}
}

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
    .voice-control-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .voice-badge {
      background: #0e2238;
      color: #38bdf8;
      font-weight: 700;
      font-size: 13px;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid #1e3a5f;
      white-space: nowrap;
    }
    .play-sample-btn {
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: #083344;
      border: 1px solid #0e7490;
      color: #38bdf8;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 16px;
      flex-shrink: 0;
      transition: background 0.2s;
    }
    .play-sample-btn:active {
      transform: scale(0.95);
      background: #0e7490;
      color: #fff;
    }
    .voice-hint {
      font-size: 12px;
      color: #64748b;
      margin-top: 4px;
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
  </style>
</head>
<body>

  <div class="wrapper">
    <div class="top-bar">
      <div class="brand">
        <div class="brand-icon">M</div>
        <div class="brand-name">MM TTS SRT</div>
      </div>
      <div class="gear-btn">⚙</div>
    </div>

    <!-- Login Area -->
    <div id="loginArea" style="display: flex; flex-direction: column; gap: 16px;">
      <div class="hero-section">
        <div class="hero-tags">FASTAPI • EDGE • MULTI-VOICE • SRT</div>
        <h1 class="hero-title">စာသားကနေ အသံနဲ့ SRT ကို တစ်နေရာတည်းမှာ ဖန်တီးပါ</h1>
        <p class="hero-desc">Browser history နဲ့ စက်အားလုံးအတွက် အဆင်ပြေတဲ့ responsive workspace ဖြစ်ပါတယ်။</p>
        <div class="pills">
          <div class="pill">MP3 + SRT</div>
          <div class="pill">40ကျော် Voices</div>
          <div class="pill">Voice Preview</div>
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
          <select id="engineSel">
            <option value="group">အကိုလေး၊ မြမြ တို့အုပ်စု</option>
            <option value="gemini">Gemini API</option>
          </select>
        </div>

        <div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span class="label" style="margin: 0;">Voices (အသံရွေးချယ်ပါ)</span>
            <span style="font-size: 12px; color: #64748b;">[V1] မှ [V10] ထိ အသုံးပြုနိုင်သည်</span>
          </div>

          <div class="voice-control-row">
            <div class="voice-badge">V1</div>
            <select id="voiceKeySel" onchange="onVoiceChange()">
              <option value="akolay">အကိုလေး (🇲🇲 - ကျား)</option>
              <option value="myamya">မြမြ (🇲🇲 - မ)</option>
              <option value="soegyi">စိုးကြီး (🇲🇲 - ကျား အသံဩဇာ)</option>
              <option value="sa_u">စာဥ (🇲🇲 - မ အသံကြည်)</option>
              <option value="thakingyi">သခင်ကြီး (🇲🇲 - ကျား အသံနက်)</option>
              <option value="chawsu">ချောစု (🇲🇲 - မ အေးဆေး)</option>
              <option value="choupro">Chou Pro Lay (🇲🇲 - ကျား အသံမြန်)</option>
              <option value="kayinma">ကရင်မ (🇲🇲 - မ သွက်လက်)</option>
              <option value="tetpu">တက်ပု (🇲🇲 - ကျား အသံစူး)</option>
              <option value="nyapsi">ညှပ်စိ (🇲🇲 - မ အသံနက်)</option>
              <option value="tatei">တာတေ (🇲🇲 - ကျား သည်းထိတ်ရင်ဖို)</option>
              <option value="james">ဂျိမ်း (🇺🇸 - ကျား)</option>
              <option value="sophia">ဆိုဖီယာ (🇺🇸 - မ)</option>
              <option value="michael">မိုက်ကယ် (🇬🇧 - ကျား)</option>
              <option value="emma">ဂျနီဖာ (🇬🇧 - မ)</option>
            </select>
            <button class="play-sample-btn" id="previewBtn" onclick="playVoicePreview()" title="နမူနာအသံ နားထောင်မည်">▶</button>
          </div>
          <div class="voice-hint">နမူနာအသံကို နားထောင်ရန် ခလုတ်ကို ကိုယ်တိုင်နှိပ်ပြီး ဖွင့်ရပါမည်။</div>
          <audio id="samplePlayer" style="display: none;"></audio>
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
            <option value="recap" selected>Movie Recap (ဇာတ်လမ်းပြော)</option>
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
            <span>Tone</span>
            <span class="slider-val" id="toneVal">0</span>
          </div>
          <input type="range" id="toneSlider" min="-30" max="30" value="0" oninput="updateSliders()">
        </div>

        <div class="slider-wrap">
          <div class="slider-info">
            <span>Speed</span>
            <span class="slider-val" id="speedVal">10</span>
          </div>
          <input type="range" id="speedSlider" min="-30" max="40" value="10" oninput="updateSliders()">
        </div>

        <div class="slider-wrap">
          <div class="slider-info">
            <span>Volume Boost</span>
            <span class="slider-val" id="volVal">10 dB</span>
          </div>
          <input type="range" id="volSlider" min="-10" max="20" value="10" oninput="updateSliders()">
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

    async function playVoicePreview() {
      const vKey = document.getElementById('voiceKeySel').value;
      const btn = document.getElementById('previewBtn');
      const player = document.getElementById('samplePlayer');

      btn.innerText = "⏳";
      btn.disabled = true;

      try {
        const res = await fetch(`/preview?voice_key=${vKey}&password=${encodeURIComponent(savedPin)}`);
        if (!res.ok) throw new Error("Preview မရပါ");

        const data = await res.json();
        const audioBlob = b64toBlob(data.audio_base64, 'audio/mpeg');
        player.src = URL.createObjectURL(audioBlob);
        player.play();
        btn.innerText = "■";

        player.onended = () => {
          btn.innerText = "▶";
          btn.disabled = false;
        };
      } catch (err) {
        alert("နမူနာအသံ ဖွင့်မရပါ");
        btn.innerText = "▶";
        btn.disabled = false;
      }
    }

    function onVoiceChange() {
      const player = document.getElementById('samplePlayer');
      player.pause();
      document.getElementById('previewBtn').innerText = "▶";
      document.getElementById('previewBtn').disabled = false;
    }

    function updateSliders() {
      document.getElementById('toneVal').innerText = document.getElementById('toneSlider').value;
      document.getElementById('speedVal').innerText = document.getElementById('speedSlider').value;
      const vol = document.getElementById('volSlider').value;
      document.getElementById('volVal').innerText = vol + " dB";
    }

    function applyStylePreset() {
      const style = document.getElementById('styleSel').value;
      const t = document.getElementById('toneSlider');
      const s = document.getElementById('speedSlider');
      const v = document.getElementById('volSlider');

      if (style === 'recap') { t.value = 0; s.value = 10; v.value = 10; }
      else if (style === 'story') { t.value = -3; s.value = -5; v.value = 0; }
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
      const vKey = document.getElementById('voiceKeySel').value;
      const userTone = parseInt(document.getElementById('toneSlider').value);
      const userSpeed = parseInt(document.getElementById('speedSlider').value);
      const userVol = parseInt(document.getElementById('volSlider').value);
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
          voice_key: vKey,
          user_pitch: userTone,
          user_speed: userSpeed,
          user_vol: userVol,
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

@app.get("/preview")
async def preview_voice(voice_key: str = "akolay", password: str = ""):
    if password in BLOCKED_KEYS or password not in ALLOWED_PASSWORDS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    profile = VOICE_PROFILES.get(voice_key, VOICE_PROFILES["akolay"])
    sample_text = "မင်္ဂလာပါ ခင်ဗျာ။ ဒါကတော့ နမူနာ အသံစမ်းသပ်ချက် ဖြစ်ပါတယ်။"
    if "en-" in profile["base"]:
        sample_text = "Hello, this is a sample preview voice."

    communicate = edge_tts.Communicate(sample_text, profile["base"], pitch=profile["pitch"], rate=profile["rate"])
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    return {"audio_base64": base64.b64encode(audio_data).decode('utf-8')}

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
    voice_key: str = "akolay",
    user_pitch: int = 0,
    user_speed: int = 10,
    user_vol: int = 10,
    password: str = ""
):
    if password in BLOCKED_KEYS or password not in ALLOWED_PASSWORDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password မှားယွင်းနေပါသည်"
        )

    profile = VOICE_PROFILES.get(voice_key, VOICE_PROFILES["akolay"])

    base_pitch_int = int(re.sub(r'[^-\d]', '', profile["pitch"]) or 0)
    base_rate_int = int(re.sub(r'[^-\d]', '', profile["rate"]) or 0)

    final_pitch = base_pitch_int + user_pitch
    final_rate = base_rate_int + user_speed

    pitch_str = f"{final_pitch:+d}Hz"
    rate_str = f"{final_rate:+d}%"
    vol_str = f"{user_vol:+d}%"

    clean_text = re.sub(r'\[V\d+\]', '', text).strip()
    communicate = edge_tts.Communicate(clean_text, profile["base"], pitch=pitch_str, rate=rate_str, volume=vol_str)
    
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
