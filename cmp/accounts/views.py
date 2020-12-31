from django.shortcuts import render,redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from accounts.models import Product,Customer,Order
from django.urls import reverse_lazy,reverse
from accounts.forms import OrderCreateForm, UserCreateForm,CustomerForm
from django.forms import inlineformset_factory
from accounts.filters import OrderFilter
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponse
# from django.contrib.auth import get_user_model
from accounts.decorators import allowed_users,admin_only,unauthenticated_user
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group

# Create your views here.

# User = get_user_model()

@unauthenticated_user
def registerPage(request):

	form = UserCreateForm()
	if request.method == 'POST':
		form = UserCreateForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')


			messages.success(request, 'Account was created for ' + username)

			return redirect('accounts:login')


	context = {'form':form}
	return render(request, 'accounts/signup.html', context)

@login_required
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()


	context = {'form':form}
	return render(request, 'accounts/account_settings.html', context)

def loginPage(request):
	if request.user.is_authenticated:
		return redirect('accounts:index')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('accounts:index')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'accounts/login.html', context)

@login_required
def logoutUser(request):
	logout(request)
	return redirect('accounts:login')

# class OrderCreateView(CreateView):
# 	# form_class = OrderCreateForm
# 	model = Order
# 	fields = ('customer','product','status')
# 	success_url = reverse_lazy('accounts:index')
#
# 	# def form_valid(self, form):
# 	# 	form.instance.customer = self.request.user
# 	# 	return super().form_valid(form)
#
# 	# def get_context_data(self, **kwargs):
# 	# 	context = super().get_context_data(**kwargs)
# 	# 	customer = Customer.objects.get(id=kwargs['pk'])
# 	# 	form = OrderCreateForm(initial={'customer':customer})

@login_required
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5 )
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	# form = OrderCreateForm(initial={'customer':customer})
	if request.method == 'POST':
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'form':formset,'customer':customer}
	return render(request, 'accounts/order_form.html', context)

@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class OrderUpdateView(LoginRequiredMixin,UpdateView):
	model = Order
	fields = ('product','status')
	success_url = reverse_lazy('accounts:index')
	# def get_absolute_url(self):
	# 	return reverse("accounts:customers", kwargs={"pk": self.object.pk})

@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class OrderDeleteView(LoginRequiredMixin,DeleteView):
	model = Order
	context_object_name = 'order'
	success_url = reverse_lazy('accounts:index')

# @method_decorator(admin_only, name='dispatch')
# class IndexView(LoginRequiredMixin,TemplateView):
# 	template_name = 'accounts/dashboard.html'
#
# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data(**kwargs)
# 		orders = Order.objects.all()
# 		customers = Customer.objects.all()
#
# 		total_customers = customers.count()
# 		total_orders = orders.count()
# 		delivered = orders.filter(status='Delivered').count()
# 		pending = orders.filter(status='Pending').count()
#
# 		context = {'orders':orders,'customers':customers, 'total_orders':total_orders,'delivered':delivered,
# 				   'pending':pending}
# 		return context


	# def get(self, request, *args, **kwargs):
	# 	return HttpResponse('/accounts/dashboard.html')
	# def dispatch(self, *args, **kwargs):
	# 	return super(IndexView, self).dispatch(*args, **kwargs)
	# def get(self, request, *args, **kwargs):
	# 	return render(request, 'accounts/dashboard.html',context_instance=RequestContext(request))

@login_required
@admin_only
def indexView(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()

	total_customers = customers.count()

	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()

	context = {'orders':orders, 'customers':customers,
	'total_orders':total_orders,'delivered':delivered,
	'pending':pending }

	return render(request, 'accounts/dashboard.html', context)

@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class CustomerView(LoginRequiredMixin,TemplateView):
	template_name = 'accounts/customers.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		customer = Customer.objects.get(id=kwargs['pk'])
		# Relation between order and customer table
		orders = customer.order_set.all()
		order_count = orders.count()

		myFilter = OrderFilter(self.request.GET, queryset=orders)
		orders = myFilter.qs

		context = {'customer':customer, 'orders':orders, 'order_count':order_count,'myFilter':myFilter}
		return context


@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class ProductView(LoginRequiredMixin,TemplateView):
	template_name = 'accounts/products.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		products = Product.objects.all()
		context = {'products':products}
		return context


# Function Based View
# def products(request):
# 	products = Product.objects.all()
#
# 	return render(request, 'accounts/products.html', {'products':products})

@method_decorator(allowed_users(allowed_roles=['customer']), name='dispatch')
class UserView(LoginRequiredMixin,TemplateView):
	template_name = 'accounts/user.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		orders = self.request.user.customer.order_set.all()

		total_orders = orders.count()
		delivered = orders.filter(status='Delivered').count()
		pending = orders.filter(status='Pending').count()

		context = {'orders':orders, 'total_orders':total_orders,'delivered':delivered,'pending':pending}
		return context
