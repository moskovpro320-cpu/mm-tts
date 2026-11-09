from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import edge_tts

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
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; padding: 16px; margin: 0; display: flex; justify-content: center; }
    .box { width: 100%; max-width: 450px; background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; box-sizing: border-box; }
    h2 { color: #38bdf8; text-align: center; margin-top: 0; }
    textarea { width: 100%; height: 120px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 8px; padding: 10px; box-sizing: border-box; font-size: 15px; }
    select, button { width: 100%; padding: 12px; margin-top: 12px; border-radius: 8px; border: none; font-size: 16px; box-sizing: border-box; }
    select { background: #0f172a; color: #fff; border: 1px solid #475569; }
    button { background: #0284c7; color: #fff; font-weight: bold; cursor: pointer; }
    button:disabled { background: #64748b; }
    audio { width: 100%; margin-top: 16px; }
    #status { margin-top: 12px; text-align: center; font-size: 14px; min-height: 20px; }
  </style>
</head>
<body>
  <div class="box">
    <h2>🇲🇲 Myanmar AI TTS</h2>
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
        const res = await fetch(`/tts?text=${encodeURIComponent(text)}&voice=${voice}`);
        if (!res.ok) throw new Error();
        const blob = await res.blob();
        aud.src = URL.createObjectURL(blob);
        aud.style.display = 'block';
        aud.play();
        status.style.color = '#22c55e';
        status.innerText = "အသံဖိုင် ရပါပြီ။ နားဆင်/ဒေါင်းလုဒ် ဆွဲနိုင်ပါပြီ။";
      } catch (e) {
        status.style.color = '#ef4444';
        status.innerText = "အသံထုတ်မရပါ၊ ခဏနေ ပြန်စမ်းပေးပါ။";
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
async def tts(text: str, voice: str = "my-MM-ThihaNeural"):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return Response(content=audio_data, media_type="audio/mpeg")
