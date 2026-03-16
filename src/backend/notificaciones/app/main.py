from travelhub_common.factory import create_app
from app.config import get_settings
# from app.routers import <modulo>  # TODO: descomentar al agregar routers

settings = get_settings()
app = create_app(
    service_name=settings.service_name,
    routers=[],   # TODO: agregar routers aqui, ej: [auth.router]
)
