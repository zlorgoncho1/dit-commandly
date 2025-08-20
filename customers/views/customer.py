from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class CustomerListView(LoginRequiredMixin, ListView):
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        # Ici nous retournerons les clients une fois les modèles créés
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des clients'
        return context


class CustomerCreateView(LoginRequiredMixin, CreateView):
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouveau client'
        context['action'] = 'Créer'
        return context


class CustomerDetailView(LoginRequiredMixin, DetailView):
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Détail du client'
        return context


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le client'
        context['action'] = 'Modifier'
        return context


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer le client'
        return context
