from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from bookapi.models import AlienUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name", "email"]
        extra_kwargs = {"password": {"write_only": True}}


class AlienUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AlienUser
        fields = ("user", "profile_image_url", "bio")


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["post"], url_path="register")
    def register_account(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                email=serializer.validated_data["email"],
            )
            alien_user = AlienUser.objects.create(
                user=user,
                profile_image_url=request.data.get(
                    "profile_image_url",
                    "https://lparchive.org/Gazillionaire-Deluxe/Update%2051/13-pilot.png",
                ),
                bio=request.data.get("bio", "Hey, I am new to Divergent Branch Books!"),
            )
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def user_login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token = Token.objects.get(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="currentUser")
    def get_alien_user(self, request):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Filter ALienUser objects for the current authenticated user
        alien_user = AlienUser.objects.filter(user=request.user).first()

        # Check if the Alien User exists
        if alien_user:
            serializer = AlienUserSerializer(alien_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Alien User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def list(self, request):
        alien_users = AlienUser.objects.all()
        serializer = AlienUserSerializer(alien_users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            alien_user = AlienUser.objects.get(pk=pk)
            serializer = AlienUserSerializer(alien_user, context={"request": request})
            return Response(serializer.data)

        except alien_user.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["put"], url_path="currentUser/update")
    def update_alien_user_profile(self, request, pk=None):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            alien_user = AlienUser.objects.filter(user=request.user).first()
        except AlienUser.DoesNotExist:
            return Response(
                {
                    "error": "Alien User not found or you don't have permission to modify this user's profile"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update profile_image_url and bio if provided in the request data
        if "profile_image_url" in request.data:
            alien_user.profile_image_url = request.data["profile_image_url"]
        if "bio" in request.data:
            alien_user.bio = request.data["bio"]

        alien_user.save()  # Save the changes to the database

        # Serialize the updated alien_user data and return it in the response
        serializer = AlienUserSerializer(alien_user)
        return Response(serializer.data, status=status.HTTP_200_OK)
