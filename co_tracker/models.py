from django.db import models
from profiles.models import Profile
from django.urls import reverse
from django.core.validators import FileExtensionValidator


class TrackerManager(models.Manager):
    def get_all_tracker(self, profile):
        return self.filter(profile=profile)


class Tracker(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE) 
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = TrackerManager()
    start_year = models.PositiveIntegerField()
    go_up_to_year = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.title)
    
    # Get all the spending on the Budget
    def get_co_count(self):
        return self.co_tracker_set.all().count()
    
    class Meta:
        ordering = ('-pk',)
    

class Category(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE) 
    title = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_delete_url(self):
        return reverse('tracker:delete-tracker', kwargs={'pk':self.pk})
    
    def get_add_report_url(self):
        # path('add-report/<int:pk>/', add_report, name='add-report')
        return reverse('tracker/add-report',kwargs={'pk':self.pk})

    

class Csv(models.Model):
    file_name = models.FileField(upload_to="csvFiles", validators=[FileExtensionValidator( ['csv'] ) ])
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.file_name)


class CoManager(models.Manager):
    def get_all_co(self, tracker):
        return self.filter(tracker=tracker)

class Co_Tracker(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE, default="Other")
    amount = models.FloatField()
    is_new = models.BooleanField(default=False)
    year = models.IntegerField(null=True, blank=True)
    objects = CoManager()
    
    def __str__(self):
        return str(self.amount)
    

class Report(models.Model):
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, default='Enter what you learned')
    image = models.ImageField(upload_to="graph/image", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title






