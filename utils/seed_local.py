#!/usr/bin/env python3
"""
Seed local de usuarios y hoteles demo para desarrollo.

Uso:
    python seed_local.py

Credenciales:
    admin@travelhub.dev     / Admin123!      (ADMIN,   tipo: viajero)
    manager@travelhub.dev   / Manager123!    (MANAGER, tipo: viajero)
    hotel@travelhub.dev     / Hotel123!      (USER,    tipo: hotel)   -> Dueno de todos los hoteles demo
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

# ── Usuarios ─────────────────────────────────────────────────────────────────

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

# ── Hoteles ──────────────────────────────────────────────────────────────────
#
# Diversidad intencional para validar filtros del listado:
# - 6 paises LATAM, ~12 hoteles.
# - Estrellas: mezcla 3, 4, 5.
# - Amenidades variadas del enum hotel_amenity_enum.
# - Habitaciones: capacidades 1, 2, 3, 4, 6 y precios $80.000 - $2.500.000 COP.
# - Ranking distribuido 3.6 - 4.9 para que rating_desc reordene.
# - Imagenes Unsplash para que la card muestre foto real.

HOTELES = [
    # ── Colombia ──────────────────────────────────────────────────────────
    {
        "nombre": "Hotel Bogota Plaza",
        "direccion": "Calle 100 #18-30",
        "pais": "Colombia", "estado": None, "departamento": "Cundinamarca", "ciudad": "Bogota",
        "descripcion": "Hotel ejecutivo en el norte de Bogota, ideal para viajes de negocios.",
        "amenidades": ["POOL", "GYM", "RESTAURANT", "WIFI", "PARKING", "BREAKFAST_INCLUDED"],
        "estrellas": 4, "ranking": 4.2,
        "imagenes": ["https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800"],
        "habitaciones": [
            {"numero": "101", "capacidad": 2, "descripcion": "Estandar doble con vista a la ciudad.", "monto": 280000, "impuestos": 53200},
            {"numero": "201", "capacidad": 2, "descripcion": "Superior con balcon.", "monto": 380000, "impuestos": 72200},
            {"numero": "301", "capacidad": 4, "descripcion": "Suite familiar con sala.", "monto": 520000, "impuestos": 98800},
        ],
    },
    {
        "nombre": "Andes Boutique Medellin",
        "direccion": "Carrera 35 #8-10, El Poblado",
        "pais": "Colombia", "estado": None, "departamento": "Antioquia", "ciudad": "Medellin",
        "descripcion": "Boutique de diseno en El Poblado con terraza y vista a la montana.",
        "amenidades": ["WIFI", "SPA", "RESTAURANT", "AIR_CONDITIONING", "PET_FRIENDLY"],
        "estrellas": 4, "ranking": 4.6,
        "imagenes": ["https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800"],
        "habitaciones": [
            {"numero": "A1", "capacidad": 1, "descripcion": "Single boutique.", "monto": 180000, "impuestos": 34200},
            {"numero": "A2", "capacidad": 2, "descripcion": "Doble con terraza.", "monto": 320000, "impuestos": 60800},
            {"numero": "B1", "capacidad": 3, "descripcion": "Triple con jacuzzi.", "monto": 480000, "impuestos": 91200},
        ],
    },
    {
        "nombre": "Cartagena Beach Resort",
        "direccion": "Carrera 1 #12-05, Bocagrande",
        "pais": "Colombia", "estado": None, "departamento": "Bolivar", "ciudad": "Cartagena",
        "descripcion": "Resort frente al mar con acceso directo a la playa y piscinas infinitas.",
        "amenidades": ["POOL", "BEACH_ACCESS", "WIFI", "RESTAURANT", "SPA", "GYM", "PARKING", "AIR_CONDITIONING"],
        "estrellas": 5, "ranking": 4.8,
        "imagenes": ["https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800"],
        "habitaciones": [
            {"numero": "M101", "capacidad": 2, "descripcion": "Deluxe vista al mar.", "monto": 850000, "impuestos": 161500},
            {"numero": "M201", "capacidad": 4, "descripcion": "Suite familiar con balcon.", "monto": 1350000, "impuestos": 256500},
            {"numero": "P301", "capacidad": 6, "descripcion": "Penthouse presidencial.", "monto": 2500000, "impuestos": 475000},
        ],
    },
    {
        "nombre": "Cali Hostal del Valle",
        "direccion": "Avenida 6 #23-15",
        "pais": "Colombia", "estado": None, "departamento": "Valle del Cauca", "ciudad": "Cali",
        "descripcion": "Opcion economica en el centro, cerca de la zona rosa.",
        "amenidades": ["WIFI", "AIR_CONDITIONING", "PARKING"],
        "estrellas": 3, "ranking": 3.8,
        "imagenes": ["https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800"],
        "habitaciones": [
            {"numero": "1", "capacidad": 1, "descripcion": "Individual economica.", "monto": 95000, "impuestos": 18050},
            {"numero": "2", "capacidad": 2, "descripcion": "Doble estandar.", "monto": 150000, "impuestos": 28500},
        ],
    },
    # ── Mexico ────────────────────────────────────────────────────────────
    {
        "nombre": "CDMX Reforma Grand",
        "direccion": "Paseo de la Reforma 250",
        "pais": "Mexico", "estado": "CDMX", "departamento": "CDMX", "ciudad": "Ciudad de Mexico",
        "descripcion": "Rascacielos de lujo sobre Paseo de la Reforma con spa en el piso 40.",
        "amenidades": ["POOL", "GYM", "SPA", "RESTAURANT", "WIFI", "PARKING", "BREAKFAST_INCLUDED", "AIR_CONDITIONING"],
        "estrellas": 5, "ranking": 4.7,
        "imagenes": ["https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800"],
        "habitaciones": [
            {"numero": "1501", "capacidad": 2, "descripcion": "King deluxe con vista al Angel.", "monto": 1200000, "impuestos": 228000},
            {"numero": "2001", "capacidad": 3, "descripcion": "Executive suite.", "monto": 1650000, "impuestos": 313500},
        ],
    },
    {
        "nombre": "Cancun Paradise Resort",
        "direccion": "Boulevard Kukulcan Km 14",
        "pais": "Mexico", "estado": "Quintana Roo", "departamento": "Quintana Roo", "ciudad": "Cancun",
        "descripcion": "All-inclusive en la zona hotelera con acceso privado a la playa.",
        "amenidades": ["POOL", "BEACH_ACCESS", "RESTAURANT", "SPA", "GYM", "WIFI", "BREAKFAST_INCLUDED", "AIR_CONDITIONING"],
        "estrellas": 5, "ranking": 4.9,
        "imagenes": ["https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800"],
        "habitaciones": [
            {"numero": "O101", "capacidad": 2, "descripcion": "Ocean view doble.", "monto": 980000, "impuestos": 186200},
            {"numero": "O201", "capacidad": 4, "descripcion": "Family ocean suite.", "monto": 1480000, "impuestos": 281200},
            {"numero": "V301", "capacidad": 6, "descripcion": "Swim-up villa.", "monto": 2200000, "impuestos": 418000},
        ],
    },
    {
        "nombre": "Playa del Carmen Eco Lodge",
        "direccion": "Quinta Avenida Norte",
        "pais": "Mexico", "estado": "Quintana Roo", "departamento": "Quintana Roo", "ciudad": "Playa del Carmen",
        "descripcion": "Eco-lodge con cabanas de palapa entre la selva y la playa.",
        "amenidades": ["POOL", "BEACH_ACCESS", "WIFI", "PET_FRIENDLY", "RESTAURANT"],
        "estrellas": 4, "ranking": 4.4,
        "imagenes": ["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800"],
        "habitaciones": [
            {"numero": "C1", "capacidad": 2, "descripcion": "Cabana doble jungla.", "monto": 420000, "impuestos": 79800},
            {"numero": "C2", "capacidad": 3, "descripcion": "Cabana triple playa.", "monto": 580000, "impuestos": 110200},
        ],
    },
    # ── Argentina ─────────────────────────────────────────────────────────
    {
        "nombre": "Buenos Aires Palermo Soho",
        "direccion": "Honduras 5700, Palermo",
        "pais": "Argentina", "estado": None, "departamento": "CABA", "ciudad": "Buenos Aires",
        "descripcion": "Hotel de diseno en el corazon de Palermo Soho, a pasos de la vida nocturna.",
        "amenidades": ["WIFI", "GYM", "RESTAURANT", "AIR_CONDITIONING", "PARKING"],
        "estrellas": 4, "ranking": 4.5,
        "imagenes": ["https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800"],
        "habitaciones": [
            {"numero": "101", "capacidad": 1, "descripcion": "Single urbano.", "monto": 220000, "impuestos": 41800},
            {"numero": "102", "capacidad": 2, "descripcion": "Doble con escritorio.", "monto": 340000, "impuestos": 64600},
            {"numero": "201", "capacidad": 4, "descripcion": "Loft familiar.", "monto": 620000, "impuestos": 117800},
        ],
    },
    {
        "nombre": "Mendoza Vineyard Inn",
        "direccion": "Ruta 60, Lujan de Cuyo",
        "pais": "Argentina", "estado": None, "departamento": "Mendoza", "ciudad": "Mendoza",
        "descripcion": "Posada entre vinedos con catas diarias y vista a los Andes.",
        "amenidades": ["POOL", "SPA", "RESTAURANT", "WIFI", "PET_FRIENDLY", "BREAKFAST_INCLUDED"],
        "estrellas": 4, "ranking": 4.6,
        "imagenes": ["https://images.unsplash.com/photo-1455587734955-081b22074882?w=800"],
        "habitaciones": [
            {"numero": "V1", "capacidad": 2, "descripcion": "Suite vineyard view.", "monto": 540000, "impuestos": 102600},
            {"numero": "V2", "capacidad": 3, "descripcion": "Suite con chimenea.", "monto": 720000, "impuestos": 136800},
        ],
    },
    # ── Peru ──────────────────────────────────────────────────────────────
    {
        "nombre": "Lima Miraflores Bay",
        "direccion": "Malecon Cisneros 1234",
        "pais": "Peru", "estado": None, "departamento": "Lima", "ciudad": "Lima",
        "descripcion": "Vista al oceano desde Miraflores, con restaurante de autor.",
        "amenidades": ["POOL", "GYM", "RESTAURANT", "WIFI", "PARKING", "AIR_CONDITIONING"],
        "estrellas": 5, "ranking": 4.7,
        "imagenes": ["https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800"],
        "habitaciones": [
            {"numero": "B101", "capacidad": 2, "descripcion": "Bay view king.", "monto": 780000, "impuestos": 148200},
            {"numero": "B201", "capacidad": 4, "descripcion": "Family bay suite.", "monto": 1150000, "impuestos": 218500},
        ],
    },
    {
        "nombre": "Cusco Andean Heritage",
        "direccion": "Calle Suecia 320",
        "pais": "Peru", "estado": None, "departamento": "Cusco", "ciudad": "Cusco",
        "descripcion": "Casona colonial a dos cuadras de la Plaza de Armas.",
        "amenidades": ["WIFI", "RESTAURANT", "BREAKFAST_INCLUDED", "PET_FRIENDLY"],
        "estrellas": 3, "ranking": 4.0,
        "imagenes": ["https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?w=800"],
        "habitaciones": [
            {"numero": "H1", "capacidad": 1, "descripcion": "Single colonial.", "monto": 130000, "impuestos": 24700},
            {"numero": "H2", "capacidad": 2, "descripcion": "Doble con patio.", "monto": 210000, "impuestos": 39900},
            {"numero": "H3", "capacidad": 4, "descripcion": "Suite familiar heritage.", "monto": 380000, "impuestos": 72200},
        ],
    },
    # ── Chile ─────────────────────────────────────────────────────────────
    {
        "nombre": "Santiago Las Condes Tower",
        "direccion": "Avenida Apoquindo 4500",
        "pais": "Chile", "estado": None, "departamento": "Region Metropolitana", "ciudad": "Santiago",
        "descripcion": "Torre ejecutiva en Las Condes con piscina panoramica.",
        "amenidades": ["POOL", "GYM", "WIFI", "RESTAURANT", "PARKING", "BREAKFAST_INCLUDED", "AIR_CONDITIONING"],
        "estrellas": 4, "ranking": 4.3,
        "imagenes": ["https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800"],
        "habitaciones": [
            {"numero": "E1", "capacidad": 1, "descripcion": "Executive single.", "monto": 260000, "impuestos": 49400},
            {"numero": "E2", "capacidad": 2, "descripcion": "Executive doble.", "monto": 390000, "impuestos": 74100},
        ],
    },
    # ── Brasil ────────────────────────────────────────────────────────────
    {
        "nombre": "Rio Copacabana Beachfront",
        "direccion": "Avenida Atlantica 2000",
        "pais": "Brasil", "estado": "Rio de Janeiro", "departamento": "Rio de Janeiro", "ciudad": "Rio de Janeiro",
        "descripcion": "Frente a la playa de Copacabana con rooftop bar.",
        "amenidades": ["POOL", "BEACH_ACCESS", "GYM", "RESTAURANT", "SPA", "WIFI", "AIR_CONDITIONING"],
        "estrellas": 5, "ranking": 4.8,
        "imagenes": ["https://images.unsplash.com/photo-1551918120-9739cb430c6d?w=800"],
        "habitaciones": [
            {"numero": "C101", "capacidad": 2, "descripcion": "Copa doble vista mar.", "monto": 1050000, "impuestos": 199500},
            {"numero": "C201", "capacidad": 3, "descripcion": "Copa junior suite.", "monto": 1450000, "impuestos": 275500},
            {"numero": "C301", "capacidad": 6, "descripcion": "Ocean penthouse.", "monto": 2400000, "impuestos": 456000},
        ],
    },
    {
        "nombre": "Sao Paulo Paulista Business",
        "direccion": "Avenida Paulista 1500",
        "pais": "Brasil", "estado": "Sao Paulo", "departamento": "Sao Paulo", "ciudad": "Sao Paulo",
        "descripcion": "Hotel de negocios sobre la Avenida Paulista.",
        "amenidades": ["WIFI", "GYM", "RESTAURANT", "PARKING", "AIR_CONDITIONING"],
        "estrellas": 3, "ranking": 3.6,
        "imagenes": ["https://images.unsplash.com/photo-1587874522487-ac01d07b2aba?w=800"],
        "habitaciones": [
            {"numero": "P1", "capacidad": 1, "descripcion": "Business single.", "monto": 170000, "impuestos": 32300},
            {"numero": "P2", "capacidad": 2, "descripcion": "Business doble.", "monto": 240000, "impuestos": 45600},
        ],
    },
]

# ── Constantes compartidas ──────────────────────────────────────────────────

CHECK_IN = time(15, 0)
CHECK_OUT = time(11, 0)
VALOR_MINIMO_MODIFICACION = 50000.0

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
            INSERT INTO usuario (id, created_at, updated_at, email, hashed_contrasena, tipo, role)
            VALUES (%s, %s, %s, %s, %s, %s::tipousuario, %s::roleenum)
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

    # -- Hoteles + habitaciones + politicas -------------------------------
    print("Insertando hoteles...")
    hotel_user_id = user_ids["hotel@travelhub.dev"]

    for h in HOTELES:
        hotel_id = uuid.uuid4()
        ts = now()

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
                "+57 300 000 0003", "hotel@travelhub.dev", h["imagenes"],
                CHECK_IN, CHECK_OUT, VALOR_MINIMO_MODIFICACION,
                str(hotel_user_id),
            ),
        )
        print(f"  OK {h['nombre']} ({h['ciudad']}, {h['pais']}, {h['estrellas']}*, rank {h['ranking']})")

        for hab in h["habitaciones"]:
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
                    hab["numero"], hab["capacidad"], hab["descripcion"], [],
                    hab["monto"], hab["impuestos"], True, str(hotel_id),
                ),
            )
            print(f"    - Hab {hab['numero']} (cap {hab['capacidad']}, ${hab['monto']:,} COP)")

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

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nSeed completado: {len(USUARIOS)} usuarios, {len(HOTELES)} hoteles.")

if __name__ == "__main__":
    main()
