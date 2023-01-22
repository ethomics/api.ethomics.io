from email.policy import default
import time
import jwt
import base64
from datetime import datetime
from timezone_field import TimeZoneField
from django_random_id_model import RandomIDModel
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password

def create_filename(instance, filename):
    """Creates a filename for some uploaded file, from the owning object's ID,
    and class name."""
    
    extension = "." + filename.split(".")[-1] if "." in filename else ""
    hashed_class = base64.b64encode(instance.__class__.__name__.encode())
    return f"{instance.id}{hashed_class}{extension}"

class Lab(RandomIDModel):

    class Meta:
        db_table = "labs"

    name = models.CharField(max_length=150)
    created = models.IntegerField(default=time.time)
    
    def __str__(self):
        return self.name

class User(RandomIDModel):

    class Meta:
        db_table = "users"
        ordering = ["created"]
    
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=100)
    is_pi = models.BooleanField(default=False)
    email = models.EmailField(max_length=200, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    image = models.FileField(null=True, blank=True, upload_to=create_filename)
    last_login = models.IntegerField(null=True, default=None)
    created = models.IntegerField(default=time.time)
    joined = models.IntegerField(default=None, null=True)
    lab = models.ForeignKey("core.Lab", related_name="users", null=True, on_delete=models.CASCADE)
    api_key = models.CharField(default=None, max_length=128, null=True, blank=True)


    def __str__(self):
        return self.name
    

    @staticmethod
    def from_token(token):
        """Takes a JWT, and if it's signed properly, isn't expired, and points
        to an actual user, returns that user."""

        try:
            token = jwt.decode(token, settings.SECRET_KEY)
            assert token["expires"] > time.time()
            user = User.objects.get(id=token["sub"])
        except: user = None
        return user
    

    def set_password(self, password):
        """"Sets the user's password, salting and hashing whatever is given
        using Django's built in functions."""

        self.password = make_password(password)
        self.save()
    

    def make_jwt(self, ttl):
        """Creates and signs a token indicating the user who signed and the time
        it was signed. It will also indicate when it expires."""
        
        now = int(time.time())
        return jwt.encode({
            "sub": self.id, "iat": now, "expires": now + ttl
        }, settings.SECRET_KEY, algorithm="HS256").decode()



class Dataset(RandomIDModel):

    class Meta:
        db_table = "datasets"
        ordering = ["-timestamp"]

    timestamp = models.FloatField()
    timezone = TimeZoneField()
    title = models.CharField(max_length=100)
    text = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name="datasets")
    lab = models.ForeignKey(Lab, related_name="meetings", on_delete=models.CASCADE)

    def __str__(self):
        date = datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d')
        users = self.users.all()
        if not users: return f"{date} Dataset"
        return f"{date} ({', '.join([u.name for u in users])})"



class Project(RandomIDModel):

    class Meta:
        db_table = "projects"
    
    name = models.CharField(max_length=60)
    description = models.TextField()
    color = models.CharField(max_length=7, validators=[RegexValidator("^#(?:[0-9a-fA-F]{3}){1,2}$")])
    users = models.ManyToManyField(User, related_name="projects")
    dataset = models.ManyToManyField(Dataset, related_name="projects")
    lab = models.ForeignKey(Lab, related_name="projects", on_delete=models.CASCADE)

    def __str__(self):
        return self.name