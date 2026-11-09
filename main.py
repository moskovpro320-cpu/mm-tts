from fastapi import FastAPI, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import edge_tts

# စက်အလုံး ၁၀၀ အတွက် မတူညီသော ၆ လုံးတွဲ PIN Password များ
ALLOWED_PASSWORDS = {
    "631378": "Master Key (ပင်မဖုန်း)",
    "101234": "ဖုန်း ၁",
    "102345": "ဖုန်း ၂",
    "103456": "ဖုန်း ၃",
    "104567": "ဖုန်း ၄",
    "105678": "ဖုန်း ၅",
    "106789": "ဖုန်း ၆",
    "107890": "ဖုန်း ၇",
    "108901": "ဖုန်း ၈",
    "109012": "ဖုန်း ၉",
    "110123": "ဖုန်း ၁၀",
    "111234": "ဖုန်း ၁၁",
    "112345": "ဖုန်း ၁၂",
    "113456": "ဖုန်း ၁၃",
    "114567": "ဖုန်း ၁၄",
    "115678": "ဖုန်း ၁၅",
    "116789": "ဖုန်း ၁၆",
    "117890": "ဖုန်း ၁၇",
    "118901": "ဖုန်း ၁၈",
    "119012": "ဖုန်း ၁၉",
    "120123": "ဖုန်း ၂၀",
    "121234": "ဖုန်း ၂၁",
    "122345": "ဖုန်း ၂၂",
    "123456": "ဖုန်း ၂၃",
    "124567": "ဖုန်း ၂၄",
    "125678": "ဖုန်း ၂၅",
    "126789": "ဖုန်း ၂၆",
    "127890": "ဖုန်း ၂၇",
    "128901": "ဖုန်း ၂၈",
    "129012": "ဖုန်း ၂၉",
    "130123": "ဖုန်း ၃၀",
    "131234": "ဖုန်း ၃၁",
    "132345": "ဖုန်း ၃၂",
    "133456": "ဖုန်း ၃၃",
    "134567": "ဖုန်း ၃၄",
    "135678": "ဖုန်း ၃၅",
    "136789": "ဖုန်း ၃၆",
    "137890": "ဖုန်း ၃၇",
    "138901": "ဖုန်း ၃၈",
    "139012": "ဖုန်း ၃၉",
    "140123": "ဖုန်း ၄၀",
    "141234": "ဖုန်း ၄၁",
    "142345": "ဖုန်း ၄၂",
    "143456": "ဖုန်း ၄၃",
    "144567": "ဖုန်း ၄၄",
    "145678": "ဖုန်း ၄၅",
    "146789": "ဖုန်း ၄၆",
    "147890": "ဖုန်း ၄၇",
    "148901": "ဖုန်း ၄၈",
    "149012": "ဖုန်း ၄၉",
    "150123": "ဖုန်း ၅၀",
    "151234": "ဖုန်း ၅၁",
    "152345": "ဖုန်း ၅၂",
    "153456": "ဖုန်း ၅၃",
    "154567": "ဖုန်း ၅၄",
    "155678": "ဖုန်း ၅၅",
    "156789": "ဖုန်း ၅၆",
    "157890": "ဖုန်း ၅၇",
    "158901": "ဖုန်း ၅၈",
    "159012": "ဖုန်း ၅၉",
    "160123": "ဖုန်း ၆၀",
    "161234": "ဖုန်း ၆၁",
    "162345": "ဖုန်း ၆၂",
    "163456": "ဖုန်း ၆၃",
    "164567": "ဖုန်း ၆၄",
    "165678": "ဖုန်း ၆၅",
    "166789": "ဖုန်း ၆၆",
    "167890": "ဖုန်း ၆၇",
    "168901": "ဖုန်း ၆၈",
    "169012": "ဖုန်း ၆၉",
    "170123": "ဖုန်း ၇၀",
    "171234": "ဖုန်း ၇၁",
    "172345": "ဖုန်း ၇၂",
    "173456": "ဖုန်း ၇၃",
    "174567": "ဖုန်း ၇၄",
    "175678": "ဖုန်း ၇၅",
    "176789": "ဖုန်း ၇၆",
    "177890": "ဖုန်း ၇၇",
    "178901": "ဖုန်း ၇၈",
    "179012": "ဖုန်း ၇၉",
    "180123": "ဖုန်း ၈၀",
    "181234": "ဖုန်း ၈၁",
    "182345": "ဖုန်း ၈၂",
    "183456": "ဖုန်း ၈၃",
    "184567": "ဖုန်း ၈၄",
    "185678": "ဖုန်း ၈၅",
    "186789": "ဖုန်း ၈၆",
    "187890": "ဖုန်း ၈၇",
    "188901": "ဖုန်း ၈၈",
    "189012": "ဖုန်း ၈၉",
    "190123": "ဖုန်း ၉၀",
    "191234": "ဖုန်း ၉၁",
    "192345": "ဖုန်း ၉၂",
    "193456": "ဖုန်း ၉၃",
    "194567": "ဖုန်း ၉၄",
    "195678": "ဖုန်း ၉၅",
    "196789": "ဖုန်း ၉၆",
    "197890": "ဖုန်း ၉၇",
    "198901": "ဖုန်း ၉၈",
    "199012": "ဖုန်း ၉၉",
    "200123": "ဖုန်း ၁၀၀",
}

# ဖုန်းတစ်လုံးကို ပိတ်ချင်ပါက PIN ကို ဤနေရာတွင် ထည့်ပါ (ဥပမာ- BLOCKED_KEYS = {"105678"})
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
    <button id="loginBtn" onclick="handleLogin()">ဝင်မည် (Enter)</button>
    <div id="login-err"></div>
  </div>

  <!-- အဆင့် ၂ - TTS App Box -->
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
    let savedPwd = localStorage.getItem("tts_auth") || "";

    if (savedPwd) {
      checkSavedAuth();
    }

    async function checkSavedAuth() {
      try {
        const res = await fetch(`/verify?password=${encodeURIComponent(savedPwd)}`);
        if (res.ok) {
          document.getElementById('loginBox').style.display = 'none';
          document.getElementById('appBox').style.display = 'block';
        } else {
          localStorage.removeItem("tts_auth");
          savedPwd = "";
        }
      } catch (e) {
        localStorage.removeItem("tts_auth");
      }
    }

    async function handleLogin() {
      const pwd = document.getElementById('inputPwd').value.trim();
      const err = document.getElementById('login-err');
      const btn = document.getElementById('loginBtn');

      if (!pwd) {
        err.style.color = '#ef4444';
        err.innerText = "Password အရင် ရိုက်ထည့်ပါ";
        return;
      }

      btn.disabled = true;
      err.style.color = '#38bdf8';
      err.innerText = "စစ်ဆေးနေပါသည်...";

      try {
        const res = await fetch
