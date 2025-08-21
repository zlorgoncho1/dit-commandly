from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db.models import Q, F
from products.models import Product, Category
from products.forms import ProductForm, CategoryForm, ProductSearchForm

# --- Produits ---

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'page_obj'
    paginate_by = 20

    def get_queryset(self):
        products = Product.objects.all()
        self.search_form = ProductSearchForm(self.request.GET)
        if self.search_form.is_valid():
            search_type = self.search_form.cleaned_data.get('search_type')
            search_query = self.search_form.cleaned_data.get('search_query')
            category = self.search_form.cleaned_data.get('category')
            product_type = self.search_form.cleaned_data.get('product_type')
            price_min = self.search_form.cleaned_data.get('price_min')
            price_max = self.search_form.cleaned_data.get('price_max')
            stock_status = self.search_form.cleaned_data.get('stock_status')
            is_active = self.search_form.cleaned_data.get('is_active')

            if search_query:
                if search_type == 'name':
                    products = products.filter(name__icontains=search_query)
                elif search_type == 'sku':
                    products = products.filter(sku__icontains=search_query)
                elif search_type == 'category':
                    products = products.filter(category__name__icontains=search_query)
                elif search_type == 'description':
                    products = products.filter(description__icontains=search_query)
            if category:
                products = products.filter(category=category)
            if product_type:
                products = products.filter(product_type=product_type)
            if price_min:
                products = products.filter(unit_price__gte=price_min)
            if price_max:
                products = products.filter(unit_price__lte=price_max)
            if stock_status:
                if stock_status == 'available':
                    products = products.filter(stock_quantity__gt=0)
                elif stock_status == 'low':
                    products = products.filter(
                        stock_quantity__gt=0,
                        stock_quantity__lte=F('min_stock_level')
                    )
                elif stock_status == 'out':
                    products = products.filter(stock_quantity=0)
            if is_active:
                products = products.filter(is_active=is_active == 'True')
        return products.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        context['search_form'] = getattr(self, 'search_form', ProductSearchForm(self.request.GET))
        context['total_products'] = products.count()
        context['active_products'] = products.filter(is_active=True).count()
        context['product_products'] = products.filter(product_type='product').count()
        context['service_products'] = products.filter(product_type='service').count()
        context['low_stock_products'] = Product.objects.filter(
            product_type='product',
            stock_quantity__gt=0,
            stock_quantity__lte=F('min_stock_level')
        ).count()
        context['out_of_stock_products'] = Product.objects.filter(
            product_type='product',
            stock_quantity=0
        ).count()
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        order_items = product.orderitem_set.all().order_by('-order__order_date')[:10]
        context['order_items'] = order_items
        context['total_orders'] = product.orderitem_set.count()
        context['total_quantity_ordered'] = sum(item.quantity for item in product.orderitem_set.all())
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Produit "{self.object.name}" créé avec succès.')
        return redirect('products:product_detail', product_id=self.object.id)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création du produit. Veuillez corriger les erreurs.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouveau produit'
        context['submit_text'] = 'Créer le produit'
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    pk_url_kwarg = 'product_id'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Produit "{self.object.name}" modifié avec succès.')
        return redirect('products:product_detail', product_id=self.object.id)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification du produit. Veuillez corriger les erreurs.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.object
        context['title'] = f'Modifier {self.object.name}'
        context['submit_text'] = 'Enregistrer les modifications'
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    pk_url_kwarg = 'product_id'
    success_url = reverse_lazy('products:product_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        has_order_items = self.object.orderitem_set.exists()
        if has_order_items:
            messages.error(request, "Impossible de supprimer ce produit car il est lié à des commandes.")
            return self.get(request, *args, **kwargs)
        product_name = self.object.name
        self.object.delete()
        messages.success(request, f'Produit "{product_name}" supprimé avec succès.')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        has_order_items = product.orderitem_set.exists()
        context['product'] = product
        context['has_order_items'] = has_order_items
        context['can_delete'] = not has_order_items
        return context


class ProductToggleStatusView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.is_active = not product.is_active
        product.save()
        status = "activé" if product.is_active else "désactivé"
        messages.success(request, f'Produit "{product.name}" {status} avec succès.')
        return JsonResponse({
            'success': True,
            'is_active': product.is_active,
            'message': f'Produit {status} avec succès.'
        })

    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})


class ProductQuickSearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query)
        ).filter(is_active=True)[:10]
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'text': product.name,
                'sku': product.sku or '',
                'price': str(product.unit_price),
                'stock': product.stock_quantity if product.product_type == 'product' else 'N/A'
            })
        return JsonResponse({'results': results})

# --- Catégories ---

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.get_queryset()
        context['total_categories'] = categories.count()
        context['active_categories'] = categories.filter(is_active=True).count()
        return context

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        produits = category.products.all()
        context['products'] = produits
        context['total_products'] = produits.count()
        context['active_products'] = produits.filter(is_active=True).count()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Catégorie "{self.object.name}" créée avec succès.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la création de la catégorie. Veuillez corriger les erreurs.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nouvelle catégorie'
        context['submit_text'] = 'Créer la catégorie'
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    pk_url_kwarg = 'category_id'
    success_url = reverse_lazy('products:category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Catégorie "{self.object.name}" modifiée avec succès.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Erreur lors de la modification de la catégorie. Veuillez corriger les erreurs.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        context['title'] = f'Modifier {self.object.name}'
        context['submit_text'] = 'Enregistrer les modifications'
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    pk_url_kwarg = 'category_id'
    success_url = reverse_lazy('products:category_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        has_products = self.object.products.exists()
        if has_products:
            messages.error(request, "Impossible de supprimer cette catégorie car elle contient des produits.")
            return self.get(request, *args, **kwargs)
        category_name = self.object.name
        self.object.delete()
        messages.success(request, f'Catégorie "{category_name}" supprimée avec succès.')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        has_products = category.products.exists()
        context['category'] = category
        context['has_products'] = has_products
        context['can_delete'] = not has_products
        return context

# --- Vues supplémentaires demandées ---

class ProductActivateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        if not produit.is_active:
            produit.is_active = True
            produit.save()
            messages.success(request, f'Produit "{produit.name}" activé avec succès.')
        else:
            messages.info(request, f'Produit "{produit.name}" est déjà actif.')
        return JsonResponse({'success': True, 'is_active': produit.is_active})

class ProductDeactivateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        if produit.is_active:
            produit.is_active = False
            produit.save()
            messages.success(request, f'Produit "{produit.name}" désactivé avec succès.')
        else:
            messages.info(request, f'Produit "{produit.name}" est déjà inactif.')
        return JsonResponse({'success': True, 'is_active': produit.is_active})

class ProductStockUpdateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        try:
            new_stock = int(request.POST.get('stock_quantity', None))
            if new_stock < 0:
                raise ValueError
            produit.stock_quantity = new_stock
            produit.save()
            messages.success(request, f'Stock du produit "{produit.name}" mis à jour à {new_stock}.')
            return JsonResponse({'success': True, 'stock_quantity': produit.stock_quantity})
        except (TypeError, ValueError):
            messages.error(request, "Valeur de stock invalide.")
            return JsonResponse({'success': False, 'message': 'Valeur de stock invalide.'}, status=400)

class ProductPriceUpdateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        try:
            new_price = float(request.POST.get('unit_price', None))
            if new_price < 0:
                raise ValueError
            produit.unit_price = new_price
            produit.save()
            messages.success(request, f'Prix du produit "{produit.name}" mis à jour à {new_price} FCFA.')
            return JsonResponse({'success': True, 'unit_price': str(produit.unit_price)})
        except (TypeError, ValueError):
            messages.error(request, "Valeur de prix invalide.")
            return JsonResponse({'success': False, 'message': 'Valeur de prix invalide.'}, status=400)

# --- Vues supplémentaires demandées ---

class ProductActivateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        if not produit.is_active:
            produit.is_active = True
            produit.save()
            messages.success(request, f'Produit "{produit.name}" activé avec succès.')
        else:
            messages.info(request, f'Produit "{produit.name}" est déjà actif.')
        return JsonResponse({'success': True, 'is_active': produit.is_active})

class ProductDeactivateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        if produit.is_active:
            produit.is_active = False
            produit.save()
            messages.success(request, f'Produit "{produit.name}" désactivé avec succès.')
        else:
            messages.info(request, f'Produit "{produit.name}" est déjà inactif.')
        return JsonResponse({'success': True, 'is_active': produit.is_active})

class ProductStockUpdateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        try:
            new_stock = int(request.POST.get('stock_quantity', None))
            if new_stock < 0:
                raise ValueError
            produit.stock_quantity = new_stock
            produit.save()
            messages.success(request, f'Stock du produit "{produit.name}" mis à jour à {new_stock}.')
            return JsonResponse({'success': True, 'stock_quantity': produit.stock_quantity})
        except (TypeError, ValueError):
            messages.error(request, "Valeur de stock invalide.")
            return JsonResponse({'success': False, 'message': 'Valeur de stock invalide.'}, status=400)

class ProductPriceUpdateView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        produit = get_object_or_404(Product, id=product_id)
        try:
            new_price = float(request.POST.get('unit_price', None))
            if new_price < 0:
                raise ValueError
            produit.unit_price = new_price
            produit.save()
            messages.success(request, f'Prix du produit "{produit.name}" mis à jour à {new_price} FCFA.')
            return JsonResponse({'success': True, 'unit_price': str(produit.unit_price)})
        except (TypeError, ValueError):
            messages.error(request, "Valeur de prix invalide.")
            return JsonResponse({'success': False, 'message': 'Valeur de prix invalide.'}, status=400)
