from django.shortcuts import render, redirect

from django.http import HttpResponse

from rango.models import Category, Page

from rango.forms import CategoryForm, PageForm

from django.urls import reverse

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


def add_category(request):
    form = CategoryForm()
    
    #HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        #is it valid?
        if form.is_valid():
            form.save(commit = True)
            return redirect('/rango/')
            #after saving go back to index
        else:
            #not valid form
            print(form.errors)
    #bad form, new from, no form cases
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    #you cannot ass a page to a category if the category is doesn't exist
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit = False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('rango:show_category', kwargs = {'category_name_slug': category_name_slug}))
        
        else:
            print(form.errors)
    context_dict = {'form': form,
                    'category': category}
    return render(request, 'rango/add_page.html',  context = context_dict)
    