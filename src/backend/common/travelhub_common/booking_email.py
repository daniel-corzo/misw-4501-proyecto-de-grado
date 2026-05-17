import smtplib
from datetime import date, datetime
from email.message import EmailMessage
from email.utils import formataddr
from enum import Enum
from html import escape

from pydantic import BaseModel, Field

from travelhub_common.config import BaseAppSettings


class BookingEmailEvent(str, Enum):
    confirmed = "confirmada"
    cancelled = "cancelada"
    payment_receipt = "comprobante de pago"


class BookingEmailConfigurationError(RuntimeError):
    pass


class BookingEmailPayload(BaseModel):
    event: BookingEmailEvent
    recipient_email: str = Field(min_length=1)
    hotel_name: str = Field(min_length=1)
    reservation_id: str = Field(min_length=1)
    reservation_code: str | None = None
    room_name: str | None = None
    room_number: str | None = None
    check_in: date
    check_out: date
    guest_count: int = Field(ge=1)
    traveler_name: str | None = None
    payment_amount: int | None = None
    payment_method: str | None = None
    payment_date: datetime | None = None
    card_last4: str | None = None
    total_nights: int | None = Field(default=None, ge=0)
    total_amount: int | None = None


class BookingEmailContent(BaseModel):
    subject: str
    html_body: str
    text_body: str


_EVENT_META = {
    BookingEmailEvent.confirmed: {
        "accent": "#34C759",
        "icon": "&#10003;",
        "headline": "Tu reserva ya está confirmada",
        "intro": "Ya puedes contar con tu hospedaje. Preparamos este correo como comprobante con los datos más importantes de tu reserva.",
        "cta": "Ver más viajes",
    },
    BookingEmailEvent.cancelled: {
        "accent": "#FF383C",
        "icon": "&#10005;",
        "headline": "Tu reserva fue cancelada",
        "intro": "Queremos ponértelo fácil: aquí tienes el resumen de la reserva cancelada para que conserves el registro y puedas planear tu próxima escapada.",
        "cta": "Explorar hoteles",
    },
    BookingEmailEvent.payment_receipt: {
        "accent": "#0077FF",
        "icon": "&#128179;",
        "headline": "Recibimos tu pago con éxito",
        "intro": "Tu pago quedó registrado correctamente. Este correo funciona como comprobante y resume los detalles clave de tu hospedaje.",
        "cta": "Ir a TravelHub",
    },
}


def _format_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%d/%m/%Y %H:%M UTC")


def _format_money(value: int | None) -> str | None:
    if value is None:
        return None
    return f"${value:,.0f}".replace(",", ".")


def _normalize_frontend_url(frontend_base_url: str) -> str:
    normalized = frontend_base_url.strip() or "https://travel-hub.online"
    return normalized.rstrip("/")


def _build_detail_rows(payload: BookingEmailPayload) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    room_display = payload.room_name or "Habitación asignada"
    if payload.room_number:
        room_display = f"{room_display} · {payload.room_number}"

    base_details = [
        ("Reserva", payload.reservation_code or payload.reservation_id),
        ("Hotel", payload.hotel_name),
        ("Habitación", room_display),
        ("Check-in", _format_date(payload.check_in)),
        ("Check-out", _format_date(payload.check_out)),
        ("Huéspedes", str(payload.guest_count)),
    ]

    optional_details: list[tuple[str, str]] = []
    if payload.total_nights is not None:
        optional_details.append(("Noches", str(payload.total_nights)))
    if payload.total_amount is not None:
        total_amount = _format_money(payload.total_amount)
        if total_amount:
            optional_details.append(("Total estimado", total_amount))
    if payload.event == BookingEmailEvent.payment_receipt:
        payment_amount = _format_money(payload.payment_amount)
        if payment_amount:
            optional_details.append(("Pago recibido", payment_amount))
        if payload.payment_method:
            optional_details.append(("Medio de pago", payload.payment_method))
        if payload.card_last4:
            optional_details.append(
                ("Tarjeta", f"Terminada en {payload.card_last4}")
            )
        payment_date = _format_datetime(payload.payment_date)
        if payment_date:
            optional_details.append(("Fecha de pago", payment_date))

    return base_details, optional_details


def render_booking_email(
    payload: BookingEmailPayload,
    frontend_base_url: str,
) -> BookingEmailContent:
    meta = _EVENT_META[payload.event]
    website_url = _normalize_frontend_url(frontend_base_url)
    subject = f"Reserva en {payload.hotel_name} - {payload.event.value}"
    traveler_name = payload.traveler_name.strip() if payload.traveler_name else "viajero"
    greeting_name = escape(traveler_name)
    base_details, optional_details = _build_detail_rows(payload)

    all_rows = "".join(
        (
            f"<tr>"
            f"<td style=\"padding: 10px 0; color: #6E6E73; font-size: 14px; border-bottom: 1px solid #E5E5EA;\">{escape(label)}</td>"
            f"<td style=\"padding: 10px 0; color: #1C1C1E; font-size: 14px; font-weight: 600; text-align: right; border-bottom: 1px solid #E5E5EA;\">{escape(value)}</td>"
            f"</tr>"
        )
        for label, value in [*base_details, *optional_details]
    )

    html_body = f"""
<!DOCTYPE html>
<html lang=\"es\">
  <body style=\"margin: 0; padding: 24px 0; background: #F5F5F7; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1C1C1E;\">
    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse: collapse;\">
      <tr>
        <td align=\"center\">
          <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width: 640px; border-collapse: collapse;\">
            <tr>
              <td style=\"padding: 0 24px 24px; text-align: center; color: #0077FF; font-size: 28px; font-weight: 700;\">TravelHub</td>
            </tr>
            <tr>
              <td style=\"background: linear-gradient(135deg, #0077FF 0%, #005FCC 100%); border-radius: 20px 20px 0 0; padding: 32px 32px 20px; text-align: center;\">
                <div style=\"width: 88px; height: 88px; margin: 0 auto 20px; border-radius: 999px; background: {meta['accent']}; color: #FFFFFF; font-size: 40px; font-weight: 700; line-height: 88px; text-align: center;\">{meta['icon']}</div>
                <div style=\"color: #FFFFFF; font-size: 30px; font-weight: 700; line-height: 1.2; margin-bottom: 12px;\">{escape(meta['headline'])}</div>
                <div style=\"color: rgba(255, 255, 255, 0.92); font-size: 16px; line-height: 1.6;\">{escape(meta['intro'])}</div>
              </td>
            </tr>
            <tr>
              <td style=\"background: #FFFFFF; border-radius: 0 0 20px 20px; padding: 32px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.08);\">
                <p style=\"margin: 0 0 16px; font-size: 16px; line-height: 1.6;\">Hola, {greeting_name}.</p>
                <p style=\"margin: 0 0 24px; font-size: 16px; line-height: 1.6; color: #3A3A3C;\">Gracias por confiar en TravelHub. Te compartimos el resumen de tu reserva para que tengas todo a la mano.</p>
                <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse: collapse; margin-bottom: 24px;\">
                  {all_rows}
                </table>
                <div style=\"background: #F5F5F7; border-radius: 16px; padding: 20px 24px; margin-bottom: 24px;\">
                  <div style=\"font-size: 14px; font-weight: 700; color: #0077FF; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em;\">Tu próximo paso</div>
                  <div style=\"font-size: 15px; line-height: 1.6; color: #3A3A3C;\">Si quieres revisar más hospedajes, gestionar nuevas reservas o seguir planeando tu viaje, entra a nuestra web.</div>
                </div>
                <div style=\"text-align: center; margin-bottom: 24px;\">
                  <a href=\"{escape(website_url)}\" style=\"display: inline-block; background: #0077FF; color: #FFFFFF; text-decoration: none; font-size: 16px; font-weight: 700; padding: 14px 24px; border-radius: 10px;\">{escape(meta['cta'])}</a>
                </div>
                <p style=\"margin: 0; font-size: 13px; line-height: 1.6; color: #6E6E73; text-align: center;\">Este correo fue enviado por TravelHub. Si no reconoces esta actividad, comunícate con nuestro equipo desde <a href=\"{escape(website_url)}\" style=\"color: #0077FF; text-decoration: none;\">{escape(website_url)}</a>.</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()

    text_lines = [
        f"TravelHub | {meta['headline']}",
        "",
        f"Hola, {traveler_name}.",
        meta["intro"],
        "",
        "Resumen de la reserva:",
        *[f"- {label}: {value}" for label, value in base_details],
        *[f"- {label}: {value}" for label, value in optional_details],
        "",
        f"Visita TravelHub: {website_url}",
    ]
    text_body = "\n".join(text_lines)

    return BookingEmailContent(
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )


def send_booking_email(
    payload: BookingEmailPayload,
    settings: BaseAppSettings,
) -> BookingEmailContent:
    missing = [
        name
        for name, value in {
            "smtp_host": settings.smtp_host.strip(),
            "smtp_user": settings.smtp_user.strip(),
            "smtp_pass": settings.smtp_pass,
            "smtp_from_email": settings.smtp_from_email.strip(),
        }.items()
        if not value
    ]
    if missing:
        raise BookingEmailConfigurationError(
            "Configuración SMTP incompleta: " + ", ".join(missing)
        )

    content = render_booking_email(payload, settings.frontend_base_url)
    message = EmailMessage()
    message["Subject"] = content.subject
    message["From"] = formataddr(
        (settings.smtp_sender_name.strip() or "TravelHub", settings.smtp_from_email)
    )
    message["To"] = payload.recipient_email
    message.set_content(content.text_body)
    message.add_alternative(content.html_body, subtype="html")

    timeout = max(settings.smtp_timeout_seconds, 1)
    use_ssl = settings.smtp_port == 465
    if use_ssl:
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=timeout,
        ) as smtp_client:
            smtp_client.login(settings.smtp_user, settings.smtp_pass)
            smtp_client.send_message(message)
        return content

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=timeout,
    ) as smtp_client:
        smtp_client.ehlo()
        if settings.smtp_use_tls:
            smtp_client.starttls()
            smtp_client.ehlo()
        smtp_client.login(settings.smtp_user, settings.smtp_pass)
        smtp_client.send_message(message)

    return content