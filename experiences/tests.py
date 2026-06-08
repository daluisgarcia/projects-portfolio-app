# tests.py — Smoke test suite for the experiences app.
#
# First test suite in this project. Uses plain django.test.TestCase
# (no pytest). Run with: .venv/bin/python manage.py test experiences
#
# Coverage maps to the testable scenarios in spec #81:
#   1. test_str                         — model __str__ format
#   2. test_url_resolves                — /experiences/ route wired
#   3. test_view_returns_200            — view responds OK
#   4. test_view_uses_base_template     — template extends base.html
#   5. test_view_sets_active_page       — nav highlight context var
#   6. test_inactive_excluded           — is_active filter in queryset
#   7. test_ordering_respected          — display_order, -priority, -start_date
#
# Edge-case scenarios from spec #81 (end_date < start_date validation,
# priority boundary values, en-dash exact character in template) are
# covered by manual code review and the in-batch clean() smoke test,
# not by automated tests, to keep this first suite small and fast.

from django.test import TestCase
from django.urls import resolve, reverse

from experiences.models import Experience
from experiences.views import ExperienceListView
from projects.models import Technology


class ExperienceModelTests(TestCase):
    """Tests for the Experience model itself."""

    @classmethod
    def setUpTestData(cls):
        # Shared across all test methods in this class — created once, rolled back per test method.
        cls.tech_python = Technology.objects.create(
            name="Python",
            date_experience_began="2020-01-01",
            icon_name="code",
            tech_domain=90,
            is_active=True,
            priority=95,
        )
        cls.exp_active = Experience.objects.create(
            company="Acme Corp",
            role_title="Senior Engineer",
            start_date="2022-01-01",
            end_date=None,
            description="Did the thing.",
            is_active=True,
            priority=90,
            display_order=10,
            accent_style=Experience.AccentStyle.PRIMARY,
        )
        cls.exp_active.skills.add(cls.tech_python)
        cls.exp_inactive = Experience.objects.create(
            company="Old Co",
            role_title="Junior Engineer",
            start_date="2018-01-01",
            end_date="2020-01-01",
            description="Learned the ropes.",
            is_active=False,
            priority=50,
            display_order=50,
            accent_style=Experience.AccentStyle.OUTLINE,
        )

    def test_str(self):
        # Verifies model __str__ format from spec #81: "role_title @ company"
        self.assertEqual(str(self.exp_active), "Senior Engineer @ Acme Corp")


class ExperienceURLTests(TestCase):
    """Tests for the /experiences/ URL routing."""

    def test_url_resolves(self):
        # Verifies app/urls.py wires the route to ExperienceListView with name="experiences"
        url = reverse("experiences")
        self.assertEqual(url, "/experiences/")
        match = resolve(url)
        self.assertEqual(match.func.view_class, ExperienceListView)


class ExperienceViewTests(TestCase):
    """Tests for the ExperienceListView TemplateView."""

    @classmethod
    def setUpTestData(cls):
        cls.tech = Technology.objects.create(
            name="Go", date_experience_began="2018-01-01", icon_name="speed", tech_domain=80, is_active=True, priority=80
        )
        cls.exp_top = Experience.objects.create(
            company="Top Co", role_title="Lead",
            start_date="2023-01-01", end_date=None,
            description="d", is_active=True, priority=90, display_order=10,
            accent_style=Experience.AccentStyle.PRIMARY,
        )
        cls.exp_top.skills.add(cls.tech)
        cls.exp_mid = Experience.objects.create(
            company="Mid Co", role_title="Senior",
            start_date="2021-01-01", end_date="2022-12-31",
            description="d", is_active=True, priority=80, display_order=20,
            accent_style=Experience.AccentStyle.TERTIARY,
        )
        cls.exp_bottom = Experience.objects.create(
            company="Old Co", role_title="Junior",
            start_date="2018-01-01", end_date="2020-01-01",
            description="d", is_active=True, priority=70, display_order=30,
            accent_style=Experience.AccentStyle.OUTLINE,
        )
        cls.exp_hidden = Experience.objects.create(
            company="Hidden Co", role_title="Ghost",
            start_date="2010-01-01", end_date="2010-12-31",
            description="d", is_active=False, priority=100, display_order=5,
            accent_style=Experience.AccentStyle.PRIMARY,
        )

    def test_view_returns_200(self):
        # Smoke: the page renders without error and returns HTTP 200
        response = self.client.get(reverse("experiences"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_base_template(self):
        # Verifies the page extends base.html (so it inherits nav, footer, etc.)
        response = self.client.get(reverse("experiences"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "experiences/list.html")

    def test_view_sets_active_page(self):
        # Verifies the context variable that drives nav highlight in base.html
        response = self.client.get(reverse("experiences"))
        self.assertEqual(response.context["active_page"], "experience")

    def test_inactive_excluded(self):
        # Verifies is_active=True filter: the hidden row must NOT be in context
        response = self.client.get(reverse("experiences"))
        experiences_in_context = list(response.context["experiences"])
        self.assertIn(self.exp_top, experiences_in_context)
        self.assertIn(self.exp_mid, experiences_in_context)
        self.assertIn(self.exp_bottom, experiences_in_context)
        self.assertNotIn(self.exp_hidden, experiences_in_context)
        # Also verify the count
        self.assertEqual(len(experiences_in_context), 3)

    def test_ordering_respected(self):
        # Verifies order_by: display_order ASC, -priority DESC, -start_date DESC
        # All three active experiences have distinct display_order, so display_order alone resolves ordering.
        # But we also test the priority tie-breaker with a 4th row that has the SAME display_order
        # as exp_top but a LOWER priority — it should come after exp_top.
        exp_tied_low = Experience.objects.create(
            company="Tied Low Co", role_title="Same Pos",
            start_date="2024-01-01", end_date=None,
            description="d", is_active=True, priority=10, display_order=10,  # same display_order as exp_top
            accent_style=Experience.AccentStyle.PRIMARY,
        )
        response = self.client.get(reverse("experiences"))
        ordered_ids = [e.pk for e in response.context["experiences"]]
        # exp_top (display_order=10, priority=90) should beat exp_tied_low (display_order=10, priority=10)
        self.assertLess(ordered_ids.index(self.exp_top.pk), ordered_ids.index(exp_tied_low.pk))
        # Overall order: exp_top (10), exp_tied_low (10, but lower priority), exp_mid (20), exp_bottom (30)
        self.assertEqual(ordered_ids, [self.exp_top.pk, exp_tied_low.pk, self.exp_mid.pk, self.exp_bottom.pk])


class ExperienceCleanValidationTests(TestCase):
    """Tests for the model.clean() method that enforces end_date >= start_date.

    Spec #81 scenario: 'When end_date is set to a date before start_date, model
    validation rejects it with a ValidationError.' Clean() is called by full_clean()
    and ModelForm.is_valid(); it is NOT called by default Model.save()."""

    def test_end_date_before_start_date_raises(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        exp = Experience(
            company="Time Travel Inc", role_title="Chrononaut",
            start_date=date(2020, 1, 1), end_date=date(2019, 1, 1),
            description="oops", priority=50, display_order=10,
            accent_style=Experience.AccentStyle.PRIMARY,
        )
        with self.assertRaises(ValidationError) as ctx:
            exp.full_clean()
        self.assertIn("end_date", ctx.exception.message_dict)

    def test_end_date_after_start_date_ok(self):
        from datetime import date
        exp = Experience(
            company="Forward Inc", role_title="Futurist",
            start_date=date(2020, 1, 1), end_date=date(2025, 1, 1),
            description="ok", priority=50, display_order=10,
            accent_style=Experience.AccentStyle.PRIMARY,
        )
        # Should not raise
        exp.full_clean()

    def test_end_date_none_ok(self):
        from datetime import date
        exp = Experience(
            company="Present Co", role_title="Current",
            start_date=date(2020, 1, 1), end_date=None,
            description="ongoing", priority=50, display_order=10,
            accent_style=Experience.AccentStyle.PRIMARY,
        )
        # Should not raise
        exp.full_clean()
