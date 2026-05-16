# Microservicio: busquedas

**Puerto:** 8003  
**Swagger:** http://localhost:8003/docs  
**Responsabilidad:** Motor de búsqueda de alojamiento disponible dado destino, fechas y número de huéspedes.

## Endpoints

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| `GET` | `/api/busquedas/hoteles` | Buscar hoteles disponibles | Sí |

## Parámetros de búsqueda

| Parámetro | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `ciudad` | `string` | Sí | Ciudad de destino |
| `fecha_entrada` | `date` (YYYY-MM-DD) | Sí | Fecha de llegada |
| `fecha_salida` | `date` (YYYY-MM-DD) | Sí | Fecha de salida |
| `num_huespedes` | `integer` | No (default: 1) | Número de huéspedes |

### Ejemplo de llamada

```http
GET /api/busquedas/hoteles?ciudad=Bogotá&fecha_entrada=2025-06-01&fecha_salida=2025-06-05&num_huespedes=2
Authorization: Bearer <token>
```

### Respuesta

```json
{
  "total": 3,
  "resultados": [
    {
      "id": "uuid",
      "nombre": "Hotel Dann Carlton",
      "ciudad": "Bogotá",
      "estrellas": 5,
      "precio_por_noche": 280000.0,
      "habitaciones_disponibles": 4,
      "imagen_url": "https://..."
    }
  ]
}
```

## Lógica de disponibilidad

El servicio consulta los datos de hoteles y habitaciones, filtra por ciudad y calcula disponibilidad real para el rango de fechas solicitado (excluye habitaciones ya reservadas en ese periodo). Solo devuelve hoteles con al menos una habitación libre.

## Caché

Los resultados de búsqueda se cachean en **Redis** con una TTL corta para reducir carga sobre la base de datos en búsquedas repetidas del mismo destino y fechas.

## Dependencias

- PostgreSQL: datos de hoteles y reservas existentes
- Redis: caché de resultados
- Requiere token JWT válido (usa clave pública del servicio `usuarios`)
