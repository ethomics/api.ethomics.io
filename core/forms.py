from django.db.models.base import Model
from django.forms import ModelForm, ModelMultipleChoiceField, CharField
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import *

class SignupForm(ModelForm):
    """Creates a user object."""

    class Meta:
        model = User
        fields = ["email", "name", "password", "is_pi"]

    lab_name = CharField()


    def clean_email(self):
        """Lower cases the email."""

        email = self.data["email"].lower()
        from admin.models import WaitingUser
        if not WaitingUser.objects.filter(approved=True, email=email).count():
            self.add_error("email", "Email not approved yet.")
        return email
    

    def clean_lab_name(self):
        lab_name = self.data["lab_name"]
        max_length = Lab._meta.get_field("name").max_length
        if len(lab_name) > max_length:
            self.add_error("lab_name", f"Lab name should be less than {max_length} characters.")
        return lab_name


    def clean_password(self):
        """Runs the password validators specified in settings."""

        validate_password(self.data["password"])
        return self.data["password"]

        
    def save(self):
        """Hash password before saving."""

        user = ModelForm.save(self, commit=False)
        user.set_password(self.cleaned_data.get("password"))
        user.lab = Lab.objects.create(name=self.cleaned_data["lab_name"])
        user.save()


 
class UpdateUserForm(ModelForm):
    """Edits the basic fields of a user."""

    class Meta:
        model = User
        fields = ["name", "email"]
    

    def clean_email(self):
        """Lower cases the email."""

        return self.data["email"].lower()



class UpdatePasswordForm(ModelForm):
    """Edits the password field of a user, and nothing else. Requires the
    current password."""

    class Meta:
        model = User
        fields = []
    
    current = CharField(required=True)
    new = CharField(required=True)

    def clean_current(self):
        """Checks that the supplied current password is currect."""

        if not check_password(self.data["current"], self.instance.password):
            self.add_error("current", "Current password not correct.")
        return self.data["current"]


    def clean_new(self):
        """Runs the password validators specified in settings."""

        validate_password(self.data["new"])
        return self.data["new"]


    def save(self):
        self.instance.set_password(self.cleaned_data.get("new"))



class DatasetForm(ModelForm):

    class Meta:
        model = Dataset
        exclude = ["id"]
    
    projects = ModelMultipleChoiceField(queryset=Project.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields["members"].required = False
    

    def save(self, *args, **kwargs):
        ModelForm.save(self, *args, **kwargs)
        for project in self.instance.projects.all():
            self.instance.projects.remove(project)
        for project in self.cleaned_data["projects"]:
            self.instance.projects.add(project)



class ProjectForm(ModelForm):

    class Meta:
        model = Project
        exclude = ["id"]
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields["datasets"].required = False
        self.fields["members"].required = False