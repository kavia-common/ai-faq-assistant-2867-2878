from rest_framework import serializers
from .models import KnowledgeBaseEntry


class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    """Serializer for KnowledgeBaseEntry model."""
    class Meta:
        model = KnowledgeBaseEntry
        fields = ['id', 'title', 'question', 'answer', 'tags', 'source', 'metadata', 'is_active', 'created_at', 'updated_at']


class AskRequestSerializer(serializers.Serializer):
    """Request payload for the ask endpoint."""
    question = serializers.CharField(max_length=5000, help_text="User's question to the AI FAQ bot")


class AskResponseSerializer(serializers.Serializer):
    """Response payload for the ask endpoint."""
    answer = serializers.CharField()
    contexts = serializers.ListField(child=serializers.DictField(), help_text="Retrieved related KB snippets")
    latency_ms = serializers.IntegerField()
    query_id = serializers.IntegerField(help_text="Query log ID for traceability")


class SearchResponseSerializer(serializers.Serializer):
    """Response schema for search endpoint."""
    results = KnowledgeBaseEntrySerializer(many=True)


class AuthRequestSerializer(serializers.Serializer):
    """Request schema for authentication endpoint."""
    username = serializers.CharField()
    password = serializers.CharField()
