from api.mixins import StaffEditorPermissionMixin, UserQuerySetMixin
from rest_framework import generics

from .models import Article
from .serializers import ArticleSerializer


class ArticleListView(UserQuerySetMixin, generics.ListCreateAPIView):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        qs = Article.objects.published()
        return qs


class ArticleDetailView(StaffEditorPermissionMixin, UserQuerySetMixin, generics.RetrieveAPIView):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
