# 📋 Sistema de Registro de Descargas

## Descripción

Se ha agregado un módulo completo para registrar todas las descargas de facturas. Cada descarga se registra automáticamente con información de fecha, hora, IP del cliente y detalles de la factura.

## 📁 Archivo de Registro

El registro se guarda en: `frontend/app/descargas.json`

Formato:
```json
{
  "metadata": {
    "version": "1.0",
    "fecha_creacion": "2026-05-13T23:30:00.000000",
    "descripcion": "Registro de facturas descargadas",
    "ultima_actualizacion": "2026-05-13T23:35:45.000000",
    "total_descargas": 5
  },
  "descargas": [
    {
      "id_factura": "FAC-001",
      "fecha_hora": "2026-05-13T23:32:15.000000",
      "ip_cliente": "172.19.0.1",
      "estado": "exitosa",
      "detalles": {
        "empresa": "Empresa XYZ S.L.",
        "cliente": "Cliente ABC",
        "total": 1250.50
      }
    }
  ]
}
```

## 🔌 Endpoints API

### 1. Obtener Historial Completo
```
GET /api/historial
```

**Respuesta:**
```json
{
  "success": true,
  "total": 5,
  "descargas": [...]
}
```

### 2. Obtener Resumen Estadístico
```
GET /api/resumen
```

**Respuesta:**
```json
{
  "success": true,
  "resumen": {
    "total_descargas": 5,
    "descargas_exitosas": 5,
    "descargas_con_error": 0,
    "facturas_unicas": 4,
    "ips_unicas": 2,
    "ultima_actualizacion": "2026-05-13T23:35:45.000000"
  }
}
```

### 3. Obtener Historial de una Factura Específica
```
GET /api/historial/<id_factura>
```

**Ejemplo:**
```
GET /api/historial/FAC-001
```

**Respuesta:**
```json
{
  "success": true,
  "id_factura": "FAC-001",
  "total": 2,
  "descargas": [...]
}
```

## 💡 Cómo Usar

### Desde el navegador:
```
http://localhost:3000/api/resumen
http://localhost:3000/api/historial
http://localhost:3000/api/historial/FAC-001
```

### Desde la terminal (curl):
```bash
# Ver resumen
curl http://localhost:3000/api/resumen

# Ver historial completo
curl http://localhost:3000/api/historial

# Ver historial de una factura
curl http://localhost:3000/api/historial/FAC-001
```

### Desde JavaScript:
```javascript
// Obtener resumen
fetch('/api/resumen')
  .then(res => res.json())
  .then(data => console.log(data.resumen));

// Obtener historial completo
fetch('/api/historial')
  .then(res => res.json())
  .then(data => console.log(data.descargas));
```

## 🔄 Flujo de Registro

1. Usuario ingresa ID de factura
2. Se genera el PDF de la factura
3. **Automáticamente** se registra:
   - ID de factura
   - Fecha y hora exact
   - IP del cliente
   - Nombre de empresa
   - Nombre de cliente
   - Monto total
   - Estado de la operación

## 📊 Información Capturada

| Campo | Descripción |
|-------|------------|
| `id_factura` | Identificador único de la factura |
| `fecha_hora` | Timestamp ISO de la descarga |
| `ip_cliente` | IP del cliente que descargó |
| `estado` | 'exitosa' o 'error' |
| `empresa` | Nombre de la empresa de la factura |
| `cliente` | Nombre del cliente de la factura |
| `total` | Monto total de la factura |

## ⚙️ Personalización

Para modificar qué información se registra, edita el archivo `frontend/app/main.py`, función `generar_pdf()`, sección de `detalles`:

```python
detalles = {
    "empresa": factura.get('empresa', {}).get('nombre', 'N/A'),
    "cliente": factura.get('cliente', {}).get('nombre', 'N/A'),
    "total": factura.get('total', 0)
    # Agregar más campos aquí
}
```

## 📝 Módulo de Registro

El módulo `registro.py` proporciona las siguientes funciones:

- `registrar_descarga()` - Registra una nueva descarga
- `obtener_historial()` - Obtiene todas las descargas
- `obtener_historial_por_factura()` - Filtra por ID de factura
- `obtener_resumen()` - Estadísticas generales
