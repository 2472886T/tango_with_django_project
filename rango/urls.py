from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    
    #
    path("about/", views.AboutView.as_view(), name='about'),
    
    #path("category/<slug:category_name_slug>/", views.show_category, name='show_category'),
    path("category/<slug:category_name_slug>/", views.ShowCategory.as_view(), name='show_category'),
    
    
    path("add_category/", views.AddCategoryView.as_view(), name = 'add_category'),
    
    #path("category/<slug:category_name_slug>/add_page/", views.add_page, name = 'add_page'),
    path("category/<slug:category_name_slug>/add_page/", views.AddPage.as_view(), name = 'add_page'),

    #path('restricted/', views.restricted, name='restricted'),
    path('restricted/', views.RestrictedPage.as_view(), name='restricted'),

    #path('goto/', views.goto_url, name='goto'),
    path('goto/', views.GoTo.as_view(), name='goto'),

    #path('register_profile/', views.register_profile, name='register_profile'),
    path('register_profile/', views.RegisterProfile.as_view(), name='register_profile'),
    
    #
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    #
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    
    #login without redux
    #path("register/", views.register, name='register'),
    #path("login/", views.user_login, name="login"),
    #path('logout/', views.user_logout, name='logout'),
    
    #generic serach
    #path('search/', views.search, name='search'),
    
    #old non class based about and ass category view
    #path("about/", views.about, name='about'),
    #path("add_category/", views.add_category, name = 'add_category'),
    ]