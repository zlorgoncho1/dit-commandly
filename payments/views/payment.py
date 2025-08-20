from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class PaymentListView(LoginRequiredMixin, ListView):
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        # Ici nous retournerons les paiements une fois les modèles créés
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des paiements'
        return context


class PaymentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:payment_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouveau paiement'
        context['action'] = 'Créer'
        return context


class PaymentDetailView(LoginRequiredMixin, DetailView):
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Détail du paiement'
        return context


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:payment_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le paiement'
        context['action'] = 'Modifier'
        return context


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'payments/payment_confirm_delete.html'
    success_url = reverse_lazy('payments:payment_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer le paiement'
        return context
