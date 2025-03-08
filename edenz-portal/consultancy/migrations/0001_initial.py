# Generated by Django 5.1.5 on 2025-02-02 13:06

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('BUSINESS', 'Consultancy Business'), ('PROCESSING', 'Processing Team'), ('ADMIN', 'System Admin'), ('STUDENT', 'Student')], default='BUSINESS', max_length=20)),
                ('approved', models.BooleanField(default=False)),
                ('is_student', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BusinessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('license_number', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('phone_number', models.CharField(max_length=20)),
                ('website', models.URLField(blank=True)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_of_applicant', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('program_of_interest', models.CharField(max_length=200)),
                ('application_date', models.DateTimeField(auto_now_add=True)),
                ('father_name', models.CharField(blank=True, max_length=255)),
                ('student_cnic', models.CharField(blank=True, max_length=15)),
                ('fathers_occupation', models.CharField(blank=True, max_length=100)),
                ('fathers_cnic', models.CharField(blank=True, max_length=15)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('contact_no', models.CharField(blank=True, max_length=20)),
                ('passport_no', models.CharField(blank=True, max_length=50)),
                ('name_of_country', models.CharField(blank=True, max_length=100)),
                ('address', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('PASSPORT', 'Passport'), ('ID_CARD', 'National ID Card'), ('MATRIC', 'Matric/O-Level Certificate'), ('FSC', 'FSC/A-Level Certificate'), ('DAE', 'DAE Certificate'), ('BACH_DEGREE', "Bachelor's Degree"), ('BACH_TRANSCRIPT', "Bachelor's Transcript"), ('MASTER_DEGREE', "Master's/MPhil Degree"), ('MASTER_TRANSCRIPT', "Master's/MPhil Transcript"), ('LOR', 'Letter of Recommendation'), ('SOP', 'Statement of Purpose'), ('EXP_CERT', 'Experience Certificate'), ('MEDICAL', 'Medical Certificate'), ('CV', 'CV/Resume'), ('PROJECTS', 'Soft Copies of Projects'), ('PUBLICATIONS', 'International Publications')], max_length=20)),
                ('file', models.FileField(upload_to='student_docs/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='consultancy.student')),
            ],
        ),
    ]
