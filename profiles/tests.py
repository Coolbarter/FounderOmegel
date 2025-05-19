from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import FounderProfile
from .forms import FounderProfileForm

User = get_user_model()

class FounderProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
    def test_founder_profile_creation(self):
        form_data = {
            'name': 'Test User',
            'interests': ['ai', 'blockchain'],
            'looking_for': ['networking', 'mentorship'],
            'languages_spoken': ['english', 'spanish'],
            'tech_stack': ['python', 'javascript'],
            'startup_values': ['innovation', 'growth'],
            'preferred_call_availability': ['morning', 'weekdays'],
            'company_name': 'Test Company',
            'industry': 'tech',
            'stage': 'mvp',
            'description': 'A test company',
            'website': 'https://example.com',
            'country': 'United States',
            'city_region': 'San Francisco',
            'timezone': 'UTC',
            'gender': 'prefer_not_to_say',
            'role': 'founder',
            'years_experience': 5,
            'preferred_call_duration': 30
        }
        
        response = self.client.post(reverse('profile_create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        
        # Verify profile was created with correct data
        profile = FounderProfile.objects.get(user=self.user)
        self.assertEqual(profile.name, 'Test User')
        self.assertEqual(set(profile.interests), {'ai', 'blockchain'})
        self.assertEqual(set(profile.looking_for), {'networking', 'mentorship'})
        self.assertEqual(set(profile.languages_spoken), {'english', 'spanish'})
        self.assertEqual(set(profile.tech_stack), {'python', 'javascript'})
        self.assertEqual(set(profile.startup_values), {'innovation', 'growth'})
        self.assertEqual(set(profile.preferred_call_availability), {'morning', 'weekdays'})
        
    def test_founder_profile_update(self):
        # First create a profile
        profile = FounderProfile.objects.create(
            user=self.user,
            name='Test User',
            company_name='Test Company'
        )
        
        update_data = {
            'name': 'Updated User',
            'interests': ['saas', 'mobile'],
            'looking_for': ['investment', 'cofounder'],
            'languages_spoken': ['english', 'french'],
            'tech_stack': ['react', 'nodejs'],
            'startup_values': ['customer_focus', 'quality'],
            'preferred_call_availability': ['afternoon', 'weekends'],
            'company_name': 'Updated Company',
            'industry': 'fintech',
            'stage': 'growth',
            'description': 'An updated company',
            'website': 'https://updated-example.com',
            'country': 'Canada',
            'city_region': 'Toronto',
            'timezone': 'America/Toronto',
            'gender': 'prefer_not_to_say',
            'role': 'ceo',
            'years_experience': 7,
            'preferred_call_duration': 45
        }
        
        response = self.client.post(reverse('profile_update'), data=update_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        
        # Verify profile was updated with correct data
        profile.refresh_from_db()
        self.assertEqual(profile.name, 'Updated User')
        self.assertEqual(set(profile.interests), {'saas', 'mobile'})
        self.assertEqual(set(profile.looking_for), {'investment', 'cofounder'})
        self.assertEqual(set(profile.languages_spoken), {'english', 'french'})
        self.assertEqual(set(profile.tech_stack), {'react', 'nodejs'})
        self.assertEqual(set(profile.startup_values), {'customer_focus', 'quality'})
        self.assertEqual(set(profile.preferred_call_availability), {'afternoon', 'weekends'})
        
    def test_invalid_form_submission(self):
        # Test with invalid data
        form_data = {
            'name': '',  # Name is required
            'interests': ['invalid_interest'],  # Invalid choice
            'looking_for': ['invalid_looking_for'],  # Invalid choice
        }
        
        response = self.client.post(reverse('profile_create'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Should stay on form page
        self.assertTrue('form' in response.context)  # Form should be in context
        self.assertTrue(response.context['form'].errors)  # Should have form errors
