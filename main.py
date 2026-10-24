import logging
import os

import config
from telegram.ext import ApplicationBuilder

from logging_config import configure_logging
from database import Database
from data_provider import MockProvider, PyQuotexAdapter
from signal_engine import SignalEngine
from result_engine import ResultEngine
from market_scanner import MarketScanner
from scheduler import Scheduler
from telegram_bot.handlers import register


# ==================================================
# Telegram bot lifecycle
# ==================================================

async def post_init(app):
    """Connect the provider and start the signal scheduler."""

    cfg = app.bot_data["cfg"]
    provider = app.bot_data["provider"]
    scheduler = app.bot_data["scheduler"]

    try:
        await provider.connect()

        if cfg.provider_mode == "mock":
            logging.getLogger(__name__).warning(
                "MOCK MODE enabled: prices and payouts are synthetic. "
                "Do not treat mock results as live trading performance."
            )

        if cfg.database_path:
            database_dir = os.path.dirname(cfg.database_path)

            if database_dir:
                os.makedirs(database_dir, exist_ok=True)

        await scheduler.start()

        logging.getLogger(__name__).info(
            "Provider connected and scheduler started."
        )

    except Exception:
        logging.getLogger(__name__).exception(
            "Bot startup failed during provider/scheduler initialization."
        )

        try:
            await provider.close()
        except Exception:
            logging.getLogger(__name__).exception(
                "Provider cleanup failed after startup error."
            )

        raise


async def post_shutdown(app):
    """Stop the scheduler and close the provider safely."""

    log = logging.getLogger(__name__)

    scheduler = app.bot_data.get("scheduler")
    provider = app.bot_data.get("provider")

    if scheduler is not None:
        try:
            await scheduler.stop()
            log.info("Scheduler stopped.")
        except Exception:
            log.exception("Error while stopping scheduler.")

    if provider is not None:
        try:
            await provider.close()
            log.info("Provider connection closed.")
        except Exception:
            log.exception("Error while closing provider.")


# ==================================================
# Main signal callback
# ==================================================

def main():
    configure_logging()
    log = logging.getLogger(__name__)

    # Load and validate configuration.
    try:
        cfg = config.from_env()
    except Exception as exc:
        raise SystemExit(
            f"Configuration error: {exc}"
        ) from exc

    # Initialize database.
    try:
        if cfg.database_path:
            database_dir = os.path.dirname(cfg.database_path)

            if database_dir:
                os.makedirs(database_dir, exist_ok=True)

        db = Database(cfg.database_path)

    except Exception as exc:
        log.exception("Database initialization failed.")
        raise SystemExit(
            f"Database error: {exc}"
        ) from exc

    # Initialize market data provider.
    try:
        if cfg.provider_mode == "mock":
            provider = MockProvider()

        elif cfg.provider_mode == "quotex":
            provider = PyQuotexAdapter(
                cfg.quotex_email,
                cfg.quotex_password,
            )

        else:
            raise ValueError(
                f"Unsupported provider mode: {cfg.provider_mode}"
            )

    except Exception as exc:
        log.exception("Provider initialization failed.")
        raise SystemExit(
            f"Provider error: {exc}"
        ) from exc

    # Initialize signal and result engines.
    try:
        engine = SignalEngine(
            cfg,
            db,
            provider,
        )

        results = ResultEngine(
            db,
            provider,
            cfg,
        )

        scanner = MarketScanner(
            provider,
            engine,
            cfg,
        )

    except Exception as exc:
        log.exception("Engine initialization failed.")
        raise SystemExit(
            f"Engine initialization error: {exc}"
        ) from exc

    # Build the Telegram application before registering callbacks.
    app = (
        ApplicationBuilder()
        .token(cfg.bot_token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Publish eligible signals to the configured Telegram channel.
    async def on_signal(signal):
        from telegram_bot.formatting import signal_text

        log.info(
            "Signal persisted: id=%s pair=%s strategy=%s direction=%s",
            signal.get("id"),
            signal.get("pair"),
            signal.get("strategy"),
            signal.get("direction"),
        )

        channel_id = cfg.signal_channel_id

        if not channel_id:
            log.warning(
                "Signal was generated, but no signal channel is configured."
            )
            return

        try:
            message = signal_text(signal, cfg)

            await app.bot.send_message(
                chat_id=channel_id,
                text=message,
            )

            log.info(
                "Signal published successfully to %s.",
                channel_id,
            )

        except Exception:
            log.exception(
                "Signal publication failed. "
                "The persisted signal was not deleted."
            )

    # Initialize scheduler.
    scheduler = Scheduler(
        scanner,
        results,
        db,
        cfg,
        on_signal,
    )

    # Share application components with lifecycle callbacks and handlers.
    app.bot_data.update(
        cfg=cfg,
        db=db,
        provider=provider,
        engine=engine,
        results=results,
        scanner=scanner,
        scheduler=scheduler,
    )

    # Register Telegram commands and callbacks.
    register(app)

    log.info(
        "Starting STM PRO BOT | provider_mode=%s | strategies=%s",
        cfg.provider_mode,
        ",".join(sorted(cfg.enabled_strategies)),
    )

    # Start polling and let python-telegram-bot manage the lifecycle.
    app.run_polling(
        allowed_updates=[
            "message",
            "callback_query",
        ],
    )


# ==================================================
# Entry point
# ==================================================

if __name__ == "__main__":
    main()
