from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.

class FounderProfile(models.Model):
    INTEREST_CHOICES = [
        ('ai', 'Artificial Intelligence'),
        ('blockchain', 'Blockchain'),
        ('saas', 'SaaS'),
        ('marketplace', 'Marketplace'),
        ('mobile', 'Mobile Apps'),
        ('iot', 'Internet of Things'),
        ('data', 'Data Analytics'),
        ('security', 'Cybersecurity'),
        ('cloud', 'Cloud Computing'),
        ('social', 'Social Media'),
        ('gaming', 'Gaming'),
        ('ar_vr', 'AR/VR'),
        ('robotics', 'Robotics'),
        ('biotech', 'Biotech'),
        ('cleantech', 'CleanTech'),
    ]

    LOOKING_FOR_CHOICES = [
        ('networking', 'Networking'),
        ('cofounder', 'Co-founder'),
        ('mentorship', 'Mentorship'),
        ('hiring', 'Hiring'),
        ('investment', 'Investment'),
    ]

    JOB_CHOICES = [
        ('founder', 'Founder'),
        ('cto', 'CTO'),
        ('cmo', 'CMO'),
        ('ceo', 'CEO'),
        ('coo', 'COO'),
        ('product_manager', 'Product Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('sales', 'Sales'),
        ('marketing', 'Marketing'),
        ('operations', 'Operations'),
        ('other', 'Other'),
    ]

    # Required fields for sign-up
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='founder_profile')
    name = models.CharField(max_length=255, default='')
    interests = models.JSONField(help_text="Select your interests and expertise areas")
    looking_for = models.JSONField(help_text="What kind of connections are you looking for?")

    # Optional fields
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=20, choices=[
        ('tech', 'Technology'),
        ('health', 'Healthcare'),
        ('fintech', 'FinTech'),
        ('edtech', 'EdTech'),
        ('ecommerce', 'E-commerce'),
        ('other', 'Other'),
    ], blank=True)
    stage = models.CharField(max_length=20, choices=[
        ('idea', 'Idea Stage'),
        ('mvp', 'MVP'),
        ('early', 'Early Stage'),
        ('growth', 'Growth Stage'),
        ('scaling', 'Scaling'),
    ], blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    
    # Location Information
    country = models.CharField(max_length=100, blank=True)
    city_region = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    languages_spoken = models.JSONField(default=list, blank=True)
    
    # Personal Information
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-binary'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ], blank=True)
    job_title = models.CharField(max_length=50, choices=JOB_CHOICES, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    has_exited = models.BooleanField(default=False)
    
    # Company Information
    revenue_stage = models.CharField(max_length=20, choices=[
        ('pre_revenue', 'Pre-revenue'),
        ('1k_10k', '$1K-$10K MRR'),
        ('10k_50k', '$10K-$50K MRR'),
        ('50k_100k', '$50K-$100K MRR'),
        ('100k_plus', '$100K+ MRR'),
        ('profitable', 'Profitable'),
    ], blank=True)
    funding_stage = models.CharField(max_length=20, choices=[
        ('pre_seed', 'Pre-seed'),
        ('seed', 'Seed'),
        ('series_a', 'Series A'),
        ('series_b', 'Series B'),
        ('series_c', 'Series C'),
        ('series_d', 'Series D+'),
    ], blank=True)
    capital_raised = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    company_size = models.PositiveIntegerField(default=1, help_text="Number of employees")
    business_model = models.CharField(max_length=20, choices=[
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
        ('b2b2c', 'B2B2C'),
        ('c2c', 'C2C'),
        ('d2c', 'D2C'),
        ('other', 'Other'),
    ], blank=True)
    
    # Additional Information
    university = models.CharField(max_length=255, blank=True)
    accelerator = models.CharField(max_length=255, blank=True)
    is_vc_backed = models.BooleanField(default=False)
    is_bootstrapped = models.BooleanField(default=False)
    
    # Technical Information
    tech_stack = models.JSONField(default=list, blank=True)
    goals_next_6_months = models.TextField(blank=True)
    biggest_challenge = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.company_name}"

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Let's ensure the timezone is always present
        if not self.timezone:
            self.timezone = 'UTC'
        super().save(*args, **kwargs)
