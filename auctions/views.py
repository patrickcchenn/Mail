from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, auction_listings, bids, comments
from django.core.exceptions import ObjectDoesNotExist


class create_form(forms.Form):
    name = forms.CharField(
        max_length=30, label="Listing Title", widget=forms.TextInput(attrs={'class': 'form'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Description'}), max_length=200, label="")
    starting_bid = forms.IntegerField(
        min_value=0, label="Starting Price", widget=forms.TextInput(attrs={'class': 'form'}))
    image_url = forms.URLField(
        required=False, widget=forms.TextInput(attrs={'class': 'form'}))
    category = forms.CharField(
        max_length=30, label="Category", widget=forms.TextInput(attrs={'class': 'form'}))


class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Comment'}), max_length=200, label="")


def index(request):
    return render(request, "auctions/index.html", {"listings": auction_listings.objects.all()})


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
        return render(request, "auctions/login.html")


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


@login_required
def create_listing(request):
    if request.method == "POST":
        form = create_form(request.POST)
        # insert into database
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            start_bid = form.cleaned_data['starting_bid']
            image = form.cleaned_data['image_url']
            category = form.cleaned_data['category']

            auction_listings.objects.create(
                name=name, creator=request.user, initial_price=start_bid, description=description, image_url=image, category=category)

            return HttpResponseRedirect(reverse("index"))

    else:
        form = create_form()
        return render(request, "auctions/create_listing.html", {'form': form})


def listing(request, listing_id):
    # try to get the bid/s for the active listing and will return none if bid/s doesn't exist
    try:
        bidss = bids.objects.filter(
            item=auction_listings.objects.get(id=listing_id)).latest('price')
    except ObjectDoesNotExist:
        bidss = None

    if request.method == "POST":
        # bid form is submitted
        if 'bid' in request.POST:
            new_bid = request.POST.get('place_bid', 0)
            bids.objects.create(item=auction_listings.objects.get(id=listing_id),
                                bidder=request.user,
                                price=int(new_bid)
                                )
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

        # watchlist button is pressed
        elif 'watchlist' in request.POST:
            # access the user and listing object in order to add watchlist
            user = request.user
            listing = auction_listings.objects.get(pk=listing_id)
            # check if the listing is already on the user watchlist. Add if yes remove otherwise.
            if listing in user.watchlist.all():
                user.watchlist.remove(listing)
            else:
                user.watchlist.add(listing)
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

        elif 'close' in request.POST:
            listing = auction_listings.objects.get(pk=listing_id)
            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))

    else:
        comment_form = CommentForm()
        commentt = comments.objects.filter(
            listing=auction_listings.objects.get(pk=listing_id))
        return render(request, "auctions/listing.html",
                      {'listing': auction_listings.objects.get(id=listing_id),
                       'user': request.user,
                       'bids': bidss,
                       'comment_form': comment_form,
                       'comments': commentt
                       })


@login_required
def watchlist(request):
    user = request.user
    return render(request, "auctions/index.html", {"listings": user.watchlist.all(), 'watchlist': "Watchlist"})


def category(request, category_):
    listings = auction_listings.objects.filter(category=category_)
    return render(request, "auctions/index.html", {"listings": listings, 'category': category_})


def comment(request, listing_id):
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            commentt = comment_form.cleaned_data['comment']

            comments.objects.create(
                message=commentt, name=request.user, listing=auction_listings.objects.get(id=listing_id))
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': listing_id}))


def categoriess(request):
    listingss = auction_listings.objects.all().values_list('category', flat=True)

    return render(request, "auctions/index.html", {"listings": listingss, 'categories': 'True'})
