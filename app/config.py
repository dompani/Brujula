"""Variables de entorno tipadas (§6.4). Sin valores secretos por defecto."""
import os
from dataclasses import dataclass, field
from decimal import Decimal


def _bool(nombre, defecto=False):
    return os.environ.get(nombre, str(defecto)).strip().lower() in ("1", "true", "si", "yes")


@dataclass
class Config:
    app_env: str = field(default_factory=lambda: os.environ.get("APP_ENV", "dev"))
    database_url: str = field(default_factory=lambda: os.environ.get("DATABASE_URL", "sqlite:///./brujula_dev.db"))
    llm_mode: str = field(default_factory=lambda: os.environ.get("LLM_MODE", "demo"))
    llm_provider: str = field(default_factory=lambda: os.environ.get("LLM_PROVIDER", "anthropic"))
    llm_model: str = field(default_factory=lambda: os.environ.get("LLM_MODEL", "claude-sonnet-5-5"))
    llm_api_key: str = field(default_factory=lambda: os.environ.get("LLM_API_KEY", ""))
    cookie_secure: bool = field(default_factory=lambda: _bool("COOKIE_SECURE"))
    allowed_origins: list = field(default_factory=lambda: [o.strip().rstrip("/") for o in (
        os.environ.get("ALLOWED_ORIGINS", "") + "," + os.environ.get("RENDER_EXTERNAL_URL", "")).split(",") if o.strip()]
        or ["http://localhost:8000", "http://127.0.0.1:8000", "http://testserver"])
    session_ttl_hours: int = field(default_factory=lambda: int(os.environ.get("SESSION_TTL_HOURS", "24")))
    profile_validity_months: int = field(default_factory=lambda: int(os.environ.get("PROFILE_VALIDITY_MONTHS", "12")))
    rate_limit_session_per_min: int = field(default_factory=lambda: int(os.environ.get("RATE_LIMIT_SESSION_PER_MIN", "10")))
    rate_limit_session_total: int = field(default_factory=lambda: int(os.environ.get("RATE_LIMIT_SESSION_TOTAL", "50")))
    hmac_secret: str = field(default_factory=lambda: os.environ.get("HMAC_SECRET", "solo-desarrollo"))
    privacy_contact_email: str = field(default_factory=lambda: os.environ.get("PRIVACY_CONTACT_EMAIL", ""))
    app_version: str = field(default_factory=lambda: os.environ.get("APP_VERSION", "0.1.0"))
    git_sha: str = field(default_factory=lambda: (os.environ.get("GIT_SHA") or os.environ.get("RENDER_GIT_COMMIT")
                                                  or "local")[:12])
    budget_daily_usd: Decimal = field(default_factory=lambda: Decimal(os.environ.get("LLM_BUDGET_DAILY_USD", "1")))
    budget_monthly_usd: Decimal = field(default_factory=lambda: Decimal(os.environ.get("LLM_BUDGET_MONTHLY_USD", "10")))
    budget_eval_usd: Decimal = field(default_factory=lambda: Decimal(os.environ.get("LLM_BUDGET_EVAL_USD", "5")))
    price_in: Decimal = field(default_factory=lambda: Decimal(os.environ.get("LLM_PRICE_INPUT_USD_PER_MTOK", "2")))
    price_out: Decimal = field(default_factory=lambda: Decimal(os.environ.get("LLM_PRICE_OUTPUT_USD_PER_MTOK", "10")))
    historico_enabled: bool = field(default_factory=lambda: _bool("HISTORICO_ENABLED", True))

    @property
    def kill_switch(self) -> bool:  # se lee en cada petición, para activarlo sin desplegar de nuevo
        return _bool("LLM_KILL_SWITCH")

    @property
    def llm_real(self) -> bool:
        return self.llm_mode == "real" and bool(self.llm_api_key)


def cargar() -> Config:
    return Config()
