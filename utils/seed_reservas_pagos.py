#!/usr/bin/env python3
"""
Seed de reservas y pagos para desarrollo local.

Descubre automáticamente los hoteles, habitaciones y viajeros existentes
en la BD y les inserta pagos exitosos distribuidos mes a mes en el año
actual. No elimina ni modifica ningún dato existente.

Requisitos:
    pip install psycopg2-binary --index-url https://pypi.org/simple/

Uso:
    python seed_reservas_pagos.py
"""

import uuid
from datetime import datetime, timedelta, timezone

import psycopg2

# ── Configuración ─────────────────────────────────────────────────────────────

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "travelhub"
DB_USER = "travelhub"
DB_PASS = "travelhub"

# Distribución de reservas por mes del año actual.
# (mes, dia_pago, noches): se repite cíclicamente sobre las habitaciones
# disponibles por hotel.
PATRON_MENSUAL = [
    (1,   8, 2),
    (1,  20, 3),
    (2,   5, 2),
    (2,  18, 1),
    (3,   3, 2),
    (3,  14, 3),
    (3,  25, 3),
    (4,   9, 1),
    (4,  22, 4),
    (5,   2, 1),
    (5,  14, 2),
]


def utc_dt(year: int, month: int, day: int, hour: int = 12) -> datetime:
    return datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc)


def main() -> None:
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )
    conn.autocommit = False
    cur = conn.cursor()

    anio = datetime.now().year

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

        # Asigna habitaciones cíclicamente al patrón mensual
        print(f"  Insertando {len(PATRON_MENSUAL)} reservas...")
        for i, (mes, dia, noches) in enumerate(PATRON_MENSUAL):
            hab_id, numero, monto, impuestos = habitaciones[i % len(habitaciones)]
            monto_total = noches * (monto + impuestos)

            pago_id   = uuid.uuid4()
            reserva_id = uuid.uuid4()
            pago_ts   = utc_dt(anio, mes, dia)
            check_in  = utc_dt(anio, mes, dia + 1, 15)
            check_out = check_in + timedelta(days=noches)

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

            print(
                f"    {anio}-{mes:02d}-{dia:02d}  Hab {numero}  {noches}n"
                f"  ${monto_total:,} COP"
            )
            total_insertado += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"\n✓ Seed completado: {total_insertado} reservas + pagos insertados.")
    print(f"  Inicia sesión con el partner de cualquier hotel para ver el gráfico.")


if __name__ == "__main__":
    main()
