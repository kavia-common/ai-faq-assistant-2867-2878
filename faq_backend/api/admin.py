from django.contrib import admin
from .models import KnowledgeBaseEntry, QueryLog


@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "updated_at")
    list_filter = ("is_active", "tags")
    search_fields = ("title", "question", "answer", "source")
    ordering = ("-updated_at",)


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "latency_ms", "created_at")
    list_filter = ("status",)
    search_fields = ("question", "answer", "error")
    ordering = ("-created_at",)
