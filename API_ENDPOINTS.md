# 📚 Nerius Learning Platform - API Documentation

## 🚀 Endpoints Implementados

### 1. **Health Check**
Verifica si el servidor está funcionando.

**Request:**
```bash
GET http://localhost:8000/api/v1/health/
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. **Login (Iniciar Sesión)**
Autenticación de usuario con email y contraseña. Retorna una cookie de sesión.

**Request:**
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

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
    "id": "uuid-del-usuario",
    "email": "user@example.com",
    "first_name": "Juan",
    "last_name": "Perez",
    "status": "active"
  }
}
```

**Cookie Set:** `session_id` (HttpOnly, 7 días de expiración)

---

### 3. **Get Current User Info (Usuario Actual)**
Obtiene información del usuario actualmente autenticado.

**Request:**
```bash
GET http://localhost:8000/api/v1/auth/me
```

**Requiere:** Cookie `session_id` (se envía automáticamente en el navegador)

**Response:**
```json
{
  "id": "uuid-del-usuario",
  "email": "user@example.com",
  "first_name": "Juan",
  "last_name": "Perez",
  "status": "active"
}
```

---

### 4. **Logout (Cerrar Sesión)**
Invalida la sesión y elimina la cookie.

**Request:**
```bash
POST http://localhost:8000/api/v1/auth/logout
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

### 5. **Get All Published Courses (Obtener Cursos Disponibles)**
Obtiene la lista de todos los cursos publicados en la plataforma (sin requerir autenticación).

**Request:**
```bash
GET http://localhost:8000/api/v1/courses/
```

**Response:**
```json
[
  {
    "id": "uuid-curso",
    "title": "Python for Beginners",
    "description": "Learn the basics of Python programming language.",
    "status": "published",
    "estimated_minutes": 480,
    "cover_url": "https://via.placeholder.com/300x200?text=Python"
  },
  {
    "id": "uuid-curso",
    "title": "Web Development with FastAPI",
    "description": "Build modern web applications with FastAPI.",
    "status": "published",
    "estimated_minutes": 600,
    "cover_url": "https://via.placeholder.com/300x200?text=FastAPI"
  },
  ...
]
```

---

### 6. **Get User's Pending Courses (Obtener Cursos Pendientes del Usuario)**
Obtiene los cursos en los que el usuario está actualmente inscrito (con estado ACTIVE).

**Request:**
```bash
GET http://localhost:8000/api/v1/courses/user/pending
```

**Requiere:** Cookie `session_id` (usuario autenticado)

**Response:**
```json
[
  {
    "id": "uuid-enrollment",
    "course_id": "uuid-curso",
    "status": "active",
    "progress_percent": 45.0,
    "course": {
      "id": "uuid-curso",
      "title": "Python for Beginners",
      "description": "Learn the basics of Python programming language.",
      "status": "published",
      "estimated_minutes": 480,
      "cover_url": "https://via.placeholder.com/300x200?text=Python"
    }
  },
  {
    "id": "uuid-enrollment",
    "course_id": "uuid-curso",
    "status": "active",
    "progress_percent": 20.0,
    "course": {
      "id": "uuid-curso",
      "title": "Web Development with FastAPI",
      "description": "Build modern web applications with FastAPI.",
      "status": "published",
      "estimated_minutes": 600,
      "cover_url": "https://via.placeholder.com/300x200?text=FastAPI"
    }
  }
]
```

---

### 6A. **Get User's Pending Assigned Courses (Obtener Cursos Asignados Pendientes del Usuario)**
Obtiene los cursos que fueron asignados al usuario autenticado y que todavia no han sido completados.

Un curso asignado se considera pendiente cuando:
- Existe un registro en `course_assignments` para ese usuario.
- El usuario no tiene un enrollment en estado `completed` para ese curso.

**Request:**
```bash
GET http://localhost:8000/api/v1/courses/user/assigned/pending
```

**Requiere:** Cookie `session_id` (usuario autenticado)

**Response:**
```json
[
  {
    "id": "uuid-assignment",
    "course_id": "uuid-course",
    "assigned_by_user_id": "uuid-admin",
    "assigned_to_user_id": "uuid-user",
    "due_date": "2026-03-31T23:59:59",
    "created_at": "2026-03-12T17:00:00",
    "assigned_by_name": "Content Admin",
    "course": {
      "id": "uuid-course",
      "title": "Introduccion a Google Gemini para Empresas",
      "description": "Descubre el potencial de Google Gemini como asistente de inteligencia artificial para el entorno empresarial.",
      "status": "published",
      "estimated_minutes": 240,
      "cover_url": "https://www.gstatic.com/lamda/images/gemini_aurora_thumbnail_4g_e74822ff0ca4259beb718.png"
    }
  }
]
```

**Notas:**
- Si el usuario ya completo el curso, no aparece en este endpoint aunque siga existiendo la asignacion.
- Si el usuario todavia no se ha enrollado, el curso sigue apareciendo como pendiente.
- Si el usuario esta enrollado pero no ha completado el curso, tambien sigue apareciendo como pendiente.

---

### 6B. **Get Recommended Courses (Obtener Cursos Recomendados)**
Obtiene cursos publicados recomendados para el usuario autenticado.

La recomendacion sigue esta prioridad:
- Primero regresa solo cursos del mismo area del usuario.
- Esos cursos deben ser cursos que el usuario todavia no ha tomado, es decir, sin enrollment previo.
- Si no hay coincidencias en la misma area, entonces regresa cursos publicados de cualquier area que el usuario todavia no ha tomado.

**Request:**
```bash
GET http://localhost:8000/api/v1/courses/user/recommended
```

**Requiere:** Cookie `session_id` (usuario autenticado)

**Response:**
```json
[
  {
    "id": "uuid-course",
    "title": "Google Workspace + Gemini para Productividad",
    "description": "Domina la integración de Gemini con todas las herramientas de Google Workspace.",
    "status": "published",
    "estimated_minutes": 600,
    "cover_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1PJeq6VwlYN45w6KvEkmVdmn5qLD48AqteA&s"
  },
  {
    "id": "uuid-course",
    "title": "Seguridad y Administración de Google Workspace",
    "description": "Aprende a administrar y proteger Google Workspace en tu organización.",
    "status": "published",
    "estimated_minutes": 420,
    "cover_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHRF0ybXDh5GPkvdobK2MH6VhrRkQbzGhN8w&s"
  }
]
```

**Notas:**
- Un curso con enrollment `active`, `completed` o `dropped` ya no se recomienda.
- Los cursos asignados siguen pudiendo aparecer aqui si el usuario aun no tiene enrollment en ellos.
- El fallback a otras areas solo ocurre si no hay opciones disponibles en la misma area del usuario.

---

### 7. **Get User Badges (Obtener Badges del Usuario)**
Obtiene todas las badges ganadas por el usuario autenticado, incluyendo su información visual para mostrarlas en el frontend.

**Request:**
```bash
GET http://localhost:8000/api/v1/courses/user/badges
```

**Requiere:** Cookie `session_id` (usuario autenticado)

**Response:**
```json
[
  {
    "id": "uuid-user-badge",
    "badge": {
      "id": "uuid-badge",
      "name": "Early Adopter",
      "description": "Eres uno de los primeros miembros de la plataforma Nerius.",
      "icon_url": "https://img.icons8.com/fluency/96/rocket.png",
      "main_color": "#06b6d4",
      "secondary_color": "#0369a1"
    },
    "awarded_at": "2026-03-12T10:15:30.123456"
  },
  {
    "id": "uuid-user-badge",
    "badge": {
      "id": "uuid-badge",
      "name": "A Mitad del Camino",
      "description": "Alcanzaste el 50% de progreso en cualquier curso.",
      "icon_url": "https://img.icons8.com/fluency/96/medal-first-place.png",
      "main_color": "#f97316",
      "secondary_color": "#c2410c"
    },
    "awarded_at": "2026-03-12T10:18:05.654321"
  }
]
```

**Uso recomendado en frontend:**
- Mostrar historial de badges del usuario en perfil o dashboard.
- Usar `main_color` y `secondary_color` para tarjetas, chips o gradientes.
- Ordenar visualmente por `awarded_at` descendente si se desea destacar las más recientes.

---

### 8. **Get Courses Ranking (Ranking de Empleados por Cursos Completados)**
Obtiene el ranking de empleados ordenado por la cantidad de cursos completados.

Si hay empate en cantidad de cursos completados, el desempate se resuelve por quién completó sus cursos en menor tiempo total.

**Request:**
```bash
GET http://localhost:8000/api/v1/courses/ranking
```

**Requiere:** Cookie `session_id` (usuario autenticado)

**Response:**
```json
[
  {
    "name": "Juan Perez",
    "total_completed_courses": 5,
    "area": "Tecnología"
  },
  {
    "name": "Ana Lopez",
    "total_completed_courses": 5,
    "area": "Negocios"
  },
  {
    "name": "Carlos Ruiz",
    "total_completed_courses": 4,
    "area": "Tecnología"
  }
]
```

**Reglas de negocio:**
- Solo se consideran cursos con enrollment en estado `completed`.
- El primer criterio de orden es `total_completed_courses` descendente.
- Si dos usuarios tienen la misma cantidad de cursos completados, gana quien tenga menor tiempo total de finalización.
- El tiempo de finalización se calcula por curso usando `completed_at - started_at`.
- Si `started_at` no existe, se usa `created_at` del enrollment como referencia inicial.

**Uso recomendado en frontend:**
- Mostrar leaderboard de empleados por aprendizaje.
- Refrescar esta vista al completar un curso o al entrar al dashboard.
- Si se desea destacar el top 3, basta con tomar los primeros tres elementos de la respuesta.

---

### 9. **Update Lesson Progress (Actualizar Progreso de una Lección)**
Actualiza el progreso del usuario en una lección específica y recalcula el progreso general del curso.

Además, este endpoint ahora revisa si el nuevo progreso total del curso desbloquea alguna badge asociada al curso. Si eso ocurre, la respuesta incluye las badges recién obtenidas para que el frontend pueda mostrar una notificación inmediatamente.

**Request:**
```bash
PUT http://localhost:8000/api/v1/courses/{course_id}/lessons/{lesson_id}/progress
Content-Type: application/json
```

**Body:**
```json
{
  "progress_percent": 100,
  "time_spent_seconds": 840,
  "status": "completed"
}
```

**Requiere:** Cookie `session_id` (usuario autenticado y enrollado en el curso)

**Response sin nueva badge:**
```json
{
  "lesson_id": "uuid-lesson",
  "status": "completed",
  "progress_percent": 100.0,
  "time_spent_seconds": 840,
  "enrollment_progress_percent": 44.44,
  "earned_badges": []
}
```

**Response con badge recién obtenida:**
```json
{
  "lesson_id": "uuid-lesson",
  "status": "completed",
  "progress_percent": 100.0,
  "time_spent_seconds": 840,
  "enrollment_progress_percent": 50.0,
  "earned_badges": [
    {
      "badge": {
        "id": "uuid-badge",
        "name": "A Mitad del Camino",
        "description": "Alcanzaste el 50% de progreso en cualquier curso.",
        "icon_url": "https://img.icons8.com/fluency/96/medal-first-place.png",
        "main_color": "#f97316",
        "secondary_color": "#c2410c"
      },
      "awarded_at": "2026-03-12T10:30:12.000000"
    }
  ]
}
```

**Reglas de negocio:**
- `earned_badges` solo incluye badges nuevas obtenidas en esa llamada.
- Si el usuario ya tenía una badge, no se vuelve a incluir en `earned_badges`.
- La validación se hace sobre el progreso total del curso (`enrollment_progress_percent`), no solo sobre la lección individual.
- Puede devolver más de una badge si en la misma actualización se cruzan varios umbrales.

**Uso recomendado en frontend:**
- Si `earned_badges.length > 0`, mostrar toast, modal o banner de felicitación.
- Guardar el progreso normalmente aunque no haya badges nuevas.
- Si se necesita el listado completo de badges del usuario después de la notificación, consultar `GET /api/v1/courses/user/badges`.

---

## 👥 Mock Users (Datos de Prueba)

| Email | Password | Rol |
|-------|----------|-----|
| superadmin@example.com | password123 | Super Admin |
| admin@example.com | password123 | Content Admin |
| user@example.com | password123 | Learner (Usuario Regular) |

---

## 📚 Mock Courses (Cursos Disponibles)

1. **Python for Beginners** - 480 minutos
2. **Web Development with FastAPI** - 600 minutos
3. **Business Management 101** - 360 minutos
4. **Database Design and SQL** - 420 minutos
5. **Leadership Skills** - 300 minutos

**El usuario "user@example.com" está inscrito en 3 cursos:**
- Python for Beginners (45% de progreso)
- Web Development with FastAPI (20% de progreso)
- Business Management 101 (0% de progreso)

---

## 🔐 Autenticación y Sesiones

- **Cookie Security:** HttpOnly (protegida contra XSS)
- **SameSite:** Lax (protegida contra CSRF)
- **Duración de Sesión:** 7 días
- **Almacenamiento:** En memoria (para producción se recomienda usar Redis)

---

## 🧪 Flujo Completo de Uso

### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' \
  -c cookies.txt
```

### 2. Get User Info (usando cookie)
```bash
curl http://localhost:8000/api/v1/auth/me \
  -b cookies.txt
```

### 3. Get All Courses
```bash
curl http://localhost:8000/api/v1/courses/
```

### 4. Get Pending Courses (requiere autenticación)
```bash
curl http://localhost:8000/api/v1/courses/user/pending \
  -b cookies.txt
```

### 5. Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt \
  -c cookies.txt
```

---

## ⚙️ Configuración

- **Base URL:** http://localhost:8000
- **API Version:** /api/v1/
- **CORS:** Habilitado para localhost:3000, localhost:5173, localhost:8080
- **Database:** SQLite (app.db) en desarrollo

---

## 📝 Notas Importantes para Frontend

1. **Cookies Automáticas:** Las cookies se manejan automáticamente en el navegador
2. **CORS:** Ya está configurado para acepta credenciales desde el frontend
3. **Session Check:** Usar `/api/v1/auth/me` para verificar si la sesión es válida
4. **Error Handling:** Los errores de autenticación retornan código 401
5. **Localhost Only:** Actualmente configurado solo para localhost (cambiar en producción)
