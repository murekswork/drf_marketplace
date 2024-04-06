from api.mixins import StaffEditorPermissionMixin, UserQuerySetMixin
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Article
from .serializers import ArticleSerializer


class ArticleListView(UserQuerySetMixin, generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        qs = Article.objects.published().select_related("product")
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            "Your article is on review. Thanks!",
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ArticleDetailView(
    StaffEditorPermissionMixin, UserQuerySetMixin, generics.RetrieveAPIView
):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
