from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.db.models import Q

# Create your views here.
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from haytunes.forms import SignUpForm, ProfileForm, UserForm
from haytunes.models import Category, Product, Profile, Discount
# from haytunes.tasks impor set_discount_as_active, set_discount_as_inactive
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse, Http404
import re
import os
import datetime as dt

from haytunes.celery import app


def get_credit(request):
    curr_user = Profile.objects.filter(user__username=request.user)
    return {'credits': curr_user[0].credit}


def index(request):
    products_audio = Product.objects.filter(type='a')[:6]
    products_video = Product.objects.filter(type='v')[:6]
    products_image = Product.objects.filter(type='i')[:6]
    context = {'products_audio': products_audio, 'products_video': products_video, 'products_image': products_image}
    return render(request, 'index.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def profile(request):
    return render(request, 'haytunes/profile.html')


def add_credits(request):
    if request.method == 'POST':
        user_id = request.POST.get('search_text')
        amount = int(request.POST.get('amount'))
        found_user = Profile.objects.filter(id=int(user_id))
        if found_user:
            # found_user = found_user[0]
            curr_credits = found_user[0].credit or 0
            curr_credits += int(amount)
            found_user.update(credit=curr_credits)
            return render(request, 'haytunes/add_credits.html', {"success": True, "username": found_user[0].user})
        else:
            return render(request, 'haytunes/add_credits.html', {"user_not_found": True})

    return render(request, 'haytunes/add_credits.html')


def create_discount(request):
    context = {}
    if request.method == 'POST':
        category = request.POST.get("category")
        existing_discount = Discount.objects.filter(product_category=category)
        existing_discount = [discount for discount in existing_discount if discount.is_active()]
        if not existing_discount:
            start_date = request.POST.get("start_date")
            start_date = dt.datetime.strptime(start_date + ' 00:01', '%Y-%m-%d %H:%M')
            end_date = request.POST.get("end_date")
            end_date = dt.datetime.strptime(end_date + ' 23:59', '%Y-%m-%d %H:%M')
            percentage = int(request.POST.get("percentage"))
            new_discount = Discount.create(category, percentage, start_date, end_date)
            new_discount.save()
        else:
            context = {'already_discount': True}

    active_discounts = Discount.objects.filter()
    categories = Category.objects.filter()
    context['active_discounts'] = active_discounts
    context['categories'] = categories
    return render(request, 'haytunes/create_discount.html', context)


def view_list(request):
    context = {}
    if request.POST.get("product_ratings"):
        product_ratings = Product.objects.filter().order_by('-rating')
        context['product_ratings'] = product_ratings

    if request.POST.get("product_downloads"):
        product_downloads = Product.objects.filter().order_by('-downloads')
        context['product_downloads'] = product_downloads

    if request.POST.get("client_downloads"):
        client_downloads = Profile.objects.filter()
        context['client_downloads'] = client_downloads.order_by('-downloads')

    return render(request, 'haytunes/view_list.html', context)


def search_client(request):
    if request.method == 'POST':
        search_string = request.POST.get('search_text')
        # search_string = result.group(1)
        searched_users = None

        if b'code' in request.body:
            searched_users = Profile.objects.filter(id__icontains=int(search_string))
        if b'name' in request.body:
            searched_users = Profile.objects.filter(user__username__icontains=search_string)

        return render(request, 'haytunes/search_client.html', {"clients": searched_users})

    return render(request, 'haytunes/search_client.html')


def client_detail(request, id):
    # TODO: change to generic.DetailView
    profile = Profile.objects.filter(id=id)
    return render(request, 'haytunes/profile_detail.html', {'profile': profile[0]})


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        #profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            #profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        #profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'haytunes/update_profile.html', {
        'user_form': user_form,
        #'profile_form': profile_form
    })


class CategoryListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'haytunes.can_admin_content'
    model = Category


class CategoryDetailView(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'haytunes.can_admin_content'
    model = Category


class CategoryCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'haytunes.can_admin_content'
    model = Category
    fields = '__all__'


class CategoryUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'haytunes.can_admin_content'
    model = Category
    fields = '__all__'


class CategoryDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'haytunes.can_admin_content'
    model = Category
    success_url = reverse_lazy('categories')


class ProductListView(generic.ListView):
    model = Product
    paginate_by = 10

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', None)
        new_context = None
        if filter_val:
            new_context = Product.objects.filter(
                Q(title__icontains=filter_val) | Q(category__name__icontains=filter_val)
            )
        else:
            new_context = Product.objects.filter()
        return new_context

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', None)
        return context


class ProductDetailView(generic.DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['msg'] = 'hola'
        existing_discount = Discount.objects.filter(product_category=context['product'].category)
        existing_discount = [discount for discount in existing_discount if discount.is_active()]
        if existing_discount:
            context['discount_percentage'] = existing_discount[0].percentage
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        curr_user = Profile.objects.filter(user__username=request.user)
        curr_credit = curr_user[0].credit
        curr_product = Product.objects.filter(id=context['product'].id)
        existing_discount = Discount.objects.filter(product_category=context['product'].category)
        existing_discount = [discount for discount in existing_discount if discount.is_active()]
        if existing_discount:
            context['discount_percentage'] = existing_discount[0].percentage

        if request.POST.get("buy"):
            users_list = set(user.username for user in context['product'].owner.all())
            if request.user.username in users_list:
                context['already_bought'] = True
                return self.render_to_response(context=context)

            price = context['product'].price
            if context['discount_percentage']:
                price = price * context['discount_percentage']/100
            if price <= curr_credit:
                # check if user already has that product

                context['bought'] = True
                curr_credit -= price
                curr_user.update(credit=curr_credit)
                curr_product[0].owner.add(curr_user[0].user)
            else:
                context['not_money'] = True
                # return self.render_to_response(context=context)

        if request.POST.get("gift"):
            if request.POST.get("destiny_username") == request.user.username:
                context['same_user'] = True
                return self.render_to_response(context=context)

            receiver = Profile.objects.filter(user__username=request.POST.get("destiny_username"))

            if receiver:
                users_list = set(user.username for user in context['product'].owner.all())
                if receiver[0].user.username in users_list:
                    context['receiver_bought'] = True
                    return self.render_to_response(context=context)

                price = context['product'].price
                if context['discount_percentage']:
                    price = price * context['discount_percentage'] / 100

                if price <= curr_credit:
                    curr_credit -= price
                    curr_user.update(credit=curr_credit)
                    curr_product[0].owner.add(receiver[0].user)
                    context['gift_sent'] = True
                    # return self.render_to_response(context=context)

                else:
                    context['not_money'] = True
                    # return self.render_to_response(context=context)

            else:
                context['not_receiver'] = True
                # return self.render_to_response(context=context)

        if request.POST.get("download"):
            users_list = set(user.username for user in context['product'].owner.all())
            if request.user.username in users_list:
                file_path = os.path.join(settings.MEDIA_ROOT, str(context['product'].content))
                curr_user.update(downloads=curr_user[0].downloads + 1)
                curr_product.update(downloads=curr_product[0].downloads + 1)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as fh:
                        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                        return response
            else:
                context['can_download'] = False

            # return self.render_to_response(context=context)

        if request.POST.get("rate"):
            owner_users_list = set(user.username for user in context['product'].owner.all())
            rating_users_list = set(user.username for user in context['product'].rated_by.all())
            if request.user.username not in owner_users_list:
                context['cant_rate'] = True
                return self.render_to_response(context=context)

            if request.user.username in rating_users_list:
                context['already_rated'] = True
            else:
                context['product'].update_rating(curr_user[0].user, int(request.POST.get("rating")))

        return self.render_to_response(context=context)


class ProductCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'haytunes.can_admin_content'
    model = Product
    fields = ['title', 'price', 'author', 'type', 'category', 'owner', 'content']


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'haytunes.can_admin_content'
    model = Product
    fields = ['title', 'price', 'author', 'type', 'category', 'owner', 'content']


class ProductDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'haytunes.can_admin_content'
    model = Product
    success_url = reverse_lazy('products')
