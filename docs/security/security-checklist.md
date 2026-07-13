# Security Checklist

- Hash de contrasenas con Argon2id.
- Tokens de acceso y refresh separados.
- Cookies HttpOnly previstas.
- CORS restringido por origen.
- Sin `eval`, `exec`, SQL dinamico ni Cypher arbitrario.
- Respuestas administrativas pendientes de ampliacion antes de produccion.
- Datos demo marcados como demostracion.
