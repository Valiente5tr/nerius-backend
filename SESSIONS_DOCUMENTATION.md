# Sistema de Sesiones con Base de Datos

## 📋 Resumen

Se ha implementado un sistema de sesiones persistente almacenado en MySQL, reemplazando el almacenamiento en memoria que se perdía al reiniciar el servidor.

---

## 🔄 Cambios Implementados

### 1. **Modelo de Base de Datos: `Session`**
Ubicación: `src/db/models/learning_platform.py`

```python
class Session(Base):
    __tablename__ = "sessions"
    
    id: str  # Token de sesión (64 caracteres)
    user_id: str  # FK a users.id
    created_at: datetime  # Cuándo se creó
    expires_at: datetime  # Cuándo expira
    last_activity_at: datetime  # Última actividad (se actualiza en cada request)
    user_agent: str | None  # Navegador del usuario
    ip_address: str | None  # IP del usuario
```

### 2. **Configuración Ajustable**
Ubicación: `src/core/config.py`

```python
session_expire_days: int = 30  # Duración de las sesiones (30 días por defecto)
```

Puedes cambiar esto en tu archivo `.env`:
```bash
SESSION_EXPIRE_DAYS=30  # O cualquier otro valor
```

### 3. **Funciones Actualizadas**
Ubicación: `src/core/auth.py`

#### **`create_session(user_id, db, user_agent=None, ip_address=None)`**
- Genera token seguro con `secrets.token_urlsafe(32)`
- Almacena en la base de datos
- Retorna el session_id

#### **`validate_session(session_id, db)`**
- Verifica que la sesión existe
- Verifica que no haya expirado
- Actualiza `last_activity_at` automáticamente
- Elimina sesión si está expirada
- Retorna datos del usuario

#### **`invalidate_session(session_id, db)`**
- Elimina la sesión de la base de datos
- Se usa en logout

#### **`cleanup_expired_sessions(db)`**
- Limpia todas las sesiones expiradas de golpe
- Retorna cantidad de sesiones eliminadas
- Útil para ejecutar como tarea periódica

---

## 🆕 Nuevos Endpoints

### **GET /api/v1/auth/sessions**
Lista todas las sesiones activas del usuario actual.

**Response:**
```json
{
  "total": 2,
  "sessions": [
    {
      "id": "abc123...",
      "created_at": "2026-03-12T00:00:00",
      "expires_at": "2026-04-11T00:00:00",
      "last_activity_at": "2026-03-12T01:30:00",
      "user_agent": "Mozilla/5.0...",
      "ip_address": "192.168.1.100",
      "is_current": true
    }
  ]
}
```

### **DELETE /api/v1/auth/sessions/{session_id}**
Revoca una sesión específica (cerrar sesión en otro dispositivo).

**Response:**
```json
{
  "message": "Session revoked successfully"
}
```

---

## 🍪 Cookies

Las cookies ahora duran **30 días** (antes 7):

```python
response.set_cookie(
    key="session_id",
    value=session_id,
    httponly=True,  # No accessible desde JavaScript
    secure=False,  # Cambiar a True en producción con HTTPS
    samesite="lax",  # Protección CSRF
    max_age=30 * 24 * 60 * 60,  # 30 días
)
```

---

## 🔧 Utilidades

### **Script de Limpieza**
Ubicación: `cleanup_sessions.py`

```bash
python cleanup_sessions.py
```

Elimina todas las sesiones expiradas de la base de datos.

### **Script de Testing**
Ubicación: `test_sessions.sh` (ejecutable)

```bash
./test_sessions.sh
```

Prueba completa del sistema:
- Login
- Validación de sesión
- Listado de sesiones
- Verificación en BD
- Logout
- Verificación de eliminación

---

## 📊 Comparación: Antes vs Ahora

| Característica | Antes (Memoria) | Ahora (Base de Datos) |
|----------------|-----------------|------------------------|
| **Persistencia** | ❌ Se pierde al reiniciar | ✅ Persiste en MySQL |
| **Duración** | 7 días | 30 días (configurable) |
| **Info adicional** | Solo user_id y email | user_agent, IP, timestamps |
| **Gestión** | No disponible | Ver y revocar sesiones |
| **Escalabilidad** | ❌ Solo 1 servidor | ✅ Múltiples servidores |
| **Auditoría** | ❌ No hay historial | ✅ Logs de actividad |

---

## 🔐 Seguridad

### Mejoras Implementadas:
1. **Tokens seguros**: Se usa `secrets.token_urlsafe(32)` (256 bits de entropía)
2. **Expiración automática**: Sesiones expiradas se eliminan al validar
3. **Actualización de actividad**: `last_activity_at` se actualiza en cada request
4. **HttpOnly cookies**: No accesibles desde JavaScript
5. **SameSite protection**: Protección contra CSRF
6. **Revocación selectiva**: Los usuarios pueden cerrar sesiones específicas

### Recomendaciones para Producción:
1. Cambiar `secure=True` en las cookies (requiere HTTPS)
2. Ejecutar `cleanup_sessions.py` periódicamente (ej. con cron)
3. Implementar rate limiting en login
4. Considerar usar Redis para sesiones de alta frecuencia
5. Agregar 2FA si se manejan datos sensibles

---

## 🚀 Migración

La migración de Alembic creó automáticamente la tabla `sessions`:

```bash
alembic upgrade head
```

**Tabla creada:**
```sql
CREATE TABLE sessions (
    id VARCHAR(64) NOT NULL PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_expires_at (expires_at)
);
```

---

## 🧹 Mantenimiento

### Limpieza Automática (Recomendado)

**Opción 1: Cron Job**
```bash
# Ejecutar cada día a las 3 AM
0 3 * * * cd /path/to/project && /path/to/python cleanup_sessions.py
```

**Opción 2: FastAPI Background Task**
Agregar en `src/main.py`:
```python
from fastapi import BackgroundTasks
from src.core.auth import cleanup_expired_sessions

@app.on_event("startup")
async def startup_cleanup():
    """Cleanup expired sessions on startup."""
    db = SessionLocal()
    try:
        count = cleanup_expired_sessions(db)
        print(f"Cleaned up {count} expired sessions")
    finally:
        db.close()
```

---

##  💡 Casos de Uso

### 1. Ver sesiones activas
```bash
curl -b cookies.txt http://localhost:8000/api/v1/auth/sessions
```

### 2. Cerrar sesión en todos los dispositivos
```python
# En el frontend, obtener todas las sesiones
sessions = await fetchSessions()

# Revocar todas excepto la actual
for session in sessions:
    if not session.is_current:
        await revokeSession(session.id)
```

### 3. Monitorear actividad sospechosa
```sql
-- Sesiones con múltiples IPs
SELECT user_id, COUNT(DISTINCT ip_address) as ip_count
FROM sessions
GROUP BY user_id
HAVING ip_count > 3;

-- Sesiones antiguas sin actividad
SELECT * FROM sessions
WHERE last_activity_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
```

---

## ✅ Ventajas del Nuevo Sistema

1. **Persistencia**: Las sesiones sobreviven reinicios del servidor
2. **Trazabilidad**: Se puede ver qué dispositivos/IPs han accedido
3. **Control**: Los usuarios pueden cerrar sesiones remotamente
4. **Escalabilidad**: Múltiples instancias del servidor pueden compartir sesiones
5. **Seguridad**: Mejor control sobre la duración y revocación de sesiones
6. **Auditoría**: Historial de cuándo se crearon y usaron las sesiones

---

## 🐛 Solución de Problemas

### "Session expired or invalid"
- La sesión pudo haber expirado después de 30 días
- El usuario hizo logout en otro dispositivo
- La sesión fue revocada manualmente
- **Solución**: Hacer login nuevamente

### Las sesiones no persisten
- Verificar que la tabla `sessions` existe en la BD
- Verificar logs de errores en el servidor
- **Verificar**: `SELECT * FROM sessions;`

### Demasiadas sesiones acumuladas
- Ejecutar `python cleanup_sessions.py`
- Configurar limpieza automática con cron

---

## 📚 Referencias

- [src/db/models/learning_platform.py](src/db/models/learning_platform.py) - Modelo Session
- [src/core/auth.py](src/core/auth.py) - Funciones de gestión de sesiones
- [src/api/routes/auth.py](src/api/routes/auth.py) - Endpoints de autenticación
- [src/core/config.py](src/core/config.py) - Configuración
- [alembic/versions/b0efe930db00_add_sessions_table.py](alembic/versions/b0efe930db00_add_sessions_table.py) - Migración
