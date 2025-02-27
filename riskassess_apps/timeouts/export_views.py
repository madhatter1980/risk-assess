import csv
import pandas as pd
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Timeout, BusinessUser
from .filters import TimeoutFilter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from django.contrib.staticfiles import finders


@login_required
def export_timeouts_csv(request):
    user = request.user
    business_user = get_object_or_404(BusinessUser, user=request.user)
    business = business_user.business
    timeouts = Timeout.objects.filter(business=business).order_by("-created_at")

    # Apply filters based on request parameters
    timeout_filter = TimeoutFilter(request.GET, queryset=timeouts, business=business)
    timeouts = timeout_filter.qs

    response = HttpResponse(content_type='text/csv')
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="{current_datetime}_timeouts.csv"'

    writer = csv.writer(response)

    # Write business details
    writer.writerow(['Business Name:', business.name])
    writer.writerow(['Business Branch:', business.branch])
    writer.writerow(['Business Address:', business.address])
    writer.writerow(['Business City:', business.city])
    writer.writerow(['Business State:', business.state])
    writer.writerow(['Business Postcode:', business.postcode])
    writer.writerow(['Business Phone:', business.phone])
    writer.writerow([])  # Empty row for separation
    writer.writerow(['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])  # Empty row for separation
    writer.writerow([])  # Empty row for separation

    # Table Headers
    writer.writerow([
        'Timeout', 'Task', 'Location', 'Submitted By', 'Date Submitted', 
        'Controls & Hazards Adequate'
    ])

    # Write data rows
    for timeout in timeouts:
        hazards_adequate = "No" if timeout.warning else "Yes"
        writer.writerow([
            timeout.questionnaire_name, timeout.task, timeout.location, 
            f"{timeout.first_name} {timeout.last_name}", 
            timeout.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
            hazards_adequate
        ])

    return response


# @login_required
# def export_timeouts_xlsx(request):
#     user = request.user
#     business_user = get_object_or_404(BusinessUser, user=request.user)
#     business = business_user.business
#     timeouts = Timeout.objects.filter(business=business).order_by("-created_at")

#     # Apply filters based on request parameters
#     timeout_filter = TimeoutFilter(request.GET, queryset=timeouts, business=business)
#     timeouts = timeout_filter.qs

#     # Prepare data for the DataFrame
#     data = []
#     for timeout in timeouts:
#         hazards_adequate = "No" if timeout.warning else "Yes"
#         data.append([
#             timeout.questionnaire_name, timeout.task, timeout.location, 
#             f"{timeout.first_name} {timeout.last_name}", 
#             timeout.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
#             hazards_adequate
#         ])

#     # Create a DataFrame
#     df = pd.DataFrame(data, columns=['Questionnaire Name', 'Task', 'Location', 'User', 'Created At', 'Hazards Adequate'])

#     # Create a response object and set the appropriate headers
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#     response['Content-Disposition'] = f'attachment; filename="{current_datetime}_timeouts.xlsx"'

#     # Use pandas to write the DataFrame to the response
#     with pd.ExcelWriter(response, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Timeouts')

#     return response

@login_required
def export_timeouts_xlsx(request):
    user = request.user
    business_user = get_object_or_404(BusinessUser, user=request.user)
    business = business_user.business
    timeouts = Timeout.objects.filter(business=business).order_by("-created_at")

    # Apply filters based on request parameters
    timeout_filter = TimeoutFilter(request.GET, queryset=timeouts, business=business)
    timeouts = timeout_filter.qs

    # Prepare data for the DataFrame
    data = []
    for timeout in timeouts:
        hazards_adequate = "No" if timeout.warning else "Yes"
        data.append([
            timeout.questionnaire_name, timeout.task, timeout.location, 
            f"{timeout.first_name} {timeout.last_name}", 
            timeout.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
            hazards_adequate
        ])

    # Create a DataFrame for the timeouts data
    df_timeouts = pd.DataFrame(data, columns=['Questionnaire Name', 'Task', 'Location', 'User', 'Created At', 'Hazards Adequate'])

    # Create a DataFrame for the business details
    business_details = [
        ['Business Name:', business.name],
        ['Business Branch:', business.branch],
        ['Business Address:', business.address],
        ['Business City:', business.city],
        ['Business State:', business.state],
        ['Business Postcode:', business.postcode],
        ['Business Phone:', business.phone],
        [],
        ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        [],
        []
    ]
    df_business = pd.DataFrame(business_details)

    # Create a response object and set the appropriate headers
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="{current_datetime}_timeouts.xlsx"'

    # Use pandas to write the DataFrames to the response
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_business.to_excel(writer, index=False, header=False, sheet_name='Timeouts')
        df_timeouts.to_excel(writer, index=False, sheet_name='Timeouts', startrow=len(df_business) + 2)

    return response


@login_required
def export_timeouts_pdf(request):
    user = request.user
    business_user = get_object_or_404(BusinessUser, user=request.user)
    business = business_user.business
    timeouts = Timeout.objects.filter(business=business).order_by("-created_at")

    # Apply filters based on request parameters
    timeout_filter = TimeoutFilter(request.GET, queryset=timeouts, business=business)
    timeouts = timeout_filter.qs

    response = HttpResponse(content_type='application/pdf')
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response['Content-Disposition'] = f'attachment; filename="Timeouts_Report_{current_datetime}.pdf"'

    # Create the PDF object
    p = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    # **Header Section**
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 50, "Timeouts Report")

    p.setFont("Helvetica", 11)
    p.drawString(50, height - 80, f"Business Name: {business.name}")
    p.drawString(50, height - 100, f"Branch: {business.branch}")
    p.drawString(50, height - 120, f"Address: {business.address}, {business.city}, {business.state} {business.postcode}")

    # **Add "Risk-Assess.com.au" Above Logo**
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 160, height - 50, "Risk-Assess.com.au")

    # **Add Logo**
    image_path = finders.find('images/logo_large.png')
    if image_path:
        p.drawImage(image_path, width - 140, height - 140, width=80, height=80)  # Adjusted position below the text
    else:
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(width - 140, height - 150, "Logo not found")

    # **Report Date**
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 150, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # **Applied Filters Section**
    y = height - 170
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Filters Applied:")

    p.setFont("Helvetica", 10)
    y -= 20

    filter_values = [f"{key.replace('_', ' ').title()}: {value}" for key, value in request.GET.items() if value]

    if filter_values:
        for filter_text in filter_values:
            p.drawString(70, y, filter_text)
            y -= 15
    else:
        p.drawString(70, y, "No filters applied.")

    # **Table Headers**
    y -= 30
    p.setFont("Helvetica-Bold", 10)

    col_positions = [50, 180, 310, 440, 570, 700]  # Adjusted to fit within landscape A4 width

    headers = [
        "Timeout", 
        "Task", 
        "Location", 
        "Submitted By", 
        "Date Submitted", 
        "Controls &\nHazards Adequate"  # Wrap header text
    ]

    # Calculate the maximum number of lines in headers for vertical alignment
    max_lines = max(len(header.split("\n")) for header in headers)

    for i, header in enumerate(headers):
        lines = header.split("\n")
        total_height = len(lines) * 12
        start_y = y - ((max_lines * 12 - total_height) // 2)  # Center align vertically

        for j, line in enumerate(lines):
            p.drawString(col_positions[i], start_y - (j * 12), line)

    # **Table Data**
    p.setFont("Helvetica", 9)
    y -= 30
    row_height = 18

    for timeout in timeouts:
        if y < 40:
            p.showPage()
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, height - 50, "Timeouts Report (Continued)")
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, height - 150, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            p.drawString(50, height - 170, "Filters Applied:")
            y = height - 200

            p.setFont("Helvetica-Bold", 10)
            for i, header in enumerate(headers):
                lines = header.split("\n")
                for j, line in enumerate(lines):
                    p.drawString(col_positions[i], y - (j * 12), line)

            y -= 25

        hazards_adequate = "No" if timeout.warning else "Yes"

        data = [
            timeout.questionnaire_name[:15],  
            timeout.task[:15],  
            timeout.location[:15],  
            f"{timeout.first_name} {timeout.last_name}"[:15],  
            timeout.created_at.strftime('%Y-%m-%d'),  
            hazards_adequate  
        ]

        for i, value in enumerate(data):
            p.drawString(col_positions[i], y, value)

        y -= row_height

    # **Footer**
    p.setFont("Helvetica", 8)
    p.drawString(50, 30, "Report provided by Risk-Assess.com.au")
    p.drawString(50, 20, "© 2025 Risk-Assess Pty Ltd. All rights reserved.")
    p.drawString(50, 10, "This report is generated for informational purposes only. Risk-Assess.com.au assumes no liability for decisions made based on this report.")

    # Close the PDF object
    p.showPage()
    p.save()

    return response