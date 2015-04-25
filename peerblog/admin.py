from django.contrib import admin

from models import Blog
class BlogAdmin(admin.ModelAdmin):
    list_display = ('key', 'address_from', 'block_index', 'tx_id')
    search_fields = ('key', 'address_from', 'block_index', 'tx_id')
admin.site.register(Blog, BlogAdmin)

from models import Subscription
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('address', 'time')
    search_fields = ('address',)
admin.site.register(Subscription, SubscriptionAdmin)