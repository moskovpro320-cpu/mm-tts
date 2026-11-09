from fastapi import FastAPI, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import edge_tts

# စက်အလုံး ၁၀၀ အတွက် Password များ
ALLOWED_PASSWORDS = {"631378": "Master Key"}

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
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: radial-gradient(circle at top, #0f2027, #0b1320, #06090e);
      color: #fff;
      padding: 16px;
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .wrapper { width: 100%; max-width: 460px; }
    
    /* Top Bar */
    .top-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
    }
    .logo-badge {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .logo-icon {
      background: #38bdf8;
      color: #000;
      font-weight: 900;
      width: 38px;
      height: 38px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      font-size: 18px;
    }
    .logo-text { font-size: 18px; font-weight: bold; letter-spacing: 0.5px; }

    /* Hero Text */
    .hero-tag {
      font-size: 11px;
      font-weight: 700;
      color: #38bdf8;
      letter-spacing: 2px;
      margin-bottom: 10px;
      text-transform: uppercase;
    }
    .hero-title {
      font-size: 26px;
      font-weight: 800;
      line-height: 1.35;
      margin: 0 0 12px 0;
    }
    .hero-desc {
      color: #94a3b8;
      font-size: 13.5px;
      line-height: 1.5;
      margin-bottom: 16px;
    }
    .tags-row {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }
    .tag-item {
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
    }

    /* VIP Card */
    .card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .card-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }
    .vip-badge {
      font-size: 11px;
      letter-spacing: 1.5px;
      color: #38bdf8;
      font-weight: bold;
      text-transform: uppercase;
    }
    .card-title {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 16px;
    }
    .input-label {
      font-size: 12px;
      color: #94a3b8;
      font-weight: bold;
      letter-spacing: 1px;
      margin-bottom: 8px;
      display: block;
    }
    input[type="password"], textarea {
      width: 100%;
      background: #080d16;
      color: #fff;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 14px;
      font-size: 15px;
      outline: none;
    }
    input[type="password"]:focus, textarea:focus {
      border-color: #38bdf8;
    }
    textarea { height: 120px; resize: vertical; }
    select {
      width: 100%;
      background: #080d16;
      color: #fff;
      border: 1px solid #1e293b;
      padding: 12px;
      border-radius: 10px;
      margin-top: 12px;
      font-size: 15px;
    }
    .submit-btn {
      width: 100%;
      padding: 13px;
      margin-top: 16px;
      border-radius: 10px;
      border: none;
      font-size: 16px;
      font-weight: bold;
      background: linear-align(135deg, #38bdf8, #2dd4bf);
      background-color: #38bdf8;
      color: #04121d;
      cursor: pointer;
    }
    .submit-btn:disabled { background-color: #475569; color: #94a3b8; }
    .logout-btn {
      background: #ef4444;
      color: #fff;
      border: none;
      padding
