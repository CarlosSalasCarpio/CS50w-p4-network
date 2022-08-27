from django.contrib import admin
from .models import PostModel, User

# Register your models here.
admin.site.register(PostModel)
admin.site.register(User)