from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class ProductListView(LoginRequiredMixin, ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        # Ici nous retournerons les produits une fois les modèles créés
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des produits'
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouveau produit'
        context['action'] = 'Créer'
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Détail du produit'
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le produit'
        context['action'] = 'Modifier'
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer le produit'
        return context
