from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, CustomUser, Customer

# Register Company model
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'email', 'phone', 'image']
    search_fields = ['name', 'address', 'email']
    list_filter = ['name']
    # Add more configurations as needed

# Register CustomUser model
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'company', 'is_staff', 'is_active', 'image', 'level']
    search_fields = ['email']
    list_filter = ['company']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Company'), {'fields': ('company',)}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Personal'), {'fields': ('image', 'level')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'company', 'is_staff', 'is_active', 'image', 'level')}
        ),
    )
    ordering = ['email']

# Register Customer model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'email', 'phone_1', 'CNPJ', 'status', 'creation_date', 'image']
    search_fields = ['name', 'email', 'CNPJ']
    list_filter = ['company', 'status']
    # Add more configurations as needed
