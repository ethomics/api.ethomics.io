import pytz
import graphene
from graphql import GraphQLError
from core.mutations import *

class Query(graphene.ObjectType):
    """The root query object. It supplies the user attribute, which is the
    portal through which other attributes are accessed."""

    access_token = graphene.String()
    me = graphene.Field("core.queries.UserType")
    search = graphene.Field("core.queries.SearchType", term=graphene.String(required=True))

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        if not user: return None
        return info.context.user


    def resolve_access_token(self, info, **kwargs):
        token = info.context.COOKIES.get("ethomics_refresh_token")
        if not token:
            raise GraphQLError(json.dumps({"token": "No refresh token supplied"}))
        user = User.from_token(token)
        if user:
            info.context.ethomics_refresh_token = user.make_jwt(31536000)
            return user.make_jwt(900)
        raise GraphQLError(json.dumps({"token": "Refresh token not valid"}))
    

    def resolve_search(self, info, **kwargs):
        if len(kwargs["term"]) < 3:
            raise GraphQLError('{"term": "Must be at least three characters"}')
        return kwargs




class Mutation(graphene.ObjectType):
    signup = SignupMutation.Field()
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()

    update_user = UpdateUserMutation.Field()
    update_password = UpdatePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
    

schema = graphene.Schema(query=Query, mutation=Mutation)
