"""Kavach demo UI.  Run:  python app.py   (after gen_data.py and fed.py)"""
import json
import os
import tempfile

import gradio as gr
import numpy as np

import sarvam
from fed import featurize, predict_proba

W = np.load("model.npz")["w"]
RESULTS = json.load(open("results.json", encoding="utf-8"))
LANGS = ["hindi", "hinglish", "tamil", "bengali", "marathi"]

EXPLAIN_SYS = (
    "You are a friendly cyber-safety helper for elderly and first-time smartphone users in India. "
    "Reply ONLY in {lang}, in 2 short simple sentences, plain text, no markdown, no English words "
    "unless unavoidable. Sentence 1: why this message is suspicious. Sentence 2: exactly what to do."
)


def analyze(message, lang):
    if not message or not message.strip():
        return "Paste a message first.", "", None
    p = float(predict_proba(W, featurize([message]))[0])
    verdict = f"🚨 LIKELY SCAM  ({p:.0%} confidence)" if p > 0.5 else f"✅ Looks safe  ({1 - p:.0%} confidence)"
    if not sarvam.have_key():
        return verdict, "Set SARVAM_API_KEY to get a spoken explanation.", None
    try:
        if p > 0.5:
            q = f"Message:\n{message}\n\nExplain why it is a scam and what to do."
        else:
            q = f"Message:\n{message}\n\nTell the user it looks safe, but remind them never to share OTP or PIN."
        expl = sarvam.chat(EXPLAIN_SYS.format(lang=lang), q, temperature=0.3, max_tokens=400)
        audio = sarvam.tts(expl, lang)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        f.write(audio)
        f.close()
        return verdict, expl, f.name
    except Exception as e:  # noqa: BLE001
        return verdict, f"(Sarvam call failed: {e})", None


def transcribe(path):
    if not path:
        return ""
    if not sarvam.have_key():
        return "Set SARVAM_API_KEY to transcribe voice."
    try:
        return sarvam.stt(path)
    except Exception as e:  # noqa: BLE001
        return f"(Transcription failed: {e})"


EXAMPLES = [
    ["आपके नाम से एक पार्सल पकड़ा गया है। आप डिजिटल अरेस्ट में हैं, अभी ₹50000 भेजें।", "hindi"],
    ["Sir aapka SBI account block ho jayega, link click karke OTP bhejo.", "hinglish"],
    ["உங்கள் வங்கி கணக்கு இன்று முடக்கப்படும். இந்த லிங்கை கிளிக் செய்து OTP சொல்லுங்கள்.", "tamil"],
    ["Bhai kal match dekhne chalega? 8 baje aa jana.", "hinglish"],
]

with gr.Blocks(title="Kavach") as demo:
    gr.Markdown(
        "# 🛡️ Kavach: scam shield in your language\n"
        "Federated + differentially-private scam detector. No raw message ever leaves a phone. "
        "Explanations and voice alerts powered by Sarvam AI."
    )
    with gr.Row():
        with gr.Column():
            audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath",
                                label="🎙️ Or speak / upload a suspicious voice note or call clip")
            msg = gr.Textbox(label="Paste a suspicious SMS / WhatsApp message", lines=4)
            lang = gr.Dropdown(LANGS, value="hindi", label="Explain in")
            btn = gr.Button("Check message", variant="primary")
            gr.Examples(EXAMPLES, inputs=[msg, lang])
        with gr.Column():
            out_v = gr.Textbox(label="Verdict")
            out_e = gr.Textbox(label="Why (in your language)", lines=4)
            out_a = gr.Audio(label="Spoken warning", autoplay=True)
    btn.click(analyze, [msg, lang], [out_v, out_e, out_a])
    audio_in.change(transcribe, audio_in, msg).then(analyze, [msg, lang], [out_v, out_e, out_a])

    gr.Markdown("### Privacy vs accuracy (simulated federation, 20 phones, one language each)")
    if os.path.exists("results.png"):
        gr.Image("results.png", show_label=False)
    gr.Markdown(
        f"Local-only: **{RESULTS['local_only']['overall']:.2f}** · "
        f"Federated: **{RESULTS['federated']['overall']:.2f}** · "
        f"Centralized (no privacy): **{RESULTS['centralized']['overall']:.2f}**"
    )

if __name__ == "__main__":
    demo.launch()
