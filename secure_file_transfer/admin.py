from django.contrib import admin
from .models import User, FileUpload, Blockchain, Wallet

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'ipfs_hash', 'original_filename', 'uploaded_at')
    search_fields = ('sender__email', 'recipient__email', 'ipfs_hash', 'original_filename')

@admin.register(Blockchain)
class BlockchainAdmin(admin.ModelAdmin):
    list_display = ('block_number', 'timestamp', 'previous_hash', 'hash', 'data')
    search_fields = ('block_number', 'hash', 'previous_hash')
    readonly_fields = ('timestamp',)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('owner', 'balance')
    search_fields = ('owner__email',)
