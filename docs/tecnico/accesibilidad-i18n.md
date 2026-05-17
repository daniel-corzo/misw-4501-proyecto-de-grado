# Accesibilidad e Internacionalización — TravelHub

## Frontend web — Internacionalización (i18n)

El frontend usa **Transloco** para i18n. Los archivos de traducción viven en `src/frontend/public/assets/i18n/`.

| Idioma | Archivo |
|---|---|
| Español | `es.json` |
| Inglés | `en.json` |

### Idioma por defecto

Al iniciar, `app.config.ts` determina el idioma así:

1. Si hay un valor guardado en `localStorage` bajo la clave `appLang`, se usa ese.
2. Si no, se toma el idioma del navegador (`navigator.language`).
3. Si el idioma del navegador no es `es` ni `en`, se usa `es` como fallback.

El idioma activo se guarda en `localStorage` para persistir entre sesiones.

### Propagación al backend

El interceptor `language.interceptor.ts` adjunta el header `Accept-Language` en cada petición HTTP.

---

## Accesibilidad

El servicio `AccessibilityService` (`src/frontend/src/app/core/services/accessibility.service.ts`) centraliza dos categorías de ajustes: modos para daltonismo y tamaño de fuente. Ambos persisten en `localStorage` y se aplican inmediatamente al elemento `<html>` mediante clases CSS.

### Modos para daltonismo

| Valor | Clase en `<html>` | Descripción |
|---|---|---|
| `off` | (ninguna) | Sin filtro |
| `protanopia` | `cb-protanopia` | Dificultad para distinguir rojos |
| `deuteranopia` | `cb-deuteranopia` | Dificultad para distinguir verdes (más común) |
| `tritanopia` | `cb-tritanopia` | Dificultad para distinguir azules |

Los filtros CSS se aplican globalmente mediante el componente `ColorBlindFiltersComponent` que agrega filtros SVG al DOM. La clave de `localStorage` es `appColorBlindMode`.

### Tamaño de fuente

| Valor | Clase en `<html>` | Descripción |
|---|---|---|
| `normal` | (ninguna) | Tamaño base |
| `large` | `fs-large` | Fuente aumentada |
| `xlarge` | `fs-xlarge` | Fuente extra grande |

La clave de `localStorage` es `appFontSize`.

### Dónde se configuran

El usuario accede a estos ajustes desde **Configuración** (`/settings`). La pantalla muestra botones para cada modo de daltonismo y para cada tamaño de fuente. Los cambios se aplican en tiempo real sin necesidad de recargar la página.

---

## Agregar nuevas traducciones (web)

1. Agrega la clave en `es.json` y su equivalente en `en.json`.
2. Usa `{{ 'tu.clave' | transloco }}` en la plantilla HTML, o `transloco.translate('tu.clave')` en el TypeScript.
3. No hay proceso de compilación adicional — Transloco carga los archivos JSON en runtime.

---

## App iOS — Internacionalización (i18n)

La app usa el formato nativo de Xcode 15: **String Catalogs** (`.xcstrings`). Los archivos viven en `src/mobile/ios/TravelHub/TravelHub/I18n/` y están organizados por pantalla o feature.

| Archivo | Contenido |
|---|---|
| `HotelList.xcstrings` | Listado y filtros de hoteles |
| `HotelDetail.xcstrings` | Detalle de hotel y habitaciones |
| `HotelAmenities.xcstrings` | Amenidades |
| `CreateBooking.xcstrings` | Formulario de reserva |
| `BookingDetail.xcstrings` | Detalle de reserva |
| `MyBookings.xcstrings` | Listado de reservas |
| `Payment.xcstrings` | Flujo de pago |
| `LogIn.xcstrings` | Login |
| `SignUp.xcstrings` | Registro |
| `Profile.xcstrings` | Perfil |
| `TabBar.xcstrings` | Barra de navegación inferior |
| `Dates.xcstrings` | Formato de fechas |
| `Notifications.xcstrings` | Textos de notificaciones locales |
| `HttpErrors.xcstrings` | Mensajes de error HTTP |
| `UserData.xcstrings` | Campos de datos de usuario |

**Idiomas soportados:** inglés (`en`, idioma fuente) y español (`es`).

Las strings se referencian en código con `LocalizedStringResource` de forma tipada, lo que detecta claves faltantes en tiempo de compilación.

### Agregar nuevas traducciones (iOS)

1. Abre o crea el `.xcstrings` correspondiente en Xcode (o edítalo como JSON).
2. Agrega la clave con su valor en inglés y español.
3. En el código, referencia la clave con `LocalizedStringResource("clave", table: "NombreArchivo")`.

---

## App iOS — Accesibilidad

La app delega la accesibilidad al sistema iOS — no hay una capa personalizada equivalente al `AccessibilityService` del frontend web.

### Dynamic Type

SwiftUI respeta automáticamente el tamaño de fuente configurado en **Ajustes → Accesibilidad → Tamaño del texto** del iPhone cuando se usan estilos de fuente del sistema (`.title`, `.body`, `.caption`, etc.).

### Modos de daltonismo y contraste

No hay filtros propios en la app. El usuario puede activar los modos de daltonismo y el alto contraste directamente desde **Ajustes → Accesibilidad** en iOS, y el sistema los aplica a toda la interfaz.
