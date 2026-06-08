from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Experience(models.Model):
    class AccentStyle(models.TextChoices):
        PRIMARY = 'PRIMARY', 'Primary'
        TERTIARY = 'TERTIARY', 'Tertiary'
        OUTLINE = 'OUTLINE', 'Outline'

    company = models.CharField(max_length=100)
    role_title = models.CharField(max_length=100)
    start_date = models.DateField()
    # null end_date renders as "Present" in the template
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    # priority is a quality/relevance signal (1-100, high = important)
    priority = models.IntegerField(
        default=50,
        validators=[MaxValueValidator(100), MinValueValidator(1)],
    )
    # display_order is a manual position override (low number first)
    display_order = models.PositiveIntegerField(default=100)
    # accent_style drives BOTH marker color and chip color via CSS class lookup
    accent_style = models.CharField(
        max_length=20,
        choices=AccentStyle.choices,
        default=AccentStyle.PRIMARY,
    )
    # M2M reuses projects.Technology as the single source of truth for skill names/icons
    skills = models.ManyToManyField(
        'projects.Technology',
        related_name='experiences',
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', '-priority', '-start_date')
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'

    # Used in admin list_display and template card heading
    def __str__(self):
        return f'{self.role_title} @ {self.company}'

    # Spec #81: reject end_date < start_date (called by full_clean() and ModelForm.is_valid())
    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})
