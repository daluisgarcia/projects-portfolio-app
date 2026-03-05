from datetime import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Technology(models.Model):
    # class TechnologyType(models.TextChoices):
    #     LANGUAGE = 'Language', 'Language'
    #     FRAMEWORK = 'Framework', 'Framework'

    name = models.CharField(max_length=100)
    date_experience_began = models.DateField()
    icon_name = models.CharField(max_length=50)
    tech_domain = models.IntegerField(
        default = 1,
        validators=[MaxValueValidator(100), MinValueValidator(1)]
    )
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(
        default = 1,
        validators=[MaxValueValidator(100), MinValueValidator(1)
    ])
    # type = models.CharField(
    #     max_length=12,
    #     choices=TechnologyType.choices,
    #     default=TechnologyType.LANGUAGE,
    # )

    base_tech = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def time_of_experience(self) -> str:
        years_difference = datetime.now().year - self.date_experience_began.year
        
        if years_difference == 0:
            return '<1 year'

        return f'+{years_difference} years'


def validate_is_image(file):
    import os
    from django.core.exceptions import ValidationError
    valid_file_extensions = ['.jpg', '.gif', '.png', '.jpeg', '.svg']
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_file_extensions:
        raise ValidationError('The file must be an image.')


class MediaFile(models.Model):
    file = models.FileField(upload_to='mediafiles', validators=[validate_is_image])

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='media_files')


class DevelopmentMethodology(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class ProjectField(models.Model):
    name = models.CharField(max_length=60)
    icon_name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Project(models.Model):
    class ProjectPurpose(models.TextChoices):
        PERSONAL = 'Personal', 'Personal'
        PROFESSIONAL = 'Professional', 'Professional'

    name = models.CharField(max_length=100)
    description = models.TextField()
    year_of_realization = models.IntegerField()
    time_invested = models.CharField(max_length=50)
    project_link = models.CharField(max_length=100, blank=True)
    github_link = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    purpose = models.CharField(
        max_length=12,
        choices=ProjectPurpose.choices,
        default=ProjectPurpose.PERSONAL,
    )
    priority = models.IntegerField(
        default = 1,
        validators=[MaxValueValidator(100), MinValueValidator(1)]
    )
    pinned = models.BooleanField(default=False)

    tech_fields = models.ManyToManyField(ProjectField, related_name='projects')
    technologies = models.ManyToManyField(Technology, related_name='projects')
    methodology_used = models.ForeignKey(DevelopmentMethodology, on_delete=models.SET_NULL, related_name='projects', null=True)

    def __str__(self):
        return self.name

    def methodology(self) -> str:
        if not self.methodology_used:
            return 'N/A'
        
        return self.methodology_used.name
