from sqlalchemy import text
from travelhub_common.database import make_get_db, init_db, get_engine
from app.config import get_settings
import app.models  # noqa: F401

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
    # unaccent habilita búsquedas por ciudad insensibles a acentos
    engine = get_engine(settings.db_url, settings.environment == "local")
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
