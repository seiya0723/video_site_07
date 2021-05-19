from django.contrib import admin
from .models import Video,Tag,Category,VideoComment

admin.site.register(Video)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(VideoComment)