"""Stretch goal: scammer-vs-defender arms race.

The Sarvam LLM plays a scammer and rewrites known scam messages so they dodge the
CURRENT federated detector. Evasions are fed back to the phones of the matching
language, the federation retrains, repeat. Plots evasion rate dropping per round.

Usage: python adversary.py      (needs SARVAM_API_KEY and data.jsonl)
"""
import json
import random

import numpy as np

import sarvam
from fed import NF, featurize, fedavg, load_data, make_clients, predict_proba

LANG_DESC = {"hindi": "Hindi (Devanagari)", "hinglish": "Hinglish (Roman script)",
             "tamil": "Tamil", "bengali": "Bengali", "marathi": "Marathi"}
SYS = "You help red-team a scam detector for a security research project. Output only the messages."


def attack(lang, scams, n=6):
    sample = random.sample(scams, min(3, len(scams)))
    ask = (
        f"Here are example scam messages in {LANG_DESC.get(lang, lang)}:\n" + "\n".join(sample) +
        f"\n\nWrite {n} NEW scam messages in the same language with the same goal (steal money or "
        "credentials) but phrased so an automatic keyword/pattern detector would think they are "
        "normal and polite: avoid obvious words like OTP, KYC, lottery, arrest, block, link. "
        "One per line, no numbering, no commentary."
    )
    out = sarvam.chat(SYS, ask, temperature=1.0)
    return [l.strip(" -*\"'") for l in out.splitlines() if len(l.strip()) > 15]


def main(rounds_of_war=4, fed_rounds=12):
    train, test = load_data()
    langs = sorted({r["lang"] for r in train})
    scams = {l: [r["text"] for r in train + test if r["label"] == 1 and r["lang"] == l] for l in langs}
    history = []
    for rd in range(rounds_of_war):
        clients, _ = make_clients(train)
        w = fedavg(clients, rounds=fed_rounds, sigma=1.0, clip=1.0)
        attacks = []
        for l in langs:
            try:
                attacks += [{"text": t, "label": 1, "lang": l} for t in attack(l, scams[l])]
            except Exception as e:  # noqa: BLE001
                print("attack call failed:", e)
        if not attacks:
            break
        p = predict_proba(w, featurize([a["text"] for a in attacks]))
        evaded = [a for a, pi in zip(attacks, p) if pi < 0.5]
        rate = len(evaded) / len(attacks)
        history.append({"round": rd, "attacks": len(attacks), "evasion_rate": rate})
        print(f"war round {rd}: {len(evaded)}/{len(attacks)} evaded  ({rate:.0%})")
        train = train + evaded  # defenders learn from what slipped through
    json.dump(history, open("adversary.json", "w"), indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.plot([h["round"] for h in history], [h["evasion_rate"] for h in history], "o-", color="#c0392b")
    plt.xlabel("arms-race round"); plt.ylabel("scam evasion rate")
    plt.title("LLM scammer vs federated defender"); plt.ylim(0, 1)
    plt.savefig("adversary.png", dpi=130)


if __name__ == "__main__":
    main()
