from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import re

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Telefon numarası zorunludur.')
        
        phone_number = phone_number.strip()
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        return self._create_user(phone_number, password, **extra_fields)
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(phone_number, password, **extra_fields)
    
    def _create_user(self, phone_number, password, **extra_fields):
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
from django.core.validators import RegexValidator
phone_validator = RegexValidator(
    regex=r'^(\+90|0)?5[0-9]{9}$',
    message="Telefon numarası geçerli formatta olmalı. Örnek: 05551234567 ya da +905551234567"
)
class CustomUser(AbstractUser):
    # Telefon numarası regex'i (Türkiye)
    phone_regex = re.compile(r'^(\+90|0)?[5][0-9]{9}$')
    
    username = None  # username alanını kullanmıyoruz
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[phone_validator],
        verbose_name='Telefon Numarası'
    )
    is_phone_verified = models.BooleanField(default=False, verbose_name='Telefon Doğrulandı')
    
    # Çocuk bilgileri
    has_children = models.BooleanField(default=False, verbose_name='Çocuğu Var mı?')
    children_count = models.PositiveIntegerField(default=0, verbose_name='Çocuk Sayısı')
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

class Child(models.Model):
    GRADE_CHOICES = [
        ('3_yas', '3 Yaş'),
        ('4_yas', '4 Yaş'),
        ('5_yas', '5 Yaş'),
        ('1_sinif', '1. Sınıf'),
        ('2_sinif', '2. Sınıf'),
        ('3_sinif', '3. Sınıf'),
        ('4_sinif', '4. Sınıf'),
        ('5_sinif', '5. Sınıf'),
        ('6_sinif', '6. Sınıf'),
        ('7_sinif', '7. Sınıf'),
        ('8_sinif', '8. Sınıf'),
        ('9_sinif', '9. Sınıf'),
        ('10_sinif', '10. Sınıf'),
        ('11_sinif', '11. Sınıf'),
        ('12_sinif', '12. Sınıf'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='children', verbose_name='Kullanıcı')
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, verbose_name='Sınıf')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    class Meta:
        verbose_name = 'Çocuk'
        verbose_name_plural = 'Çocuklar'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Çocuk - {self.get_grade_display()}"
