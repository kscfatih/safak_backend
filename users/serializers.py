from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Child

class ChildSerializer(serializers.ModelSerializer):
    grade_display = serializers.CharField(source='get_grade_display', read_only=True)
    
    class Meta:
        model = Child
        fields = ['id', 'name', 'grade', 'grade_display', 'created_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    children = ChildSerializer(many=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'first_name', 'last_name', 
            'password', 'password_confirm', 'has_children', 
            'children_count', 'children'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'has_children': {'required': False},
            'children_count': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor.")
        
        # Çocuk bilgileri validasyonu
        has_children = attrs.get('has_children', False)
        children_count = attrs.get('children_count', 0)
        children = attrs.get('children', [])
        
        if has_children and children_count <= 0:
            raise serializers.ValidationError("Çocuk sayısı 0'dan büyük olmalıdır.")
        
        if has_children and children_count != len(children):
            raise serializers.ValidationError("Çocuk sayısı ile girilen çocuk bilgileri eşleşmiyor.")
        
        if not has_children and (children_count > 0 or children):
            raise serializers.ValidationError("Çocuğu yoksa çocuk bilgileri girilmemelidir.")
        
        return attrs
    
    def create(self, validated_data):
        children_data = validated_data.pop('children', [])
        password_confirm = validated_data.pop('password_confirm')
        
        user = CustomUser.objects.create_user(**validated_data)
        
        # Çocuk bilgilerini kaydet
        for child_data in children_data:
            Child.objects.create(user=user, **child_data)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
            if not user:
                raise serializers.ValidationError("Geçersiz telefon numarası veya şifre.")
            if not user.is_active:
                raise serializers.ValidationError("Hesabınız aktif değil.")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Telefon numarası ve şifre gereklidir.")
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    children = ChildSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'first_name', 'last_name', 
            'is_phone_verified', 'has_children', 'children_count', 
            'children', 'date_joined'
        ]
        read_only_fields = ['id', 'phone_number', 'is_phone_verified', 'date_joined']

class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    children = ChildSerializer(many=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'current_password', 
            'new_password', 'has_children', 'children_count', 'children'
        ]
    
    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        
        if new_password and not current_password:
            raise serializers.ValidationError("Yeni şifre için mevcut şifre gereklidir.")
        
        if current_password and not self.instance.check_password(current_password):
            raise serializers.ValidationError("Mevcut şifre yanlış.")
        
        # Çocuk bilgileri validasyonu
        has_children = attrs.get('has_children', self.instance.has_children)
        children_count = attrs.get('children_count', self.instance.children_count)
        children = attrs.get('children', [])
        
        if has_children and children_count <= 0:
            raise serializers.ValidationError("Çocuk sayısı 0'dan büyük olmalıdır.")
        
        if has_children and children_count != len(children):
            raise serializers.ValidationError("Çocuk sayısı ile girilen çocuk bilgileri eşleşmiyor.")
        
        if not has_children and (children_count > 0 or children):
            raise serializers.ValidationError("Çocuğu yoksa çocuk bilgileri girilmemelidir.")
        
        return attrs
    
    def update(self, instance, validated_data):
        children_data = validated_data.pop('children', [])
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        
        # Şifre güncelleme
        if new_password:
            instance.set_password(new_password)
        
        # Diğer alanları güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Çocuk bilgilerini güncelle
        if 'has_children' in validated_data or 'children_count' in validated_data:
            # Mevcut çocukları sil
            instance.children.all().delete()
            
            # Yeni çocuk bilgilerini ekle
            for child_data in children_data:
                Child.objects.create(user=instance, **child_data)
        
        return instance

class PhoneVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    verification_code = serializers.CharField()

class ChildUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'name', 'grade']
    
    def validate(self, attrs):
        user = self.context['request'].user
        child_id = self.instance.id if self.instance else None
        
        # Aynı isimde başka çocuk var mı kontrol et
        existing_child = Child.objects.filter(
            user=user, 
            name=attrs['name']
        ).exclude(id=child_id).first()
        
        if existing_child:
            raise serializers.ValidationError("Bu isimde bir çocuk zaten mevcut.")
        
        return attrs 