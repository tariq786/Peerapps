from django.contrib import admin

from models import BlockchainScan
class BlockchainScanAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)
admin.site.register(BlockchainScan, BlockchainScanAdmin)

from models import MemPoolScan
class MemPoolScanAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)
admin.site.register(MemPoolScan, MemPoolScanAdmin)

