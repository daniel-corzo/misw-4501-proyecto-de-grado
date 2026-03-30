from travelhub_common.database import make_get_db
from app.config import get_settings

settings = get_settings()
get_db = make_get_db(
    db_url=settings.db_url,
    debug=settings.environment == "local",
)
