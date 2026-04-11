import app.models  # noqa: F401 — register SQLAlchemy metadata for create_all

from travelhub_common.database import make_get_db, init_db
from app.config import get_settings

settings = get_settings()
get_db = make_get_db(
    db_url=settings.db_url,
    debug=settings.environment == "local",
)

async def initialize_database():
    await init_db(
        db_url=settings.db_url,
        debug=settings.environment == "local",
    )
