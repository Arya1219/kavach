# 🛡️ Kavach: federated, private scam shield for Indian languages

> Scam protection that works in your language, speaks to your grandmother, and never reads your messages.

Digital-arrest, UPI and KYC scams reach people in Hindi, Tamil, Bengali, Marathi and code-mixed Hinglish.
Detectors need real messages to work, but nobody wants to upload their private chats to a server.
Kavach learns a scam detector **across phones without any message leaving a phone**, using
federated learning with differential privacy, and uses **Sarvam AI** to make it work in Indian languages and by voice.

**Showcase page:** https://arya1219.github.io/kavach/

## What it does
1. **Sarvam LLM** generates realistic scam and normal messages in 5 Indian languages (Hindi, Hinglish, Tamil, Bengali, Marathi).
2. 20 simulated phones each hold messages in one language and train a small model locally.
3. Only **clipped + noised updates** (DP-FedAvg) are sent to the server, never raw messages.
4. In the demo app, paste a message **or speak / upload a voice note** (Sarvam speech-to-text).
5. If it looks like a scam, **Sarvam explains why in your language** and **speaks the warning aloud** (Sarvam text-to-speech).

## Results (simulated federation, 375 Sarvam-generated messages, 94 held-out test messages)
| Setup | Accuracy |
|---|---|
| Local only (each phone alone) | 61% |
| Federated (no DP) | 89% |
| Centralized (everyone uploads, no privacy) | 85% |
| Federated + DP, ε≈145 | 78% |
| Federated + DP, ε≈26 | 70% |
| Federated + DP, ε≈5 | 61% |

Federated learning lifts accuracy by about 28 points over training alone, without sharing any messages.
Stronger privacy (smaller ε) costs accuracy. See `results.png` for the trade-off chart.

## Files
| File | Role |
|---|---|
| `sarvam.py` | Sarvam client: LLM chat, text-to-speech, speech-to-text |
| `seeds.py` | Hand-written fallback templates (used if no API key) |
| `gen_data.py` | Generates the multilingual dataset with the Sarvam LLM into `data.jsonl` |
| `fed.py` | Federated + DP training, ε accounting, comparison, chart; saves `model.npz`, `results.json`, `results.png` |
| `app.py` | Gradio demo: text or voice in, verdict, explanation and spoken warning out |
| `adversary.py` | Optional: an LLM "scammer" tries to evade the detector, the federation retrains |
| `index.html` | Static showcase page for GitHub Pages |

## Run it
```bash
pip install -r requirements.txt
export SARVAM_API_KEY=your_key        # PowerShell: $env:SARVAM_API_KEY="your_key"
python gen_data.py                    # Sarvam writes the dataset -> data.jsonl
python fed.py                         # federated + DP training -> results, model
python app.py                         # demo UI at http://127.0.0.1:7860
python adversary.py                   # optional arms-race experiment
```
Optional environment variables if your account uses other model names:
`SARVAM_CHAT_MODEL` (default `sarvam-105b-conversations`), `SARVAM_TTS_MODEL` (default `bulbul:v4-flash`), `SARVAM_TTS_SPEAKER`.

## How the privacy works
- **Features:** hashed character n-grams, which handle spelling variation and transliterated Hinglish with a tiny on-device model.
- **Federated averaging:** each phone trains locally and sends only a model update.
- **Differential privacy:** each update is clipped to a maximum norm and the server adds Gaussian noise.
- **Accounting:** ε comes from Rényi DP composition of the Gaussian mechanism over all rounds (δ=1e-5, user-level, all clients every round, no subsampling).

## Honest limitations
- The federation is **simulated on one machine**; the update, clipping, noise and averaging steps are real, but there are no real devices yet.
- The dataset is **LLM-generated**, not real SMS, and the test set is small (94 messages), so numbers are noisy.
- With only 20 simulated phones the privacy budgets are large (ε of about 5 to 145). This demonstrates the mechanism and the accuracy trade-off, not a production-grade privacy guarantee.
- Federated beating centralized here reflects the tiny dataset and extra local training steps, so treat them as comparable.

## Next steps
Real on-device training, a much larger federation, human-verified Indic scam data, and more languages (Telugu, Kannada, Malayalam, Gujarati).

Built for the Sarvam AI Buildathon.
