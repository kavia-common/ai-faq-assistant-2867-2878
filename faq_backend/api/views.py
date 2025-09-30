from django.contrib.auth import authenticate
from django.db import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import KnowledgeBaseEntry, QueryLog
from .serializers import (
    KnowledgeBaseEntrySerializer,
    AskRequestSerializer,
    AskResponseSerializer,
    SearchResponseSerializer,
    AuthRequestSerializer,
)
from .services import rag_service


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health(request):
    """Simple health check endpoint."""
    return Response({"message": "Server is up!"})


class AuthView(APIView):
    """Authenticate a user and return JWT tokens."""

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id="auth_login",
        operation_summary="Authenticate and obtain JWT tokens",
        operation_description="Authenticate a user with username and password. Returns access and refresh tokens.",
        request_body=AuthRequestSerializer,
        responses={200: openapi.Response("Tokens", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access": openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
            }
        ))},
        tags=["auth"],
    )
    # PUBLIC_INTERFACE
    def post(self, request):
        """Authenticate a user and return JWT tokens."""
        serializer = AuthRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)})


class AskView(APIView):
    """Handle user questions using RAG pipeline."""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id="ask_question",
        operation_summary="Ask a question",
        operation_description="Submit a question to the AI FAQ bot. The backend uses RAG to retrieve relevant knowledge and compose an answer.",
        request_body=AskRequestSerializer,
        responses={200: AskResponseSerializer},
        tags=["qa"],
    )
    # PUBLIC_INTERFACE
    def post(self, request):
        """Answer a question using RAG."""
        req_ser = AskRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)
        question = req_ser.validated_data["question"]

        try:
            answer, contexts, latency_ms = rag_service.ask(question)
            qlog = QueryLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                question=question,
                retrieved_context_ids=[c["id"] for c in contexts],
                answer=answer,
                latency_ms=latency_ms,
                status="ok",
            )
            resp = AskResponseSerializer({
                "answer": answer,
                "contexts": contexts,
                "latency_ms": latency_ms,
                "query_id": qlog.id,
            })
            return Response(resp.data)
        except Exception as exc:
            qlog = QueryLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                question=question,
                retrieved_context_ids=[],
                answer="",
                latency_ms=0,
                status="error",
                error=str(exc),
            )
            return Response({"detail": "Failed to generate answer", "query_id": qlog.id}, status=500)


class SearchView(APIView):
    """Search knowledge base entries."""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id="search_kb",
        operation_summary="Search knowledge base",
        operation_description="Full-text like search over titles, questions, and answers.",
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search query string", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('limit', openapi.IN_QUERY, description="Max results", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={200: SearchResponseSerializer},
        tags=["search"],
    )
    # PUBLIC_INTERFACE
    def get(self, request):
        """Search KB for matching entries."""
        query = request.query_params.get("query", "").strip()
        limit = int(request.query_params.get("limit", "10"))
        if not query:
            return Response({"results": []})
        qs = KnowledgeBaseEntry.objects.filter(is_active=True).filter(
            models.Q(title__icontains=query) |
            models.Q(question__icontains=query) |
            models.Q(answer__icontains=query)
        ).order_by('-updated_at')[:limit]
        data = KnowledgeBaseEntrySerializer(qs, many=True).data
        return Response({"results": data})


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """CRUD for Knowledge Base entries. Auth required for write operations."""
    queryset = KnowledgeBaseEntry.objects.all().order_by('-updated_at')
    serializer_class = KnowledgeBaseEntrySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @swagger_auto_schema(
        operation_id="kb_refresh_index",
        operation_summary="Refresh RAG index",
        operation_description="Rebuild the in-memory vector index from current KB contents. Useful after bulk updates.",
        responses={200: openapi.Response("OK")},
        tags=["kb"],
    )
    @action(detail=False, methods=['post'], url_path='refresh-index', permission_classes=[permissions.IsAdminUser])
    # PUBLIC_INTERFACE
    def refresh_index(self, request):
        """Rebuild the RAG vector index."""
        rag_service.refresh_index()
        return Response({"status": "ok"})
