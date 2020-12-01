from rest_framework import generics as rest_generics
from rest_framework import status
from rest_framework.response import Response


class CreateAPIView(rest_generics.CreateAPIView):
    def get_response_serializer_class(self, instance):
        if hasattr(self, 'response_serializer_class'):
            return self.response_serializer_class

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        if hasattr(self, 'get_response_serializer_class') and (
            serializer_klass := self.get_response_serializer_class(instance)
        ):
            serializer = serializer_klass(instance)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
