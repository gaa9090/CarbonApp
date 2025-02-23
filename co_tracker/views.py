from django.shortcuts import render, redirect, get_object_or_404
from .models import Tracker, Co_Tracker, Category, Csv, Report
from profiles.models import Profile
import pandas as pd
from .utils import get_name_from_id, get_plot, get_category_name_from_id, get_plot_image
from .forms import ChartSearch, CsvUploadForm, ReportForm, TrackerForm
import csv
from django.http import JsonResponse, HttpResponse
from django.contrib import messages

from django.template.loader import get_template
from xhtml2pdf import pisa

from django.db.models import Q

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
    
# Report Views 


# @login_required
# def view_report(request, slug ,pk):
#     profile = Profile.objects.get(user=request.user)
#     budget = get_object_or_404(Budget, slug=slug, user=profile)
#     report = get_object_or_404(Report, budget=budget, pk=pk)
#     context = {'budget': budget, 'report': report}
#     # return render(request, 'budget/report/report-detail.html', context)
#     return render(request, 'budget/report-detail.html', context)


# @login_required
def delete_report(request, pk):
    profile = Profile.objects.get(user=request.user)
    report = get_object_or_404(Report, profile=profile, pk=pk)
    if report:
        report.delete()
        messages.info(request, 'The Report has been delete successfully')
        return redirect('tracker:tracker')


def view_report(request ,pk):
    profile = Profile.objects.get(user=request.user)
    report = get_object_or_404(Report, profile=profile, pk=pk)
    context = {'report': report}
    # return render(request, 'budget/report/report-detail.html', context)
    return render(request, 'report/report-detail.html', context)



def render_pdf_view(request, pk):
    template_path = 'report/pdf-report.html'
    profile = Profile.objects.get(user=request.user)
    # budget = get_object_or_404(Budget, slug=slug, user=profile)
    report = get_object_or_404(Report, profile=profile, pk=pk)
    # context = {'budget': budget, 'report':report}
    context = {'report':report}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response




def all_report(request):
    query = None
    if request.method == 'POST':
        query = request.POST.get('q')
        lookup = Q(title__icontains=query)
        # lookup = Q(title__icontains=query)|Q(budget__name__icontains=query)|Q(budget__month__icontains=query)|Q(budget__monthly_budget__icontains=query)
        report = Report.objects.filter(lookup)
        report_count = report.count()
    else:
        report = Report.objects.all()
        report_count = report.count()
    
    context = {'report':report, 'report_count':report_count, 'query':query}
    return render(request, 'report/all-report.html', context)