from django.shortcuts import render

from django.http import HttpResponse

from rango.models import Category, Page

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    
    most_viewed_pages = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = most_viewed_pages
    
    
    return render(request, 'rango/index.html', context = context_dict)


def about(request):
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        #either returns one Category object or raises an error - hence the try/except
        category = Category.objects.get(slug = category_name_slug)
        
        #get all associated pages and add it to context_dict
        pages = Page.objects.filter(category = category)
        context_dict['pages'] = pages
        
        #add category, for verification in the template
        context_dict['category'] = category
        
    except Category.DoesNotExist:
        #if there is no category with that name
        context_dict['category'] = None
        context_dict['pages'] = None
        
    return render(request, 'rango/category.html', context = context_dict)