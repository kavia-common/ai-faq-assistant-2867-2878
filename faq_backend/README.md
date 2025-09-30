# AI FAQ Backend (Django)

This Django app provides REST APIs for an AI FAQ bot with Retrieval Augmented Generation (RAG), search, authentication (JWT), and knowledge base (KB) management.

Key endpoints:
- POST /api/ask — submit a question, returns generated answer with retrieved contexts
- GET /api/search — simple search over KB
- POST /api/auth — username/password authentication, returns JWT tokens
- /api/kb/ — CRUD for KB entries (list/retrieve public; create/update/delete admin)

Docs:
- Swagger UI: /docs
- Redoc: /redoc
- OpenAPI JSON: /swagger.json

Environment variables (configure via .env by orchestrator):
- VECTOR_BACKEND (optional): choose vector DB impl in future
- GENERATION_MODEL (optional): choose LLM in future

Setup:
1) Install requirements
2) python manage.py migrate
3) python manage.py createsuperuser
4) (optional) Load sample KB data
5) Runserver and navigate to /docs

Notes:
- RAG is implemented with a simple TF-IDF vector index for development. Replace with a managed vector DB in production. 
- After updating KB in bulk, call POST /api/kb/refresh-index/ (admin) to rebuild vectors.
