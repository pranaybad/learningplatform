from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Course, Category ,Contact
from .forms import CourseForm
from .forms import UserForm, UserProfileForm
from .models import UserProfile,Enrollment
from django.core.exceptions import PermissionDenied

def index(request):

    featured_courses = Course.objects.filter(is_featured=True)
    
   
    return render(request, 'index.html', {'featured_courses': featured_courses})

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    category = course.category  
    related_courses = Course.objects.filter(category=category).exclude(id=course.id)

    return render(request, 'course_detail.html', {
        'course': course,
        'category': category,  
        'related_courses': related_courses,  
    })


def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            # Ensure that either video_url or video_file is provided
            if not course.video_url and not course.video_file:
                form.add_error(None, 'You must provide either a video URL or upload a video file.')
            elif course.video_url and course.video_file:
                form.add_error(None, 'Please provide only one of the video URL or video file.')
            else:
                course.created_by = request.user
                course.save()
                return redirect('course_list')
    else:
        form = CourseForm()
    
    return render(request, 'create_course.html', {'form': form})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def courses_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    courses = Course.objects.filter(category=category)
    return render(request, 'courses_by_category.html', {'category': category, 'courses': courses})

@login_required
def dashboard(request):
    user = request.user
    
    
    enrolled_courses = Enrollment.objects.filter(user=user)
    
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    

    upcoming_deadlines = []
    recent_activity = []
    notifications = []

    context = {
        'user': user,
        'user_profile': user_profile,
        'enrolled_courses': enrolled_courses,
        'upcoming_deadlines': upcoming_deadlines,
        'recent_activity': recent_activity,
        'notifications': notifications,
    }
    
    return render(request, 'dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  
            return redirect('home')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')  
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})





@login_required
def profile(request):
    user = request.user

    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'profile.html', context)

def contact(request):
    if request.method=='GET':
        return render(request, 'contact.html')
    else:
        uname= request.POST['name']
        email= request.POST['email']
        message= request.POST['message']

        data= Contact.objects.create(uname=uname, email=email, message=message)
        data.save()

        return redirect('')



@login_required
def add_course(request):
    
    if not request.user.userprofile.role == 'creator':
        raise PermissionDenied

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            return redirect('course_list')  
    else:
        form = CourseForm()

    return render(request, 'add_course.html', {'form': form})