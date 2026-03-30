from travelhub_common.factory import create_app
from app.config import get_settings
from app.database import get_db, initialize_database
from app.routers import auth, usuarios

settings = get_settings()
app = create_app(
    service_name=settings.service_name,
    routers=[auth.router, usuarios.router],
    get_db=get_db,
)


if settings.environment != "test":
    @app.on_event("startup")
    async def startup_initialize_database():
        await initialize_database()
