from rest_framework import viewsets, status
from rest_framework import serializers
from rest_framework.response import Response
from bookapi.models import Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "label"]


class GenreViewSet(viewsets.ViewSet):
    def list(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            genre = Genre.objects.get(pk=pk)
            serializer = GenreSerializer(genre)
            return Response(serializer.data)
        except Genre.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        label = request.data.get("label")

        # Create a comment database row first, so you have a
        # primary key to work with
        genre = Genre.objects.create(
            # maybe issues with label /  request.user
            label=label
        )

        serializer = GenreSerializer(genre, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            genre = Genre.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this genre?
            self.check_object_permissions(request, genre)

            serializer = GenreSerializer(data=request.data)
            if serializer.is_valid():
                genre.label = serializer.validated_data["label"]
                # genre.created_on = serializer.validated_data["created_on"]
                genre.save()

                serializer = GenreSerializer(genre, context={"request": request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Genre.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            genre = Genre.objects.get(pk=pk)
            self.check_object_permissions(request, genre)
            genre.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Genre.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
