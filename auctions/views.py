from nis import cat
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F

from .models import *


def index(request):
    listings = Listing.objects.all().filter(active=True).order_by('-created_date')
    return render(request, "auctions/index.html", {'listings': listings})


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

def create_listing(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["bid"]
        image_url = request.POST["image_url"]
        category = Category.objects.get(title = request.POST["category"])
        owner = User.objects.get(id = request.user.id)

        new_listing = Listing.objects.create(
            title = title,
            description = description,
            starting_bid = starting_bid,
            image_url = image_url,
            category = category,
            owner = owner
        )
        new_listing.save()
        
        return render(request, "auctions/create.html", {
            'message': 'New Listing Added Successfully',
            'categories': categories
        })
    else:
        if request.user.is_authenticated:
            return render(request, "auctions/create.html", context)
        else:
            return render(request, "auctions/login.html")


def listing(request, id):
    # id that comes in is the id of the listing
    if request.method == "POST":
        listing = Listing.objects.get(id = id)
        latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
        bid = request.POST["bid"]

        if float(bid) > float(latest_bid[0].bid):
            user = User.objects.get(id = request.user.id)
            new_bid = Bid.objects.create(
                bid = bid,
                bidder = user,
                for_listing = listing
            )
            new_bid.save()
            # updating the M2M relationship between user and listing (through watchlist)
            user.watchlist.add(listing)
            user.save()
            return render(request, "auctions/listing.html", {
                'listing': listing,
                'message': 'Submitted Successfully',
                'latest_bid': latest_bid[0] if latest_bid else None,
            })
        else:
            return render(request, "auctions/listing.html", {
                'listing': listing,
                'message': 'You have to bid higher!',
                'latest_bid': latest_bid[0] if latest_bid else None,
            })
    else:
        listing = Listing.objects.get(id=id)
        comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')
        latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
        # users = User.objects.get(id = request.user.id)
        return render(request, "auctions/listing.html", {
            'listing': listing,
            'latest_bid': latest_bid[0] if latest_bid else None,
            'comments': comments
        })

def add_comment(request, id):
    if request.method == "POST":

        listing = Listing.objects.get(id=id)
        latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
        user = User.objects.get(id=request.user.id)

        new_comment = Comment.objects.create(
            text = request.POST["comment"],
            writer = user,
            for_listing = listing
        )
        new_comment.save()

        comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')

        return render(request, "auctions/listing.html", {
            'listing': listing,
            'latest_bid': latest_bid[0] if latest_bid else None,
            'comments': comments
        })

def watchlist(request):
    user = User.objects.get(id = request.user.id)
    watchlist = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {'watchlist': watchlist})

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories})

def category(request, category):
    category = Category.objects.get(title = category)
    listings = Listing.objects.all().filter(category=category.id)
    return render(request, "auctions/category.html", {
        'category': category,
        'listings': listings
    })