from django.db.models.signals import post_save
from django.dispatch import receiver

from riskassess_apps.businesses.models import Business

from .models import TimeoutQuestionnaire
from .utils import create_default_questions


@receiver(post_save, sender=Business)
def create_default_questionnaire(sender, instance, created, **kwargs):
    if created:
        questionnaire = TimeoutQuestionnaire.objects.create(
            name="Safety Timout",
            business=instance,
            business_name=instance.name,
            business_branch=instance.branch,
        )
        create_default_questions(questionnaire)