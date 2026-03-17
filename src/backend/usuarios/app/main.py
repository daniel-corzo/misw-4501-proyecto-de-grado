from travelhub_common.factory import create_app
from app.config import get_settings
from app.database import get_db
from app.routers import usuarios

settings = get_settings()
app = create_app(
    service_name=settings.service_name,
    routers=[usuarios.router],
    get_db=get_db,
)
