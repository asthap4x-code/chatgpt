import os
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

# ==================================================
# STM PRO BOT - Configuration
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

# Load .env without overriding hosting environment variables.
load_dotenv(BASE_DIR / ".env", override=False)


# ==================================================
# Environment helpers
# ==================================================

def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def get_int(name: str, default: int, minimum: int = 1) -> int:
    raw = get_env(name, str(default))

    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(
            f"Configuration error: {name} must be an integer."
        )

    if value < minimum:
        raise ValueError(
            f"Configuration error: {name} must be >= {minimum}."
        )

    return value


def get_float(
    name: str,
    default: float,
    minimum: float = 0.0,
    maximum: float | None = None,
) -> float:
    raw = get_env(name, str(default))

    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(
            f"Configuration error: {name} must be numeric."
        )

    if value < minimum:
        raise ValueError(
            f"Configuration error: {name} must be >= {minimum}."
        )

    if maximum is not None and value > maximum:
        raise ValueError(
            f"Configuration error: {name} must be <= {maximum}."
        )

    return value


def get_bool(name: str, default: bool = False) -> bool:
    raw = get_env(name, str(default)).lower()

    if raw in {"1", "true", "yes", "on"}:
        return True

    if raw in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Configuration error: {name} must be true or false."
    )


def get_admin_ids() -> frozenset[int]:
    raw = get_env("ADMIN_IDS")

    if not raw:
        return frozenset()

    try:
        ids = {
            int(item.strip())
            for item in raw.split(",")
            if item.strip()
        }
    except ValueError:
        raise ValueError(
            "Configuration error: ADMIN_IDS must contain numeric IDs."
        )

    if any(admin_id <= 0 for admin_id in ids):
        raise ValueError(
            "Configuration error: ADMIN_IDS must contain positive IDs."
        )

    return frozenset(ids)


# ==================================================
# Telegram configuration
# ==================================================

TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN")

CHANNEL_ID = get_env("CHANNEL_ID")
CHANNEL_USERNAME = get_env("CHANNEL_USERNAME").lstrip("@")

ADMIN_IDS = get_admin_ids()
ADMIN_USERNAME = get_env("ADMIN_USERNAME").lstrip("@")

FEEDBACK_CONTACT = get_env("FEEDBACK_CONTACT")
REFERRAL_URL = get_env("REFERRAL_URL")


# ==================================================
# Market and signal configuration
# ==================================================

PAYOUT_THRESHOLD = get_float(
    "PAYOUT_THRESHOLD",
    default=80.0,
    minimum=0.0,
    maximum=100.0,
)

TIMEZONE = get_env("TIMEZONE", "UTC")

try:
    DISPLAY_TIMEZONE = ZoneInfo(TIMEZONE)
except (ZoneInfoNotFoundError, ValueError):
    raise ValueError(
        "Configuration error: TIMEZONE must be a valid IANA timezone."
    )

SCAN_INTERVAL = get_int(
    "SCAN_INTERVAL",
    default=5,
    minimum=1,
)

SIGNAL_LEAD_SECONDS = get_int(
    "SIGNAL_LEAD_SECONDS",
    default=5,
    minimum=1,
)

EXPIRY_SECONDS = get_int(
    "EXPIRY_SECONDS",
    default=60,
    minimum=1,
)


# ==================================================
# Database configuration
# ==================================================

DATABASE_PATH = Path(
    get_env(
        "DATABASE_PATH",
        str(BASE_DIR / "data" / "stm_pro_bot.db"),
    )
).expanduser()

if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = (BASE_DIR / DATABASE_PATH).resolve()


# ==================================================
# Provider configuration
# ==================================================

PROVIDER_MODE = get_env("PROVIDER_MODE", "mock").lower()

if PROVIDER_MODE not in {"mock", "quotex"}:
    raise ValueError(
        "Configuration error: PROVIDER_MODE must be mock or quotex."
    )

QUOTEX_EMAIL = get_env("QUOTEX_EMAIL")
QUOTEX_PASSWORD = get_env("QUOTEX_PASSWORD")
QUOTEX_BASE_URL = get_env("QUOTEX_BASE_URL")

PROVIDER_TIMEOUT = get_int(
    "PROVIDER_TIMEOUT",
    default=20,
    minimum=1,
)

PROVIDER_MAX_RETRIES = get_int(
    "PROVIDER_MAX_RETRIES",
    default=3,
    minimum=0,
)

MAX_CONCURRENT_SCANS = get_int(
    "MAX_CONCURRENT_SCANS",
    default=5,
    minimum=1,
)

CANDLE_LOOKBACK = get_int(
    "CANDLE_LOOKBACK",
    default=200,
    minimum=60,
)

MAX_CANDLE_AGE_SECONDS = get_int(
    "MAX_CANDLE_AGE_SECONDS",
    default=90,
    minimum=1,
)


# ==================================================
# Strategy configuration
# ==================================================

ENABLE_AI_STRATEGY = get_bool(
    "ENABLE_AI_STRATEGY",
    True,
)

ENABLE_STM_STRATEGY = get_bool(
    "ENABLE_STM_STRATEGY",
    True,
)

ENABLE_RANDOM_STRATEGY = get_bool(
    "ENABLE_RANDOM_STRATEGY",
    False,
)

ENABLE_BLACK4X = get_bool(
    "ENABLE_BLACK4X",
    True,
)

ENABLE_OPX4O = get_bool(
    "ENABLE_OPX4O",
    True,
)

STM_PVIP_PRECEDING_CANDLES = get_int(
    "STM_PVIP_PRECEDING_CANDLES",
    default=3,
    minimum=3,
)

if STM_PVIP_PRECEDING_CANDLES > 10:
    raise ValueError(
        "Configuration error: STM_PVIP_PRECEDING_CANDLES "
        "must be between 3 and 10."
    )

STM_PVIP2_BODY_PERCENT = get_float(
    "STM_PVIP2_BODY_PERCENT",
    default=55.0,
    minimum=1.0,
    maximum=85.0,
)

AI_MIN_CONFIDENCE = get_float(
    "AI_MIN_CONFIDENCE",
    default=70.0,
    minimum=0.0,
    maximum=100.0,
)


# ==================================================
# Risk and session configuration
# ==================================================

LOSS_STREAK_LIMIT = get_int(
    "LOSS_STREAK_LIMIT",
    default=2,
    minimum=1,
)

COOLDOWN_HOURS = get_int(
    "COOLDOWN_HOURS",
    default=6,
    minimum=1,
)

ENABLE_MTG_CLASSIFICATION = get_bool(
    "ENABLE_MTG_CLASSIFICATION",
    default=False,
)

MAX_RECOVERY_ATTEMPTS = (
    1 if ENABLE_MTG_CLASSIFICATION else 0
)


# ==================================================
# Random strategy configuration
# ==================================================

RANDOM_STRATEGY_TEST_ONLY = get_bool(
    "RANDOM_STRATEGY_TEST_ONLY",
    default=True,
)


# ==================================================
# Configuration validation
# ==================================================

def validate_config() -> None:
    """Validate required settings before bot startup."""

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "Configuration error: TELEGRAM_BOT_TOKEN is required."
        )

    if not ADMIN_IDS:
        raise ValueError(
            "Configuration error: ADMIN_IDS must contain "
            "at least one admin ID."
        )

    if not CHANNEL_ID and not CHANNEL_USERNAME:
        raise ValueError(
            "Configuration error: CHANNEL_ID or "
            "CHANNEL_USERNAME is required."
        )

    if PROVIDER_MODE == "quotex":
        if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
            raise ValueError(
                "Configuration error: QUOTEX_EMAIL and "
                "QUOTEX_PASSWORD are required when "
                "PROVIDER_MODE=quotex."
            )

    if ENABLE_RANDOM_STRATEGY and not RANDOM_STRATEGY_TEST_ONLY:
        raise ValueError(
            "Configuration error: random signals must remain "
            "test-only."
        )

    try:
        DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as exc:
        raise ValueError(
            "Configuration error: cannot create the database directory."
        ) from exc


# ==================================================
# Lowercase settings factory
# ==================================================

def from_env():
    """
    Validate configuration and return a settings object.

    main.py uses lowercase attributes such as:
    cfg.bot_token
    cfg.database_path
    cfg.provider_mode
    """

    validate_config()

    enabled_strategies = {
        name
        for name, enabled in {
            "AI": ENABLE_AI_STRATEGY,
            "STM": ENABLE_STM_STRATEGY,
            "BLACK4X": ENABLE_BLACK4X,
            "OPX4O": ENABLE_OPX4O,
            "RANDOM": ENABLE_RANDOM_STRATEGY,
        }.items()
        if enabled
    }

    signal_channel_id = (
        CHANNEL_ID
        if CHANNEL_ID
        else f"@{CHANNEL_USERNAME}"
        if CHANNEL_USERNAME
        else ""
    )

    return SimpleNamespace(
        # Telegram
        bot_token=TELEGRAM_BOT_TOKEN,
        channel_id=CHANNEL_ID,
        channel_username=CHANNEL_USERNAME,
        signal_channel_id=signal_channel_id,
        admin_ids=ADMIN_IDS,
        admin_username=ADMIN_USERNAME,
        feedback_contact=FEEDBACK_CONTACT,
        referral_url=REFERRAL_URL,

        # Market and signals
        payout_threshold=PAYOUT_THRESHOLD,
        timezone=TIMEZONE,
        display_timezone=DISPLAY_TIMEZONE,
        scan_interval=SCAN_INTERVAL,
        signal_lead_seconds=SIGNAL_LEAD_SECONDS,
        expiry_seconds=EXPIRY_SECONDS,

        # Database
        database_path=str(DATABASE_PATH),

        # Provider
        provider_mode=PROVIDER_MODE,
        quotex_email=QUOTEX_EMAIL,
        quotex_password=QUOTEX_PASSWORD,
        quotex_base_url=QUOTEX_BASE_URL,
        provider_timeout=PROVIDER_TIMEOUT,
        provider_max_retries=PROVIDER_MAX_RETRIES,
        max_concurrent_scans=MAX_CONCURRENT_SCANS,
        candle_lookback=CANDLE_LOOKBACK,
        max_candle_age_seconds=MAX_CANDLE_AGE_SECONDS,

        # Strategies
        enabled_strategies=enabled_strategies,
        enable_ai_strategy=ENABLE_AI_STRATEGY,
        enable_stm_strategy=ENABLE_STM_STRATEGY,
        enable_random_strategy=ENABLE_RANDOM_STRATEGY,
        enable_black4x=ENABLE_BLACK4X,
        enable_opx4o=ENABLE_OPX4O,
        stm_pvip_preceding_candles=STM_PVIP_PRECEDING_CANDLES,
        stm_pvip2_body_percent=STM_PVIP2_BODY_PERCENT,
        ai_min_confidence=AI_MIN_CONFIDENCE,

        # Risk and recovery
        loss_streak_limit=LOSS_STREAK_LIMIT,
        cooldown_hours=COOLDOWN_HOURS,
        enable_mtg_classification=ENABLE_MTG_CLASSIFICATION,
        max_recovery_attempts=MAX_RECOVERY_ATTEMPTS,
        random_strategy_test_only=RANDOM_STRATEGY_TEST_ONLY,
    )


# ==================================================
# Standalone validation
# ==================================================

if __name__ == "__main__":
    validate_config()
    settings = from_env()

    print("STM PRO BOT configuration is valid.")
    print(f"Provider mode: {settings.provider_mode}")
    print(f"Database path: {settings.database_path}")
    print(
        "Enabled strategies: "
        + ", ".join(sorted(settings.enabled_strategies))
    )
