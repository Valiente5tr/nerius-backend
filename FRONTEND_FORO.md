# 📋 Documentación del Foro - API Endpoints

Guía completa para integrar el sistema de foro en el frontend.

## 📑 Tabla de Contenidos

1. [Listar Posts del Foro](#1-listar-posts-del-foro)
2. [Ver Detalle de un Post](#2-ver-detalle-de-un-post)
3. [Obtener Comentarios de un Post](#3-obtener-comentarios-de-un-post)
4. [Crear un Comentario](#4-crear-un-comentario)
5. [Crear una Respuesta (Comentario Anidado)](#5-crear-una-respuesta-comentario-anidado)
6. [Borrar un Comentario](#6-borrar-un-comentario)
7. [Buscar en el Foro](#7-buscar-en-el-foro)
8. [Ejemplos de Interfaz en React](#8-ejemplos-de-interfaz-en-react)

---

## 1. Listar Posts del Foro

### 📌 Endpoint
```
GET /api/forum
```

### 🔓 Autenticación
No requerida (lectura pública)

### 📥 Query Parameters
- `limit` (opcional): Máximo de posts a retornar (1-50, default: 10)
- `skip` (opcional): Número de posts a omitir (para paginación, default: 0)

### 📤 Respuesta
```json
[
  {
    "id": "uuid-del-post",
    "title": "¿Cómo mejorar mis habilidades de liderazgo?",
    "content": "Estoy buscando consejos prácticos para desarrollar...",
    "multimedia_url": "https://example.com/video/leadership-tips.mp4",
    "author": {
      "id": "uuid-autor",
      "first_name": "María",
      "last_name": "López",
      "email": "maria.lopez@example.com"
    },
    "status": "published",
    "created_at": "2026-03-10T08:30:00",
    "published_at": "2026-03-10T09:00:00",
    "comments_count": 15
  },
  {
    "id": "uuid-otro-post",
    "title": "Recursos recomendados para aprender Python",
    "content": "Me gustaría compartir algunos recursos que me han ayudado...",
    "multimedia_url": null,
    "author": {
      "id": "uuid-autor-2",
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan.perez@example.com"
    },
    "status": "published",
    "created_at": "2026-03-09T15:20:00",
    "published_at": "2026-03-09T15:30:00",
    "comments_count": 8
  }
]
```

### 💻 Ejemplo cURL
```bash
# Obtener los últimos 10 posts
curl -X GET "http://localhost:8000/api/forum"

# Obtener 20 posts con paginación
curl -X GET "http://localhost:8000/api/forum?limit=20&skip=0"

# Segunda página (20 posts más)
curl -X GET "http://localhost:8000/api/forum?limit=20&skip=20"
```

---

## 2. Ver Detalle de un Post

### 📌 Endpoint
```
GET /api/forum/{post_id}
```

### 🔓 Autenticación
No requerida (lectura pública)

### 📥 Path Parameters
- `post_id`: UUID del post

### 📤 Respuesta
```json
{
  "id": "uuid-del-post",
  "title": "¿Cómo mejorar mis habilidades de liderazgo?",
  "content": "Estoy buscando consejos prácticos para desarrollar mis habilidades de liderazgo. He completado algunos cursos pero me gustaría saber qué opinan otros sobre este tema...",
  "multimedia_url": "https://example.com/images/leadership-cover.jpg",
  "author": {
    "id": "uuid-autor",
    "first_name": "María",
    "last_name": "López",
    "email": "maria.lopez@example.com"
  },
  "status": "published",
  "created_at": "2026-03-10T08:30:00",
  "updated_at": "2026-03-10T09:00:00",
  "published_at": "2026-03-10T09:00:00",
  "comments_count": 15
}
```

### 💻 Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/forum/38b9e3ca-e2eb-4245-b579-25a413e5da9f"
```

### ⚠️ Errores
- **404**: Post no encontrado o no publicado

---

## 3. Obtener Comentarios de un Post

### 📌 Endpoint
```
GET /api/forum/{post_id}/comments
```

### 🔓 Autenticación
No requerida (lectura pública)

### 📥 Path Parameters
- `post_id`: UUID del post

### 📤 Respuesta
Retorna solo comentarios de nivel superior (sin `parent_comment_id`). Para cargar respuestas anidadas, usa `replies_count`.

```json
[
  {
    "id": "comment-uuid-1",
    "post_id": "post-uuid",
    "author": {
      "id": "user-uuid",
      "first_name": "Carlos",
      "last_name": "Ramírez",
      "email": "carlos.ramirez@example.com"
    },
    "parent_comment_id": null,
    "content": "Excelente pregunta. Yo recomendaría empezar por desarrollar tu inteligencia emocional...",
    "created_at": "2026-03-10T10:15:00",
    "updated_at": null,
    "replies_count": 3
  },
  {
    "id": "comment-uuid-2",
    "post_id": "post-uuid",
    "author": {
      "id": "user-uuid-2",
      "first_name": "Ana",
      "last_name": "García",
      "email": "ana.garcia@example.com"
    },
    "parent_comment_id": null,
    "content": "Totalmente de acuerdo con los comentarios anteriores. También sugiero...",
    "created_at": "2026-03-10T11:30:00",
    "updated_at": null,
    "replies_count": 0
  }
]
```

### 💻 Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/forum/38b9e3ca-e2eb-4245-b579-25a413e5da9f/comments"
```

### 📝 Nota sobre Comentarios Anidados
Este endpoint retorna **solo comentarios de primer nivel**. Para cargar las respuestas (nested replies):
- Usa el campo `replies_count` para saber cuántas respuestas tiene un comentario
- Actualmente las replies se obtienen haciendo una consulta a todos los comentarios y filtrando por `parent_comment_id` en el frontend
- **Próximamente**: Endpoint dedicado para obtener replies de un comentario específico

---

## 4. Crear un Comentario

### 📌 Endpoint
```
POST /api/forum/{post_id}/comments
```

### 🔒 Autenticación
**Requerida** - Cookie: `session_id`

### 📥 Path Parameters
- `post_id`: UUID del post

### 📥 Request Body
```json
{
  "content": "Este es mi comentario sobre el tema...",
  "parent_comment_id": null
}
```

**Campos:**
- `content` (requerido): Contenido del comentario (1-5000 caracteres)
- `parent_comment_id` (opcional): `null` para comentario raíz, o UUID para respuesta anidada

### 📤 Respuesta (HTTP 201)
```json
{
  "id": "nuevo-comment-uuid",
  "post_id": "post-uuid",
  "author": {
    "id": "tu-user-uuid",
    "first_name": "Tu",
    "last_name": "Nombre",
    "email": "tu.email@example.com"
  },
  "parent_comment_id": null,
  "content": "Este es mi comentario sobre el tema...",
  "created_at": "2026-03-12T14:30:00",
  "updated_at": null,
  "replies_count": 0
}
```

### 💻 Ejemplo cURL
```bash
curl -X POST "http://localhost:8000/api/forum/38b9e3ca-e2eb-4245-b579-25a413e5da9f/comments" \
  -H "Cookie: session_id=2caaebfa-3fad-405e-a887-7b3b88a833fd" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Excelente post. Me gustaría añadir que...",
    "parent_comment_id": null
  }'
```

### ⚠️ Errores
- **401**: No autenticado (sin session_id)
- **404**: Post no encontrado o no publicado
- **422**: Validación fallida (content vacío o muy largo)

---

## 5. Crear una Respuesta (Comentario Anidado)

### 📌 Endpoint
```
POST /api/forum/{post_id}/comments
```

### 🔒 Autenticación
**Requerida** - Cookie: `session_id`

### 📥 Request Body
```json
{
  "content": "Gracias por tu comentario. Estoy de acuerdo con tu punto sobre...",
  "parent_comment_id": "uuid-del-comentario-padre"
}
```

**La diferencia con un comentario normal es que `parent_comment_id` contiene el UUID del comentario al que estás respondiendo.**

### 📤 Respuesta (HTTP 201)
```json
{
  "id": "reply-uuid",
  "post_id": "post-uuid",
  "author": {
    "id": "tu-user-uuid",
    "first_name": "Tu",
    "last_name": "Nombre",
    "email": "tu.email@example.com"
  },
  "parent_comment_id": "uuid-del-comentario-padre",
  "content": "Gracias por tu comentario. Estoy de acuerdo con tu punto sobre...",
  "created_at": "2026-03-12T15:00:00",
  "updated_at": null,
  "replies_count": 0
}
```

### 💻 Ejemplo cURL
```bash
curl -X POST "http://localhost:8000/api/forum/38b9e3ca-e2eb-4245-b579-25a413e5da9f/comments" \
  -H "Cookie: session_id=2caaebfa-3fad-405e-a887-7b3b88a833fd" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Totalmente de acuerdo contigo!",
    "parent_comment_id": "comment-uuid-1"
  }'
```

### ⚠️ Errores
- **401**: No autenticado
- **404**: Post o comentario padre no encontrado
- **404**: El comentario padre no pertenece a este post

---

## 6. Borrar un Comentario

### 📌 Endpoint
```
DELETE /api/forum/{post_id}/comments/{comment_id}
```

### 🔒 Autenticación
**Requerida** - Cookie: `session_id`

### 📥 Path Parameters
- `post_id`: UUID del post
- `comment_id`: UUID del comentario a borrar

### 📤 Respuesta (HTTP 204)
Sin contenido (éxito)

### 🗑️ Comportamiento de Cascade
Cuando borras un comentario que tiene respuestas, **todas las respuestas anidadas también se borran automáticamente**.

### 💻 Ejemplo cURL
```bash
curl -X DELETE "http://localhost:8000/api/forum/38b9e3ca-e2eb-4245-b579-25a413e5da9f/comments/comment-uuid-1" \
  -H "Cookie: session_id=2caaebfa-3fad-405e-a887-7b3b88a833fd"
```

### ⚠️ Errores
- **401**: No autenticado
- **403**: No tienes permiso (solo el autor puede borrar su comentario)
- **404**: Comentario no encontrado

---

## 7. Buscar en el Foro

### 📌 Endpoint
```
GET /api/forum/search
```

### 🔓 Autenticación
No requerida (lectura pública)

### 📥 Query Parameters
- `q` (requerido): Query de búsqueda (mínimo 2 caracteres, máximo 100)
- `limit` (opcional): Máximo de resultados (1-50, default: 10)
- `skip` (opcional): Número de resultados a omitir (para paginación, default: 0)

### 📤 Respuesta
Retorna posts que coinciden con el término de búsqueda en el **título** o **contenido**, ordenados por fecha de publicación (más recientes primero).

```json
[
  {
    "id": "uuid-del-post",
    "title": "¿Cómo mejorar mis habilidades de liderazgo?",
    "content": "Estoy buscando consejos prácticos para desarrollar...",
    "multimedia_url": "https://example.com/video/leadership-tips.mp4",
    "author": {
      "id": "uuid-autor",
      "first_name": "María",
      "last_name": "López",
      "email": "maria.lopez@example.com"
    },
    "status": "published",
    "created_at": "2026-03-10T08:30:00",
    "published_at": "2026-03-10T09:00:00",
    "comments_count": 15
  }
]
```

### 💻 Ejemplo cURL
```bash
# Buscar posts que contengan "liderazgo"
curl -X GET "http://localhost:8000/api/forum/search?q=liderazgo"

# Buscar con paginación
curl -X GET "http://localhost:8000/api/forum/search?q=python&limit=20&skip=0"

# Buscar frase
curl -X GET "http://localhost:8000/api/forum/search?q=inteligencia%20emocional"
```

### 🔍 Comportamiento de la Búsqueda
- Búsqueda **case-insensitive** (no distingue mayúsculas/minúsculas)
- Busca en **título** y **contenido** de los posts
- Solo retorna posts **publicados**
- Búsqueda de texto parcial (ej: "lider" encuentra "liderazgo")
- Resultados ordenados por fecha de publicación (más recientes primero)

### ⚠️ Errores
- **422**: Query inválido (menos de 2 caracteres o más de 100)

### 💡 Mejores Prácticas

**Para el Frontend:**
1. **Debouncing**: Espera 300-500ms después del último cambio antes de buscar
2. **Validación**: Valida mínimo 2 caracteres antes de enviar request
3. **Cancelación**: Cancela requests previos cuando el usuario sigue escribiendo
4. **UX**: Muestra indicador de "buscando..." mientras carga
5. **Resultados vacíos**: Muestra mensaje claro cuando no hay resultados

**Para Performance:**
- Limita resultados (máximo 50)
- Implementa paginación para muchos resultados
- Considera caché para búsquedas populares

---

## 8. Ejemplos de Interfaz en React

### 8.1 Componente: Búsqueda con Debouncing

```jsx
import React, { useState, useEffect } from 'react';

function ForumSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Debouncing: Espera 300ms después del último cambio
  useEffect(() => {
    if (searchQuery.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setLoading(true);
    const timer = setTimeout(() => {
      performSearch(searchQuery);
    }, 300); // Espera 300ms

    return () => clearTimeout(timer); // Cancela búsquedas previas
  }, [searchQuery]);

  const performSearch = async (query) => {
    try {
      const response = await fetch(
        `/api/forum/search?q=${encodeURIComponent(query)}&limit=10`
      );
      const data = await response.json();
      setResults(data);
      setShowResults(true);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  const highlightMatch = (text, query) => {
    if (!query || !text) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, i) => 
      regex.test(part) ? <mark key={i}>{part}</mark> : part
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="forum-search">
      <div className="search-input-container">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => searchQuery.length >= 2 && setShowResults(true)}
          placeholder="🔍 Buscar en el foro..."
          className="search-input"
        />
        
        {loading && (
          <div className="search-spinner">⏳</div>
        )}
        
        {searchQuery.length > 0 && searchQuery.length < 2 && (
          <div className="search-hint">Escribe al menos 2 caracteres</div>
        )}
      </div>

      {showResults && searchQuery.length >= 2 && (
        <div className="search-results-dropdown">
          {results.length === 0 && !loading ? (
            <div className="no-results">
              No se encontraron resultados para "{searchQuery}"
            </div>
          ) : (
            <div className="results-list">
              <div className="results-header">
                {results.length} resultado{results.length !== 1 ? 's' : ''}
              </div>
              
              {results.map((post) => (
                <a
                  key={post.id}
                  href={`/forum/${post.id}`}
                  className="search-result-item"
                  onClick={() => setShowResults(false)}
                >
                  <div className="result-title">
                    {highlightMatch(post.title, searchQuery)}
                  </div>
                  <div className="result-preview">
                    {highlightMatch(
                      post.content.substring(0, 150),
                      searchQuery
                    )}...
                  </div>
                  <div className="result-meta">
                    <span>Por {post.author.first_name} {post.author.last_name}</span>
                    <span> · </span>
                    <span>{formatDate(post.published_at)}</span>
                    <span> · </span>
                    <span>💬 {post.comments_count}</span>
                  </div>
                </a>
              ))}
              
              {results.length === 10 && (
                <a 
                  href={`/forum/search?q=${encodeURIComponent(searchQuery)}`} 
                  className="view-all"
                >
                  Ver todos los resultados →
                </a>
              )}
            </div>
          )}
        </div>
      )}

      {/* Overlay para cerrar dropdown */}
      {showResults && (
        <div 
          className="search-overlay"
          onClick={() => setShowResults(false)}
        />
      )}
    </div>
  );
}

export default ForumSearch;
```

### 8.2 CSS para Búsqueda

```css
/* Search Container */
.forum-search {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 20px 0;
}

.search-input-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  font-size: 16px;
  border: 2px solid #dadce0;
  border-radius: 24px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: #1a73e8;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.2);
}

.search-spinner {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.search-hint {
  position: absolute;
  top: calc(100% + 4px);
  left: 16px;
  font-size: 12px;
  color: #5f6368;
}

/* Search Results Dropdown */
.search-results-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dadce0;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  max-height: 500px;
  overflow-y: auto;
  z-index: 1000;
}

.results-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e8eaed;
  font-size: 14px;
  color: #5f6368;
  font-weight: 500;
  background: #f8f9fa;
}

.results-list {
  max-height: 450px;
  overflow-y: auto;
}

.search-result-item {
  display: block;
  padding: 12px 16px;
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid #f1f3f4;
  transition: background 0.15s;
  cursor: pointer;
}

.search-result-item:hover {
  background: #f8f9fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-title {
  font-weight: 500;
  color: #1a73e8;
  margin-bottom: 4px;
  font-size: 15px;
}

.result-preview {
  font-size: 14px;
  color: #3c4043;
  margin-bottom: 6px;
  line-height: 1.4;
}

.result-meta {
  font-size: 12px;
  color: #5f6368;
}

.no-results {
  padding: 32px 16px;
  text-align: center;
  color: #5f6368;
}

.view-all {
  display: block;
  padding: 12px 16px;
  text-align: center;
  color: #1a73e8;
  font-weight: 500;
  text-decoration: none;
  border-top: 1px solid #e8eaed;
  background: #f8f9fa;
}

.view-all:hover {
  background: #e8f0fe;
}

.search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  background: transparent;
}

/* Highlighting */
mark {
  background-color: #fff59d;
  padding: 2px 0;
  font-weight: 500;
}
```

### 8.3 Hook Personalizado: useDebounce

```jsx
// hooks/useDebounce.js
import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Uso:
function SearchComponent() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      fetch(`/api/forum/search?q=${encodeURIComponent(debouncedQuery)}`)
        .then(res => res.json())
        .then(data => setResults(data));
    }
  }, [debouncedQuery]);

  return (
    <input 
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Buscar..."
    />
  );
}
```

---

### 8.4 Componente: Lista de Posts del Foro

```jsx
import React, { useState, useEffect } from 'react';

function ForumPostsList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const POSTS_PER_PAGE = 10;

  useEffect(() => {
    fetchPosts();
  }, [page]);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/forum?limit=${POSTS_PER_PAGE}&skip=${page * POSTS_PER_PAGE}`
      );
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) return <div>Cargando posts...</div>;

  return (
    <div className="forum-posts-list">
      <h1>Foro de Discusión</h1>
      
      {posts.map((post) => (
        <div key={post.id} className="forum-post-card">
          <h2>
            <a href={`/forum/${post.id}`}>{post.title}</a>
          </h2>
          
          {/* Mostrar imagen/video si existe */}
          {post.multimedia_url && (
            <div className="post-media-preview">
              <img 
                src={post.multimedia_url} 
                alt={post.title}
                style={{ width: '100%', maxHeight: '200px', objectFit: 'cover', borderRadius: '4px' }}
              />
            </div>
          )}
          
          <div className="post-meta">
            <span className="author">
              Por {post.author.first_name} {post.author.last_name}
            </span>
            <span className="date">{formatDate(post.published_at)}</span>
            <span className="comments-count">
              💬 {post.comments_count} comentarios
            </span>
          </div>
          
          <p className="post-preview">
            {post.content.substring(0, 200)}...
          </p>
          
          <a href={`/forum/${post.id}`} className="read-more">
            Leer más →
          </a>
        </div>
      ))}
      
      <div className="pagination">
        <button 
          onClick={() => setPage(p => Math.max(0, p - 1))}
          disabled={page === 0}
        >
          ← Anterior
        </button>
        <span>Página {page + 1}</span>
        <button 
          onClick={() => setPage(p => p + 1)}
          disabled={posts.length < POSTS_PER_PAGE}
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
}

export default ForumPostsList;
```

### 8.5 Componente: Detalle de Post con Comentarios

```jsx
import React, { useState, useEffect } from 'react';

function ForumPostDetail({ postId }) {
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPostAndComments();
  }, [postId]);

  const fetchPostAndComments = async () => {
    setLoading(true);
    try {
      // Fetch post details
      const postResponse = await fetch(`/api/forum/${postId}`);
      const postData = await postResponse.json();
      setPost(postData);

      // Fetch comments
      const commentsResponse = await fetch(`/api/forum/${postId}/comments`);
      const commentsData = await commentsResponse.json();
      setComments(commentsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    
    if (!newComment.trim()) return;

    try {
      const response = await fetch(`/api/forum/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Para enviar cookies
        body: JSON.stringify({
          content: newComment,
          parent_comment_id: replyingTo,
        }),
      });

      if (response.ok) {
        const newCommentData = await response.json();
        // Agregar el nuevo comentario a la lista
        setComments([...comments, newCommentData]);
        setNewComment('');
        setReplyingTo(null);
      } else {
        alert('Error al crear comentario');
      }
    } catch (error) {
      console.error('Error creating comment:', error);
      alert('Error al crear comentario');
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!confirm('¿Estás seguro de que quieres borrar este comentario?')) {
      return;
    }

    try {
      const response = await fetch(
        `/api/forum/${postId}/comments/${commentId}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (response.ok) {
        // Remover el comentario de la lista
        setComments(comments.filter(c => c.id !== commentId));
      } else if (response.status === 403) {
        alert('No tienes permiso para borrar este comentario');
      } else {
        alert('Error al borrar comentario');
      }
    } catch (error) {
      console.error('Error deleting comment:', error);
      alert('Error al borrar comentario');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) return <div>Cargando...</div>;
  if (!post) return <div>Post no encontrado</div>;

  return (
    <div className="forum-post-detail">
      {/* Post Content */}
      <article className="post-content">
        <h1>{post.title}</h1>
        
        <div className="post-meta">
          <span className="author">
            Por {post.author.first_name} {post.author.last_name}
          </span>
          <span className="date">{formatDate(post.published_at)}</span>
        </div>
        
        {/* Multimedia si existe */}
        {post.multimedia_url && (
          <div className="post-multimedia">
            <img 
              src={post.multimedia_url} 
              alt={post.title}
              style={{ width: '100%', maxHeight: '500px', objectFit: 'cover', borderRadius: '8px' }}
            />
          </div>
        )}
        
        <div className="post-body">
          {post.content}
        </div>
      </article>

      {/* Comments Section */}
      <section className="comments-section">
        <h2>💬 Comentarios ({post.comments_count})</h2>
        
        {/* New Comment Form */}
        <form onSubmit={handleSubmitComment} className="comment-form">
          {replyingTo && (
            <div className="replying-to">
              Respondiendo a un comentario
              <button type="button" onClick={() => setReplyingTo(null)}>
                ✕ Cancelar
              </button>
            </div>
          )}
          
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder={replyingTo ? "Escribe tu respuesta..." : "Escribe un comentario..."}
            rows={4}
            maxLength={5000}
          />
          
          <button type="submit">
            {replyingTo ? 'Publicar Respuesta' : 'Publicar Comentario'}
          </button>
        </form>

        {/* Comments List */}
        <div className="comments-list">
          {comments.length === 0 ? (
            <p>No hay comentarios aún. ¡Sé el primero en comentar!</p>
          ) : (
            comments.map((comment) => (
              <Comment
                key={comment.id}
                comment={comment}
                onReply={setReplyingTo}
                onDelete={handleDeleteComment}
                currentUserId={null} // Aquí deberías pasar el ID del usuario actual
              />
            ))
          )}
        </div>
      </section>
    </div>
  );
}

// Subcomponente para un comentario individual
function Comment({ comment, onReply, onDelete, currentUserId }) {
  const isAuthor = currentUserId === comment.author.id;

  return (
    <div className="comment">
      <div className="comment-header">
        <strong>
          {comment.author.first_name} {comment.author.last_name}
        </strong>
        <span className="comment-date">
          {new Date(comment.created_at).toLocaleDateString()}
        </span>
      </div>
      
      <div className="comment-content">
        {comment.content}
      </div>
      
      <div className="comment-actions">
        <button onClick={() => onReply(comment.id)}>
          💬 Responder
        </button>
        
        {comment.replies_count > 0 && (
          <span className="replies-count">
            {comment.replies_count} respuestas
          </span>
        )}
        
        {isAuthor && (
          <button 
            onClick={() => onDelete(comment.id)}
            className="delete-btn"
          >
            🗑️ Borrar
          </button>
        )}
      </div>
    </div>
  );
}

export default ForumPostDetail;
```

### 8.6 CSS Sugerido

```css
/* Forum Posts List */
.forum-posts-list {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.forum-post-card {
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  transition: box-shadow 0.2s;
}

.forum-post-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.forum-post-card h2 {
  margin: 0 0 12px 0;
}

.forum-post-card h2 a {
  color: #1a73e8;
  text-decoration: none;
}

.forum-post-card h2 a:hover {
  text-decoration: underline;
}

.post-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #5f6368;
  margin-bottom: 12px;
}

.post-preview {
  color: #3c4043;
  margin: 12px 0;
}

.read-more {
  color: #1a73e8;
  text-decoration: none;
  font-weight: 500;
}

/* Post Detail */
.forum-post-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.post-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.post-content h1 {
  margin: 0 0 16px 0;
  color: #202124;
}

.post-body {
  line-height: 1.6;
  color: #3c4043;
  white-space: pre-wrap;
}

/* Comments Section */
.comments-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
}

.comments-section h2 {
  margin: 0 0 20px 0;
  color: #202124;
}

.comment-form {
  margin-bottom: 24px;
}

.replying-to {
  background: #e8f0fe;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #dadce0;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 8px;
}

.comment-form button {
  background: #1a73e8;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.comment-form button:hover {
  background: #1557b0;
}

/* Comments List */
.comments-list {
  margin-top: 20px;
}

.comment {
  border-left: 3px solid #e8eaed;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-header strong {
  color: #202124;
}

.comment-date {
  font-size: 13px;
  color: #5f6368;
}

.comment-content {
  color: #3c4043;
  margin-bottom: 8px;
  white-space: pre-wrap;
}

.comment-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.comment-actions button {
  background: none;
  border: none;
  color: #1a73e8;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 8px;
}

.comment-actions button:hover {
  text-decoration: underline;
}

.delete-btn {
  color: #d93025 !important;
}

.replies-count {
  font-size: 13px;
  color: #5f6368;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #dadce0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  background: #f8f9fa;
}
```

---

### 8.7 Componente: Mostrar Multimedia

Los posts del foro ahora soportan una URL de multimedia (`multimedia_url`) que puede ser una imagen, video, o cualquier otro contenido multimedia.

### Helper para Detectar Tipo de Multimedia

```jsx
// Detecta el tipo de contenido multimedia basado en la URL
const getMediaType = (url) => {
  if (!url) return null;
  
  const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov'];
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
  
  const lowerUrl = url.toLowerCase();
  
  if (videoExtensions.some(ext => lowerUrl.includes(ext))) {
    return 'video';
  }
  
  if (imageExtensions.some(ext => lowerUrl.includes(ext))) {
    return 'image';
  }
  
  // Detectar URLs de YouTube, Vimeo, etc.
  if (lowerUrl.includes('youtube.com') || lowerUrl.includes('youtu.be')) {
    return 'youtube';
  }
  
  if (lowerUrl.includes('vimeo.com')) {
    return 'vimeo';
  }
  
  return 'link'; // Enlace genérico
};
```

### Componente MediaDisplay

```jsx
function MediaDisplay({ url }) {
  const mediaType = getMediaType(url);
  
  if (!url) return null;
  
  switch (mediaType) {
    case 'image':
      return (
        <div className="media-container">
          <img 
            src={url} 
            alt="Post media" 
            className="post-image"
            loading="lazy"
          />
        </div>
      );
      
    case 'video':
      return (
        <div className="media-container">
          <video 
            controls 
            className="post-video"
            preload="metadata"
          >
            <source src={url} />
            Tu navegador no soporta la reproducción de video.
          </video>
        </div>
      );
      
    case 'youtube':
      // Extraer ID del video de YouTube
      const youtubeId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s]+)/)?.[1];
      return youtubeId ? (
        <div className="media-container video-embed">
          <iframe
            src={`https://www.youtube.com/embed/${youtubeId}`}
            title="YouTube video"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      ) : null;
      
    case 'vimeo':
      const vimeoId = url.match(/vimeo\.com\/(\d+)/)?.[1];
      return vimeoId ? (
        <div className="media-container video-embed">
          <iframe
            src={`https://player.vimeo.com/video/${vimeoId}`}
            title="Vimeo video"
            frameBorder="0"
            allow="autoplay; fullscreen; picture-in-picture"
            allowFullScreen
          />
        </div>
      ) : null;
      
    case 'link':
    default:
      return (
        <div className="media-container">
          <a href={url} target="_blank" rel="noopener noreferrer" className="media-link">
            🔗 Ver contenido multimedia
          </a>
        </div>
      );
  }
}
```

### Uso en ForumPostCard

```jsx
<div className="forum-post-card">
  <h2>
    <a href={`/forum/${post.id}`}>{post.title}</a>
  </h2>
  
  {/* Mostrar multimedia si existe */}
  {post.multimedia_url && (
    <MediaDisplay url={post.multimedia_url} />
  )}
  
  <div className="post-meta">
    <span className="author">
      Por {post.author.first_name} {post.author.last_name}
    </span>
    <span className="date">{formatDate(post.published_at)}</span>
    <span className="comments-count">
      💬 {post.comments_count} comentarios
    </span>
  </div>
  
  <p className="post-preview">
    {post.content.substring(0, 200)}...
  </p>
  
  <a href={`/forum/${post.id}`} className="read-more">
    Leer más →
  </a>
</div>
```

### CSS para Multimedia

```css
/* Media containers */
.media-container {
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
}

.post-image {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  max-height: 400px;
}

.post-video {
  width: 100%;
  height: auto;
  display: block;
  max-height: 500px;
}

.video-embed {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
}

.video-embed iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.media-link {
  display: block;
  padding: 16px;
  text-align: center;
  color: #1a73e8;
  text-decoration: none;
  font-weight: 500;
}

.media-link:hover {
  background: #e8f0fe;
}
```

---

## 📚 Flujo de Trabajo Típico

### Para Ver el Foro:
1. **GET** `/api/forum` → Lista de posts
2. **Click en un post** → **GET** `/api/forum/{post_id}` → Detalle
3. **GET** `/api/forum/{post_id}/comments` → Comentarios

### Para Comentar:
1. Usuario auténticado entra a un post
2. Escribe un comentario en el formulario
3. **POST** `/api/forum/{post_id}/comments` con `parent_comment_id: null`
4. El comentario aparece en la lista

### Para Responder un Comentario:
1. Usuario hace click en "Responder" en un comentario
2. El formulario muestra "Respondiendo a..."
3. **POST** `/api/forum/{post_id}/comments` con `parent_comment_id: {comment_id}`
4. La respuesta aparece vinculada al comentario padre

### Para Borrar:
1. Usuario ve opción "Borrar" solo en sus propios comentarios
2. Confirma la acción
3. **DELETE** `/api/forum/{post_id}/comments/{comment_id}`
4. El comentario desaparece (y sus respuestas también)

---

## 🔐 Autenticación

### ¿Qué necesita autenticación?
- ✅ Leer posts: **NO**
- ✅ Leer comentarios: **NO**
- 🔒 Crear comentarios: **SÍ**
- 🔒 Borrar comentarios: **SÍ**

### Cómo enviar la autenticación:
```javascript
// Con fetch
fetch('/api/forum/POST_ID/comments', {
  method: 'POST',
  credentials: 'include', // Envía cookies automáticamente
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ content: '...' })
});

// O manualmente con la cookie
fetch('/api/forum/POST_ID/comments', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Cookie': 'session_id=YOUR_SESSION_ID'
  },
  body: JSON.stringify({ content: '...' })
});
```

---

## 🎯 Mejores Prácticas

1. **Validación en el Frontend**
   - Valida que el comentario tenga entre 1-5000 caracteres antes de enviarlo
   - Muestra el contador de caracteres

2. **Manejo de Errores**
   - Muestra mensajes claros cuando la autenticación falla
   - Redirige al login si es necesario
   - Maneja errores 403 (sin permisos) apropiadamente

3. **UX de Respuestas Anidadas**
   - Muestra visualmente qué comentario se está respondiendo
   - Permite cancelar la respuesta
   - Indenta las respuestas para mostrar jerarquía

4. **Optimización**
   - Implementa paginación para posts
   - Para comentarios con muchas respuestas, implementa "Ver más" en lugar de cargar todo
   - Usa optimistic updates para mejorar la percepción de velocidad

5. **Accesibilidad**
   - Usa botones semánticos (`<button>`)
   - Añade labels a los formularios
   - Implementa navegación por teclado

---

## 📋 Checklist de Implementación

- [ ] Lista de posts del foro con paginación
- [ ] Vista de detalle de un post
- [ ] Formulario para crear comentarios
- [ ] Botón "Responder" en cada comentario
- [ ] Formulario de respuesta con indicador visual
- [ ] Botón "Borrar" solo en comentarios propios
- [ ] Confirmación antes de borrar
- [ ] Manejo de errores de autenticación
- [ ] Contador de caracteres (5000 max)
- [ ] Timestamps formateados correctamente
- [ ] Indicador de comentarios anidados (replies_count)
- [ ] Estilos responsivos para móviles

---

## 🚀 Próximas Mejoras Sugeridas

1. **Endpoint para obtener respuestas específicas**
   ```
   GET /api/forum/{post_id}/comments/{comment_id}/replies
   ```

2. **Editar comentarios**
   ```
   PUT /api/forum/{post_id}/comments/{comment_id}
   ```

3. **Búsqueda en el foro**
   ```
   GET /api/forum/search?q=query
   ```

4. **Filtros por área o tags**
   ```
   GET /api/forum?area_id=uuid
   ```

5. **Ordenamiento personalizado**
   ```
   GET /api/forum?sort=popular|recent|trending
   ```

6. **Reacciones a comentarios** (likes, etc.)

7. **Notificaciones** cuando alguien responde tu comentario

---

¿Necesitas ayuda con alguna parte específica de la implementación? 🚀
