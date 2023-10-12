from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class User(AbstractUser):
    description = models.TextField(blank=True, max_length=250)
    followers = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="user_followers")
    following = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="user_following")

    def __str__(self):
        return f"Profile of {self.username}"
    
    def follow(self, user_to_follow):
        self.following.add(user_to_follow)

    def unfollow(self, user_to_unfollow):
        self.following.remove(user_to_unfollow)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "description": self.description
        }

class Post(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="user_posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField('User', through='Like', related_name='like_posts', blank=True)

    def like(self, user_who_like):
        self.likes.add(user_who_like)
    
    def unlike(self, user_who_unlike):
        self.likes.remove(user_who_unlike)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes_count": self.likes.count(),
            # You can also include a list of user IDs who liked the post
            "likes_users": [like.user.id for like in self.likes.all()],
        }

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
    
class Like(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="like_users")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='like_posts')

    def __str__(self):
        return f"{self.user.username} likes {self.post.pk}"
    


    
