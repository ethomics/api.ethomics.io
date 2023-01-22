import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from .models import *

class UserType(DjangoObjectType):
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()
    lab = graphene.Field("core.queries.LabType")



class LabType(DjangoObjectType):
    
    class Meta:
        model = Lab
    
    id = graphene.ID()

class ProjectType(DjangoObjectType):
    
    class Meta:
        model = Project
    
    id = graphene.ID()
    color = graphene.String()

class DatasetType(DjangoObjectType):
    
    class Meta:
        model = Dataset
    id = graphene.ID()
    timezone = graphene.String()

class SearchType(graphene.ObjectType):

    projects = graphene.List(graphene.String)
    datasets = graphene.List(graphene.String)

    def resolve_projects(self, info, **kwargs):
        return []
        user = info.context.user
        return (
            user.projects.filter(name__icontains=self["term"])
          | user.projects.filter(description__icontains=self["term"])
        ).distinct()
    

    def resolve_datasets(self, info, **kwargs):
        return []
        user = info.context.user
        return (
            user.datasets.filter(title__icontains=self["term"])
          | user.datasets.filter(text__icontains=self["term"])
        ).distinct()

    # member = graphene.Field(
    #     "core.queries.LabMemberType", id=graphene.ID(required=True)
    # )
    dataset = graphene.Field(
        "core.queries.DatasetType", id=graphene.ID(required=True)
    )
    project = graphene.Field(
        "core.queries.ProjectType", id=graphene.ID(required=True)
    )

    def resolve_member(self, info, **kwargs):
        member = self.members.filter(id=int(kwargs["id"])).first()
        if member: return member
        raise GraphQLError('{"member": "Does not exist"}')
    

    def resolve_dataset(self, info, **kwargs):
        dataset = self.datasets.filter(id=int(kwargs["id"])).first()
        if dataset: return dataset
        raise GraphQLError('{"member": "Does not exist"}')
    

    def resolve_project(self, info, **kwargs):
        project = self.projects.filter(id=int(kwargs["id"])).first()
        if project: return project
        raise GraphQLError('{"project": "Does not exist"}')