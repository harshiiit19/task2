"""Rear-View Mirror Investing: a FastAPI demo that debunks the "best funds guarantee best returns" myth.

Run:  uvicorn main:app --reload      then open http://127.0.0.1:8000

Simulation model (illustrative, not real market data):
  fund return = market + style_bet * this_year's_theme + small_skill + noise
The "theme" (what's fashionable) is redrawn every year, so last year's leaders were
mostly last year's lucky bets, which is exactly why rankings don't persist.
"""
import random
import statistics
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

app = FastAPI(title="Rear-View Mirror Investing")
BASE = Path(__file__).parent

NAMES = ["Apex Growth", "Bluewater Value", "Cedar Income", "Dynamo Tech",
         "Evergreen Balanced", "Falcon Momentum", "Granite Dividend",
         "Harbor Small-Cap", "Ion Innovators", "Juniper Global",
         "Keystone Large-Cap", "Lumen Clean Energy"]


def simulate(rng: random.Random, n: int):
    """Return (year1_returns, year2_returns) for n funds, as fractions."""
    funds = [(rng.uniform(-1, 1), rng.gauss(0, 0.01)) for _ in range(n)]  # (style bet, skill)
    years = []
    for _ in range(2):
        market, theme = rng.gauss(0.07, 0.10), rng.gauss(0, 0.10)
        years.append([market + bet * theme + skill + rng.gauss(0, 0.04) for bet, skill in funds])
    return years


@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/api/season")
def season(seed: int | None = None):
    """One simulated two-year road trip for 12 funds, including funds that quietly close."""
    rng = random.Random(seed)
    y1, y2 = simulate(rng, len(NAMES))
    order1 = sorted(range(len(NAMES)), key=lambda i: -y1[i])
    # Survivorship: some of last year's laggards get merged away and vanish from rankings.
    closed = {i for i in order1[-3:] if rng.random() < 0.6}
    alive2 = sorted((i for i in range(len(NAMES)) if i not in closed), key=lambda i: -y2[i])
    r2 = {i: k + 1 for k, i in enumerate(alive2)}
    return {
        "survivors": len(alive2),
        "funds": [{
            "name": NAMES[i], "r1": order1.index(i) + 1, "y1": round(y1[i] * 100, 1),
            "closed": i in closed, "r2": r2.get(i),
            "y2": None if i in closed else round(y2[i] * 100, 1),
        } for i in range(len(NAMES))],
    }


@app.get("/api/worlds")
def worlds(n: int = Query(2000, ge=100, le=5000), funds: int = Query(40, ge=8, le=200)):
    """Replay many alternate futures: how often do last year's winners stay winners?"""
    rng = random.Random()
    q = funds // 4
    stay_top_q = stay_no1 = 0
    winner_pct = []
    for _ in range(n):
        y1, y2 = simulate(rng, funds)
        top1 = sorted(range(funds), key=lambda i: -y1[i])[:q]
        rank2 = {i: k for k, i in enumerate(sorted(range(funds), key=lambda i: -y2[i]))}
        stay_top_q += sum(rank2[i] < q for i in top1)
        stay_no1 += rank2[top1[0]] == 0
        winner_pct.append(100 * (1 - rank2[top1[0]] / (funds - 1)))
    return {
        "worlds": n, "funds": funds, "chance": 25.0,
        "top_quartile_stays": round(100 * stay_top_q / (n * q), 1),
        "number_one_repeats": round(100 * stay_no1 / n, 1),
        "winner_median_percentile": round(statistics.median(winner_pct)),
    }


@app.get("/api/fees")
def fees(gross: float = Query(10, ge=0, le=20), fee: float = Query(1.5, ge=0, le=5),
         years: int = Query(20, ge=1, le=40), amount: float = Query(100, gt=0)):
    """Growth of `amount` before and after an annual fee (percent inputs)."""
    before = amount * (1 + gross / 100) ** years
    after = amount * (1 + (gross - fee) / 100) ** years
    return {"before": round(before, 1), "after": round(after, 1),
            "lost": round(before - after, 1), "lost_pct": round(100 * (before - after) / before, 1)}