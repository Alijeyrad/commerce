from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name='watchlist', blank=True)
    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"

class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.FloatField(default=0)
    image_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="owner")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} by {self.owner}"


class Comment(models.Model):
    text = models.CharField(max_length=255)
    time_added = models.DateTimeField(auto_now_add=True)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    for_listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

class Bid(models.Model):
    bid = models.FloatField()
    time_added = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    for_listing = models.ForeignKey(Listing, on_delete=models.CASCADE)