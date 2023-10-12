from django.contrib import admin
from .models import AuctionListing, Bid, Comment

# Register your models here.

class AuctionListingAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ("id", "title", "description", "starting_bid", "current_bid",
                     "start_time", "end_time", "seller", "category", "image")

admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Comment)
