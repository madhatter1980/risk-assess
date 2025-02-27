from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from riskassess_apps.businesses.models import Business, BusinessUser


class TimeoutQuestionnaire(models.Model):
    # This model is used as a container for the questions and is linked to the business model
    name = models.CharField(max_length=255, default="Safety Timeout")
    description = models.CharField(max_length=255, default="Default Timeout Questions")
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True)
    business_name = models.CharField(max_length=255)
    business_branch = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    haz_control_lines = models.IntegerField(default=3)

    def __str__(self):
        return self.name


class TimeoutQuestion(models.Model):
    # This model is used to store the questions for the questionnaire
    QUESTION_TYPES = [
        ("YN", "Yes/No"),
        ("TX", "Text"),
    ]
    ANSWER_CHOICES = [
        ("YES", "Yes"),
        ("NO", "No"),
        ("N/A", "Not Applicable"),
    ]
    questionnaire = models.ForeignKey(
        TimeoutQuestionnaire, related_name="timeoutquestions", on_delete=models.CASCADE
    )
    order = models.IntegerField(default=1)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)
    preferred_answer = models.CharField(max_length=255, choices=ANSWER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]


class Timeout(models.Model):
    # This model is used as a header to store the timeoutanswers and also the timeouthazards
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True)
    business_name = models.CharField(max_length=255)
    business_branch = models.CharField(max_length=255)
    questionnaire = models.ForeignKey(TimeoutQuestionnaire, on_delete=models.SET_NULL, null=True, blank=True)
    questionnaire_name = models.CharField(max_length=255)
    task = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    warning = models.BooleanField(default=False)


class TimeoutAnswer(models.Model):
    # This model is used to store the answers to the questions
    timeout = models.ForeignKey(Timeout, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    preferred_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class TimeoutHazard(models.Model):
    # This model is used to store the answers to the questions
    timeout = models.ForeignKey(Timeout, on_delete=models.CASCADE)
    hazard = models.CharField(max_length=255)
    control = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
