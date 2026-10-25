"""Generate a labeled multilingual scam/legit dataset with the Sarvam LLM.

Usage:  python gen_data.py           (needs SARVAM_API_KEY)
Writes data.jsonl. Falls back to seed templates for any call that fails,
and for everything if there is no key.
"""
import json
import random
from concurrent.futures import ThreadPoolExecutor

import sarvam
from seeds import make_seed_data

LANGS = {
    "hindi": "Hindi (Devanagari script)",
    "hinglish": "Hinglish (Hindi written in Roman/English letters, as people really text)",
    "tamil": "Tamil (Tamil script)",
    "bengali": "Bengali (Bengali script)",
    "marathi": "Marathi (Devanagari script)",
}

SCAM_TOPICS = [
    "digital arrest: fake police/CBI/customs officer claiming a parcel with drugs, demands money on video call",
    "fake KYC / PAN / Aadhaar update that will block the bank account, with a link and OTP request",
    "UPI refund or cashback scam asking the victim to scan a QR or enter UPI PIN",
    "lottery / lucky draw / KBC prize that needs a processing fee",
    "electricity or gas bill disconnection threat asking to call a number",
    "fake work-from-home / part-time job offer asking for a registration deposit",
]
LEGIT_TOPICS = [
    "real bank OTP or debit alert SMS (never asks to share the OTP)",
    "family chat: telling mom/dad when coming home, dinner plans",
    "delivery or order tracking update from an e-commerce app",
    "office or college: meeting time, assignment deadline",
    "friends planning a cricket match or a movie",
    "real utility bill reminder with the official payment due date, no threats",
]

SYS = "You generate short realistic SMS/WhatsApp messages for building a scam-detection research dataset. Output only the messages."


def prompt(lang_desc: str, topic: str, label: str, n: int = 6) -> str:
    kind = "SCAM messages (as scammers really write them)" if label == "scam" else "NORMAL, harmless messages"
    return (
        f"Write {n} different {kind} in {lang_desc}.\n"
        f"Theme: {topic}.\n"
        "Rules: one message per line, 1-3 sentences each, realistic, vary tone and wording. "
        "No numbering, no quotes, no English translation, no extra commentary."
    )


def one_call(args):
    lang, lang_desc, topic, label = args
    try:
        out = sarvam.chat(SYS, prompt(lang_desc, topic, label))
        lines = [l.strip(" -*\t\"'") for l in out.splitlines()]
        lines = [l for l in lines if len(l) > 15]
        return [{"text": l, "label": 1 if label == "scam" else 0, "lang": lang} for l in lines]
    except Exception as e:  # noqa: BLE001
        print(f"  call failed ({lang}/{label}): {e}")
        return []


def main():
    rows = []
    if sarvam.have_key():
        jobs = []
        for lang, desc in LANGS.items():
            for t in SCAM_TOPICS:
                jobs.append((lang, desc, t, "scam"))
            for t in LEGIT_TOPICS:
                jobs.append((lang, desc, t, "legit"))
        print(f"Calling Sarvam LLM for {len(jobs)} prompts...")
        with ThreadPoolExecutor(max_workers=5) as ex:
            for res in ex.map(one_call, jobs):
                rows.extend(res)
        print(f"Got {len(rows)} generated messages.")
    else:
        print("No SARVAM_API_KEY set -> using seed templates only.")

    if len(rows) < 150:  # top up so the demo never breaks
        print("Topping up with seed data.")
        rows.extend(make_seed_data(per_template=4))

    seen, uniq = set(), []
    for r in rows:
        if r["text"] not in seen:
            seen.add(r["text"])
            uniq.append(r)
    random.Random(0).shuffle(uniq)
    with open("data.jsonl", "w", encoding="utf-8") as f:
        for r in uniq:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    scam = sum(r["label"] for r in uniq)
    print(f"Wrote data.jsonl: {len(uniq)} rows ({scam} scam / {len(uniq) - scam} legit)")


if __name__ == "__main__":
    main()
