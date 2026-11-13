"""Persistencia (§8.1): tablas con SQLAlchemy Core. PostgreSQL en publicación; SQLite en pruebas locales."""
import sqlalchemy as sa

meta = sa.MetaData()
FK = {"ondelete": "CASCADE"}

sessions = sa.Table(
    "sessions", meta,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
    sa.Column("consent_version", sa.String(10), nullable=False),
    sa.Column("adult_declared", sa.Boolean, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),
)
profiles = sa.Table(
    "profiles", meta,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id", **FK), nullable=False, index=True),
    sa.Column("version", sa.Integer, nullable=False),
    sa.Column("questionnaire_version", sa.String(10), nullable=False),
    sa.Column("policy_version", sa.String(10), nullable=False),
    sa.Column("answers", sa.JSON, nullable=False),
    sa.Column("result", sa.JSON, nullable=False),
    sa.Column("status", sa.String(24), nullable=False),
    sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
)
goals = sa.Table(
    "goals", meta,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id", **FK), nullable=False, index=True),
    sa.Column("version", sa.Integer, nullable=False),
    sa.Column("profile_version", sa.Integer, nullable=False),
    sa.Column("data", sa.JSON, nullable=False),
    sa.Column("evaluation", sa.JSON, nullable=False),
    sa.Column("profile_card", sa.JSON, nullable=False),
    sa.Column("status", sa.String(24), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)
comparisons = sa.Table(
    "comparisons", meta,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id", **FK), nullable=False, index=True),
    sa.Column("profile_version", sa.Integer, nullable=False),
    sa.Column("goal_version", sa.Integer, nullable=False),
    sa.Column("policy_version", sa.String(10), nullable=False),
    sa.Column("status", sa.String(12), nullable=False),
    sa.Column("result", sa.String(32), nullable=False),
    sa.Column("payload", sa.JSON, nullable=False),
    sa.Column("explanation", sa.JSON),
    sa.Column("explanation_generated_by", sa.String(12)),
    sa.Column("explanation_model_id", sa.String(64)),
    sa.Column("explanation_prompt_version", sa.String(10)),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)
llm_spend = sa.Table(
    "llm_spend", meta,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("day", sa.String(10), nullable=False, index=True),
    sa.Column("month", sa.String(7), nullable=False, index=True),
    sa.Column("operation", sa.String(16), nullable=False),
    sa.Column("model_id", sa.String(64), nullable=False),
    sa.Column("prompt_version", sa.String(10), nullable=False),
    sa.Column("tokens_in", sa.Integer),
    sa.Column("tokens_out", sa.Integer),
    sa.Column("cost_reserved_usd", sa.Numeric(12, 6), nullable=False),
    sa.Column("cost_settled_usd", sa.Numeric(12, 6)),
    sa.Column("status", sa.String(12), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)
audit_events = sa.Table(
    "audit_events", meta,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("trace_id", sa.String(32), nullable=False),
    sa.Column("corr_token", sa.String(16)),
    sa.Column("operation", sa.String(32), nullable=False),
    sa.Column("policy_version", sa.String(10)),
    sa.Column("prompt_version", sa.String(10)),
    sa.Column("model_id", sa.String(64)),
    sa.Column("duration_ms", sa.Integer),
    sa.Column("status", sa.String(24), nullable=False),
    sa.Column("error_code", sa.String(48)),
    sa.Column("tokens_in", sa.Integer),
    sa.Column("tokens_out", sa.Integer),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
)
rate_limits = sa.Table(
    "rate_limits", meta,
    sa.Column("key_hash", sa.String(64), primary_key=True),
    sa.Column("window_start", sa.String(16), primary_key=True),
    sa.Column("count", sa.Integer, nullable=False),
)


def motor(url: str):
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    eng = sa.create_engine(url, connect_args=args, pool_pre_ping=True, future=True)
    if url.startswith("sqlite"):
        @sa.event.listens_for(eng, "connect")
        def _fk(dbapi_con, _):
            dbapi_con.execute("PRAGMA foreign_keys=ON")
    return eng


def migrar(eng) -> None:
    meta.create_all(eng)
