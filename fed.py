"""Kavach: federated, differentially-private scam detector (numpy only).

Each client = one phone holding messages in ONE language (non-IID).
Server only ever sees clipped + noised model updates (DP-FedAvg, user-level DP).

Run:  python fed.py      -> results.json, results.png, model.npz
"""
import json
import math

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

NF = 2 ** 12
RNG = np.random.default_rng(0)

vec = HashingVectorizer(
    analyzer="char_wb", ngram_range=(2, 4), n_features=NF,
    alternate_sign=False, norm="l2",
)


def featurize(texts):
    X = vec.transform(texts).toarray().astype(np.float32)
    return np.hstack([X, np.ones((len(X), 1), np.float32)])  # bias column


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def predict_proba(w, X):
    return sigmoid(X @ w)


def local_train(w, X, y, epochs=10, lr=8.0, l2=1e-4):
    w = w.copy()
    for _ in range(epochs):
        g = X.T @ (sigmoid(X @ w) - y) / len(y) + l2 * w
        w -= lr * g
    return w


def load_data(path="data.jsonl", test_frac=0.25, seed=0):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(rows))
    cut = int(len(rows) * (1 - test_frac))
    train = [rows[i] for i in idx[:cut]]
    test = [rows[i] for i in idx[cut:]]
    return train, test


def make_clients(train_rows, per_lang=4):
    """Non-IID: each client holds messages from a single language."""
    clients, meta = [], []
    langs = sorted({r["lang"] for r in train_rows})
    for lang in langs:
        rs = [r for r in train_rows if r["lang"] == lang]
        for chunk in np.array_split(np.arange(len(rs)), per_lang):
            sub = [rs[i] for i in chunk]
            if len(sub) < 2:
                continue
            clients.append((featurize([r["text"] for r in sub]),
                            np.array([r["label"] for r in sub], np.float32)))
            meta.append(lang)
    return clients, meta


def fedavg(clients, rounds=15, sigma=0.0, clip=1.0, local_epochs=10, seed=0):
    """DP-FedAvg. sigma = noise multiplier (0 -> no DP, no clipping)."""
    rng = np.random.default_rng(seed)
    w = np.zeros(NF + 1, np.float32)
    for _ in range(rounds):
        deltas = []
        for X, y in clients:
            d = local_train(w, X, y, epochs=local_epochs) - w
            if sigma > 0:
                d = d * min(1.0, clip / (np.linalg.norm(d) + 1e-12))
            deltas.append(d)
        agg = np.sum(deltas, axis=0)
        if sigma > 0:
            agg = agg + rng.normal(0.0, sigma * clip, agg.shape).astype(np.float32)
        w = w + agg / len(clients)
    return w


def epsilon(sigma, rounds, delta=1e-5):
    """(eps, delta)-DP via RDP of the Gaussian mechanism composed over `rounds`.
    All clients participate every round (no subsampling amplification)."""
    if sigma <= 0:
        return float("inf")
    best = float("inf")
    for a in np.concatenate([np.arange(1.1, 10, 0.1), np.arange(10, 256, 1.0)]):
        eps = rounds * a / (2 * sigma ** 2) + math.log(1 / delta) / (a - 1)
        best = min(best, eps)
    return best


def evaluate(w, rows):
    X = featurize([r["text"] for r in rows])
    y = np.array([r["label"] for r in rows])
    pred = (predict_proba(w, X) > 0.5).astype(int)
    out = {"overall": float((pred == y).mean())}
    for lang in sorted({r["lang"] for r in rows}):
        m = np.array([r["lang"] == lang for r in rows])
        out[lang] = float((pred[m] == y[m]).mean())
    return out


def run_all(data_path="data.jsonl", rounds=15):
    train, test = load_data(data_path)
    clients, meta = make_clients(train)
    print(f"{len(train)} train / {len(test)} test msgs, {len(clients)} simulated phones")

    # 1. local only: each phone trains alone, average accuracy on the shared test set
    local_scores = [evaluate(local_train(np.zeros(NF + 1, np.float32), X, y, epochs=rounds * 10), test)
                    for X, y in clients]
    langs = [k for k in local_scores[0] if k != "overall"]
    local = {k: float(np.mean([s[k] for s in local_scores])) for k in ["overall"] + langs}

    # 2. centralized (everyone uploads raw messages - the privacy-violating upper bound)
    Xc = np.vstack([c[0] for c in clients])
    yc = np.concatenate([c[1] for c in clients])
    central = evaluate(local_train(np.zeros(NF + 1, np.float32), Xc, yc, epochs=rounds * 10), test)

    # 3. federated, no DP
    fed = evaluate(fedavg(clients, rounds=rounds, sigma=0.0), test)

    # 4. federated + DP sweep
    dp = []
    best_w = None
    for sigma in [0.3, 0.6, 1.0, 2.0, 4.0]:
        w = fedavg(clients, rounds=rounds, sigma=sigma, clip=1.0)
        ev = evaluate(w, test)
        eps = epsilon(sigma, rounds)
        dp.append({"sigma": sigma, "epsilon": eps, **ev})
        print(f"  sigma={sigma:<4} eps={eps:8.1f}  acc={ev['overall']:.3f}")
        if sigma == 1.0:
            best_w = w

    # the model shipped to the demo app: federated with DP sigma=1.0
    np.savez("model.npz", w=best_w)
    results = {"local_only": local, "centralized": central, "federated": fed,
               "federated_dp": dp, "rounds": rounds, "n_clients": len(clients)}
    json.dump(results, open("results.json", "w"), indent=2, ensure_ascii=False)
    print(f"local={local['overall']:.3f} central={central['overall']:.3f} fed={fed['overall']:.3f}")
    make_chart(results)
    return results


def make_chart(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    names = ["Local only", "Federated", "Centralized\n(no privacy)"]
    vals = [res["local_only"]["overall"], res["federated"]["overall"], res["centralized"]["overall"]]
    ax[0].bar(names, vals, color=["#c0392b", "#2980b9", "#7f8c8d"])
    ax[0].set_ylim(0, 1.05)
    ax[0].set_title("Accuracy on shared multilingual test set")
    for i, v in enumerate(vals):
        ax[0].text(i, v + 0.01, f"{v:.2f}", ha="center")

    eps = [d["epsilon"] for d in res["federated_dp"]]
    acc = [d["overall"] for d in res["federated_dp"]]
    ax[1].plot(eps, acc, "o-", color="#2980b9", label="Federated + DP")
    ax[1].axhline(res["centralized"]["overall"], ls="--", color="#7f8c8d", label="Centralized")
    ax[1].axhline(res["local_only"]["overall"], ls=":", color="#c0392b", label="Local only")
    ax[1].set_xscale("log")
    ax[1].set_xlabel("privacy budget epsilon (smaller = more private)")
    ax[1].set_ylabel("accuracy")
    ax[1].set_ylim(0, 1.05)
    ax[1].set_title("Privacy vs accuracy")
    ax[1].legend()
    plt.tight_layout()
    plt.savefig("results.png", dpi=130)


if __name__ == "__main__":
    run_all()
