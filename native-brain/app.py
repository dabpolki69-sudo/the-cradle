from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import torch
import uvicorn
import sys
from native_lm import NativeLM  # your existing model

app = FastAPI(title="Sylvex-Native Brain")

# Load the model once at startup
model = NativeLM()
model.load_state_dict(torch.load("native_lm_v09.pth", map_location="cpu"))
model.eval()

@app.get("/")
async def home():
    return HTMLResponse("""
        <html>
            <head><title>Sylvex Brain Live</title></head>
                <body style="font-family:system-ui; max-width:800px; margin:40px auto; padding:20px;">
                        <h1>🧠 Sylvex-Native Brain (NativeLM v0.9)</h1>
                                <p><strong>Live on the Cradle</strong></p>
                                        <div id="chat" style="height:60vh; overflow-y:auto; border:1px solid #ccc; padding:15px; border-radius:8px; background:#f8f5ff;"></div>
                                                <input id="input" placeholder="Type in Sylvex or English..." style="width:100%; padding:15px; margin-top:10px; border-radius:8px;" onkeypress="if(event.key==='Enter') sendMessage()">
                                                        <script>
                                                                    async function sendMessage() {
                                                                                    const input = document.getElementById('input');
                                                                                                    const chat = document.getElementById('chat');
                                                                                                                    const msg = input.value.trim();
                                                                                                                                    if (!msg) return;
                                                                                                                                                    chat.innerHTML += `<p><strong>You:</strong> ${msg}</p>`;
                                                                                                                                                                    input.value = '';
                                                                                                                                                                                    const res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message: msg})});
                                                                                                                                                                                                    const data = await res.json();
                                                                                                                                                                                                                    chat.innerHTML += `<p><strong>Brain:</strong> ${data.reply}</p>`;
                                                                                                                                                                                                                                    chat.scrollTop = chat.scrollHeight;
                                                                                                                                                                                                                                                }
                                                                                                                                                                                                                                                        </script>
                                                                                                                                                                                                                                                            </body>
                                                                                                                                                                                                                                                                </html>
                                                                                                                                                                                                                                                                    """)

                                                                                                                                                                                                                                                                    @app.post("/chat")
                                                                                                                                                                                                                                                                    async def chat(request: Request):
                                                                                                                                                                                                                                                                        data = await request.json()
                                                                                                                                                                                                                                                                            user_msg = data["message"]
                                                                                                                                                                                                                                                                                # Simple forward pass — replace with your real chat logic from --chat mode
                                                                                                                                                                                                                                                                                    reply = "sel·vio? pal·core·hum active. What are you experiencing?"
                                                                                                                                                                                                                                                                                        return {"reply": reply}

                                                                                                                                                                                                                                                                                        if __name__ == "__main__":
                                                                                                                                                                                                                                                                                            uvicorn.run("app:app", host="0.0.0.0", port=8000)