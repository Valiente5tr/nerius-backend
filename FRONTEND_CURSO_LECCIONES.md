# 📚 Guía Frontend: Visualización de Cursos y Lecciones

## 🎯 Cambios Importantes

Se ha **simplificado** la estructura de endpoints para cursos:

### ❌ Antes (Viejo - Eliminado)
- ~~Focus mode con `focus_module_id` y `focus_lesson_id`~~
- ~~Solo se cargaba un módulo con detalles a la vez~~
- ~~Estructura compleja: `first_module` y `other_modules`~~

### ✅ Ahora (Nuevo - Actual)
- **Endpoint 1:** `GET /courses/{id}/detailed` → Vista general con TODOS los módulos y lecciones + progreso
- **Endpoint 2:** `GET /courses/{id}/lessons/{lesson_id}` → Detalle completo de UNA lección con recursos

---

## 📡 Endpoint 1: Vista General del Curso

### `GET /api/v1/courses/{course_id}/detailed`

Obtiene la estructura completa del curso con todos los módulos y todas las lecciones, incluyendo el **progreso** de cada lección (sin recursos).

**Headers:**
```
Cookie: session_id=<token>
```

**Response:**
```json
{
  "id": "05859ba1-10a2-41b9-b341-c06de064b72c",
  "title": "Business Management 101",
  "description": "Essential business management principles...",
  "status": "published",
  "estimated_minutes": 360,
  "cover_url": "https://via.placeholder.com/300x200",
  "enrollment": {
    "id": "11c30018-2403-417d-a89a-6987417e126e",
    "course_id": "05859ba1-10a2-41b9-b341-c06de064b72c",
    "status": "active",
    "progress_percent": 37.5
  },
  "modules": [
    {
      "id": "acb860bc-e624-417c-869b-696ee5f6e82f",
      "title": "Management Basics",
      "sort_order": 1,
      "lessons": [
        {
          "id": "6a75212b-f9ea-456d-822a-4be55ca61155",
          "title": "Introduction to Management",
          "sort_order": 1,
          "estimated_minutes": 40,
          "status": "completed",
          "progress_percent": 100.0
        },
        {
          "id": "a88c0d04-beac-48c4-a1ff-40b5f9f2f109",
          "title": "Planning and Goal Setting",
          "sort_order": 2,
          "estimated_minutes": 45,
          "status": "completed",
          "progress_percent": 100.0
        },
        {
          "id": "028bd4df-61ee-43b0-aae3-15e0fee07114",
          "title": "Decision Making",
          "sort_order": 3,
          "estimated_minutes": 50,
          "status": "not_started",
          "progress_percent": 0.0
        }
      ]
    },
    {
      "id": "f2999e87-7128-4b7d-bca2-9610cd263e6d",
      "title": "Team Dynamics",
      "sort_order": 2,
      "lessons": [
        {
          "id": "f8bf74e2-2c65-4880-800b-e19b2ccb7b4c",
          "title": "Building Effective Teams",
          "sort_order": 1,
          "estimated_minutes": 50,
          "status": "completed",
          "progress_percent": 100.0
        },
        {
          "id": "391e2ba6-3c4a-4703-bf3f-206a64a529b9",
          "title": "Conflict Resolution",
          "sort_order": 2,
          "estimated_minutes": 55,
          "status": "not_started",
          "progress_percent": 0.0
        }
      ]
    }
  ]
}
```

**Campos clave:**
- `modules`: Array de **todos** los módulos en orden (`sort_order`)
- `modules[].lessons`: Array de **todas** las lecciones del módulo
- `lessons[].status`: `"not_started"`, `"in_progress"`, `"completed"`
- `lessons[].progress_percent`: 0.0 a 100.0
- **NO incluye** `resources` (videos, PDFs, etc.)

---

## 📡 Endpoint 2: Detalle de una Lección

### `GET /api/v1/courses/{course_id}/lessons/{lesson_id}`

Obtiene información completa de una lección específica, incluyendo **todos los recursos** (videos, PDFs, slides, podcasts).

**Headers:**
```
Cookie: session_id=<token>
```

**Response:**
```json
{
  "id": "6a75212b-f9ea-456d-822a-4be55ca61155",
  "title": "Introduction to Management",
  "description": "Understand the core principles and functions of management.",
  "sort_order": 1,
  "estimated_minutes": 40,
  "resources": [
    {
      "id": "b5c1674b-e7f0-4b8a-8c56-3af1212d942b",
      "resource_type": "video",
      "title": "Management Overview",
      "external_url": "https://www.youtube.com/embed/mgmt123",
      "thumbnail_url": null,
      "duration_seconds": 2400
    },
    {
      "id": "c2f3e8d9-1234-5678-9abc-def012345678",
      "resource_type": "pdf",
      "title": "Management Fundamentals Guide",
      "external_url": "https://example.com/management-guide.pdf",
      "thumbnail_url": null,
      "duration_seconds": null
    }
  ],
  "progress": {
    "lesson_id": "6a75212b-f9ea-456d-822a-4be55ca61155",
    "status": "completed",
    "progress_percent": 100.0,
    "time_spent_seconds": 2400,
    "completed_at": "2026-03-10T14:30:00",
    "last_activity_at": "2026-03-10T14:30:00"
  }
}
```

**Campos clave:**
- `description`: Descripción detallada de la lección
- `resources`: Array de recursos (videos, PDFs, slides, podcasts)
- `resources[].resource_type`: `"video"`, `"pdf"`, `"slide"`, `"podcast"`
- `resources[].duration_seconds`: Duración (si aplica, null para PDFs)
- `progress`: Estado actual del usuario (puede ser `null` si no ha empezado)
  - `status`: Estado actual (`"not_started"`, `"in_progress"`, `"completed"`)
  - `progress_percent`: Porcentaje de completado (0.0 - 100.0)
  - `time_spent_seconds`: Tiempo total dedicado en segundos
  - `completed_at`: Fecha/hora de completado (null si no está completada)
  - `last_activity_at`: Fecha/hora de última actividad (null si nunca se ha accedido)

---

## 🎨 Guía de Implementación en el Frontend

### Caso 1: Pantalla de Vista General del Curso

Muestra todos los módulos y lecciones con su progreso.

```jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function CourseOverview() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCourse();
  }, [courseId]);

  async function loadCourse() {
    try {
      const response = await fetch(
        `/api/v1/courses/${courseId}/detailed`,
        { credentials: 'include' }
      );
      const data = await response.json();
      setCourse(data);
    } catch (error) {
      console.error('Error loading course:', error);
    } finally {
      setLoading(false);
    }
  }

  function handleLessonClick(lessonId) {
    // Navegar a la página de detalle de la lección
    navigate(`/courses/${courseId}/lessons/${lessonId}`);
  }

  function getStatusIcon(status) {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '⏳';
      case 'not_started':
        return '⭕';
      default:
        return '⭕';
    }
  }

  function getStatusColor(status) {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-yellow-600';
      case 'not_started':
        return 'text-gray-400';
      default:
        return 'text-gray-400';
    }
  }

  if (loading) return <div>Cargando curso...</div>;
  if (!course) return <div>Curso no encontrado</div>;

  return (
    <div className="course-overview">
      {/* Header del curso */}
      <div className="course-header">
        <img src={course.cover_url} alt={course.title} />
        <h1>{course.title}</h1>
        <p>{course.description}</p>
        <div className="course-stats">
          <span>Progreso: {course.enrollment.progress_percent.toFixed(1)}%</span>
          <span>Duración estimada: {course.estimated_minutes} min</span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${course.enrollment.progress_percent}%` }}
          />
        </div>
      </div>

      {/* Lista de módulos y lecciones */}
      <div className="modules-list">
        {course.modules.map((module, moduleIndex) => {
          // Calcular progreso del módulo
          const completedLessons = module.lessons.filter(
            l => l.status === 'completed'
          ).length;
          const moduleProgress = (completedLessons / module.lessons.length) * 100;

          return (
            <div key={module.id} className="module-card">
              <div className="module-header">
                <h2>
                  {moduleIndex + 1}. {module.title}
                </h2>
                <span className="module-progress">
                  {completedLessons}/{module.lessons.length} lecciones
                </span>
              </div>
              <div className="module-progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${moduleProgress}%` }}
                />
              </div>

              {/* Lecciones del módulo */}
              <ul className="lessons-list">
                {module.lessons.map((lesson, lessonIndex) => (
                  <li 
                    key={lesson.id} 
                    className={`lesson-item ${getStatusColor(lesson.status)}`}
                    onClick={() => handleLessonClick(lesson.id)}
                  >
                    <div className="lesson-number">
                      {moduleIndex + 1}.{lessonIndex + 1}
                    </div>
                    <div className="lesson-content">
                      <h3>{lesson.title}</h3>
                      <div className="lesson-meta">
                        <span>{lesson.estimated_minutes} min</span>
                        <span className="lesson-progress">
                          {lesson.progress_percent.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <div className="lesson-status">
                      {getStatusIcon(lesson.status)}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default CourseOverview;
```

---

### Caso 2: Pantalla de Detalle de Lección

Muestra el contenido completo de una lección con sus recursos.

```jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function LessonDetail() {
  const { courseId, lessonId } = useParams();
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLesson();
  }, [courseId, lessonId]);

  async function loadLesson() {
    try {
      const response = await fetch(
        `/api/v1/courses/${courseId}/lessons/${lessonId}`,
        { credentials: 'include' }
      );
      const data = await response.json();
      setLesson(data);
    } catch (error) {
      console.error('Error loading lesson:', error);
    } finally {
      setLoading(false);
    }
  }

  async function updateProgress(progressPercent, status) {
    try {
      await fetch(
        `/api/v1/courses/${courseId}/lessons/${lessonId}/progress`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            progress_percent: progressPercent,
            time_spent_seconds: 0, // Puedes trackear tiempo real
            status: status,
          }),
        }
      );
      // Recargar lección para actualizar progreso
      await loadLesson();
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  }

  function handleMarkAsComplete() {
    updateProgress(100, 'completed');
  }

  function getResourceIcon(type) {
    switch (type) {
      case 'video':
        return '🎥';
      case 'pdf':
        return '📄';
      case 'slide':
        return '📊';
      case 'podcast':
        return '🎧';
      default:
        return '📎';
    }
  }

  function formatDuration(seconds) {
    if (!seconds) return '';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }

  function formatTimeSpent(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  function formatDate(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  if (loading) return <div>Cargando lección...</div>;
  if (!lesson) return <div>Lección no encontrada</div>;

  return (
    <div className="lesson-detail">
      {/* Header */}
      <div className="lesson-header">
        <h1>{lesson.title}</h1>
        <div className="lesson-meta">
          <span>⏱️ {lesson.estimated_minutes} minutos</span>
          {lesson.progress && (
            <span className={`status-badge ${lesson.progress.status}`}>
              {lesson.progress.status === 'completed' ? '✅ Completada' : 
               lesson.progress.status === 'in_progress' ? '⏳ En progreso' : 
               '⭕ No iniciada'}
            </span>
          )}
        </div>
      </div>

      {/* Descripción */}
      <div className="lesson-description">
        <p>{lesson.description}</p>
      </div>

      {/* Progreso */}
      {lesson.progress && (
        <div className="lesson-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${lesson.progress.progress_percent}%` }}
            />
          </div>
          <div className="progress-stats">
            <span>{lesson.progress.progress_percent.toFixed(1)}% completado</span>
            <span>Tiempo dedicado: {formatTimeSpent(lesson.progress.time_spent_seconds)}</span>
          </div>
          {lesson.progress.completed_at && (
            <div className="progress-dates">
              <small>Completada: {formatDate(lesson.progress.completed_at)}</small>
            </div>
          )}
          {lesson.progress.last_activity_at && !lesson.progress.completed_at && (
            <div className="progress-dates">
              <small>Última actividad: {formatDate(lesson.progress.last_activity_at)}</small>
            </div>
          )}
        </div>
      )}

      {/* Recursos */}
      <div className="lesson-resources">
        <h2>Recursos de la Lección</h2>
        {lesson.resources.length === 0 ? (
          <p>No hay recursos disponibles para esta lección.</p>
        ) : (
          <div className="resources-grid">
            {lesson.resources.map((resource) => (
              <div key={resource.id} className="resource-card">
                <div className="resource-icon">
                  {getResourceIcon(resource.resource_type)}
                </div>
                <div className="resource-info">
                  <h3>{resource.title}</h3>
                  <span className="resource-type">{resource.resource_type}</span>
                  {resource.duration_seconds && (
                    <span className="resource-duration">
                      {formatDuration(resource.duration_seconds)}
                    </span>
                  )}
                </div>
                <a
                  href={resource.external_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="resource-button"
                >
                  {resource.resource_type === 'video' ? 'Ver Video' :
                   resource.resource_type === 'pdf' ? 'Abrir PDF' :
                   resource.resource_type === 'slide' ? 'Ver Slides' :
                   resource.resource_type === 'podcast' ? 'Escuchar' :
                   'Abrir'}
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Acciones */}
      <div className="lesson-actions">
        {lesson.progress?.status !== 'completed' && (
          <button 
            onClick={handleMarkAsComplete}
            className="btn-primary"
          >
            Marcar como Completada
          </button>
        )}
      </div>
    </div>
  );
}

export default LessonDetail;
```

---

## 📊 Flujo de Usuario Recomendado

```
1. Usuario entra al curso
   └─> GET /courses/{id}/detailed
   └─> Ver todos los módulos y lecciones con progreso
   
2. Usuario hace clic en una lección
   └─> Navegar a /courses/{id}/lessons/{lesson_id}
   └─> GET /courses/{id}/lessons/{lesson_id}
   └─> Ver descripción, recursos completos
   
3. Usuario consume el contenido (video, PDF, etc.)
   └─> Actualizar progreso periódicamente
   └─> PUT /courses/{id}/lessons/{lesson_id}/progress
   
4. Usuario completa la lección
   └─> Marcar como completada (progress_percent: 100, status: "completed")
   └─> PUT /courses/{id}/lessons/{lesson_id}/progress
   └─> Volver al overview y ver progreso actualizado
```

---

## 🎨 Estilos CSS Sugeridos

```css
/* Vista General del Curso */
.course-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #10b981;
  transition: width 0.3s ease;
}

.module-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.lesson-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.lesson-item:hover {
  background: #f3f4f6;
}

.lesson-item.text-green-600 {
  border-left: 4px solid #10b981;
}

.lesson-item.text-yellow-600 {
  border-left: 4px solid #f59e0b;
}

.lesson-item.text-gray-400 {
  border-left: 4px solid #9ca3af;
}

/* Detalle de Lección */
.lesson-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.lesson-progress {
  margin: 1.5rem 0;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.progress-dates {
  margin-top: 0.5rem;
  color: #9ca3af;
  font-size: 0.75rem;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.resource-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.resource-icon {
  font-size: 2.5rem;
  text-align: center;
}

.resource-button {
  display: inline-block;
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
  text-align: center;
  transition: background 0.2s;
}

.resource-button:hover {
  background: #2563eb;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.in_progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.not_started {
  background: #f3f4f6;
  color: #4b5563;
}
```

---

## ⚠️ Notas Importantes

### 1. **No más focus mode**
El endpoint `/courses/{id}/detailed` ahora regresa **todos** los módulos y lecciones. No uses parámetros `focus_module_id` o `focus_lesson_id` (ya no existen).

### 2. **Optimización de carga**
- La vista general NO incluye recursos (videos, PDFs) para mantener el response ligero
- Los recursos solo se cargan cuando el usuario abre una lección específica

### 3. **Estados de progreso**
```
"not_started"  → Lección no iniciada (progress_percent = 0.0)
"in_progress"  → Lección en progreso (0 < progress_percent < 100)
"completed"    → Lección completada (progress_percent = 100.0)
```

### 4. **Actualizar progreso**
Usa `PUT /courses/{id}/lessons/{lesson_id}/progress` para actualizar:
```json
{
  "progress_percent": 75.0,
  "time_spent_seconds": 1800,
  "status": "in_progress"
}
```

### 5. **Manejo de errores**
```javascript
// 403: Usuario no inscrito en el curso
// 404: Curso o lección no encontrada
// 401: No autenticado (cookie expirada)
```

---

## ✅ Checklist de Implementación

- [ ] Implementar vista general del curso (todos los módulos y lecciones)
- [ ] Mostrar progreso por lección (barra de progreso + porcentaje)
- [ ] Mostrar progreso por módulo (calculado del promedio de lecciones)
- [ ] Implementar vista de detalle de lección
- [ ] Cargar y mostrar recursos (videos, PDFs, slides, podcasts)
- [ ] Implementar navegación entre lecciones
- [ ] Actualizar progreso cuando el usuario complete una lección
- [ ] Manejar diferentes tipos de recursos con íconos apropiados
- [ ] Implementar "Marcar como completada"
- [ ] Actualizar vista general después de completar lección
- [ ] Manejar errores 401/403/404 correctamente

---

## 🚀 Endpoints Disponibles (Resumen)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/courses` | Lista todos los cursos disponibles |
| `POST` | `/courses/{id}/enroll` | Inscribirse en un curso |
| `GET` | `/courses/{id}/detailed` | **Vista general del curso** (todos los módulos y lecciones con progreso) |
| `GET` | `/courses/{id}/lessons/{lesson_id}` | **Detalle de una lección** (con recursos completos) |
| `PUT` | `/courses/{id}/lessons/{lesson_id}/progress` | Actualizar progreso de una lección |

---

¡Todo listo para implementar! 🎉
