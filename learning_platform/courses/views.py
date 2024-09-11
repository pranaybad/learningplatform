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
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
import hashlib

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    category = course.category
    related_courses = Course.objects.filter(category=category).exclude(id=course.id)

    if course.is_premium:
        enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        if not enrolled:
            return redirect('checkout', slug=slug)

    return render(request, 'course_detail.html', {
        'course': course,
        'category': category,
        'related_courses': related_courses,
    })

@login_required

def checkout(request, slug):
    # Get the course object based on the slug
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    # context={}
    # context['amount']=900
    
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if enrollment and enrollment.paid:
        return redirect('course_detail', slug=slug)


    # if request.method == 'POST':
        # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    # Prepare order details
    order_amount = int(course.price * 100)  # Convert to smallest currency unit (e.g., paise for INR)
    order_currency = "INR"
    # order_receipt = f'order_rcptid_{slug[:35]}'

    # Create order
    order = client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        # 'receipt': order_receipt,
        'payment_capture': '1'
    })
    # Prepare context for rendering the template
    context = {
        'course': course,
        'order_id': order['id'],
        'amount': order_amount / 100,
        'currency': order_currency,
        'razorpay_key': settings.RAZORPAY_KEY_ID
    }
    print('his context',context,)
        # Render the checkout template with the context
    return render(request, 'checkout.html',context)

    # Render the checkout page for GET requests
    return render(request, 'checkout.html', {'course': course})



@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        course_slug = request.POST.get('course_slug')
        course = get_object_or_404(Course, slug=course_slug)
        user = request.user
        
        # Get or create the enrollment record
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        
        if created or not enrollment.paid:
            enrollment.paid = True
            enrollment.save()

        return redirect('course_detail', slug=course_slug)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


 # index and other page routing

def index(request):
    featured_courses = Course.objects.filter(is_featured=True)
    comments = Contact.objects.all()

    # Optionally, you can log the messages for debugging
    for comment in comments:
        print(comment.message)
    
    return render(request, 'index.html', {'featured_courses': featured_courses, 'comments': comments})

def course_list(request):
    courses = Course.objects.all()
    enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
    return render(request, 'course_list.html', {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    })

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    has_paid = enrollment.paid if enrollment else False
    
    if course.is_premium and not has_paid:
        return redirect('checkout', slug=slug)
    
    context = {
        'course': course,
        'enrolled': enrolled,
        'has_paid': has_paid
    }
    
    return render(request, 'course_detail.html', context)



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
    
    enrolled_courses = Enrollment.objects.filter(user=request.user).values_list('course_id', flat=True) if request.user.is_authenticated else []
    
    return render(request, 'courses_by_category.html', {
        'category': category,
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    })

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
        print('this is the comments',data)

        return redirect('/')



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