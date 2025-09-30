from django.db import models
from django.contrib.auth import get_user_model


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class KnowledgeBaseEntry(TimeStampedModel):
    """Represents a Q/A or document snippet in the knowledge base used by RAG."""
    title = models.CharField(max_length=255, db_index=True)
    question = models.TextField(blank=True, default="")
    answer = models.TextField()
    tags = models.JSONField(blank=True, default=list)
    source = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(blank=True, default=dict)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['title']),
        ]
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return self.title or f"KB Entry {self.id}"


class QueryLog(TimeStampedModel):
    """Stores user questions, selected contexts and generated answers for analytics and debugging."""
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    question = models.TextField()
    retrieved_context_ids = models.JSONField(blank=True, default=list)
    answer = models.TextField(blank=True, default="")
    latency_ms = models.IntegerField(default=0)
    status = models.CharField(max_length=32, default="ok")  # ok|error
    error = models.TextField(blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"QueryLog({self.id})"
