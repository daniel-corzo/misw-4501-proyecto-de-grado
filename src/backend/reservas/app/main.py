from travelhub_common.factory import create_app
from app.config import get_settings
from app.database import get_db
from app.routers import reservas

settings = get_settings()
app = create_app(
    service_name=settings.service_name,
    routers=[reservas.router],
    get_db=get_db,
)
