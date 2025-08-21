from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from orders.models import Order, OrderItem
from orders.forms import OrderForm, OrderItemForm, OrderSearchForm
from customers.models import Customer
from products.models import Product


@login_required
def order_list(request):
    """
    Liste des commandes avec recherche et pagination
    """
    # Récupération des paramètres de recherche
    search_form = OrderSearchForm(request.GET)
    orders = Order.objects.all()
    
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
    
    # Tri par défaut
    orders = orders.order_by('-order_date')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcul des statistiques
    total_orders = orders.count()
    total_amount = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    orders_by_status = {}
    for status_choice in Order.STATUS_CHOICES:
        status_code = status_choice[0]
        orders_by_status[status_code] = orders.filter(status=status_code).count()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_orders': total_orders,
        'total_amount': total_amount,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """
    Détail d'une commande
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Récupération des lignes de commande
    order_items = order.items.all().order_by('id')
    
    # Récupération de la facture associée si elle existe
    invoice = getattr(order, 'invoice', None)
    
    context = {
        'order': order,
        'order_items': order_items,
        'invoice': invoice,
        'subtotal_ht': order.subtotal_ht,
        'tax_amount': order.tax_amount,
        'total_amount': order.total_amount,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_create(request):
    """
    Création d'une nouvelle commande
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'Commande "{order.order_number}" créée avec succès.')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Erreur lors de la création de la commande. Veuillez corriger les erreurs.')
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle commande',
        'submit_text': 'Créer la commande'
    }
    
    return render(request, 'orders/order_form.html', context)


@login_required
def order_update(request, order_id):
    """
    Modification d'une commande existante
    """
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            messages.success(request, f'Commande "{order.order_number}" modifiée avec succès.')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Erreur lors de la modification de la commande. Veuillez corriger les erreurs.')
    else:
        form = OrderForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
        'title': f'Modifier la commande {order.order_number}',
        'submit_text': 'Enregistrer les modifications'
    }
    
    return render(request, 'orders/order_form.html', context)


@login_required
def order_delete(request, order_id):
    """
    Suppression d'une commande
    """
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Commande "{order_number}" supprimée avec succès.')
        return redirect('orders:order_list')
    
    # Vérification des dépendances
    has_invoice = hasattr(order, 'invoice')
    
    context = {
        'order': order,
        'has_invoice': has_invoice,
        'can_delete': not has_invoice
    }
    
    return render(request, 'orders/order_confirm_delete.html', context)


@login_required
def order_update_status(request, order_id):
    """
    Mise à jour du statut d'une commande
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
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
                'status_color': order.get_status_display_color(),
                'message': f'Statut mis à jour avec succès.'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide.'})
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


# Vues pour les lignes de commande
@login_required
def order_item_create(request, order_id):
    """
    Ajout d'une ligne de commande
    """
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            order_item = form.save(commit=False)
            order_item.order = order
            order_item.save()
            
            messages.success(request, f'Produit ajouté à la commande avec succès.')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Erreur lors de l\'ajout du produit. Veuillez corriger les erreurs.')
    else:
        form = OrderItemForm()
    
    context = {
        'form': form,
        'order': order,
        'title': f'Ajouter un produit à la commande {order.order_number}',
        'submit_text': 'Ajouter le produit'
    }
    
    return render(request, 'orders/order_item_form.html', context)


@login_required
def order_item_update(request, order_id, item_id):
    """
    Modification d'une ligne de commande
    """
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, id=item_id, order=order)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST, instance=order_item)
        if form.is_valid():
            order_item.save()
            messages.success(request, f'Ligne de commande modifiée avec succès.')
            return redirect('orders:order_detail', order_id=order.id)
        else:
            messages.error(request, 'Erreur lors de la modification. Veuillez corriger les erreurs.')
    else:
        form = OrderItemForm(instance=order_item)
    
    context = {
        'form': form,
        'order': order,
        'order_item': order_item,
        'title': f'Modifier la ligne de commande',
        'submit_text': 'Enregistrer les modifications'
    }
    
    return render(request, 'orders/order_item_form.html', context)


@login_required
def order_item_delete(request, order_id, item_id):
    """
    Suppression d'une ligne de commande
    """
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, id=item_id, order=order)
    
    if request.method == 'POST':
        product_name = order_item.product.name
        order_item.delete()
        messages.success(request, f'Produit "{product_name}" supprimé de la commande.')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'order_item': order_item,
    }
    
    return render(request, 'orders/order_item_confirm_delete.html', context)


@login_required
def order_quick_search(request):
    """
    Recherche rapide de commandes pour les formulaires
    """
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
