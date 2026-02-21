## 6. Conclusiones y Decisión Arquitectónica

* **Fecha de ejecución:** 21 de Febrero de 2026
* **Ejecutado por:** Equipo de Arquitectura
* **Resultado empírico:** Bajo una prueba de estrés de 200 peticiones asíncronas concurrentes, el motor de base de datos relacional (PostgreSQL) registró una latencia p95 de **1197.17 ms**, incumpliendo críticamente el SLA del negocio establecido en $\le 800$ ms. 
  Por su parte, la proyección de los datos en la caché en memoria (Redis) procesó la misma carga concurrente con una latencia p95 de **327.85 ms**, representando una reducción del **72% en el tiempo de respuesta** y cumpliendo holgadamente el Atributo de Calidad de Desempeño.
* **Decisión:** Se aprueba de manera definitiva la inclusión del patrón Cache-Aside con Redis en la arquitectura de referencia de TravelHub. Se dictamina que el servicio de búsqueda no debe consultar directamente la base de datos relacional en escenarios de operación normal, mitigando el riesgo de abandono de carritos por degradación de latencia.


# Resultados de ejecucion 
```
Iniciando Spike de Arquitectura: PostgreSQL vs Redis...

Inyectando datos de prueba (1 registro simulando un hotel muy consultado)...
Lanzando 200 peticiones concurrentes a PostgreSQL...
[PostgreSQL] Latencia p95: 1197.17 ms
[PostgreSQL] Latencia Max: 1206.95 ms

Lanzando 200 peticiones concurrentes a Redis...
[Redis] Latencia p95: 327.85 ms
[Redis] Latencia Max: 334.21 ms

Experimento finalizado exitosamente.
```