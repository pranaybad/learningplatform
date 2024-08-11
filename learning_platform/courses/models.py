from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

ROLE_CHOICES = (
    ('student', 'Student'),
    ('creator', 'Course Creator'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    date_created = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_created']

class Contact(models.Model):
    uname = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    message = models.TextField(max_length=150)

    def __str__(self):
        return f'{self.uname} - {self.email}'

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    progress = models.IntegerField(default=0)  # Optional field to track progress in a course

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'
