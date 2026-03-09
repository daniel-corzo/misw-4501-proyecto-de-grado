import asyncio
import time
import asyncpg
import redis.asyncio as redis
import numpy as np

# Cadenas de conexión hacia los contenedores locales
PG_URL = "postgresql://admin:password@localhost/travelhub"
REDIS_URL = "redis://localhost"

async def preparar_datos(pool, redis_client):
    print("Inyectando datos de prueba (1 registro simulando un hotel muy consultado)...")
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            hotel_id SERIAL PRIMARY KEY,
            disponibilidad INT
        )
    """)
    # Insertamos un registro base en Postgres
    await pool.execute("INSERT INTO inventario (hotel_id, disponibilidad) VALUES (1, 15) ON CONFLICT DO NOTHING")
    
    # Proyectamos el mismo dato en la caché de Redis simulando el patrón Cache-Aside
    await redis_client.set("hotel:1:disponibilidad", "15")

async def consulta_postgres(pool):
    inicio = time.perf_counter()
    async with pool.acquire() as conn:
        await conn.fetchval("SELECT disponibilidad FROM inventario WHERE hotel_id = 1")
    return (time.perf_counter() - inicio) * 1000  # Tiempo en milisegundos

async def consulta_redis(redis_client):
    inicio = time.perf_counter()
    await redis_client.get("hotel:1:disponibilidad")
    return (time.perf_counter() - inicio) * 1000  # Tiempo en milisegundos

async def ejecutar_estres(nombre_motor, funcion_consulta, cliente, concurrencia=200):
    print(f"Lanzando {concurrencia} peticiones concurrentes a {nombre_motor}...")
    
    # Manejo de concurrencia con TaskGroup para lanzar múltiples tareas de consulta
    async with asyncio.TaskGroup() as tg:
        tareas = [tg.create_task(funcion_consulta(cliente)) for _ in range(concurrencia)]
    
    # Recolectamos los tiempos de todas las tareas completadas
    tiempos = [t.result() for t in tareas]
    p95 = np.percentile(tiempos, 95)
    
    print(f"[{nombre_motor}] Latencia p95: {p95:.2f} ms")
    print(f"[{nombre_motor}] Latencia Max: {max(tiempos):.2f} ms\n")

async def main():
    print("Iniciando Spike de Arquitectura: PostgreSQL vs Redis...\n")
    
    # Creación del pool de conexiones (evita saturar los sockets)
    pool = await asyncpg.create_pool(PG_URL, min_size=10, max_size=50)
    redis_client = redis.from_url(REDIS_URL)
    
    await preparar_datos(pool, redis_client)
    
    # Ejecutamos el set de pruebas
    await ejecutar_estres("PostgreSQL", consulta_postgres, pool)
    await ejecutar_estres("Redis", consulta_redis, redis_client)
    
    # Cierre limpio de conexiones
    await pool.close()
    await redis_client.aclose()
    print("Experimento finalizado exitosamente.")

if __name__ == "__main__":
    asyncio.run(main())