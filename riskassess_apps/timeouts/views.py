from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone


from riskassess_apps.businesses.models import Business, BusinessUser
from .models import (
    TimeoutQuestionnaire,
    TimeoutQuestion,
    Timeout,
    TimeoutAnswer,
    TimeoutHazard,
)
from .filters import TimeoutFilter
from .forms import TimeoutQuestionnaireForm, TimeoutQuestionForm
from .serializers import TimeoutQuestionSerializer, TimeoutQuestionnaireSerializer

from .utils import create_default_questions


from django.db.models import Count, Q
from django.utils import timezone

@login_required
def questionnaires_list(request):
    business_user = BusinessUser.objects.filter(user=request.user).first()
    if business_user is None:
        return redirect('add_business')
    
    business = business_user.business
    
    current_date = timezone.now()

    questionnaires = TimeoutQuestionnaire.objects.filter(
        business=business_user.business
    ).annotate(
        user_submission_count_month=Count(
            'timeout',
            filter=Q(timeout__created_at__year=current_date.year) & 
                   Q(timeout__created_at__month=current_date.month) & 
                   Q(timeout__user=request.user)
        ),
        user_submission_count_year=Count(
            'timeout',
            filter=Q(timeout__created_at__year=current_date.year) & 
                   Q(timeout__user=request.user)
        ),
        submission_count_month=Count(
            'timeout',
            filter=Q(timeout__created_at__year=current_date.year) & 
                   Q(timeout__created_at__month=current_date.month)
        ),
        submission_count_year=Count(
            'timeout',
            filter=Q(timeout__created_at__year=current_date.year)
        )
    )

    context = {
        "business_user": business_user,
        "business": business,
        "questionnaires": questionnaires,
    }
    return render(request, "timeouts/questionnaires_list.html", context)


@login_required
def questionnaire_create(request):
    business_user = BusinessUser.objects.filter(user=request.user).first()

    if not business_user.is_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('questionnaires_list')
    
    if request.method == "POST":
        form = TimeoutQuestionnaireForm(request.POST)
        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.questionnaire_name = questionnaire.name
            questionnaire.business = business_user.business
            questionnaire.business_name = business_user.business.name
            questionnaire.business_branch = business_user.business.branch
            questionnaire.save()

            # Add default questions from utils.py
            create_default_questions(questionnaire)

            messages.success(
                request,
                f"Questionnaire created successfully.",
            )

            return redirect("questionnaires_list")
    else:
        form = TimeoutQuestionnaireForm()
    return render(request, "timeouts/questionnaire_create.html", {"form": form})


def questionnaire_delete(request, pk):
    questionnaire = get_object_or_404(TimeoutQuestionnaire, pk=pk)
    if request.method == 'POST':
        questionnaire.delete()
        messages.success(request, 'Questionnaire deleted successfully.')
        return redirect('questionnaires_list')
    return render(request, 'timeouts/questionnaire_delete.html', {'questionnaire': questionnaire})


@login_required
def questionnaire_detail(request, questionnaire_id):
    business_user = BusinessUser.objects.filter(user=request.user).first()

    if not business_user.is_admin:
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('questionnaires_list')

    questionnaire = (
        TimeoutQuestionnaire.objects.filter(
            business=business_user.business, id=questionnaire_id
        )
        .prefetch_related("timeoutquestions")
        .first()
    )

    context = {"questionnaire": questionnaire}
    return render(request, "timeouts/questionnaire_detail.html", context)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def timeout_questionnaire_form(request, questionnaire_id):
    questionnaire = get_object_or_404(TimeoutQuestionnaire, id=questionnaire_id)

    if request.method == "POST":
        # Use Django form to handle questionnaire data
        questionnaire_form = TimeoutQuestionnaireForm(
            request.POST, instance=questionnaire
        )

        if questionnaire_form.is_valid():
            # Save the updated questionnaire
            questionnaire_form.save()
        else:
            # If the form is not valid, return an error response
            return Response(
                {"error": questionnaire_form.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        # Collect new questions for the response
        questions_data = []

        try:
            # Use a transaction to ensure atomic updates
            with transaction.atomic():
                for key in request.POST:
                    if key.startswith("question_text_"):
                        index = key.split("_")[-1]
                        question_id = request.POST.get(f"question_id_{index}")
                        question_data = {
                            "order": request.POST.get(f"order_{index}"),
                            "question_text": request.POST.get(f"question_text_{index}"),
                            "question_type": request.POST.get(f"question_type_{index}"),
                            "preferred_answer": request.POST.get(f"preferred_answer_{index}"),
                        }

                        # Use the form to validate the input
                        form = TimeoutQuestionForm(question_data)
                        if form.is_valid():
                            cleaned_data = form.cleaned_data

                            if question_id:
                                # Update an existing question
                                question = TimeoutQuestion.objects.get(id=question_id)
                                question.order = cleaned_data["order"]
                                question.question_text = cleaned_data["question_text"]
                                question.question_type = cleaned_data["question_type"]
                                question.preferred_answer = cleaned_data["preferred_answer"]
                                question.save()
                            else:
                                # Create a new question
                                new_question = TimeoutQuestion.objects.create(
                                    questionnaire=questionnaire,
                                    order=cleaned_data["order"],
                                    question_text=cleaned_data["question_text"],
                                    question_type=cleaned_data["question_type"],
                                    preferred_answer=cleaned_data["preferred_answer"],
                                )
                                questions_data.append(new_question)
                        else:
                            # If the form is not valid, return an error response
                            return Response(
                                {"error": form.errors},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
            
            # Fetch and serialize the updated list of questions
            questions = TimeoutQuestion.objects.filter(
                questionnaire=questionnaire
            ).order_by("order")
            serializer = TimeoutQuestionSerializer(questions, many=True)
            return Response({"questions": serializer.data}, status=status.HTTP_200_OK)
        
        except TimeoutQuestion.DoesNotExist:
            return Response(
                {"error": "Question does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    else:
        # Handle GET request to fetch questionnaire details
        serializer = TimeoutQuestionnaireSerializer(questionnaire)
        return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    try:
        question = get_object_or_404(TimeoutQuestion, id=question_id)
        question.delete()
        return Response(
            {"message": "Question deleted successfully"}, status=status.HTTP_200_OK
        )
    except TimeoutQuestion.DoesNotExist:
        return Response(
            {"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND
        )


@login_required
def timeout_select(request):
    business_user = BusinessUser.objects.filter(user=request.user).first()
    if business_user is None:
        return redirect('add_business')

    questionnaires = TimeoutQuestionnaire.objects.filter(
        business=business_user.business
    )
    context = {"questionnaires": questionnaires}
    return render(request, "timeouts/questionnaire_select_timeout.html", context)


@login_required
def timeout_form(request, questionnaire_id):
    timeout_questionnaire = get_object_or_404(TimeoutQuestionnaire.objects.select_related('business'), id=questionnaire_id)
    timeout_questions = TimeoutQuestion.objects.filter(questionnaire=questionnaire_id).order_by("order")
    hazard_control_lines = range(timeout_questionnaire.haz_control_lines)

    if request.method == "POST":
        task = request.POST.get("task")
        location = request.POST.get("location")
        user = request.user
        first_name = user.first_name
        last_name = user.last_name
        business = timeout_questionnaire.business
        business_name = business.name
        business_branch = business.branch
        questionnaire_name = timeout_questionnaire.name + " - " + timeout_questionnaire.description
        warning = False

        # Create Timeout instance
        timeout_instance = Timeout.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            business=business,
            business_name=business_name,
            business_branch=business_branch,
            questionnaire=timeout_questionnaire,
            questionnaire_name=questionnaire_name,
            task=task,
            location=location,
            warning=warning,
        )

        timeout_answers = []
        timeout_hazards = []

        # Iterate through POST data
        for key, value in request.POST.items():
            # Process TimeoutAnswers
            if key.startswith("question_text_"):
                question_id = key.split("_")[-1]
                answer_text = request.POST.get(f"options-outlined-{question_id}", "") or request.POST.get(f"answer-{question_id}", "")
                preferred_answer = request.POST.get(f"preferred_answer_{question_id}", "")
                timeout_answers.append(TimeoutAnswer(timeout=timeout_instance, question=value, answer=answer_text, preferred_answer=preferred_answer))

                # Check if the answer_text is not equal to the preferred_answer, ignoring N/A
                if preferred_answer.lower() != "n/a" and answer_text.lower() != preferred_answer.lower():
                    warning = True

            # Process TimeoutHazards
            elif key.startswith("hazard_"):
                hazard_id = key.split("_")[-1]
                control_value = request.POST.get(f"control_{hazard_id}", "")
                if value or control_value:  # Ensure either value or control_value is not empty
                    timeout_hazards.append(TimeoutHazard(timeout=timeout_instance, hazard=value, control=control_value))

        # Update the flag on the Timeout instance
        timeout_instance.warning = warning
        timeout_instance.save()


        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Bulk create TimeoutAnswer and TimeoutHazard instances
            TimeoutAnswer.objects.bulk_create(timeout_answers)
            TimeoutHazard.objects.bulk_create(timeout_hazards)
        
        if warning == True:
            messages.error(
                request,
                "<strong>WARNING !</strong><br>"
                "Contact your <strong>Supervisor</strong> before Proceeding.<br>"
                "There are potential hazards or controls that need to be addressed.",
            )

        if warning == False:
            messages.success(
                request,
                "Timeout Submitted Successfully.",
            )

        return redirect("user_timeout_list")

    context = {
        "timeout_questionnaire": timeout_questionnaire,
        "timeout_questions": timeout_questions,
        "hazard_control_lines": hazard_control_lines,
    }

    return render(request, "timeouts/timeout_form.html", context)


@login_required
def user_timeout_list(request):
    user = request.user
    timeouts = Timeout.objects.filter(user=user).order_by("-created_at")[:10]

    context = {
        "user": user,
        "timeouts": timeouts
        }

    return render(request, "timeouts/user_timeout_list.html", context)


@login_required
def timeout_list(request):
    user = request.user
    business_user = get_object_or_404(BusinessUser, user=request.user)
    business = business_user.business
    timeouts = Timeout.objects.filter(business=business).order_by("-created_at")

    timeout_filter = TimeoutFilter(request.GET, queryset=timeouts, business=business)
    timeouts = timeout_filter.qs

    context = {
        "user": user,
        "business": business,
        "timeouts": timeouts,
        "filter": timeout_filter,
        }

    return render(request, "timeouts/timeout_list.html", context)


@login_required
def timeout_detail(request, timeout_id):
    timeout = get_object_or_404(Timeout, id=timeout_id)
    bunsiness_user = get_object_or_404(BusinessUser, user=request.user)

    # Check if the logged-in user is the owner of the timeout
    if timeout.user != request.user:
        # Check if the user is a business user admin
        if not bunsiness_user.is_admin:
            return redirect("home")
    
    timeout_answers = TimeoutAnswer.objects.filter(timeout=timeout)
    timeout_hazards = TimeoutHazard.objects.filter(timeout=timeout)

    context = {
        "timeout": timeout,
        "timeout_answers": timeout_answers,
        "timeout_hazards": timeout_hazards,
    }

    return render(request, "timeouts/timeout_detail.html", context)
