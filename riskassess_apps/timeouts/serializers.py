from rest_framework import serializers

from .models import TimeoutQuestion, TimeoutQuestionnaire


class TimeoutQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeoutQuestion
        fields = ["id", "order", "question_text", "question_type", "preferred_answer"]


class TimeoutQuestionnaireSerializer(serializers.ModelSerializer):
    questions = TimeoutQuestionSerializer(many=True, source="timeoutquestions")

    class Meta:
        model = TimeoutQuestionnaire
        fields = ["id", "name", "description", "haz_control_lines", "questions"]
