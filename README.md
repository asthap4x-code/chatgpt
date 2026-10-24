# STM PRO BOT

Signal-only Telegram bot with SQLite persistence and modular strategies. It never places orders.

## Important provider limitation

The public PyQuotex repository documents a `get_candles(asset, end_from_time, offset, period)` method and candle shapes, but it is community-maintained and may break. No reliable documented payout API or authoritative settlement source was established in the docs reviewed for this project. Therefore the live adapter deliberately returns `None` for payout and settlement: live signal generation is skipped and real results remain unresolved until a verified source is implemented. Do not patch this by guessing payout or prices. PyQuotex docs: https://cleitonleonel.github.io/pyquotex/en/ and source: https://github.com/cleitonleonel/pyquotex/blob/master/pyquotex/_api/history.py

## Termux setup

1. Install Termux from a trusted source, then run `pkg update && pkg upgrade -y && pkg install python git -y`.
2. Put the project folder on your device or clone your private GitHub repository.
3. `cd STM-PRO-BOT && python -m venv .venv && source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `cp .env.example .env`, then edit `.env` locally. Never commit `.env`.
6. Add the bot as a member/admin in the channel if membership verification is enabled.
7. `python main.py`
8. Tests: `pytest -q`

## GitHub setup

Create a private repository, copy project files, run `git status`, confirm `.env` is not listed, then commit. If a secret was ever committed, revoke/rotate it; deleting the file in a later commit is not enough. Use GitHub Actions/deployment secrets for hosted deployments.

## Commands and user flow

- `/start`: welcome, join link, membership verification.
- After verification: Get Signal -> categories -> pairs -> strategies -> request signals.
- Admin-only by numeric Telegram user ID: `/STMON`, `/STMOP`, `/STMUTO`, `/pause`, `/resume`.
- `/status`, `/stats`, `/help`.
- `/STMUTO` asks for 10/20/25/30/40 eligible persisted signals. A skipped candidate does not count; it can continue indefinitely if no eligible signals exist, so monitor `/status` and stop with `/STMOP`.

## Strategies and definitions

- **AI** is deterministic confluence scoring, not a trained model and not a probability. EMA 10/20/50 ordering contributes two points; MACD direction, stochastic direction, a close beyond the prior candle extreme, and confirmed swing trend add confluence. At least four points and ATR-based range checks are required.
- **STM PVIP**: confirmed swing trend; in an uptrend, N preceding bullish closed candles then a bearish pullback candle closing above EMA20 proposes CALL. Mirrored for downtrend. N is configurable 3-10.
- **STM PVIP 2**: candle body percentage is `abs(close-open)/(high-low)*100`; must be between threshold (55%) and cap (85%). Current candle open must match prior close within ATR tolerance, be on the proper EMA10 side, and close beyond the prior high/low.
- **BLACK4X**: previous non-doji candle direction continues. Doji yields no candidate.
- **OPX4O**: opposite direction to previous candle; true/near doji within tolerance yields no candidate because its color is ambiguous.
- **RANDOM**: mock/testing only; disabled in live mode and never presented as a prediction.
- Indicators include EMA/SMA, stochastic, RSI, MACD, ATR, candle body/range and confirmed swing helpers. Supply/demand, liquidity-sweep and BOS/CHOCH heuristics are not enabled as signal triggers until validated and tested; do not infer these from unconfirmed future swings.

## Timing, settlement, statistics

Signals target the next minute boundary and one-minute expiry; provider/network latency may shift actual entry. Timestamps are stored in UTC and displayed in `TIMEZONE`. Payout below `PAYOUT_THRESHOLD`, missing payout, stale candles, malformed OHLC, and unclosed candles are rejected. Duplicate pair/entry/strategy signals are prevented by a SQLite unique key. Result engine never fabricates data; missing settlement remains open/pending for retry. CALL wins only if verified exit > entry; PUT wins only if verified exit < entry; equal is TIE. The mock provider uses synthetic data only. Recovery classification is a setting placeholder; this version does not automatically issue a second signal or double stakes. Loss-streak cooldown fields are persisted but production recovery/cooldown policy requires confirmed result updates.

## Security and privacy

- Never share bot token or Quotex password. Use deployment secrets or a local `.env` excluded from Git.
- This is signal-only. It does not place trades, handle funds, or validate affiliate registration.
- Telegram `getChatMember` is reliable only when the bot has sufficient channel permissions. Referral registration cannot be proven from membership.
- Confidence is a rule score, not a calibrated win probability. No accuracy or profit is promised.
- Review local laws, broker terms, and risks before use. Avoid martingale; no recovery method guarantees recovery.

## Known limitations

Live payout and authoritative result endpoints are intentionally not guessed. PyQuotex is unofficial and can break. Live mode is fail-closed until a verified payout and settlement adapter is supplied. The scheduler publishes eligible persisted signals to `SIGNAL_CHANNEL_ID` when configured; users can also request up to five eligible signals in private chat. The scheduler only creates scheduled candidates during the final ten seconds before a minute boundary. Daily summary/OTC grouping is not enabled because provider categories and settlement support must be verified first. Backtesting is a basic chronological holdout helper and does not simulate provider latency, payouts, or execution.
