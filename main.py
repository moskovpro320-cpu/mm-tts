from fastapi import FastAPI, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import edge_tts

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
      background-color: #060b13;
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px;
    }
    .container {
      width: 100%;
      max-width: 460px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    /* Top Bar */
    .top-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 0;
    }
    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .logo-badge {
      width: 42px;
      height: 42px;
      background: #38bdf8;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: #031326;
    }
    .brand-title {
      font-size: 19px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    /* Hero Header */
    .hero-tags {
      color: #38bdf8;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .hero-title {
      font-size: 32px;
      font-weight: 800;
      line-height: 1.25;
      color: #ffffff;
      margin-bottom: 12px;
    }
    .hero-desc {
      color: #94a3b8;
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 14px;
    }
    .pills {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .pill {
      background: #111a28;
      border: 1px solid #1e293b;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      color: #cbd5e1;
      font-weight: 600;
    }
    /* Card Component */
    .card {
      background: #0d1522;
      border: 1px solid #1e293b;
      border-radius: 20px;
      padding: 24px;
      margin-top: 6px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .card-subtitle {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      color: #38bdf8;
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    .card-title {
      font-size: 22px;
      font-weight: 700;
      color: #ffffff;
    }
    .field-label {
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1px;
      color: #94a3b8;
      margin-bottom: 8px;
      text-transform: uppercase;
    }
    input[type="password"], textarea, select {
      width: 100%;
      background: #060b13;
      border: 1px solid #1e293b;
      border-radius: 12px;
      color: #ffffff;
      padding: 14px 16px;
      font-size: 15px;
      font-family: inherit;
      outline: none;
      transition: border-color 0.2s;
    }
    input[type="password"]:focus, textarea:focus, select:focus {
      border-color: #38bdf8;
    }
    textarea { height: 130px; resize: vertical; margin-bottom: 12px; }
    select { margin-bottom: 12px; }
    .btn-submit {
      width: 100%;
      background: #38bdf8;
      color: #031326;
      border: none;
      border-radius: 12px;
      padding: 14px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 16px;
      font-family: inherit;
      transition: opacity 0.2s, transform 0.1s;
    }
    .btn-submit:active { transform: scale(0.98); }
    .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
    .logout-btn {
      background: #ef4444;
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }
    #error-msg, #status {
      margin-top: 12px;
      text-align: center;
      font-size: 14px;
      min-height: 20px;
    }
    audio { width: 100%; margin-top: 16px; }
  </style>
</head>
<body>

  <div class="container">
    <!-- Top Navigation -->
    <div class="top-nav">
      <div class="brand-wrap">
        <div class="logo-badge">M</div>
        <div class="brand-title">MM TTS SRT</div>
      </div>
    </div>

    <!-- Hero Header Banner -->
    <div class="hero-section">
      <div class="hero-tags">FASTAPI • EDGE • GEMINI</div>
      <h1 class="hero-title">စာသားကနေ အသံနဲ့ SRT ကို တစ်နေရာတည်းမှာ ဖန်တီးပါ</h1>
      <p class="hero-desc">Browser history နဲ့ စက်အားလုံးအတွက် အဆင်ပြေတဲ့ responsive workspace ဖြစ်ပါတယ်။</p>
      <div class="pills">
        <div class="pill">MP3 + SRT</div>
        <div class="pill">40ကျော် Voices</div>
        <div class="pill">IndexedDB</div>
      </div>
    </div>

    <!-- Login Card Screen -->
    <div class="card" id="loginCard">
      <div class="card-header">
        <div>
          <div class="card-subtitle">VIP ACCESS</div>
          <div class="card-title">အကောင့်ဝင်ရန်</div>
        </div>
        <div style="color: #38bdf8; font-size: 20px;">⚡</div>
      </div>
      <div class="field-label">VIP PIN</div>
      <input type="password" id="inputPin" placeholder="PIN ထည့်ပါ" />
      <button class="btn-submit" id="loginBtn" onclick="handleLogin()">ဝင်ရောက်မည်</button>
      <div id="error-msg"></div>
    </div>

    <!-- TTS Workspace Screen (PIN မှန်မှ ပေါ်မည်) -->
    <div class="card" id="appCard" style="display: none;">
      <div class="card-header">
        <div>
          <div class="card-subtitle">AI WORKSPACE</div>
          <div class="card-title">အသံထုတ်ယူရန်</div>
        </div>
        <button class="logout-btn" onclick="handleLogout()">ထွက်မည်</button>
      </div>

      <div class="field-label">မြန်မာစာ ရိုက်ထည့်ပါ</div>
      <textarea id="txt" placeholder="အသံပြောင်းလိုသော စာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ..."></textarea>
      
      <div class="field-label">အသံရွေးချယ်ပါ</div>
      <select id="vc">
        <option value="my-MM-ThihaNeural">သီဟ (ကျား - Thiha)</option>
        <option value="my-MM-NilarNeural">နီလာ (မ - Nilar)</option>
      </select>

      <button class="btn-submit" id="btn" onclick="gen()">Generate Audio</button>
      <div id="status"></div>
      <audio id="aud" controls style="display:none;"></audio>
    </div>
  </div>

  <script>
    let savedPin = localStorage.getItem("tts_pin") || "";

    if (savedPin) {
      checkSavedPin();
    }

    async function checkSavedPin() {
      try {
        const res = await fetch(`/verify?password=${encodeURIComponent(savedPin)}`);
        if (res.ok) {
          document.getElementById('loginCard').style.display = 'none';
          document.getElementById('appCard').style.display = 'block';
        } else {
          localStorage.removeItem("tts_pin");
          savedPin = "";
        }
      } catch (e) {
        localStorage.removeItem("tts_pin");
      }
    }

    async function handleLogin() {
      const pin = document.getElementById('inputPin').value.trim();
      const err = document.getElementById('error-msg');
      const btn = document.getElementById('loginBtn');

      if (!pin) {
        err.style.color = '#ef4444';
        err.innerText = "PIN အရင် ရိုက်ထည့်ပေးပါ";
        return;
      }

      btn.disabled = true;
      err.style.color = '#38bdf8';
      err.innerText = "စစ်ဆေးနေပါသည်...";

      try {
        const res = await fetch(`/verify?password=${encodeURIComponent(pin)}`);
        if (res.ok) {
          savedPin = pin;
          localStorage.setItem("tts_pin", pin);
          err.innerText = "";
          document.getElementById('loginCard').style.display = 'none';
          document.getElementById('appCard').style.display = 'block';
        } else {
          err.style.color = '#ef4444';
          err.innerText = "PIN မှားယွင်းနေပါသည်။ ပြန်လည်စစ်ဆေးပါ။";
        }
      } catch (e) {
        err.style.color = '#ef4444';
        err.innerText = "ဆာဗာနှင့် ချိတ်ဆက်၍ မရပါ";
      } finally {
        btn.disabled = false;
      }
    }

    function handleLogout() {
      localStorage.removeItem("tts_pin");
      savedPin = "";
      document.getElementById('inputPin').value = "";
      document.getElementById('error-msg').innerText = "";
      document.getElementById('appCard').style.display = 'none';
      document.getElementById('loginCard').style.display = 'block';
    }

    async function gen() {
      const text = document.getElementById('txt').value.trim();
      const voice = document.getElementById('vc').value;
      const btn = document.getElementById('btn');
      const status = document.getElementById('status');
      const aud = document.getElementById('aud');

      if (!text) { 
        status.style.color = '#ef4444';
        status.innerText = "စာအရင် ရိုက်ထည့်ပါ"; 
        return; 
      }

      btn.disabled = true;
      aud.style.display = 'none';
      status.style.color = '#38bdf8';
      status.innerText = "အသံဖိုင် ဖန်တီးနေပါသည်... ခဏစောင့်ပါ...";

      try {
        const res = await fetch(`/tts?text=${encodeURIComponent(text)}&voice=${voice}&password=${encodeURIComponent(savedPin)}`);
        
        if (res.status === 401) {
          handleLogout();
          document.getElementById('error-msg').style.color = '#ef4444';
          document.getElementById('error-msg').innerText = "စကားဝှက် သက်တမ်းကုန်သွားပါပြီ (သို့မဟုတ် အပိတ်ခံရပါသည်)။";
          throw new Error("PIN မှားယွင်းနေပါသည်");
        }
        if (!res.ok) throw new Error("အသံထုတ်မရပါ");
        
        const blob = await res.blob();
        aud.src = URL.createObjectURL(blob);
        aud.style.display = 'block';
        aud.play();
        status.style.color = '#22c55e';
        status.innerText = "အသံဖိုင် ရပါပြီ။ နားဆင်/ဒေါင်းလုဒ် ဆွဲနိုင်ပါပြီ။";
      } catch (e) {
        if (res?.status !== 401) {
          status.style.color = '#ef4444';
          status.innerText = e.message;
        }
      } finally {
        btn.disabled = false;
      }
    }
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

@app.get("/tts")
async def tts(text: str, voice: str = "my-MM-ThihaNeural", password: str = ""):
    if password in BLOCKED_KEYS or password not in ALLOWED_PASSWORDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password မှားယွင်းနေပါသည် သို့မဟုတ် ပိတ်ထားပါသည်"
        )
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return Response(content=audio_data, media_type="audio/mpeg")
