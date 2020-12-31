from django.urls import path
from accounts import views
from django.urls import reverse_lazy

app_name = 'accounts'

urlpatterns = [
    path('', views.indexView, name='index'),
    path('profile_settings/', views.accountSettings, name='profile_settings'),
    path('signup/', views.registerPage, name='signup'),
    path('user/', views.UserView.as_view(), name='user'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name="logout"),
    path('customers/<str:pk>/', views.CustomerView.as_view(), name='customers'),
    path('products/', views.ProductView.as_view(), name='products'),
    path('createorder/<str:pk>/', views.createOrder, name='createorder'),
    path('updateorder/<str:pk>/', views.OrderUpdateView.as_view(), name='updateorder'),
    path('deleteorder/<str:pk>/', views.OrderDeleteView.as_view(), name='deleteorder'),
]
