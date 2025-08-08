#!/usr/bin/env python
"""
Django Development Server Başlatma Script'i
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # Django settings'i yükle
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safak_backend.settings')
    django.setup()
    
    # Development server'ı başlat
    print("🚀 Django Development Server başlatılıyor...")
    print("📱 React Native uygulaması için: http://localhost:8000")
    print("🔧 API Endpoint'leri: http://localhost:8000/api/")
    print("⏹️  Durdurmak için: Ctrl+C")
    print("-" * 50)
    
    # Server'ı başlat
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000']) 