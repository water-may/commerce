from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass  

class Listing(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512, null=True)
    image = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    active = models.BooleanField()
    top_bid = models.FloatField()
    category = models.CharField(max_length=64, null=True)
    # bids = models.ForeignKey(Bid , on_delete=models.CASCADE, related_name="bids")
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lister")

class Watchlist(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    watchpost = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchpost")

class Comment(models.Model):
    comment = models.CharField(max_length=512)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    post = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="post")
    
class Bid(models.Model):  
    bid = models.FloatField()
    created = models.DateTimeField(auto_now_add=True, blank=True)

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="auction")
    
    def __str__(self):
        return f"{self.bid}"
 


    