from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        "auction_listings", blank=True, related_name="watchlist")


class auction_listings(models.Model):
    name = models.CharField(max_length=64)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="auction_lists")
    date_created = models.DateTimeField(auto_now_add="True")
    initial_price = models.PositiveIntegerField(null="True")
    description = models.CharField(max_length=200, null="True")
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=30, null="True")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class bids(models.Model):
    item = models.ForeignKey(
        auction_listings, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    price = models.PositiveIntegerField(null="True")

    def __str__(self):
        return f"${self.price}.00"


class comments(models.Model):
    message = models.CharField(max_length=100)
    name = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment")
    listing = models.ForeignKey(
        auction_listings, null="True", blank=True, on_delete=models.CASCADE, related_name="comment")

    def __str__(self):
        return f"{self.message}"
