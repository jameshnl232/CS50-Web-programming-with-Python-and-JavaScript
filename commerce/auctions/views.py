from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count


from .models import AuctionListing, Bid, Comment, Category
from django import forms



from .models import User


def index(request):
    return render(request, "auctions/index.html",{
        "listings": AuctionListing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html", {
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
class AuctionListingForm(forms.ModelForm):
    end_time = forms.DateTimeField(required=False,input_formats=['%Y-%m-%d %H:%M:%S'],widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM:SS'}))
    start_time = forms.DateTimeField(
        initial=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        input_formats=['%Y-%m-%d %H:%M:%S'],
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM:SS'})
    )
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'start_time',
                   'end_time', 'category', 'image']


@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST, request.FILES)
        if form.is_valid():
            auction_listing = form.save(commit=False)
            auction_listing.seller = request.user
            auction_listing.current_bid = request.POST["starting_bid"]
            auction_listing.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = AuctionListingForm()
    return render(request, "auctions/create_listings.html", {
        "form": form
    })

def display_listing(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    bid_count = Bid.objects.filter(auction_listing=listing).count()
    highest_bid = Bid.objects.filter(auction_listing=listing).order_by('bid_amount').first()
    winner = highest_bid.bidder if highest_bid else None
    comments = Comment.objects.filter(auction_listing=listing)
    if listing.active == False:
        return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_count": bid_count,
        "highest_bid": highest_bid,
        "winner": winner,
        "closed": True,
        "comments": comments
    })    
    if request.method == "POST":
        if 'Bid' in request.POST:  
            bid_amount = float(request.POST["Bid"])
            if bid_amount <= listing.current_bid:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "error": "Your bid has to be higher than current bid",
                    "bid_count": bid_count,
                    "comments": comments
                })
            else: 
                bid_count += 1
                bid = Bid(
                    auction_listing=listing,
                    bidder=request.user,  # Assuming the user is authenticated
                    bid_amount=bid_amount,
                    bid_time= datetime.datetime.now()  # Use the current date and time
                )
                bid.save()
                listing.current_bid = bid_amount
                listing.save()
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid, 
                    "bid_count": bid_count,
                    "comments": comments
                })
        elif 'comment' in request.POST:
            comment_text = request.POST["comment"]
            comment = Comment(
                auction_listing = listing,
                commenter=request.user,
                text=comment_text,
                comment_time=datetime.datetime.now()
            )
            comment.save()
            comments = Comment.objects.filter(auction_listing=listing)
            return HttpResponseRedirect(reverse('display_listing', args=(listing_id,)))
        
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_count": bid_count,
        "comments": comments
    })

    
@login_required
def close_listing(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    if request.user.is_authenticated and request.user == listing.seller:
        listing.active = False
        listing.save()
    return HttpResponseRedirect(reverse('display_listing', args=[listing_id]))

@login_required
def add_to_watchlist(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        listing = AuctionListing.objects.get(pk=listing_id)
        if request.user in listing.liked.all():
            listing.liked.remove(request.user)
        else:
            listing.liked.add(request.user)
        return render(request, "auctions/watchlist.html", {
            "listings": request.user.liked.all()
        })
    
def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, "auctions/watchlist.html", {
            "listings": request.user.liked.all()
        })


def category(request):
    listings = AuctionListing.objects.all()
    for listing in listings:
        category, created = Category.objects.get_or_create(title=listing.category)
        category.listings.add(listing)
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def display_listing_category(request, category):
    category = Category.objects.get(title=category)
    listings = category.listings.all()
    return render(request, "auctions/category_listing.html", {
        "category": category,
        "listings": listings
    })
