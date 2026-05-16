from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch

import pytest

from travelhub_common.booking_email import (
    BookingEmailConfigurationError,
    BookingEmailEvent,
    BookingEmailPayload,
    render_booking_email,
    send_booking_email,
)
from travelhub_common.config import BaseAppSettings


def _settings(**overrides):
    values = {
        "smtp_host": "email-smtp.us-east-1.amazonaws.com",
        "smtp_port": 587,
        "smtp_user": "smtp-user",
        "smtp_pass": "smtp-pass",
        "smtp_from_email": "no-reply@travel-hub.online",
        "smtp_sender_name": "TravelHub",
        "smtp_use_tls": True,
        "frontend_base_url": "https://travel-hub.online",
    }
    values.update(overrides)
    return BaseAppSettings(**values)


def _payload(event: BookingEmailEvent = BookingEmailEvent.confirmed):
    return BookingEmailPayload(
        event=event,
        recipient_email="viajero@example.com",
        hotel_name="Hotel Aurora",
        reservation_id="0d6b8bd5-52bb-4e50-8730-63d7c41d7770",
        reservation_code="TH-0D6B8BD5",
        room_name="Suite Premium",
        room_number="808",
        check_in=date(2026, 7, 2),
        check_out=date(2026, 7, 6),
        guest_count=2,
        traveler_name="María",
        payment_amount=420000,
        payment_method="tarjeta_credito",
        payment_date=datetime(2026, 6, 1, 13, 45, tzinfo=UTC),
        card_last4="4242",
        total_nights=4,
        total_amount=420000,
    )


def test_render_booking_email_confirmed_contains_branding_and_details():
    content = render_booking_email(_payload(), "https://travel-hub.online")

    assert content.subject == "Reserva en Hotel Aurora - confirmada"
    assert "TravelHub" in content.html_body
    assert "Tu reserva ya está confirmada" in content.html_body
    assert "https://travel-hub.online" in content.html_body
    assert "Suite Premium" in content.html_body
    assert "02/07/2026" in content.html_body
    assert "06/07/2026" in content.html_body
    assert "Huéspedes" in content.html_body
    assert "TH-0D6B8BD5" in content.text_body


def test_render_booking_email_payment_receipt_contains_payment_summary():
    content = render_booking_email(
        _payload(BookingEmailEvent.payment_receipt),
        "https://travel-hub.online",
    )

    assert content.subject == "Reserva en Hotel Aurora - comprobante de pago"
    assert "Recibimos tu pago con éxito" in content.html_body
    assert "Pago recibido" in content.html_body
    assert "$420.000" in content.html_body
    assert "Terminada en 4242" in content.html_body
    assert "Fecha de pago" in content.text_body


def test_send_booking_email_uses_starttls_and_sends_message():
    transport = MagicMock()
    smtp_client = MagicMock()
    transport.__enter__.return_value = smtp_client

    with patch("travelhub_common.booking_email.smtplib.SMTP", return_value=transport):
        content = send_booking_email(_payload(), _settings())

    smtp_client.ehlo.assert_called()
    smtp_client.starttls.assert_called_once()
    smtp_client.login.assert_called_once_with("smtp-user", "smtp-pass")
    smtp_client.send_message.assert_called_once()
    message = smtp_client.send_message.call_args.args[0]
    assert message["To"] == "viajero@example.com"
    assert message["Subject"] == content.subject


def test_send_booking_email_uses_ssl_when_port_465():
    transport = MagicMock()
    smtp_client = MagicMock()
    transport.__enter__.return_value = smtp_client

    with patch("travelhub_common.booking_email.smtplib.SMTP_SSL", return_value=transport) as smtp_ssl:
        send_booking_email(_payload(), _settings(smtp_port=465, smtp_use_tls=False))

    smtp_ssl.assert_called_once_with(
        "email-smtp.us-east-1.amazonaws.com",
        465,
        timeout=30,
    )
    smtp_client.login.assert_called_once_with("smtp-user", "smtp-pass")
    smtp_client.send_message.assert_called_once()


def test_send_booking_email_raises_when_config_missing():
    with pytest.raises(BookingEmailConfigurationError) as exc:
        send_booking_email(_payload(), _settings(smtp_host=""))

    assert "smtp_host" in str(exc.value)