from rest_framework import generics
from products.models import Product
from .serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserRegisterSerializer

@api_view(['GET'])
def api_root(request):
    return Response({
        "message": "Welcome to the B2B Hub API",
        "endpoints": {
            "products": "/api/products/",
            "auth_token": "/api/token/",
            "token_refresh": "/api/token/refresh/"
        }
    })
    
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Account created successfully. You can now log in."}, 
                status=status.HTTP_201_CREATED
            )
        # Return exactly what went wrong (e.g. username already taken)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)