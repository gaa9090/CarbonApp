from django.shortcuts import render, redirect, get_object_or_404
from .models import Tracker, Co_Tracker, Category, Csv, Report
from profiles.models import Profile
import pandas as pd
from .utils import get_name_from_id, get_plot, get_category_name_from_id, get_plot_image
from .forms import ChartSearch, CsvUploadForm, ReportForm, TrackerForm
import csv
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.

def all_tracker(request):
    profile = Profile.objects.get(user=request.user)
    tracker = Tracker.objects.get_all_tracker(profile)
    csv_form = CsvUploadForm()
    size = tracker.count()
    tracker_from = TrackerForm(request.POST or None)
    
    if request.method == "POST":
        if tracker_from.is_valid():
            instance = tracker_from.save(commit=False)
            instance.profile = profile
            instance.save()
            messages.success(request, f'Tracker created')
            return redirect('tracker:tracker')
    
    context = {
        'profile' : profile,
        'tracker' : tracker,
        'size' : size,
        "tracker_from" : tracker_from,
        "csv_form" : csv_form,
    }
    return render(request, "co_tracker/allTracker.html", context)

def upload_file(request, pk):
    profile = Profile.objects.get(user=request.user)
    # tracker = Tracker.objects.get_all_tracker(profile)
    # tracker = get_object_or_404(Tracker, profile, pk)
    tracker = get_object_or_404(Tracker, profile=profile, pk=pk)
    # csv_form = CsvUploadForm(request.FILES, request.POST)
    csv_form = CsvUploadForm(request.POST, request.FILES)
    if request.method == 'POST' or request.method == 'FILES':
        if csv_form.is_valid():
            csv_form.save()
            csv_obj = Csv.objects.get(active=False)
            with open(csv_obj.file_name.path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                reader.__next__()
                for row in reader:
                    year = int(row[0])
                    
                    title_category = row[1]
                    
                    main_category = Category.objects.filter(profile=profile, title=title_category)
                    
                    if not main_category.exists():
                        main_category = Category.objects.create(profile=profile, title=title_category)
                    else:
                        main_category = main_category.first() 
                    
                    total = row[2]
                    Co_Tracker.objects.create(tracker=tracker, category=main_category, amount=total, year=year)
                
                csv_obj.active = True
                csv_obj.save()
            return redirect('tracker:tracker')
        else:
            return redirect('tracker:tracker')
    
    


def delete_tracker(request, pk):
    profile = Profile.objects.get(user=request.user)
    tracker = get_object_or_404(Tracker, profile=profile, pk=pk)
    if tracker:
        tracker.delete()
        print("Delete tracker")
        return redirect('tracker:tracker')


# Co Tracking 
def analyse_csv(request, pk):
    graph = None
    chart_search = None
    report_form = None
    
    profile = Profile.objects.get(user=request.user)
    tracker = get_object_or_404(Tracker, profile=profile, pk=pk)
    all_co_data = Co_Tracker.objects.get_all_co(tracker=tracker).values()
    
    if(len(all_co_data) > 0):
        df = pd.DataFrame(all_co_data)
        df.drop('id',axis=1, inplace=True)
        df.rename({
            'tracker_id': 'Tracker Title',
            'amount': 'Amount',
            'year': 'Year',
            'category_id':'Category'
        },inplace=True, axis=1)
        df['Tracker Title'] = df['Tracker Title'].apply(get_name_from_id)
        df['Category'] = df['Category'].apply(get_category_name_from_id)
        # df['Date'] = df['Date'].apply(lambda x:x.strftime('%m-%d-%Y'))
        
        chart_search = ChartSearch(request.POST or None)
        report_form = ReportForm()
        if request.method == 'POST':
            chart_type = request.POST.get('chart_type')
            
            if chart_type != "#3":
                result_by = request.POST.get('result_by')
            else:
                result_by = "#1"
                
                
            graph = get_plot(chart_type, result_by, df)
        df.sort_values(by="Year",ascending=True, inplace=True)
        df = df.to_html(index=False)
    context = {
        "tracker":tracker,
        "all_co_data":all_co_data,
        'chart_search':chart_search,
        'graph':graph,
        "df" : df,
        "report_form" : report_form,
    }
    return render(request, 'co_tracker/_co/data_view.html', context)

# def upload_csv(request, pk):
#     profile = Profile.objects.get(user=request.user)
#     tracker = get_object_or_404(Tracker, profile=profile, pk=pk)
#     form = CsvUploadForm(request.POST or None, request.FILES or None)
#     if request.method == 'POST':
#         if form.is_valid():
#             form.save()
#             csv_obj = Csv.objects.get(active=False)
#             with open(csv_obj.file_name.path, 'r') as csv_file:
#                 reader = csv.reader(csv_file)
#                 reader.__next__()
#                 for row in reader:
#                     year = int(row[0])
                    
#                     title_category = row[1]
                    
#                     main_category = Category.objects.filter(profile=profile, title=title_category)
                    
#                     if not main_category.exists():
#                         main_category = Category.objects.create(profile=profile, title=title_category)
#                     else:
#                         main_category = main_category.first() 
                    
#                     total = row[2]
#                     Co_Tracker.objects.create(tracker=tracker, category=main_category, amount=total, year=year)
                
#                 csv_obj.active = True
#                 csv_obj.save()
#             return redirect('tracker:analyse', pk)
    
#     context = {
#         "form": form,
#         "tracker":tracker,

#     }


# def upload_csv(request):
#     # Get the profile
#     profile = Profile.objects.get(user=request.user)

#     # Ensure request is POST and it's an AJAX request
#     if request.method == 'POST':
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             form = CsvUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 # Save the form and process the CSV
#                 form.save()
#                 try:
#                     # Retrieve the most recently uploaded CSV file
#                     csv_obj = Csv.objects.get(active=False)
                    
#                     # Process the CSV file
#                     with open(csv_obj.file_name.path, 'r') as csv_file:
#                         reader = csv.reader(csv_file)
#                         next(reader)  # Skip header row
                        
#                         # Assuming 'tracker' is associated with the current user (e.g., you can link tracker via the profile)
#                         tracker = get_object_or_404(Tracker, profile=profile)

#                         for row in reader:
#                             year = int(row[0])
#                             title_category = row[1]
                            
#                             # Find or create a category for the user
#                             main_category = Category.objects.filter(profile=profile, title=title_category).first()
#                             if not main_category:
#                                 main_category = Category.objects.create(profile=profile, title=title_category)
                            
#                             # Create the tracker record
#                             total = row[2]
#                             Co_Tracker.objects.create(tracker=tracker, category=main_category, amount=total, year=year)
                    
#                     # Mark the CSV as active after processing
#                     csv_obj.active = True
#                     csv_obj.save()
                    
#                     return JsonResponse({
#                         'success': True,
#                         'message': 'CSV file uploaded and processed successfully.'
#                     })
                
#                 except Csv.DoesNotExist:
#                     return JsonResponse({
#                         'success': False,
#                         'error': 'No active CSV file found.'
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'error': f'Error processing CSV file: {str(e)}'
#                     })
            
#             # If the form is invalid, return an error
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Form is invalid.'
#             })
#     else:
#         return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid request. Hit last cast'
#             })



# def upload_csv(request):
#     # Get the profile associated with the current user
#     try:
#         profile = Profile.objects.get(user=request.user)
#     except Profile.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Profile not found for the user.'})
#     print("HIT --- HIT")
#     # Ensure request is POST and it's an AJAX request
#     if request.method == 'POST':
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check for AJAX request
#             form = CsvUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 try:
#                     # Save the form and retrieve the most recently uploaded CSV file
#                     form.save()
#                     csv_obj = Csv.objects.get(active=False)  # Get the inactive CSV

#                     # Process the CSV file
#                     with open(csv_obj.file_name.path, 'r') as csv_file:
#                         reader = csv.reader(csv_file)
#                         next(reader)  # Skip header row

#                         # Get the tracker associated with the profile
#                         tracker = get_object_or_404(Tracker, profile=profile)

#                         # Iterate over the CSV rows
#                         for row in reader:
#                             year = int(row[0])
#                             title_category = row[1]

#                             # Find or create a category for the user
#                             main_category = Category.objects.filter(profile=profile, title=title_category).first()
#                             if not main_category:
#                                 main_category = Category.objects.create(profile=profile, title=title_category)

#                             # Create a Co_Tracker record
#                             total = row[2]
#                             Co_Tracker.objects.create(tracker=tracker, category=main_category, amount=total, year=year)

#                     # Mark the CSV as active after processing
#                     csv_obj.active = True
#                     csv_obj.save()

#                     return JsonResponse({
#                         'success': True,
#                         'message': 'CSV file uploaded and processed successfully.'
#                     })

#                 except Csv.DoesNotExist:
#                     # If no active CSV file is found
#                     return JsonResponse({
#                         'success': False,
#                         'error': 'No active CSV file found.'
#                     })
#                 except Exception as e:
#                     # General exception handling
#                     return JsonResponse({
#                         'success': False,
#                         'error': f'Error processing CSV file: {str(e)}'
#                     })
#             else:
#                 # If the form is invalid, return an error response
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Form is invalid.'
#                 })

#         else:
#             # If the request is not an AJAX request, return an error response
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid request type. Only AJAX requests are allowed.'
#             })
#     else:
#         # If the request is not POST, return an error response
#         return JsonResponse({
#             'success': False,
#             'error': 'Invalid request method. POST required.'
#         })




# def upload_csv(request):
#     try:
#         profile = Profile.objects.get(user=request.user)
#     except Profile.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Profile not found for the user.'}, status=400)

#     print("HIT --- HIT")

#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = CsvUploadForm(request.POST, request.FILES)
        
#         if form.is_valid():
#             try:
#                 # Save the form and retrieve the most recently uploaded CSV file
#                 form.save()
#                 csv_obj = Csv.objects.get(active=False)

#                 # Process the CSV file
#                 with open(csv_obj.file_name.path, 'r') as csv_file:
#                     reader = csv.reader(csv_file)
#                     next(reader)  # Skip header row

#                     tracker = get_object_or_404(Tracker, profile=profile)

#                     for row in reader:
#                         year = int(row[0])
#                         title_category = row[1]

#                         main_category, created = Category.objects.get_or_create(
#                             profile=profile, title=title_category
#                         )

#                         total = row[2]
#                         Co_Tracker.objects.create(tracker=tracker, category=main_category, amount=total, year=year)

#                 csv_obj.active = True
#                 csv_obj.save()

#                 return JsonResponse({'success': True, 'message': 'CSV file uploaded and processed successfully.'})

#             except Csv.DoesNotExist:
#                 return JsonResponse({'success': False, 'error': 'No active CSV file found.'}, status=400)
#             except Exception as e:
#                 return JsonResponse({'success': False, 'error': f'Error processing CSV file: {str(e)}'}, status=500)
#         else:
#             return JsonResponse({'success': False, 'error': 'Form is invalid.'}, status=400)

#     return JsonResponse({'success': False, 'error': 'Invalid request type or method.'}, status=400)







def add_report(request):
    profile = Profile.objects.get(user=request.user)
    print("HIT ---- ME")
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            title = request.POST.get('title')
            description = request.POST.get('description')
            image = request.POST.get('image')
            the_image = get_plot_image(image)
            Report.objects.create(title=title, description=description, image=the_image, profile=profile)
            return JsonResponse({})
        return JsonResponse({})