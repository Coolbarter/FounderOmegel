from django.db import migrations, models

def populate_name(apps, schema_editor):
    FounderProfile = apps.get_model('profiles', 'FounderProfile')
    for profile in FounderProfile.objects.all():
        if profile.user:
            profile.name = profile.user.email
            profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_founderprofile_accelerator_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='founderprofile',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=True,
        ),
        migrations.RunPython(populate_name, reverse_code=migrations.RunPython.noop),
    ] 