# Frontend Angular — TravelHub

## Stack

- **Angular 19** con standalone components (sin NgModules)
- **Transloco** para internacionalización (i18n)
- **Lazy loading** en todas las rutas de features
- **SCSS** para estilos por componente

## Estructura de carpetas

```
src/frontend/src/app/
├── app.component.ts        ← root component
├── app.config.ts           ← configuración de la app (providers, interceptores)
├── app.routes.ts           ← rutas principales
├── core/                   ← servicios y utilidades transversales
│   ├── guards/
│   │   ├── auth.guard.ts       ← redirige a login si no hay sesión
│   │   ├── role.guard.ts       ← protege por rol de usuario
│   │   └── type.guard.ts       ← protege por tipo de cuenta (hotel/viajero)
│   ├── interceptors/
│   │   ├── auth.interceptor.ts     ← adjunta Bearer token + maneja refresh
│   │   ├── error.interceptor.ts    ← manejo global de errores HTTP
│   │   └── language.interceptor.ts ← adjunta Accept-Language a peticiones
│   └── services/               ← servicios de API
├── features/               ← módulos de funcionalidad
│   ├── auth/               ← login / registro
│   ├── home/               ← landing / búsqueda principal
│   ├── search/             ← resultados de búsqueda de hoteles
│   ├── hotels/             ← listado y detalle de hotel
│   ├── bookings/           ← crear, editar, listar y ver detalle de reservas
│   │   ├── create-reservation/
│   │   ├── checkout/
│   │   ├── booking-detail/
│   │   └── bookings.component.ts   ← listado de reservas del usuario
│   ├── partner/            ← panel para socios hoteleros
│   │   ├── dashboard/      ← resumen de reservas del hotel
│   │   └── hotel/          ← gestión de propiedades y habitaciones
│   ├── settings/           ← perfil y configuración del usuario
│   ├── payments/           ← flujo de pago con tarjeta (cifrado RSA en cliente)
│   ├── health/             ← dashboard de salud de servicios
│   ├── terms/              ← términos y condiciones
│   └── not-found/          ← página 404
├── layout/
│   └── main-layout/        ← shell con navbar y footer
└── shared/                 ← componentes y pipes compartidos
```

## Rutas y guards

| Ruta | Componente | Guards |
|---|---|---|
| `/` | `HomeComponent` | — |
| `/hotels` | `HotelsListComponent` | `authGuard` |
| `/hotels/:id` | `HotelDetailComponent` | `authGuard` |
| `/hotels/:id/reserve` | `CreateReservationComponent` | `authGuard` |
| `/hotels/:id/checkout` | `CheckoutComponent` | `authGuard` |
| `/bookings` | `BookingsComponent` | `authGuard` |
| `/bookings/:id` | `BookingDetailComponent` | `authGuard` |
| `/bookings/:id/edit` | `CreateReservationComponent` | `authGuard` |
| `/partner/dashboard` | `PartnerDashboardComponent` | `authGuard` + `typeGuard('hotel')` |
| `/partner/hotel` | `PartnerHotelComponent` | `authGuard` + `typeGuard('hotel')` |
| `/settings` | `SettingsComponent` | `authGuard` |
| `/terms` | `TermsComponent` | — |

## Interceptores HTTP

### `auth.interceptor.ts`

Agrega el header `Authorization: Bearer <token>` a todas las peticiones salientes. Si la respuesta es `401`, intenta renovar el access token con el refresh token y reintenta la petición original.

### `error.interceptor.ts`

Captura errores HTTP globalmente y los normaliza para mostrar mensajes consistentes al usuario.

### `language.interceptor.ts`

Adjunta el header `Accept-Language` con el idioma activo de Transloco, permitiendo que el backend devuelva mensajes localizados.

## Internacionalización

El frontend usa **Transloco** para i18n. Los archivos de traducción viven en `src/frontend/src/assets/i18n/`. El `language.interceptor.ts` propaga el idioma seleccionado al backend en cada petición.

## Seguridad en el cliente

El cifrado RSA-OAEP del payload de tarjeta se ejecuta en el navegador antes de enviar al servidor. La clave pública RSA se configura en el entorno de Angular (`environment.ts`). El número completo de tarjeta nunca llega al servidor en texto plano.
