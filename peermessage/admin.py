from django.contrib import admin

from models import GPGKey
class GPGKeyAdmin(admin.ModelAdmin):
    list_display = ('address', 'mine')
    search_fields = ('address', 'tx_id')
admin.site.register(GPGKey, GPGKeyAdmin)
