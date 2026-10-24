"""Environment-backed configuration; never logs secret values."""
from dataclasses import dataclass
from pathlib import Path
import os


def _csv_ints(value: str) -> frozenset[int]:
    try: return frozenset(int(x.strip()) for x in value.split(',') if x.strip())
    except ValueError as exc: raise ValueError("ADMIN_IDS must be comma-separated numeric Telegram IDs") from exc

@dataclass(frozen=True)
class Config:
    bot_token: str
    channel_id: str
    channel_username: str
    channel_url: str
    signal_channel_id: str
    admin_ids: frozenset[int]
    admin_username: str
    feedback_contact: str
    referral_url: str
    payout_threshold: int
    timezone: str
    scan_interval: float
    database_path: str
    provider_mode: str
    quotex_email: str
    quotex_password: str
    max_concurrency: int
    max_data_age_seconds: int
    cooldown_hours: int
    recovery_classification: bool
    mock_mode: bool
    min_confidence: int
    enabled_strategies: frozenset[str]
    language: str

    @classmethod
    def from_env(cls) -> "Config":
        token=os.getenv('TELEGRAM_BOT_TOKEN','').strip()
        if not token: raise ValueError('TELEGRAM_BOT_TOKEN is required')
        admins=_csv_ints(os.getenv('ADMIN_IDS',''))
        if not admins: raise ValueError('ADMIN_IDS must contain at least one numeric Telegram ID')
        payout=int(os.getenv('PAYOUT_THRESHOLD','80'))
        if not 0 <= payout <= 100: raise ValueError('PAYOUT_THRESHOLD must be 0..100')
        mode=os.getenv('PROVIDER_MODE','mock').lower()
        if mode not in {'mock','pyquotex'}: raise ValueError('PROVIDER_MODE must be mock or pyquotex')
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        tz=os.getenv('TIMEZONE','Indian/Maldives')
        try: ZoneInfo(tz)
        except ZoneInfoNotFoundError as exc: raise ValueError(f'Unknown TIMEZONE: {tz}') from exc
        return cls(token,os.getenv('CHANNEL_ID','').strip(),os.getenv('CHANNEL_USERNAME','').strip(),
          os.getenv('CHANNEL_URL','https://t.me/').strip(),os.getenv('SIGNAL_CHANNEL_ID','').strip(),admins,os.getenv('ADMIN_USERNAME','admin'),
          os.getenv('FEEDBACK_CONTACT','not configured'),os.getenv('QUOTEX_REFERRAL_URL','https://example.com/'),payout,tz,
          float(os.getenv('SCAN_INTERVAL_SECONDS','5')),os.getenv('DATABASE_PATH','data/stm_pro.sqlite3'),mode,
          os.getenv('QUOTEX_EMAIL',''),os.getenv('QUOTEX_PASSWORD',''),int(os.getenv('MAX_CONCURRENCY','4')),
          int(os.getenv('MAX_DATA_AGE_SECONDS','90')),int(os.getenv('COOLDOWN_HOURS','6')),
          os.getenv('RECOVERY_CLASSIFICATION','false').lower()=='true',os.getenv('MOCK_MODE',mode=='mock' and 'true' or 'false').lower()=='true',
          int(os.getenv('MIN_CONFIDENCE','65')),frozenset(x.strip().upper() for x in os.getenv('ENABLED_STRATEGIES','AI,STM,BLACK4X,OPX4O').split(',') if x.strip()),
          os.getenv('LANGUAGE','en').lower())
