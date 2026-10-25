# Kavach: federated, private scam shield for Indian languages

Scam detector that learns across phones without any message leaving a phone (DP-FedAvg),
with Sarvam AI for data generation, plain-language explanations and spoken warnings.

## Run (about 5 minutes)
```bash
pip install -r requirements.txt
export SARVAM_API_KEY=your_key        # Windows PowerShell: $env:SARVAM_API_KEY="your_key"
python gen_data.py                    # Sarvam LLM writes the multilingual dataset -> data.jsonl
python fed.py                         # federated + DP training, results.json/png, model.npz
python app.py                         # demo UI
python adversary.py                   # optional: LLM scammer vs federated defender
```
Optional env vars if your account uses different model names:
`SARVAM_CHAT_MODEL` (default sarvam-m), `SARVAM_TTS_MODEL` (default bulbul:v2), `SARVAM_TTS_SPEAKER` (default anushka).

## How it works
- Each of 20 simulated phones holds messages in a single language (non-IID).
- Features: hashed char n-grams (works for transliterated Hinglish, no tokenizer).
- Training: DP-FedAvg. Each phone's update is clipped to norm 1, the server adds Gaussian noise.
- Privacy: epsilon from RDP accounting of the Gaussian mechanism (delta=1e-5), user-level, no subsampling.
- Sarvam: LLM generates the data, explains verdicts in the user's language, TTS speaks the warning.

## Honest caveats (say these in the pitch)
- The federation is simulated on one machine, and the data is LLM-generated, not real SMS.
- With 20 clients the epsilon values are large; this is a prototype of the mechanism, not a privacy guarantee.
