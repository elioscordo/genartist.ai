from django.urls import reverse_lazy
from django.views.generic import CreateView
from unfold.views import UnfoldModelAdminViewMixin
from unfold.forms import UserCreationForm  # Use Unfold's styled form

class AdminSignupView(CreateView):
    title = "Create New Admin User"  # Required for Unfold header
    template_name = "admin/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("admin:index")
