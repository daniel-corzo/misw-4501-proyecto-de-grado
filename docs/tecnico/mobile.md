# App Móvil iOS — TravelHub

## Stack

- **SwiftUI** — framework declarativo de UI de Apple
- **iOS 17+** — versión mínima soportada
- **Xcode 15+** — entorno de desarrollo
- Arquitectura **MVVM** (Model-View-ViewModel)

## Estructura del proyecto

```
src/mobile/ios/TravelHub/TravelHub/
├── TravelHubApp.swift          ← entry point de la app
├── ContentView.swift           ← vista raíz / routing inicial
├── Assets.xcassets/            ← imágenes, colores e íconos
├── Info.plist                  ← configuración de la app
├── Configuration/              ← configuración de entornos (dev, prod)
├── Models/                     ← modelos de dominio (structs/enums)
├── DTOs/                       ← objetos de transferencia de datos (codables)
├── Services/                   ← capa de red (URLSession, llamadas a API)
├── ViewModels/                 ← lógica de presentación con Swift Observation (@Observable)
├── Views/                      ← vistas SwiftUI por pantalla/feature
├── Components/                 ← componentes reutilizables de UI
├── Utility/                    ← helpers, extensiones, formatters
├── I18n/                       ← localización (strings)
└── Resources/                  ← recursos adicionales
```

## Arquitectura MVVM

```
View (SwiftUI) ←→ ViewModel (@Observable + @State en la vista) → Service (URLSession) → API REST
```

- **Views**: solo renderizan UI y delegan acciones al ViewModel.
- **ViewModels**: manejan estado con `@Observable`, se instancian/guardan desde las vistas con `@State`, llaman a Services y transforman DTOs en modelos de presentación.
- **Services**: encapsulan las llamadas HTTP, manejan autenticación (token) y deserialización JSON.
- **DTOs**: structs `Codable` que mapean exactamente la estructura JSON de la API.
- **Models**: structs de dominio, independientes de la capa de red.

## Autenticación

La app guarda los tokens JWT en **Keychain** (no en UserDefaults) para seguridad. El Service layer adjunta el `Authorization: Bearer <token>` en cada petición autenticada. Cuando el access_token expira, el Service llama al endpoint de refresh y reintenta la petición original.

## Flujos principales

### Búsqueda y reserva

```
Pantalla de búsqueda
  → (ciudad, fechas, huéspedes)
  → GET /api/busquedas/hoteles
  → Listado de resultados
  → Detalle de hotel
  → Selección de habitación
  → Formulario de reserva
  → Pantalla de pago (cifra tarjeta con RSA-OAEP)
  → Confirmación con código QR
```

### Gestión de reservas

```
Mis reservas (activas / canceladas / pasadas)
  → Detalle de reserva
  → QR de check-in
  → Cancelar reserva
```

### Panel de hotelero (socio)

Si el usuario tiene tipo de cuenta `hotel`, la app muestra el panel de partner con las reservas de su propiedad y la opción de confirmar o rechazar.

## Cifrado de pagos en el cliente

Al igual que en el frontend web, los datos de tarjeta se cifran en el dispositivo con RSA-OAEP antes de enviarse. La clave pública RSA se almacena en la configuración del entorno (`Configuration/`). El número completo de tarjeta nunca sale del dispositivo sin cifrar.

## Builds y configuración

El proyecto tiene dos configuraciones de Xcode:

| Configuración | API Base URL |
|---|---|
| Debug | `http://localhost:8080` |
| Release | URL de producción (ALB en AWS) |

Para cambiar el entorno, seleccionar el esquema correspondiente en Xcode antes de compilar.

## Testing

- `TravelHubTests/` — unit tests de ViewModels y Services con XCTest
- `TravelHubUITests/` — pruebas de UI con XCUITest
