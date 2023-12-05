from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from bookapi.models import Book, AlienUser, Genre
from .users import AlienUserSerializer
from .genres import GenreSerializer


class SimpleBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "genre",
            "title",
            "image_url",
            "content",
            "author",
        ]


class BookSerializer(serializers.ModelSerializer):
    alien_user = AlienUserSerializer(many=False)
    is_owner = serializers.SerializerMethodField()
    genre = GenreSerializer(many=False)

    def get_is_owner(self, obj):
        # Check if the authenticated user is the owner
        return self.context["request"].user == obj.alien_user.user

    class Meta:
        model = Book
        fields = [
            "id",
            "alien_user",
            "genre",
            "title",
            "publication_date",
            "image_url",
            "content",
            "author",
            "is_owner",
        ]


class BookViewSet(viewsets.ViewSet):
    def list(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book, context={"request": request})
            return Response(serializer.data)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        alien_user = AlienUser.objects.get(user=request.auth.user)
        genre = Genre.objects.get(pk=request.data["genre"])
        title = request.data.get("title")
        publication_date = request.data.get("publication_date")
        image_url = request.data.get("image_url")
        content = request.data.get("content")
        author = request.data.get("author")

        # Create a book database row first, so you have a
        # primary key to work with
        book = Book.objects.create(
            # maybe issues with alien_user /  request.user
            alien_user=alien_user,
            genre=genre,
            title=title,
            publication_date=publication_date,
            image_url=image_url,
            content=content,
            author=author,
        )

        serializer = BookSerializer(book, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this book?
            self.check_object_permissions(request, book)

            serializer = SimpleBookSerializer(data=request.data)
            if serializer.is_valid():
                # book.alien_user = serializer.validated_data["alien_user"]
                book.genre = serializer.validated_data["genre"]
                book.title = serializer.validated_data["title"]
                # book.publication_date = serializer.validated_data["publication_date"]
                book.image_url = serializer.validated_data["image_url"]
                book.content = serializer.validated_data["content"]
                book.author = serializer.validated_data["author"]
                book.save()

                serializer = BookSerializer(book, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            self.check_object_permissions(request, book)
            book.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
