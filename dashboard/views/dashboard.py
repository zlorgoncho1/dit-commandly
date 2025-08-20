from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ici nous ajouterons les statistiques du tableau de bord
        context['title'] = 'Tableau de bord'
        return context


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/stats.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Statistiques'
        return context
