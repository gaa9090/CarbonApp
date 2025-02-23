from django import forms
from .models import Csv, Report, Tracker

class ChartSearch(forms.Form):
    CHART_TYPES = (('#1', 'Pie Chart'),('#2', 'Bar Chart'),('#3', 'Line Chart'),)
    RESULT_TYPES = (('#1', 'Year'), ('#2', 'Category'),)
    chart_type = forms.ChoiceField(choices=CHART_TYPES, required=False)
    result_by = forms.ChoiceField(choices=RESULT_TYPES)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        chart_type_value = self.data.get('chart_type') if self.data else self.initial.get('chart_type')
        if chart_type_value == '#3':
            self.fields['result_by'].initial = '#1'

    def clean(self):
        cleaned_data = super().clean()

        # If 'Line Chart' is selected, ensure result_by is set to 'Date'
        if cleaned_data.get('chart_type') == '#3':  # If it's Line Chart
            cleaned_data['result_by'] = '#1'  # Ensure it's set to 'Date'
        
        return cleaned_data
        

    
class CsvUploadForm(forms.ModelForm):
    class Meta:
        model = Csv
        fields = [
            'file_name',
        ]
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'title',
            'description',

        ]


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = [
            'title',
            'description',
            'start_year',
            'go_up_to_year',
        ]