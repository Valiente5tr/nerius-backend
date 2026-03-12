# 🔧 Guía de Integración: Sistema de Sesiones para Frontend

## ✅ Resumen de la Solución

El error `Cannot use 'Cookie' for path param 'session_id'` fue causado por un **conflicto de nombres** entre:
- Path parameter: `/sessions/{session_id}`
- Cookie parameter: `Cookie("session_id")`

**Solución:** Se usó un alias en el Cookie para diferenciarlos:
```python
current_session_id: str | None = Cookie(None, alias="session_id")
```

---

## 📡 Endpoints Disponibles

### 1. **POST /api/v1/auth/login**
Inicia sesión y obtiene una cookie de sesión que dura **30 días**.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "...",
    "email": "user@example.com",
    "first_name": "Juan",
    "last_name": "Perez",
    "status": "active"
  }
}
```

**Cookie:** `session_id` (HttpOnly, 30 días)

---

### 2. **GET /api/v1/auth/sessions**
Lista todas las sesiones activas del usuario actual.

**Headers:**
```
Cookie: session_id=<token>
```

**Response:**
```json
{
  "total": 3,
  "sessions": [
    {
      "id": "rzRiwvbaZxHhONd7W4RDtk5G63sV-x1YI1s--LcwK4M",
      "created_at": "2026-03-12T06:35:31",
      "expires_at": "2026-04-11T06:35:32",
      "last_activity_at": "2026-03-12T06:35:45",
      "user_agent": "Mozilla/5.0...",
      "ip_address": "192.168.1.100",
      "is_current": true
    },
    {
      "id": "...",
      "is_current": false
    }
  ]
}
```

---

### 3. **DELETE /api/v1/auth/sessions/{session_id}**
Revoca una sesión específica (cierra sesión en otro dispositivo).

**Path Parameter:**
- `session_id`: ID de la sesión a revocar

**Headers:**
```
Cookie: session_id=<current_session_token>
```

**Response:**
```json
{
  "message": "Session revoked successfully"
}
```

**Notas:**
- Solo puedes revocar tus propias sesiones (403 si intentas revocar de otro usuario)
- No puedes revocar la sesión actual (aunque técnicamente funciona, te desloguearías)

---

### 4. **POST /api/v1/auth/logout**
Cierra la sesión actual.

**Headers:**
```
Cookie: session_id=<token>
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

## 🎯 Casos de Uso en el Frontend

### Caso 1: Mostrar dispositivos conectados

```javascript
async function getActiveSessions() {
  const response = await fetch('/api/v1/auth/sessions', {
    credentials: 'include' // Importante: envía la cookie automáticamente
  });
  
  const data = await response.json();
  
  return data.sessions.map(session => ({
    id: session.id,
    device: session.user_agent,
    ipAddress: session.ip_address,
    lastActive: new Date(session.last_activity_at),
    isCurrent: session.is_current
  }));
}
```

**UI Ejemplo:**
```
📱 Tus Sesiones Activas

✅ Este dispositivo (actual)
   Chrome en Windows - 192.168.1.100
   Última actividad: hace 5 minutos
   
🔵 iPhone de Juan
   Safari en iOS - 192.168.1.101
   Última actividad: hace 2 horas
   [Cerrar sesión]
   
🔵 MacBook
   Firefox en macOS - 192.168.1.102
   Última actividad: hace 1 día
   [Cerrar sesión]
```

---

### Caso 2: Cerrar sesión en otro dispositivo

```javascript
async function revokeSession(sessionId) {
  const response = await fetch(`/api/v1/auth/sessions/${sessionId}`, {
    method: 'DELETE',
    credentials: 'include'
  });
  
  if (response.ok) {
    alert('Sesión cerrada exitosamente');
    // Recargar la lista de sesiones
    await getActiveSessions();
  } else {
    const error = await response.json();
    alert(`Error: ${error.detail}`);
  }
}
```

---

### Caso 3: Cerrar todas las sesiones excepto la actual

```javascript
async function revokeAllOtherSessions() {
  const sessions = await getActiveSessions();
  
  // Filtrar solo las sesiones que NO son la actual
  const otherSessions = sessions.filter(s => !s.is_current);
  
  // Revocar cada una
  const promises = otherSessions.map(session => 
    fetch(`/api/v1/auth/sessions/${session.id}`, {
      method: 'DELETE',
      credentials: 'include'
    })
  );
  
  await Promise.all(promises);
  
  alert(`${otherSessions.length} sesión(es) cerrada(s)`);
}
```

---

### Caso 4: Detectar si la sesión expiró

```javascript
async function checkSession() {
  try {
    const response = await fetch('/api/v1/auth/me', {
      credentials: 'include'
    });
    
    if (response.status === 401) {
      // Sesión expirada o inválida
      window.location.href = '/login';
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error checking session:', error);
    return null;
  }
}

// Verificar cada 5 minutos
setInterval(checkSession, 5 * 60 * 1000);
```

---

## 🔐 Seguridad

### Cookies HttpOnly
Las cookies tienen `httponly=true`, lo que significa:
- ✅ No accesibles desde JavaScript (`document.cookie`)
- ✅ Protección contra XSS
- ✅ Se envían automáticamente en cada request

### CORS
Si tu frontend está en un dominio diferente al backend:

```javascript
// Asegúrate de incluir credentials
fetch('http://api.example.com/auth/login', {
  method: 'POST',
  credentials: 'include', // MUY IMPORTANTE
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ email, password })
});
```

Y en el backend (FastAPI):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend.example.com"],
    allow_credentials=True,  # Permite cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Testing con cURL

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt

# 2. Ver sesiones
curl -b cookies.txt http://localhost:8000/api/v1/auth/sessions

# 3. Revocar una sesión
curl -X DELETE -b cookies.txt \
  http://localhost:8000/api/v1/auth/sessions/<SESSION_ID>

# 4. Logout
curl -X POST -b cookies.txt http://localhost:8000/api/v1/auth/logout
```

---

## 🐛 Problemas Comunes

### No se envía la cookie automáticamente
**Problema:** Frontend no incluye la cookie en los requests.
**Solución:** Agregar `credentials: 'include'` en todas las llamadas fetch.

### Error 401: Not authenticated
**Problema:** La sesión expiró (después de 30 días de inactividad).
**Solución:** Redirigir al usuario al login.

### Error 403: Cannot revoke another user's session
**Problema:** Intentas revocar una sesión que no te pertenece.
**Solución:** Verificar que el `session_id` pertenece al usuario actual.

### CORS blocking cookies
**Problema:** Las cookies no se guardan por CORS.
**Solución:** 
1. Backend: `allow_credentials=True` en CORS
2. Frontend: `credentials: 'include'` en fetch
3. Backend: No usar `allow_origins=["*"]` (especificar origen exacto)

---

## 📊 Ejemplo Completo de React

```jsx
import { useState, useEffect } from 'react';

function SessionManager() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/auth/sessions', {
        credentials: 'include'
      });
      const data = await response.json();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleRevoke(sessionId) {
    if (!confirm('¿Cerrar esta sesión?')) return;

    try {
      const response = await fetch(`/api/v1/auth/sessions/${sessionId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        // Recargar sesiones
        await loadSessions();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error revoking session:', error);
    }
  }

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <h2>Sesiones Activas ({sessions.length})</h2>
      <ul>
        {sessions.map(session => (
          <li key={session.id}>
            <div>
              <strong>{session.user_agent}</strong>
              {session.is_current && <span> (este dispositivo)</span>}
            </div>
            <div>IP: {session.ip_address}</div>
            <div>Última actividad: {new Date(session.last_activity_at).toLocaleString()}</div>
            {!session.is_current && (
              <button onClick={() => handleRevoke(session.id)}>
                Cerrar sesión
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SessionManager;
```

---

## ✅ Checklist de Integración

- [ ] Login guarda la cookie automáticamente
- [ ] Todos los requests incluyen `credentials: 'include'`
- [ ] CORS configurado correctamente (si aplica)
- [ ] Manejo de sesión expirada (redirect a login)
- [ ] UI muestra lista de dispositivos con información
- [ ] Botón "Cerrar sesión en otros dispositivos"
- [ ] Testing con múltiples navegadores/dispositivos
- [ ] Logout limpia la cookie correctamente

---

## 📚 Referencias

- [Backend: src/api/routes/auth.py](../src/api/routes/auth.py)
- [Backend: src/core/auth.py](../src/core/auth.py)
- [Test Script: test_session_revocation.sh](../test_session_revocation.sh)
- [MDN: fetch() credentials](https://developer.mozilla.org/en-US/docs/Web/API/fetch#credentials)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
