from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField()
    security_question = models.CharField(max_length=255)
    pic = models.ImageField(upload_to='pics/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    participants = models.ManyToManyField(User)

    @staticmethod
    def get_room_name(user1, user2):
        usernames = sorted([user1.username, user2.username])
        return ''.join(usernames)

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ''
