from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Child

class SimpleChildInputSerializer(serializers.Serializer):
    grade = serializers.ChoiceField(choices=Child.GRADE_CHOICES)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    children = SimpleChildInputSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'phone_number', 'password', 'password_confirm', 'first_name', 'last_name',
            'has_children', 'children_count', 'children',
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        children_data = validated_data.pop('children', None)

        # Eğer çocuklar gönderildiyse sayaç ve has_children'ı set et
        if children_data:
            validated_data['has_children'] = True
            validated_data['children_count'] = len(children_data)

        user = CustomUser.objects.create_user(**validated_data)

        if children_data:
            Child.objects.bulk_create([
                Child(user=user, grade=child['grade']) for child in children_data
            ])

        return user

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

class PhoneVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    verification_code = serializers.CharField(max_length=6)

class ChildSerializer(serializers.ModelSerializer):
    grade_display = serializers.CharField(source='get_grade_display', read_only=True)
    
    class Meta:
        model = Child
        fields = ('id', 'grade', 'grade_display', 'created_at')
        read_only_fields = ('id', 'created_at')

class ChildUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ('id', 'grade')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    children = ChildSerializer(many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'phone_number', 'first_name', 'last_name', 
                 'is_phone_verified', 'has_children', 'children_count', 'children')
        read_only_fields = ('id', 'phone_number', 'is_phone_verified')

class UserUpdateSerializer(serializers.ModelSerializer):
    children = SimpleChildInputSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'has_children', 'children_count', 'children')

    def update(self, instance: CustomUser, validated_data):
        children_data = validated_data.pop('children', None)

        # Kullanıcı temel alanlarını güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Çocuklar gönderildiyse mevcutları değiştir
        if children_data is not None:
            # Tamamen yenileme stratejisi
            instance.children.all().delete()
            Child.objects.bulk_create([
                Child(user=instance, grade=child['grade']) for child in children_data
            ])
            instance.children_count = len(children_data)
            instance.has_children = len(children_data) > 0
            instance.save(update_fields=['children_count', 'has_children'])

        return instance