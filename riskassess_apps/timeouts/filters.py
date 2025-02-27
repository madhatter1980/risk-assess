import django_filters

from django.db.models import Q

from .models import Timeout, TimeoutQuestionnaire


class TimeoutFilter(django_filters.FilterSet):
    name_search = django_filters.CharFilter(method='filter_by_all_names', label='Name Contains')
    warning = django_filters.ChoiceFilter(
        field_name='warning',
        label="Hazards and Controls Adequate",
        choices=[
            ('', '---------'),  # Blank option
            (False, 'Adequate'),
            (True, 'Not Adequate'),
        ]
    )

    class Meta:
        model = Timeout
        fields = {
            "questionnaire": ["exact"],
            "warning": ["exact"],
        }
        labels = {
            "warning": "Warning",
        }

    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.filters['questionnaire'].queryset = TimeoutQuestionnaire.objects.filter(business=business)

    def filter_by_all_names(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )