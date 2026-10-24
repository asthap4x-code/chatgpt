import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

# ==================================================
# STM PRO BOT - Configuration
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

# Load local .env without overriding hosting secrets.
load_dotenv(BASE_DIR / ".env", override=False)


def get_env(name: str, default: str = "") -> str:
    """Read and normalize an environment variable."""
    return os.getenv(name, default).strip()


def get_int(name: str, default: int, minimum: int = 1) -> int:
    """Read and validate an integer environment variable."""
    raw = get_env(name, str(default))

    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"Configuration error: {name} must be an integer.")

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
    """Read and validate a numeric environment variable."""
    raw = get_env(name, str(default))

    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(f"Configuration error: {name} must be numeric.")

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
    """Parse a boolean environment variable."""
    raw = get_env(name, str(default)).lower()

    if raw in {"1", "true", "yes", "on"}:
        return True

    if raw in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Configuration error: {name} must be true or false."
    )


def get_admin_ids() -> frozenset[int]:
    """Parse comma-separated numeric Telegram admin IDs."""
    raw = get_env("ADMIN_IDS")

    if not raw:
        return frozenset()

    try:
        ids = {int(item.strip()) for item in raw.split(",") if item.strip()}
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
    get_env("DATABASE_PATH", str(BASE_DIR / "data" / "stm_pro_bot.db"))
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

ENABLE_AI_STRATEGY = get_bool("ENABLE_AI_STRATEGY", True)
ENABLE_STM_STRATEGY = get_bool("ENABLE_STM_STRATEGY", True)
ENABLE_RANDOM_STRATEGY = get_bool("ENABLE_RANDOM_STRATEGY", False)
ENABLE_BLACK4X = get_bool("ENABLE_BLACK4X", True)
ENABLE_OPX4O = get_bool("ENABLE_OPX4O", True)

STM_PVIP_PRECEDING_CANDLES = get_int(
    "STM_PVIP_PRECEDING_CANDLES",
    default=3,
    minimum=3,
)

if STM_PVIP_PRECEDING_CANDLES > 10:
    raise ValueError(
        "Configuration error: STM_PVIP_PRECEDING_CANDLES must be between 3 and 10."
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

MAX_RECOVERY_ATTEMPTS = 1 if ENABLE_MTG_CLASSIFICATION else 0

# ==================================================
# Random strategy configuration
# ==================================================

RANDOM_STRATEGY_TEST_ONLY = get_bool(
    "RANDOM_STRATEGY_TEST_ONLY",
    default=True,
)

# ==================================================
# Startup validation
# ==================================================

def validate_config() -> None:
    """Validate required configuration before starting the bot."""

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "Configuration error: TELEGRAM_BOT_TOKEN is required"
        )

    if not ADMIN_IDS:
        raise ValueError(
            "Configuration error: ADMIN_IDS must contain at least one admin ID"
        )

    if not CHANNEL_ID and not CHANNEL_USERNAME:
        raise ValueError(
            "Configuration error: CHANNEL_ID or CHANNEL_USERNAME is required"
        )

    if PROVIDER_MODE == "quotex":
        if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:
            raise ValueError(
                "Configuration error: QUOTEX_EMAIL and QUOTEX_PASSWORD "
                "are required when PROVIDER_MODE=quotex"
            )

    if ENABLE_RANDOM_STRATEGY and not RANDOM_STRATEGY_TEST_ONLY:
        raise ValueError(
            "Configuration error: random signals must remain test-only."
        )

    try:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise ValueError(
            "Configuration error: cannot create the database directory."
        )


if __name__ == "__main__":
    validate_config()
    print("STM PRO BOT configuration is valid.")
class config:
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN

    CHANNEL_ID = CHANNEL_ID
    CHANNEL_USERNAME = CHANNEL_USERNAME

    ADMIN_IDS = ADMIN_IDS
    ADMIN_USERNAME = ADMIN_USERNAME

    FEEDBACK_CONTACT = FEEDBACK_CONTACT
    REFERRAL_URL = REFERRAL_URL

    PAYOUT_THRESHOLD = PAYOUT_THRESHOLD
    TIMEZONE = TIMEZONE
    DISPLAY_TIMEZONE = DISPLAY_TIMEZONE

    SCAN_INTERVAL = SCAN_INTERVAL
    SIGNAL_LEAD_SECONDS = SIGNAL_LEAD_SECONDS
    EXPIRY_SECONDS = EXPIRY_SECONDS

    DATABASE_PATH = DATABASE_PATH

    PROVIDER_MODE = PROVIDER_MODE
    QUOTEX_EMAIL = QUOTEX_EMAIL
    QUOTEX_PASSWORD = QUOTEX_PASSWORD
    QUOTEX_BASE_URL = QUOTEX_BASE_URL

    PROVIDER_TIMEOUT = PROVIDER_TIMEOUT
    PROVIDER_MAX_RETRIES = PROVIDER_MAX_RETRIES
    MAX_CONCURRENT_SCANS = MAX_CONCURRENT_SCANS
    CANDLE_LOOKBACK = CANDLE_LOOKBACK
    MAX_CANDLE_AGE_SECONDS = MAX_CANDLE_AGE_SECONDS

    ENABLE_AI_STRATEGY = ENABLE_AI_STRATEGY
    ENABLE_STM_STRATEGY = ENABLE_STM_STRATEGY
    ENABLE_RANDOM_STRATEGY = ENABLE_RANDOM_STRATEGY
    ENABLE_BLACK4X = ENABLE_BLACK4X
    ENABLE_OPX4O = ENABLE_OPX4O

    STM_PVIP_PRECEDING_CANDLES = STM_PVIP_PRECEDING_CANDLES
    STM_PVIP2_BODY_PERCENT = STM_PVIP2_BODY_PERCENT
    AI_MIN_CONFIDENCE = AI_MIN_CONFIDENCE

    LOSS_STREAK_LIMIT = LOSS_STREAK_LIMIT
    COOLDOWN_HOURS = COOLDOWN_HOURS
    ENABLE_MTG_CLASSIFICATION = ENABLE_MTG_CLASSIFICATION
    MAX_RECOVERY_ATTEMPTS = MAX_RECOVERY_ATTEMPTS

    RANDOM_STRATEGY_TEST_ONLY = RANDOM_STRATEGY_TEST_ONLY

    validate = staticmethod(validate_config)
    def from_env():
    validate_config()
    return __import__(__name__)
