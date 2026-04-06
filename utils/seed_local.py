#!/usr/bin/env python3
"""
Seed local de usuarios y hotel demo para desarrollo.

Uso:
    python seed_local.py

Credenciales:
    admin@travelhub.dev     / Admin123!      (ADMIN,   tipo: viajero)
    manager@travelhub.dev   / Manager123!    (MANAGER, tipo: viajero)
    hotel@travelhub.dev     / Hotel123!      (USER,    tipo: hotel)   -> Hotel Bogota Plaza
    viajero@travelhub.dev   / Viajero123!    (USER,    tipo: viajero)
"""

import uuid
import bcrypt
import psycopg2
from datetime import datetime, time, timezone

# ── Configuracion ────────────────────────────────────────────────────────────

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "travelhub"
DB_USER = "travelhub"
DB_PASS = "travelhub"

# ── Datos ─────────────────────────────────────────────────────────────────────

USUARIOS = [
    {
        "email": "admin@travelhub.dev",
        "password": "Admin123!",
        "role": "ADMIN",
        "tipo": "VIAJERO",
        "nombre": "Admin TravelHub",
        "contacto": "+57 300 000 0001",
    },
    {
        "email": "manager@travelhub.dev",
        "password": "Manager123!",
        "role": "MANAGER",
        "tipo": "VIAJERO",
        "nombre": "Manager TravelHub",
        "contacto": "+57 300 000 0002",
    },
    {
        "email": "hotel@travelhub.dev",
        "password": "Hotel123!",
        "role": "USER",
        "tipo": "HOTEL",
        "nombre": None,
        "contacto": None,
    },
    {
        "email": "viajero@travelhub.dev",
        "password": "Viajero123!",
        "role": "USER",
        "tipo": "VIAJERO",
        "nombre": "Juan Viajero",
        "contacto": "+57 300 000 0004",
    },
]

HOTEL = {
    "nombre": "Hotel Bogota Plaza",
    "direccion": "Calle 100 #18-30",
    "pais": "Colombia",
    "estado": None,
    "departamento": "Cundinamarca",
    "ciudad": "Bogota",
    "descripcion": "Hotel demo con piscina, gimnasio y restaurante en el norte de Bogota.",
    "amenidades": ["POOL", "GYM", "RESTAURANT", "WIFI", "PARKING", "BREAKFAST_INCLUDED"],
    "estrellas": 4,
    "ranking": 4.2,
    "contacto_celular": "+57 300 000 0003",
    "contacto_email": "hotel@travelhub.dev",
    "imagenes": [],
    "check_in": time(15, 0),
    "check_out": time(11, 0),
    "valor_minimo_modificacion": 50000.0,
}

HABITACIONES = [
    {
        "numero": "101",
        "capacidad": 2,
        "descripcion": "Habitacion estandar doble con vista a la ciudad.",
        "imagenes": [],
        "monto": 180000,
        "impuestos": 34200,
        "disponible": True,
    },
    {
        "numero": "201",
        "capacidad": 2,
        "descripcion": "Habitacion superior con balcon.",
        "imagenes": [],
        "monto": 280000,
        "impuestos": 53200,
        "disponible": True,
    },
    {
        "numero": "301",
        "capacidad": 4,
        "descripcion": "Suite familiar con sala y dos camas dobles.",
        "imagenes": [],
        "monto": 450000,
        "impuestos": 85500,
        "disponible": True,
    },
]

POLITICAS = [
    {
        "nombre": "Cancelacion gratuita",
        "descripcion": "Cancelacion sin costo hasta 48 horas antes del check-in.",
        "tipo": "cancelacion",
        "penalizacion": 0,
        "dias_antelacion": 2,
    },
    {
        "nombre": "Cancelacion tardia",
        "descripcion": "Cancelacion con menos de 48 horas tiene penalizacion del 50%.",
        "tipo": "cancelacion",
        "penalizacion": 50,
        "dias_antelacion": 0,
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def now():
    return datetime.now(timezone.utc)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )
    conn.autocommit = False
    cur = conn.cursor()

    # -- Limpieza (orden por FK) -------------------------------------------
    print("Limpiando tablas...")
    cur.execute("DELETE FROM habitacion")
    cur.execute("DELETE FROM politica")
    cur.execute("DELETE FROM hotel")
    cur.execute("DELETE FROM viajero")
    cur.execute("DELETE FROM revoked_token")
    cur.execute("DELETE FROM usuario")

    # -- Usuarios ----------------------------------------------------------
    print("Insertando usuarios...")
    user_ids = {}
    for u in USUARIOS:
        uid = uuid.uuid4()
        user_ids[u["email"]] = uid
        hashed = hash_password(u["password"])
        ts = now()

        cur.execute(
            """
            INSERT INTO usuario (id, created_at, updated_at, email, hashed_contrasena, tipo, role, hotel_id)
            VALUES (%s, %s, %s, %s, %s, %s::tipousuario, %s::roleenum, NULL)
            """,
            (str(uid), ts, ts, u["email"], hashed, u["tipo"], u["role"]),
        )

        if u["nombre"]:
            cur.execute(
                """
                INSERT INTO viajero (id, created_at, updated_at, nombre, contacto, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), ts, ts, u["nombre"], u["contacto"], str(uid)),
            )

        tag = f"[{u['role']}, {u['tipo']}]"
        print(f"  OK {u['email']}  /  {u['password']}  {tag}")

    # -- Hotel -------------------------------------------------------------
    print("Insertando hotel...")
    hotel_user_id = user_ids["hotel@travelhub.dev"]
    hotel_id = uuid.uuid4()
    ts = now()
    h = HOTEL

    cur.execute(
        """
        INSERT INTO hotel (
            id, created_at, updated_at,
            nombre, direccion, pais, estado, departamento, ciudad,
            descripcion, amenidades, estrellas, ranking,
            contacto_celular, contacto_email, imagenes,
            check_in, check_out, valor_minimo_modificacion,
            usuario_id
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s::hotel_amenity_enum[], %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s
        )
        """,
        (
            str(hotel_id), ts, ts,
            h["nombre"], h["direccion"], h["pais"], h["estado"], h["departamento"], h["ciudad"],
            h["descripcion"], h["amenidades"], h["estrellas"], h["ranking"],
            h["contacto_celular"], h["contacto_email"], h["imagenes"],
            h["check_in"], h["check_out"], h["valor_minimo_modificacion"],
            str(hotel_user_id),
        ),
    )

    # Vincular hotel_id en el usuario
    cur.execute(
        "UPDATE usuario SET hotel_id = %s WHERE id = %s",
        (str(hotel_id), str(hotel_user_id)),
    )
    print(f"  OK {h['nombre']} ({h['ciudad']}, {h['estrellas']} estrellas)")

    # -- Habitaciones ------------------------------------------------------
    print("Insertando habitaciones...")
    for hab in HABITACIONES:
        cur.execute(
            """
            INSERT INTO habitacion (
                id, created_at, updated_at,
                numero, capacidad, descripcion, imagenes,
                monto, impuestos, disponible, hotel_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()), ts, ts,
                hab["numero"], hab["capacidad"], hab["descripcion"], hab["imagenes"],
                hab["monto"], hab["impuestos"], hab["disponible"], str(hotel_id),
            ),
        )
        print(f"  OK Hab {hab['numero']} (cap: {hab['capacidad']}, ${hab['monto']:,} COP)")

    # -- Politicas ---------------------------------------------------------
    print("Insertando politicas...")
    for pol in POLITICAS:
        cur.execute(
            """
            INSERT INTO politica (
                id, created_at, updated_at,
                nombre, descripcion, tipo, penalizacion, dias_antelacion, hotel_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()), ts, ts,
                pol["nombre"], pol["descripcion"], pol["tipo"],
                pol["penalizacion"], pol["dias_antelacion"], str(hotel_id),
            ),
        )
        print(f"  OK Politica: {pol['nombre']}")

    conn.commit()
    cur.close()
    conn.close()
    print("\nSeed completado.")

if __name__ == "__main__":
    main()
