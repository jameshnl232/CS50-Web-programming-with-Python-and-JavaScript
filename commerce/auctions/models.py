from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=20, decimal_places=2)
    current_bid = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    category = models.CharField(max_length=64, default=None)
    image = models.ImageField(upload_to='auctions/images')
    active = models.BooleanField(default=True)
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked", blank=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bid_auction_listing")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_amount = models.DecimalField(max_digits=20, decimal_places=2)
    bid_time = models.DateTimeField()

    def __str__(self):
        return f"{self.bidder} bidded {self.bid_amount} for {self.auction_listing}"

class Comment(models.Model):
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comment_auction_listing")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    text = models.TextField()
    comment_time = models.DateTimeField()
    
    def __str__(self):
        return f"{self.commenter} has commented on {self.auction_listing}"
    
class Category(models.Model):
    title = models.CharField(max_length=100)
    listings = models.ManyToManyField(AuctionListing, related_name="listings")

    def __str__(self):
        return f"{self.title}"