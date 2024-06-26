from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from .models import FriendRequest, Match
from django.conf import settings
from django.contrib.auth.models import User

User = get_user_model()

# Maç verilerini serileştirmek, düzenlemek için
class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'player1', 'player2', 'score', 'result', 'match_date']

# Belirli bir kullanıcını arkadaşlarını serileştirmek, düzenlemek için
class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username', 'last_name', 'has_logged_in']

# Kullanıcı kayıt olurken gelen bilgileri kolay yönetmek ve doğrulama işlemlerini yapmak için kullanılır
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'normal_avatar', 'intra_avatar', 'languagePreference')
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'password': {'required': True},
        }
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            normal_avatar=settings.DEFAULT_USER_AVATAR,
            languagePreference='Türkçe'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
# Kullanıcı bilgilerini serileştirmek düzenlemek için kullanılır
class UserSerializer(serializers.ModelSerializer):
    matches = MatchSerializer(many=True, read_only=True)  # Maçları döndürmek için MatchSerializer'ı kullan
    class Meta:
        model = User
        fields = ['id', 'username','first_name', 'last_name', 'email', 'date_joined',
                'normal_avatar','intra_avatar', 'friends', 'has_logged_in', 'languagePreference', 'matches']

# Arkadaşlık isteklerini serileştirmek düzenlemek için kullanılır
class FriendRequestSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'user_role', 'status', 'timestamp']

    def get_user_role(self, obj):
        current_user_id = self.context['request'].user.id
        if obj.sender.id == current_user_id:
            return 'sender'
        elif obj.receiver.id == current_user_id:
            return 'receiver'
        else:
            return 'unknown'
    def get_sender(self, obj):
        # sender_id = obj.sender.id
        sender_username = obj.sender.username
        # return f"{sender_id} - {sender_username}"
        return sender_username
    def get_receiver(self, obj):
        # receiver_id = obj.receiver.id
        receiver_username = obj.receiver.username
        # return f"{receiver_id} - {receiver_username}"
        return receiver_username

class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=False, write_only=True, validators=[password_validation.validate_password])
    password2 = serializers.CharField(required=False, write_only=True)
    old_password = serializers.CharField(required=False, write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'old_password', 'password', 'password2', 'avatar')

    def validate(self, attrs):
        current_user = self.context['request'].user
        password = attrs.get('password')
        password2 = attrs.get('password2')
        old_password = attrs.get('old_password')
        if password is not None and password2 is not None:
            if password != password2:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        elif User.objects.exclude(pk=current_user.pk).filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        elif User.objects.exclude(pk=current_user.pk).filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})
        elif 'old_password' in attrs and not current_user.check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
        
        # Update standard user fields
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']
        instance.has_logged_in = False
        
        if 'avatar' in validated_data:
            instance.normal_avatar = validated_data['avatar']

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance
