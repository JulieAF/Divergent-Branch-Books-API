from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework import serializers
from bookapi.models import Review, AlienUser, Book
from .users import AlienUserSerializer
from .books import BookSerializer


class SimpleReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "content",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    alien_user = AlienUserSerializer(many=False)
    is_owner = serializers.SerializerMethodField()
    book = BookSerializer(many=False)

    def get_is_owner(self, obj):
        # Check if the authenticated user is the owner
        return self.context["request"].user == obj.alien_user.user

    class Meta:
        model = Review
        fields = [
            "id",
            "book",
            "alien_user",
            "content",
            "is_owner",
            "created_on",
        ]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the object.
        return obj.alien_user.user == request.user


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def list(self, request):
        comments = Review.objects.all()
        serializer = ReviewSerializer(comments, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk)
            serializer = ReviewSerializer(review, context={"request": request})
            return Response(serializer.data)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        book = Book.objects.get(pk=request.data["book"])
        alien_user = AlienUser.objects.get(user=request.auth.user)
        content = request.data.get("content")
        created_on = request.data.get("created_on")

        # Create a review database row first, so you have a
        # primary key to work with
        review = Review.objects.create(
            # maybe issues with book /  request.user
            book=book,
            alien_user=alien_user,
            content=content,
            created_on=created_on,
        )

        serializer = ReviewSerializer(review, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this review?
            self.check_object_permissions(request, review)

            serializer = SimpleReviewSerializer(data=request.data)
            if serializer.is_valid():
                # review.book = serializer.validated_data["book"]
                # review.alien_user = serializer.validated_data["alien_user"]
                review.content = serializer.validated_data["content"]
                # review.created_on = serializer.validated_data["created_on"]
                review.save()

                serializer = ReviewSerializer(review, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk)
            self.check_object_permissions(request, review)
            review.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
