from django.contrib import admin

from .models import User, auction_listings, comments, bids
# Register your models here.
admin.site.register(User)
admin.site.register(auction_listings)
admin.site.register(comments)
admin.site.register(bids)
