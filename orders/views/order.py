from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from orders.models import Order, OrderItem
from orders.forms.order_forms import OrderForm, OrderItemForm, OrderSearchForm
from customers.models import Customer
from products.models import Product


class OrderListView(LoginRequiredMixin, ListView):
    """
    Liste des commandes avec recherche et pagination
    """
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'page_obj'
    paginate_by = 20
    login_url = reverse_lazy('users:login')
    
    def get_queryset(self):
        orders = Order.objects.all()
        
        # Récupération des paramètres de recherche
        search_form = OrderSearchForm(self.request.GET)
        if search_form.is_valid():
            search_type = search_form.cleaned_data.get('search_type')
            search_query = search_form.cleaned_data.get('search_query')
            customer = search_form.cleaned_data.get('customer')
            status = search_form.cleaned_data.get('status')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            amount_min = search_form.cleaned_data.get('amount_min')
            amount_max = search_form.cleaned_data.get('amount_max')
            
            # Application des filtres
            if search_query:
                if search_type == 'order_number':
                    orders = orders.filter(order_number__icontains=search_query)
                elif search_type == 'customer':
                    orders = orders.filter(
                        Q(customer__first_name__icontains=search_query) |
                        Q(customer__last_name__icontains=search_query) |
                        Q(customer__company_name__icontains=search_query)
                    )
                elif search_type == 'status':
                    orders = orders.filter(status__icontains=search_query)
                elif search_type == 'date':
                    orders = orders.filter(order_date__date__icontains=search_query)
            
            if customer:
                orders = orders.filter(customer=customer)
            
            if status:
                orders = orders.filter(status=status)
            
            if date_from:
                orders = orders.filter(order_date__date__gte=date_from)
            
            if date_to:
                orders = orders.filter(order_date__date__lte=date_to)
            
            if amount_min:
                orders = orders.filter(total_amount__gte=amount_min)
            
            if amount_max:
                orders = orders.filter(total_amount__lte=amount_max)
        
        return orders.order_by('-order_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_form = OrderSearchForm(self.request.GET)
        orders = self.get_queryset()
        
        # Calcul des statistiques
        total_orders = orders.count()
        total_amount = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        orders_by_status = {}
        for status_choice in Order.STATUS_CHOICES:
            status_code = status_choice[0]
            orders_by_status[status_code] = orders.filter(status=status_code).count()
        
        context.update({
            'search_form': search_form,
            'total_orders': total_orders,
            'total_amount': total_amount,
            'orders_by_status': orders_by_status,
        })
        
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Détail d'une commande
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Récupération des lignes de commande
        order_items = order.items.all().order_by('id')
        
        # Récupération de la facture associée si elle existe
        invoice = getattr(order, 'invoice', None)
        
        context.update({
            'order_items': order_items,
            'invoice': invoice,
            'subtotal_ht': order.subtotal_ht,
            'tax_amount': order.tax_amount,
            'total_amount': order.total_amount,
        })
        
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    """
    Création d'une nouvelle commande
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Nouvelle commande',
            'submit_text': 'Créer la commande'
        })
        return context
    
    def form_valid(self, form):
        order = form.save()
        messages.success(self.request, f'Commande "{order.order_number}" créée avec succès.')
        return redirect('orders:order_detail', pk=order.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création de la commande. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modification d'une commande existante
    """
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context.update({
            'title': f'Modifier la commande {order.order_number}',
            'submit_text': 'Enregistrer les modifications',
            'order': order
        })
        return context
    
    def form_valid(self, form):
        order = form.save()
        messages.success(self.request, f'Commande "{order.order_number}" modifiée avec succès.')
        return redirect('orders:order_detail', pk=order.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification de la commande. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    """
    Suppression d'une commande
    """
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')
    login_url = reverse_lazy('users:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Vérification des dépendances
        has_invoice = hasattr(order, 'invoice')
        
        context.update({
            'has_invoice': has_invoice,
            'can_delete': not has_invoice
        })
        
        return context
    
    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order_number = order.order_number
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Commande "{order_number}" supprimée avec succès.')
        return response


class OrderStatusUpdateView(LoginRequiredMixin, View):
    """
    Mise à jour du statut d'une commande
    """
    login_url = reverse_lazy('users:login')
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            
            # Mise à jour automatique de la date de livraison si nécessaire
            if new_status == 'delivered' and not order.delivered_date:
                order.delivered_date = timezone.now().date()
            
            order.save()
            
            messages.success(request, f'Statut de la commande {order.order_number} mis à jour : {old_status} → {new_status}')
            
            return JsonResponse({
                'success': True,
                'new_status': new_status,
                'status_display': order.get_status_display(),
                'status_color': getattr(order, 'get_status_display_color', lambda: 'secondary')(),
                'message': f'Statut mis à jour avec succès.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide.'})
    
    def get(self, request, pk):
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


class OrderQuickSearchView(LoginRequiredMixin, View):
    """
    Recherche rapide de commandes pour les formulaires
    """
    login_url = reverse_lazy('users:login')
    
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        orders = Order.objects.filter(
            Q(order_number__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )[:10]
        
        results = []
        for order in orders:
            results.append({
                'id': order.id,
                'text': f"{order.order_number} - {order.customer.full_name}",
                'customer': order.customer.full_name,
                'status': order.get_status_display(),
                'total': str(order.total_amount)
            })
        
        return JsonResponse({'results': results})


# Vues pour les lignes de commande
class OrderItemCreateView(LoginRequiredMixin, CreateView):
    """
    Ajout d'une ligne de commande
    """
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_form.html'
    login_url = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'order': self.order,
            'title': f'Ajouter un produit à la commande {self.order.order_number}',
            'submit_text': 'Ajouter le produit'
        })
        return context
    
    def form_valid(self, form):
        order_item = form.save(commit=False)
        order_item.order = self.order
        order_item.save()
        
        messages.success(self.request, f'Produit ajouté à la commande avec succès.')
        return redirect('orders:order_detail', pk=self.order.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de l\'ajout du produit. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class OrderItemUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modification d'une ligne de commande
    """
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/order_item_form.html'
    login_url = reverse_lazy('users:login')
    
    def get_object(self, queryset=None):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return get_object_or_404(OrderItem, pk=self.kwargs['item_pk'], order=order)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_item = self.get_object()
        context.update({
            'order': order_item.order,
            'order_item': order_item,
            'title': f'Modifier la ligne de commande',
            'submit_text': 'Enregistrer les modifications'
        })
        return context
    
    def form_valid(self, form):
        order_item = form.save()
        messages.success(self.request, f'Ligne de commande modifiée avec succès.')
        return redirect('orders:order_detail', pk=order_item.order.pk)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification. Veuillez corriger les erreurs.')
        return super().form_invalid(form)


class OrderItemDeleteView(LoginRequiredMixin, DeleteView):
    """
    Suppression d'une ligne de commande
    """
    model = OrderItem
    template_name = 'orders/order_item_confirm_delete.html'
    login_url = reverse_lazy('users:login')
    
    def get_object(self, queryset=None):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return get_object_or_404(OrderItem, pk=self.kwargs['item_pk'], order=order)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_item = self.get_object()
        context.update({
            'order': order_item.order,
            'order_item': order_item,
        })
        return context
    
    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.object.order.pk})
    
    def delete(self, request, *args, **kwargs):
        order_item = self.get_object()
        product_name = order_item.product.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Produit "{product_name}" supprimé de la commande.')
        return response