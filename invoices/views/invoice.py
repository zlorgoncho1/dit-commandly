from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class InvoiceListView(LoginRequiredMixin, ListView):
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        # Ici nous retournerons les factures une fois les modèles créés
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des factures'
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:invoice_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouvelle facture'
        context['action'] = 'Créer'
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Détail de la facture'
        return context


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:invoice_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la facture'
        context['action'] = 'Modifier'
        return context


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'invoices/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoices:invoice_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer la facture'
        return context


class InvoicePDFView(LoginRequiredMixin, DetailView):
    template_name = 'invoices/invoice_pdf.html'
    context_object_name = 'invoice'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Facture PDF'
        return context


class InvoiceStatusUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'invoices/invoice_status_form.html'
    success_url = reverse_lazy('invoices:invoice_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mettre à jour le statut'
        return context
