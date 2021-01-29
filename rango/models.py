from django.db import models

from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    NAME_MAX_LENGTH = 128
    
    name = models.CharField(max_length = NAME_MAX_LENGTH, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique = True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Page(models.Model):
    TITLE_MAX_LENGTH = 128
    URL_MAX_LENGTH = 200
    
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    title = models.CharField(max_length = TITLE_MAX_LENGTH)
    url = models.URLField()
    views = models.IntegerField(default = 0)
    
    def __str__(self):
        return self.title

    
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # additional field apart from the basic 5 from User model
    #blank=True -> can be left empty if user decides that way
    #upload_to='dir_name' -> where to store uploaded images within the MEDIA_ROOT
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    
    def __str__(self):
        return self.user.username
    
    