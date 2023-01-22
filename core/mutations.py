from admin.models import AccountCreation
import time
import json
import graphene
from graphql import GraphQLError
from django.contrib.auth.hashers import check_password
from admin.models import AdminUser
from admin.models import AccountDeletion
from core.forms import *
from core.email import send_welcome_email, send_waiting_list_email
from core.arguments import create_mutation_arguments

class SignupMutation(graphene.Mutation):

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        name = graphene.String(required=True)
        lab_name = graphene.String(required=True)

    access_token = graphene.String()
    me = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        kwargs["is_pi"] = True
        form = SignupForm(kwargs)
        if form.is_valid():
            form.instance.last_login = time.time()
            form.save()
            AccountCreation.objects.create(email=form.instance.email)
            send_welcome_email(form.instance, info.context.META.get(
                "HTTP_ORIGIN", "https://ethomics.io"
            ))
            info.context.ethomics_refresh_token = form.instance.make_jwt(31536000)
            return SignupMutation(
                access_token=form.instance.make_jwt(900),
                me=form.instance
            )
        raise GraphQLError(json.dumps(form.errors))



class LoginMutation(graphene.Mutation):

    class Arguments:
        email = graphene.String()
        password = graphene.String()
    
    access_token = graphene.String()
    me = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        time.sleep(1)
        user = User.objects.filter(email=kwargs["email"]).first()
        if user:
            if check_password(kwargs["password"], user.password):
                info.context.ethomics_refresh_token = user.make_jwt(31536000)
                user.last_login = time.time()
                user.save()
                return LoginMutation(access_token=user.make_jwt(900), me=user)
        raise GraphQLError(json.dumps({"email": ["Invalid credentials"]}))



class LogoutMutation(graphene.Mutation):
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        info.context.ethomics_refresh_token = False
        return LogoutMutation(success=True)



class UpdateUserMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(UpdateUserForm)
    
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        form = UpdateUserForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdateUserMutation(user=form.instance)
        raise GraphQLError(json.dumps(form.errors))


    
class UpdatePasswordMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(UpdatePasswordForm)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        form = UpdatePasswordForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdatePasswordMutation(success=True)
        raise GraphQLError(json.dumps(form.errors))



class DeleteUserMutation(graphene.Mutation):

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user:
            user.delete()
            AccountDeletion.objects.create(email=user.email)
            return DeleteUserMutation(success=True)
        raise GraphQLError(json.dumps({"username": ["Invalid or missing token"]}))


class CreateDatasetMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(DatasetForm, members=graphene.List(graphene.ID), projects=graphene.List(graphene.ID))
    
    meeting = graphene.Field("core.queries.DatasetType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError('{"user": "Not authorized"}')
        kwargs["user"] = info.context.user.id
        for member_id in kwargs["members"]:
            if not info.context.user.members.filter(id=member_id):
                raise GraphQLError(
                    '{"members": ["Member ' + str(member_id) + ' does not exist"]}'
                )
        for project_id in kwargs.get("projects", []):
            if not info.context.user.projects.filter(id=project_id):
                raise GraphQLError(
                    '{"projects": ["Project ' + str(project_id) + ' does not exist"]}'
                )
        form = DatasetForm(kwargs)
        if form.is_valid():
            form.save()
            return CreateDatasetMutation(dataset=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class UpdateDatasetMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(DatasetForm, edit=True,  members=graphene.List(graphene.ID), projects=graphene.List(graphene.ID))
    
    dataset = graphene.Field("core.queries.DatasetType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError('{"user": "Not authorized"}')
        kwargs["user"] = info.context.user.id
        dataset = info.context.user.datasets.filter(id=kwargs["id"])
        if not dataset: raise GraphQLError('{"dataset": ["Does not exist"]}')
        dataset = dataset.first()
        for member_id in kwargs["members"]:
            if not info.context.user.members.filter(id=member_id):
                raise GraphQLError(
                    '{"members": ["Member ' + str(member_id) + ' does not exist"]}'
                )
        for project_id in kwargs.get("projects", []):
            if not info.context.user.projects.filter(id=project_id):
                raise GraphQLError(
                    '{"projects": ["Project ' + str(project_id) + ' does not exist"]}'
                )
        form = DatasetForm(kwargs, instance=dataset)
        if form.is_valid():
            form.save()
            return UpdateDatasetMutation(dataset=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class DeleteDatasetMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError('{"user": "Not authorized"}')
        dataset = info.context.user.datasets.filter(id=kwargs["id"])
        if not dataset: raise GraphQLError('{"dataset": ["Does not exist"]}')
        dataset.first().delete()
        return DeleteDatasetMutation(success=True)
