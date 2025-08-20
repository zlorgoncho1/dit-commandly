from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        # Ici nous retournerons les commandes une fois les modèles créés
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des commandes'
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouvelle commande'
        context['action'] = 'Créer'
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Détail de la commande'
        return context


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la commande'
        context['action'] = 'Modifier'
        return context


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer la commande'
        return context


class OrderStatusUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'orders/order_status_form.html'
    success_url = reverse_lazy('orders:order_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mettre à jour le statut'
        return context
