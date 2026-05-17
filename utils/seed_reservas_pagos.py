#!/usr/bin/env python3
"""
Seed de reservas y pagos para desarrollo local.

Descubre automáticamente los hoteles, habitaciones y viajeros existentes
en la BD y les inserta reservas distribuidas en los últimos ~9 meses.

Las reservas confirmadas sirven para el reporte de ocupación y el de ingresos.
Unas pocas reservas canceladas/pendientes permiten verificar que los reportes
las excluyen correctamente.

No elimina ni modifica ningún dato existente.

Requisitos:
    pip install psycopg2-binary --index-url https://pypi.org/simple/

Uso:
    python seed_reservas_pagos.py
"""

import uuid
from datetime import date, datetime, timedelta, timezone

import psycopg2

# ── Configuración ─────────────────────────────────────────────────────────────

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "travelhub"
DB_USER = "travelhub"
DB_PASS = "travelhub"


def utc_dt(year: int, month: int, day: int, hour: int = 12) -> datetime:
    return datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc)


def generate_patron(start: date, end: date) -> list[tuple[int, int, int, int]]:
    """
    Genera una lista de (año, mes, día, noches) cubriendo el rango [start, end].
    Produce 2-3 reservas por mes con noches variadas para que cada habitación
    tenga un perfil de ocupación diferente al asignarse cíclicamente.
    """
    patron: list[tuple[int, int, int, int]] = []
    cur = date(start.year, start.month, 1)
    month_index = 0
    while cur <= end:
        year, month = cur.year, cur.month
        # 2-3 reservas por mes alternando
        slots = [
            (8,  2 + (month_index % 3)),     # noches 2, 3, 4, ciclo
            (20, 1 + ((month_index + 1) % 4)),
        ]
        if month_index % 2 == 0:
            slots.append((26, 3))

        for dia, noches in slots:
            # Evitar que check_in + noches supere el fin de mes
            try:
                check_in = date(year, month, dia + 1)
            except ValueError:
                continue
            check_out = check_in + timedelta(days=noches)
            # Solo si check_in está dentro del período [start, end]
            if check_in >= start:
                patron.append((year, month, dia, noches))

        # Avanzar al siguiente mes
        if month == 12:
            cur = date(year + 1, 1, 1)
        else:
            cur = date(year, month + 1, 1)
        month_index += 1

    return patron


def main() -> None:
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )
    conn.autocommit = False
    cur = conn.cursor()

    # ── Período: desde 9 meses atrás hasta hoy ────────────────────────────────
    today = date.today()
    start = today - timedelta(days=270)  # ~9 meses
    patron = generate_patron(start, today)

    # ── Lookup: viajero ───────────────────────────────────────────────────────
    cur.execute(
        "SELECT id, email FROM usuario WHERE tipo = 'VIAJERO' ORDER BY created_at LIMIT 1"
    )
    row = cur.fetchone()
    if not row:
        print("ERROR: no se encontró ningún usuario de tipo VIAJERO.")
        print("       Crea un usuario viajero primero (regístrate en la app).")
        return
    viajero_id, viajero_email = row
    print(f"Viajero: {viajero_email} ({viajero_id})")
    print(f"Periodo: {start} -> {today}  ({len(patron)} reservas/hotel)")

    # ── Lookup: todos los hoteles con habitaciones ────────────────────────────
    cur.execute(
        """
        SELECT h.id, h.nombre, u.email
        FROM hotel h
        JOIN usuario u ON h.usuario_id = u.id
        ORDER BY h.created_at
        """
    )
    hoteles = cur.fetchall()
    if not hoteles:
        print("ERROR: no se encontró ningún hotel.")
        print("       Registra un hotel primero desde la app.")
        return

    total_insertado = 0

    for hotel_id, hotel_nombre, partner_email in hoteles:
        cur.execute(
            "SELECT id, numero, monto, impuestos FROM habitacion WHERE hotel_id = %s ORDER BY numero",
            (hotel_id,),
        )
        habitaciones = cur.fetchall()
        if not habitaciones:
            print(f"\nSKIP '{hotel_nombre}': sin habitaciones.")
            continue

        print(f"\nHotel: {hotel_nombre} (partner: {partner_email})")
        for hab_id, numero, monto, impuestos in habitaciones:
            print(f"  Hab {numero}: id={hab_id}  monto=${monto:,}  imp=${impuestos:,}")

        # Asigna habitaciones cíclicamente al patrón mensual, con offset por mes
        # para que las habitaciones tengan perfiles de ocupación distintos.
        print(f"  Insertando {len(patron)} reservas confirmadas...")
        for i, (anio, mes, dia, noches) in enumerate(patron):
            # Offset por mes para variar la habitación asignada
            mes_index = (anio * 12 + mes) % len(habitaciones)
            hab_index = (i + mes_index) % len(habitaciones)
            hab_id, numero, monto, impuestos = habitaciones[hab_index]
            monto_total = noches * (monto + impuestos)

            pago_id    = uuid.uuid4()
            reserva_id = uuid.uuid4()
            pago_ts    = utc_dt(anio, mes, dia)
            check_in   = utc_dt(anio, mes, dia + 1, 15)
            check_out  = check_in + timedelta(days=noches)

            cur.execute(
                """
                INSERT INTO pagos (id, created_at, updated_at, monto, medio_de_pago, estado, tarjeta_ultimos_4)
                VALUES (%s, %s, %s, %s, %s, %s::estadopago, %s)
                """,
                (str(pago_id), pago_ts, pago_ts, monto_total, "credit_card", "successful", "4242"),
            )

            cur.execute(
                """
                INSERT INTO reservas (
                    id, created_at, updated_at,
                    check_in, check_out, estado, personas,
                    viajero_id, habitaciones_ids, pago_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::uuid[], %s)
                """,
                (
                    str(reserva_id), pago_ts, pago_ts,
                    check_in, check_out, "confirmada", 2,
                    str(viajero_id),
                    "{" + str(hab_id) + "}",
                    str(pago_id),
                ),
            )
            total_insertado += 1

        # Insertar 2 reservas extra con estados cancelada/pendiente para verificar
        # que los reportes las excluyan correctamente.
        if habitaciones:
            hab_id_extra, numero_extra, _, _ = habitaciones[0]
            for estado_extra in ("cancelada", "pendiente"):
                extra_id = uuid.uuid4()
                # Fecha segura: 15 días atrás
                extra_ts = utc_dt(today.year, today.month, max(1, today.day - 15))
                cur.execute(
                    """
                    INSERT INTO reservas (
                        id, created_at, updated_at,
                        check_in, check_out, estado, personas,
                        viajero_id, habitaciones_ids, pago_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::uuid[], %s)
                    """,
                    (
                        str(extra_id), extra_ts, extra_ts,
                        extra_ts, extra_ts + timedelta(days=2), estado_extra, 2,
                        str(viajero_id),
                        "{" + str(hab_id_extra) + "}",
                        None,
                    ),
                )
            print(f"  + 2 reservas extra (cancelada, pendiente) para verificacion de filtros")

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nSeed completado: {total_insertado} reservas confirmadas + pagos insertados.")
    print(f"  + 2 reservas no-confirmadas por hotel (excluidas del reporte).")
    print(f"  Inicia sesion con el partner de cualquier hotel para ver el reporte de ocupacion.")


if __name__ == "__main__":
    main()
