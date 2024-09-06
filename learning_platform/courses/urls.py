from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/create/', views.create_course, name='create_course'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.courses_by_category, name='courses_by_category'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='account_login'),
    path('logout/', views.logout_view, name='account_logout'),
    path('signup/', views.signup_view, name='account_signup'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('add-course/', views.add_course, name='add_course'),
    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
