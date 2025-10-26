"""
Web views for the website application.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class CharacterApprovalView(TemplateView):
    """
    Staff interface for reviewing and approving/rejecting character applications.
    """
    template_name = 'character_approval.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Character Approval System'
        return context


@method_decorator(login_required, name='dispatch')
class CharacterCreationView(TemplateView):
    """
    Player interface for creating new character applications.
    """
    template_name = 'character_creation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Character'
        return context
