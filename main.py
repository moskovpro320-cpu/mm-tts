
from fastapi import FastAPI, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import edge_tts

# သတ်မှတ်ထားသော Password
MY_PASSWORD = "631378"

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
  <title>Myanmar AI TTS</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; padding: 16px; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 90vh; }
    .box { width: 100%; max-width: 440px; background: #1e293b; padding: 24px; border-radius: 14px; border: 1px solid #334155; box-sizing: border-box; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
    h2 { color: #38bdf8; text-align: center; margin-top: 0; font-size: 20px; }
    input[type="password"], textarea { width: 100%; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 8px; padding: 12px; box-sizing: border-box; font-size: 15px; }
    textarea { height: 130px; resize: vertical; }
    select, button { width: 100%; padding: 13px; margin-top: 12px; border-radius: 8px; border: none; font-size: 16px; box-sizing: border-box; }
    select { background: #0f172a; color: #fff; border: 1px solid #475569; }
    button { background: #0284c7; color: #fff; font-weight: bold; cursor: pointer; transition: 0.2s; }
    button:active { transform: scale(0.98); }
    button:disabled { background: #64748b; }
    audio { width: 100%; margin-top: 16px; }
    #status, #login-err { margin-top: 12px; text-align: center; font-size: 14px; min-height: 20px; }
    .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .logout-btn { width: auto; padding: 6px 12px; margin: 0; background: #ef4444; font-size: 12px; border-radius: 6px; }
  </style>
</head>
<body>

  <!-- အဆင့် ၁ - Login Box -->
  <div class="box" id="loginBox">
    <h2>🔒 Access Password</h2>
    <p style="color: #94a3b8; font-size: 14px; text-align: center; margin-top: -6px; margin-bottom: 18px;">အသုံးပြုရန် စကားဝှက် ရိုက်ထည့်ပါ</p>
    <input type="password" id="inputPwd" placeholder="Password ရိုက်ထည့်ပါ..." />
    <button onclick="handleLogin()">ဝင်မည် (Enter)</button>
    <div id="login-err"></div>
  </div>

  <!-- အဆင့် ၂ - TTS App Box (Password မှန်မှ ပေါ်မည်) -->
  <div class="box" id="appBox" style="display: none;">
    <div class="header-bar">
      <h2 style="margin: 0;">🇲🇲 Myanmar AI TTS</h2>
      <button class="logout-btn" onclick="handleLogout()">Logout</button>
    </div>
    <textarea id="txt" placeholder="မြန်မာစာ ရိုက်ထည့်ပါ..."></textarea>
    <select id="vc">
      <option value="my-MM-ThihaNeural">သီဟ (ကျား)</option>
      <option value="my-MM-NilarNeural">နီလာ (မ)</option>
    </select>
    <button id="btn" onclick="gen()">Generate Audio</button>
    <div id="status"></div>
    <audio id="aud" controls style="display:none;"></audio>
  </div>

  <script>
    let savedPwd = sessionStorage.getItem("tts_auth") || "";

    if (savedPwd) {
      document.getElementById('loginBox').style.display = 'none';
      document.getElementById('appBox').style.display = 'block';
    }

    function handleLogin() {
      const pwd = document.getElementById('inputPwd').value.trim();
      const err = document.getElementById('login-err');

      if (!pwd) {
        err.style.color = '#ef4444';
        err.innerText = "Password အရင် ရိုက်ထည့်ပါ";
        return;
      }

      savedPwd = pwd;
      sessionStorage.setItem("tts_auth", pwd);
      document.getElementById('loginBox').style.display = 'none';
      document.getElementById('appBox').style.display = 'block';
    }

    function handleLogout() {
      sessionStorage.removeItem("tts_auth");
      savedPwd = "";
      document.getElementById('inputPwd').value = "";
      document.getElementById('login-err').innerText = "";
      document.getElementById('appBox').style.display = 'none';
      document.getElementById('loginBox').style.display = 'block';
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
        const res = await fetch(`/tts?text=${encodeURIComponent(text)}&voice=${voice}&password=${encodeURIComponent(savedPwd)}`);
        
        if (res.status === 401) {
          handleLogout();
          document.getElementById('login-err').style.color = '#ef4444';
          document.getElementById('login-err').innerText = "Password မှားယွင်းနေပါသည်။ ပြန်ရိုက်ပေးပါ။";
          throw new Error("Password မှားယွင်းနေပါသည်");
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

@app.get("/tts")
async def tts(text: str, voice: str = "my-MM-ThihaNeural", password: str = ""):
    if password != MY_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password မှားယွင်းနေပါသည်"
        )
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return Response(content=audio_data, media_type="audio/mpeg")
