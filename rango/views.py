from django.shortcuts import render, redirect

from django.http import HttpResponse

from rango.models import Category, Page

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required


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

@login_required()
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

@login_required()
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


def register(request):
    registered = False
    #boolean of the state of the registration - will turn to True when reg process is successfully done
    
    #if it's HTTP POST  we process
    if request.method == 'POST':
        #pair both forms with the incoming data
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            #save user form
            user = user_form.save()
            
            #set_password hashes the given password
            user.set_password(user.password)
            user.save()
            
            #commit delay the saving for integrity - posiible upload of profile pic
            profile = profile_form.save(commit=False)
            profile.user = user
            
            #chech if the user uploaded a profile pic
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            #now save after everything
            #cannot save without the filling out of all the possible fields
            profile.save()
            
            #update status boolean
            registered = True
        #invalid forms, mistakes, terminal problems
        else:
            print(user_form.errors, profile_form.errors)
    #if it's not HTTP POST we create to empty instances ready for filling out and rendering
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
              'rango/register.html',
              context = {'user_form': user_form,
                         'profile_form': profile_form,
                         'registered': registered})
        
            
def user_login(request):
    #if request is a HTTP POST pull out relevant information
    if request.method=='POST':
        #pair parts of the authentication
        #use request.POST.get('variable') and NOT request.POST['variable']
        #get can return none, while the other raises an error
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        #if valid it willl return a the User object, if not it returns none
        user = authenticate(username=username, password=password)
        
        if user:
            #check if it's an active account
            if user.is_active:
                #if accout  is valid and active we log them in and return to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            
            #if account is inactive
            else:
                return HttpResponse("Your Rango account is disabled.")
        
        #bad login details
        else:
            print(f"Invalid login detail: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    
    #arriving file is not POST (probs GET) - display login page
    else:
        return render(request, 'rango/login.html')
    

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))
