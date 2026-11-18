"""يولّد صوت كل سطر في script.json عبر Gemini TTS. المفتاح من GEMINI_API_KEY فقط (لا يُحفظ في أي ملف)."""
import base64, json, os, sys, time, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get("GEMINI_API_KEY")
MODELS = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts,gemini-2.5-flash-preview-tts").split(",")
VOICE = os.environ.get("TTS_VOICE", "Charon")
OUT = sys.argv[1]


def tts(text, model):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
    with urllib.request.urlopen(req, timeout=180) as r:
        return base64.b64decode(json.load(r)["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])


if __name__ == "__main__":
    if not KEY:
        sys.exit("GEMINI_API_KEY غير مضبوط")
    os.makedirs(OUT, exist_ok=True)
    for s in json.load(open(os.path.join(HERE, "script.json"), encoding="utf-8")):
        p = f"{OUT}/{s['id']}.wav"
        if os.path.exists(p):
            continue
        pcm = None
        for a in range(8):
            m = MODELS[0] if a < 5 else MODELS[-1]
            try:
                pcm = tts(s["text"], m); break
            except Exception as e:
                print(s["id"], m, e); time.sleep(15 * (a + 1))
        if pcm is None:
            sys.exit("فشل " + s["id"])
        with wave.open(p, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
        print(s["id"], round(len(pcm) / 48000, 2))
