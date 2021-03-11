from django.shortcuts import render, redirect

from django.http import HttpResponse

from rango.models import Category, Page, UserProfile

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from datetime import datetime

from rango.bing_search import run_query

from django.views import View

from django.utils.decorators import method_decorator

from django.contrib.auth.models import User


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    
    most_viewed_pages = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = most_viewed_pages
    
    #call the cookie handler on client side
    #visitor_cookie_handler(request, response)
    
    #call cookie handler on server side
    visitor_cookie_handler(request)
    
    #context_dict['visits'] = int(request.COOKIES.get('visits', '1')) #for client side cookies
    #context_dict['visits'] = request.session['visits'] #for serverside cookies
    
    #create response - same as it was in the original return
    response = render(request, 'rango/index.html', context=context_dict)
    
    #return response after cookie handling
    return response


class IndexView(View):
    def get(self, request):
        category_list = Category.objects.order_by('-likes')[:5]
        most_viewed_pages = Page.objects.order_by('-views')[:5]
        
        context_dict = {}
        context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
        context_dict['categories'] = category_list
        context_dict['pages'] = most_viewed_pages
        
        visitor_cookie_handler(request)
        
        response = render(request, 'rango/index.html', context=context_dict)
        
        return response
        
#-----------------------------------------------------------------------------
class AboutView(View):
    def get(self, request):
        context_dict = {}
        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        return render(request, 'rango/about.html', context=context_dict)


def about(request):
    visitor_cookie_handler(request)
    context_dict = {}
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/about.html', context=context_dict)

#-----------------------------------------------------------------------------
class ShowCategory(View):
    
    def contextHelper(self, category_name_slug):
        context_dict = {}
        
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')
            
            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['pages'] = None
            context_dict['category'] = None
        
        return context_dict
       
        
    def get(self, request, category_name_slug):
        context_dict = self.contextHelper(category_name_slug)
        return render(request, 'rango/category.html', context = context_dict)
    
    
    def post(self, request, category_name_slug):
        context_dict = self.contextHelper(category_name_slug)
        result_list = []
        
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
        context_dict['result_list'] = result_list
        context_dict['last_query'] = query
        
        return render(request, 'rango/category.html', context = context_dict)
        


def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        #either returns one Category object or raises an error - hence the try/except
        category = Category.objects.get(slug = category_name_slug)
        
        #get all associated pages and add it to context_dict
        pages = Page.objects.filter(category = category).order_by('-views')
        context_dict['pages'] = pages
        
        #add category, for verification in the template
        context_dict['category'] = category
        
    except Category.DoesNotExist:
        #if there is no category with that name
        context_dict['category'] = None
        context_dict['pages'] = None
        
    
    result_list = []
    query=""
    
    #from decommissioned navbar search
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    
    context_dict['result_list'] = result_list
    context_dict['last_query'] = query

        
    return render(request, 'rango/category.html', context = context_dict)

#-----------------------------------------------------------------------------
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

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add:category.html', {'form': form})
    
    @method_decorator(login_required)
    def post(self, request):
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

#-----------------------------------------------------------------------------
class AddPage(View):
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        try:
            category=Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
        
        form = PageForm()
        context_dict = {'form': form,
                        'category': category}
        return render(request, 'rango/add_page.html',  context = context_dict)
    
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        try:
            category=Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
            
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
        
        context_dict = {'form': form, 'category': category}
        
        return render(request, 'rango/add_page.html',  context = context_dict)
       



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
#-----------------------------------------------------------------------------


#login stuff withoud redux
"""
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
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))
"""
#-----------------------------------------------------------------------------
class RestrictedPage(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'rango/restricted.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')
#-----------------------------------------------------------------------------



def get_server_side_cookie(request, cookie, default_val =None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

""" old visitor cookie handler
def visitor_cookie_handler(request, response):
    #get the humber of visits to the site
    #COOKIE.get() returns the cookie for the given visit
    #if the cookie exists we return the number of their visits
    #if it doesn't we return the default 1
    visits = int(request.COOKIES.get('visits', '1'))
    
    #try to get the cookie named last_visit from the request from the client, if it doesn't exists (first time on the site) set it to now
    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    #extracts the date
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    
    #if it's been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        #increment number of visits and create a new RESPONSE COOKIE with the last_visit set to the current time
        visits = visits + 1
        response.set_cookie('last_visit', str(datetime.now()))
    else:
        #kepp the last_visit from the REQUEST  COOKIE ans set it in the RESPONSE COOKIE
        response.set_cookie('last_visit', last_visit_cookie)
    
    #create a RESPONSE COOKIE with the maybe updated number of visits
    response.set_cookie('visits', visits)
"""

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    
    #if it's been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        #increment number of visits and create a new RESPONSE COOKIE with the last_visit set to the current time
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        #kepp the last_visit from the REQUEST  COOKIE ans set it in the RESPONSE COOKIE
        request.session['last_visit'] = last_visit_cookie
    
    #create a RESPONSE COOKIE with the maybe updated number of visits
    request.session['visits'] = visits

#-----------------------------------------------------------------------------
class GoTo(View):
    def get(self, request):
        page_id = request.GET.get('page_id')
        
        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))
        
        selected_page.views += 1
        selected_page.save()
        
        return redirect(selected_page.url)








def goto_url(request):
    if request.method == 'GET':
        page_id = request.GET.get('page_id')
        
        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))
        
        selected_page.views += 1
        selected_page.save()
        
        return redirect(selected_page.url)
    
    return redirect(reverse('rango:index'))


#old generic search on navbar
"""
def search(request):
    result_list = []
    query=""
    
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    
    return render(request, 'rango/search.html', {'result_list': result_list, 'last_query': query})
"""
#-----------------------------------------------------------------------------
class RegisterProfile(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def register_profile(request):
    form = UserProfileForm()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)

#-----------------------------------------------------------------------------

class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
                                'picture': user_profile.picture})
        return (user, user_profile, form)
    
    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rango/profile.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_Valid():
            form.save(commit=True)
            return redirect('rango:profile', username)
        else:
            print(form.errors)
        
        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        
        return render(request, 'rengo/profile.html', context_dict)
    
class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()
        
        return render(request, 'rango/list_profiles.html', {'user_profile_list': profiles})