from django import forms
from .models import FounderProfile
import pytz

class FounderProfileRegistrationForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=FounderProfile.INTEREST_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select your interests...',
            'multiple': 'multiple'
        }),
        help_text="Select your areas of expertise and interests"
    )
    
    looking_for = forms.MultipleChoiceField(
        choices=FounderProfile.LOOKING_FOR_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'What are you looking for?',
            'multiple': 'multiple'
        }),
        help_text="What kind of connections are you looking for?"
    )

    class Meta:
        model = FounderProfile
        fields = ['name', 'interests', 'looking_for']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
        }

    def clean_interests(self):
        interests = self.cleaned_data.get('interests', [])
        return list(interests)

    def clean_looking_for(self):
        looking_for = self.cleaned_data.get('looking_for', [])
        return list(looking_for)


class FounderProfileForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=FounderProfile.INTEREST_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select your interests...',
            'multiple': 'multiple'
        }),
        help_text="Select your areas of expertise and interests",
        required=False
    )
    
    looking_for = forms.MultipleChoiceField(
        choices=FounderProfile.LOOKING_FOR_CHOICES,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'What are you looking for?',
            'multiple': 'multiple'
        }),
        help_text="What kind of connections are you looking for?",
        required=False
    )

    languages_spoken = forms.MultipleChoiceField(
        choices=[('english', 'English'), ('spanish', 'Spanish'), ('chinese', 'Chinese'), ('hindi', 'Hindi'),
                ('french', 'French'), ('arabic', 'Arabic'), ('portuguese', 'Portuguese'), ('japanese', 'Japanese'),
                ('german', 'German'), ('korean', 'Korean')],
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False
    )

    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False
    )

    class Meta:
        model = FounderProfile
        fields = [
            'name', 'interests', 'looking_for', 'company_name', 'industry', 'stage',
            'website', 'linkedin', 'twitter', 'profile_picture',
            'country', 'city_region', 'timezone', 'languages_spoken',
            'gender', 'job_title', 'years_experience', 'has_exited',
            'revenue_stage', 'funding_stage', 'capital_raised',
            'company_size', 'business_model',
            'university', 'accelerator', 'is_vc_backed',
            'is_bootstrapped'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize all JSON field values from instance if editing
        if self.instance and self.instance.pk:
            json_fields = [
                'interests', 'looking_for', 'languages_spoken'
            ]
            for field in json_fields:
                if hasattr(self.instance, field):
                    self.fields[field].initial = getattr(self.instance, field) or []

        # Add help text for form fields
        help_texts = {
            'languages_spoken': 'Select all languages you speak',
            'interests': 'Select your areas of interest and expertise',
            'looking_for': 'What kind of connections are you looking for?',
            'timezone': 'Select your timezone for scheduling calls'
        }
        
        for field, help_text in help_texts.items():
            if field in self.fields:
                self.fields[field].help_text = help_text

    def clean_interests(self):
        interests = self.cleaned_data.get('interests', [])
        return list(interests)

    def clean_looking_for(self):
        looking_for = self.cleaned_data.get('looking_for', [])
        return list(looking_for)

    def clean_languages_spoken(self):
        languages = self.cleaned_data.get('languages_spoken', [])
        return list(languages)