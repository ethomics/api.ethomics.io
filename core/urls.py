from graphene_file_upload.django import FileUploadGraphQLView
from graphene_django.views import GraphQLView
import django
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from core.schema import schema

urlpatterns = [
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]

if django.conf.settings.SERVE_FILES:
    urlpatterns += static(
        django.conf.settings.MEDIA_URL,
        document_root=django.conf.settings.MEDIA_ROOT
    )