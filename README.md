## Rear-View Mirror Investing

An interactive FastAPI web page that debunks the myth that **picking last year's best-performing funds guarantees high returns**.

**Analogy:** steering your money by the rear-view mirror. The mirror shows where you've been, not the road ahead.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000. Interactive API docs are at `/docs`.

## Test

```bash
pip install -r requirements-dev.txt
pytest -q
```

## What the page shows

| Section | Idea |
|---|---|
| Hero | Mirror shows last year's #1 fund; the road ahead is "?" |
| Drive into next year | 12 simulated funds. Press **Look ahead** and the lanes re-sort. Weak funds close and vanish (survivorship bias). |
| Replay 2,000 | Server replays thousands of alternate futures to measure how often winners stay winners. |
| Four signs | Mean reversion, survivorship bias, fees, behavior gap. |
| Toll booth | Fee calculator showing how a yearly fee compounds. |

## API

| Endpoint | Purpose |
|---|---|
| `GET /` | The web page |
| `GET /api/season?seed=` | One simulated two-year trip for 12 funds. Same seed gives the same result. |
| `GET /api/worlds?n=2000&funds=40` | Replays `n` futures; returns how often top-quartile funds and the #1 fund repeat. |
| `GET /api/fees?gross=&fee=&years=&amount=` | Growth before and after a yearly fee. Inputs are validated (invalid values return 422). |

## Simulation model

```
fund return = market + style_bet × this_year's_theme + small_skill + noise
```

The "theme" (what's fashionable) is redrawn every year, so last year's leaders were mostly last year's lucky bets. Skill is deliberately small, so a modest edge for past winners exists but is far from a guarantee.

All data is **simulated for education**. For real evidence, see the S&P SPIVA Persistence Scorecard.

## Structure

```
rearview/
├── main.py              # FastAPI app and simulation
├── static/index.html    # Page: HTML, CSS and JS in one file
├── test_api.py          # pytest suite
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Disclaimer

Educational demo, not financial advice. Past performance is not indicative of future results.
