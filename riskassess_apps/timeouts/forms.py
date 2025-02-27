from django import forms
from .models import TimeoutQuestionnaire, TimeoutQuestion, TimeoutAnswer


class TimeoutQuestionnaireForm(forms.ModelForm):
    class Meta:
        model = TimeoutQuestionnaire
        fields = ["name", "description", "haz_control_lines"]
        labels = {
            "haz_control_lines": "Hazard/Control Lines",
        }

    # Custom validation for hazard lines number, if needed
    def clean_haz_control_lines(self):
        haz_control_lines = self.cleaned_data.get("haz_control_lines")
        if haz_control_lines is not None and haz_control_lines < 0:
            raise forms.ValidationError("Hazard number must be a positive number.")
        return haz_control_lines


class TimeoutQuestionForm(forms.ModelForm):
    class Meta:
        model = TimeoutQuestion
        fields = ["order", "question_text", "question_type", "preferred_answer"]

    # You can add additional validation if needed, for example:
    def clean_order(self):
        order = self.cleaned_data.get("order")
        if order <= 0:
            raise forms.ValidationError("Order must be a positive number.")
        return order
