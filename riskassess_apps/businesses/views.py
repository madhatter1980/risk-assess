from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Business, BusinessUser
from .forms import BusinessForm
from .serializers import BusinessUserSerializer

User = get_user_model()


@login_required
def add_business(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save()
            business.save()
            BusinessUser.objects.create(user=request.user, business=business, is_admin=True, invite_accepted=True)
            messages.success(
                request,
                f"Business {business} created successfully.",
            )
            return redirect('business_profile')
    else:
        form = BusinessForm()
    return render(request, 'businesses/add_business.html', {'form': form})


@login_required
def update_business(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    business_user = get_object_or_404(BusinessUser, user=request.user, business=business)

    if not business_user.is_admin:
        messages.error(request, "You do not have permission to go there.")
        return redirect('business_profile')

    if request.method == 'POST':
        form = BusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Business {business} updated successfully.",
            )
            return redirect('business_profile')
    else:
        form = BusinessForm(instance=business)
    return render(request, 'businesses/add_business.html', {'form': form})


@login_required
def business_profile(request):
    user = request.user

    # Fetch business user and related data if exists
    business_user = BusinessUser.objects.filter(user=user).select_related('business').first()

    # Extract business and member count if a business user exists
    business = business_user.business if business_user else None
    members = (
        BusinessUser.objects.filter(business=business).count() if business else 0
    )

    context = {
        "business_user": business_user,
        "business": business,
        "members": members,
    }

    return render(request, "businesses/business_profile.html", context)


@login_required
def business_users(request):
    user = request.user

    # Fetch the business user and related business in a single query
    business_user = BusinessUser.objects.filter(user=user).select_related('business').first()

    if not business_user.is_admin:
        messages.error(request, "You do not have permission to go there.")
        return redirect('user_profile')

    # Extract business
    business = business_user.business if business_user else None

    context = {
        "business_user": business_user,
        "business": business,
    }

    return render(request, 'businesses/business_users.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_business_users(request):
    user = request.user
    business_user = BusinessUser.objects.filter(user=user).select_related('business').first()
    
    if not business_user.is_admin:
        messages.error(request, "You do not have permission to go there.")
        return redirect('user_profile')

    business = business_user.business if business_user else None
    members = BusinessUser.objects.filter(business=business).exclude(user=user) if business else []

    serializer = BusinessUserSerializer(members, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def business_user_toggle_admin(request, user_id):
    current_user = request.user
    current_business_user = BusinessUser.objects.filter(user=current_user).select_related('business').first()
    
    if not current_business_user.is_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('user_profile')

    user = get_object_or_404(User, id=user_id)
    business_user = BusinessUser.objects.filter(user=user).first()

    if business_user.business != current_business_user.business:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('user_profile')

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        business_user.is_admin = not business_user.is_admin
        business_user.save()
        return Response({'success': True}, status=status.HTTP_200_OK)
    return Response({'success': False, 'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business_user(request, user_id):
    user = request.user
    business_user = BusinessUser.objects.filter(user=user).select_related('business').first()
    
    if not business_user.is_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('user_profile')

    # Get the business user to be deleted
    user_to_delete = get_object_or_404(BusinessUser, user_id=user_id)

    # Check if the business user belongs to the same business
    if user_to_delete.business != business_user.business:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('user_profile')

    # Delete the business user
    user_to_delete.delete()

    # Also delete the associated User
    user_to_delete.user.delete()

    # Return the message in the JSON response
    return Response(
        {"success": True, "message": "User deleted successfully."},
        status=status.HTTP_200_OK,
    )
