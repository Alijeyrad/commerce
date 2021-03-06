from nis import cat
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
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
        category = Category.objects.get(code = request.POST["category"])
        owner = User.objects.get(id = request.user.id)

        is_valid = title and description and starting_bid and category

        if image_url == '':
            image_url = 'https://dummyimage.com/200x200/000/fff.jpg&text=NoImage'

        if is_valid:
            new_listing = Listing.objects.create(
                title = title,
                description = description,
                starting_bid = starting_bid,
                image_url = image_url,
                category = category,
                owner = owner
            )
            new_listing.save()
            message = 'New Listing Added Successfully'
        else:
            message = "Required fields shouldn't be empty"

        return render(request, "auctions/create.html", {
            'message': message,
            'categories': categories
        })
    else:
        if request.user.is_authenticated:
            return render(request, "auctions/create.html", context)
        else:
            return render(request, "auctions/login.html")

def listing(request, id):
    # id that comes in is the id of the listing
    listing = Listing.objects.get(id=id)
    comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')
    latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'latest_bid': latest_bid[0] if latest_bid else None,
        'comments': comments
    })

def add_bid(request, id):
    # incoming id is listing id
    if request.method == "POST":
        listing = Listing.objects.get(id = id)
        comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')
        latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
        bid = request.POST["bid"]
        user = User.objects.get(id = request.user.id)
        message = ''
        # create a new bid if it's valid
        if latest_bid:
            # this is when there are previous bids
            # so we'll create the bid if it's higher than the latest bid
            if latest_bid[0].bid < float(bid):
                new_bid = Bid.objects.create(
                    bid = bid,
                    bidder = user,
                    for_listing = listing
                )
                new_bid.save()

                # updating the M2M relationship between user and listing (through watchlist)
                user.watchlist.add(listing)
                user.save()
                message = 'Submitted Successfully'
                latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
            else:
                message = 'You have to bid higher than the last price. Try again.'
                
        elif listing.starting_bid < float(bid):
            # this is when there is no previous bid
            # so we'll create the bid if it's higher than starting bid
            new_bid = Bid.objects.create(
                    bid = bid,
                    bidder = user,
                    for_listing = listing
                )
            new_bid.save()

            # updating the M2M relationship between user and listing (through watchlist)
            user.watchlist.add(listing)
            user.save()
            message = 'Submitted Successfully'
            latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
        
        else:
            message = 'You have to bid higher than the last price. Try again.'


        return render(request, "auctions/listing.html", {
            'listing': listing,
            'message': message,
            'latest_bid': latest_bid[0] if latest_bid else None,
            'comments': comments
        })

def add_comment(request, id):
    if request.method == "POST":

        listing = Listing.objects.get(id=id)
        latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')
        user = User.objects.get(id=request.user.id)
        text = request.POST["comment"]
        if text.strip() == '':
            comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')
            return render(request, "auctions/listing.html", {
                'listing': listing,
                'latest_bid': latest_bid[0] if latest_bid else None,
                'comments': comments
            })

        new_comment = Comment.objects.create(
            text = text,
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

@login_required
def watchlist(request):
    user = User.objects.get(id = request.user.id)
    watchlist = user.watchlist.all()

    bids = []
    current_bids = []
    for listing_obj in watchlist:
        bid = Bid.objects.filter(for_listing=listing_obj, bidder=user).order_by('-time_added').first()
        bids.append(bid)

    for listing_obj in watchlist:
        current_bid = Bid.objects.filter(for_listing=listing_obj).order_by('-time_added').first()
        current_bids.append(current_bid)

    return render(request, "auctions/watchlist.html", {
        'watchlist': watchlist,
        'bids': bids,
        'current_bids': current_bids
    })

@login_required
def remove_watchlist(request, id):
    user = User.objects.get(id = request.user.id)
    listing = Listing.objects.get(id=id)
    # remove listing from user's watchlist
    user.watchlist.remove(id)
    # find the corresponding bid
    bid = Bid.objects.filter(bidder=user, for_listing=listing)
    bid.delete()
    # remove user's bid from listing's bid
    watchlist = user.watchlist.all()

    bids = []
    current_bids = []
    for listing_obj in watchlist:
        bid = Bid.objects.filter(for_listing=listing_obj, bidder=user).order_by('-time_added').first()
        bids.append(bid)

    for listing_obj in watchlist:
        current_bid = Bid.objects.filter(for_listing=listing_obj).order_by('-time_added').first()
        current_bids.append(current_bid)

    comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')
    latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'latest_bid': latest_bid[0] if latest_bid else None,
        'comments': comments
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories})

def category(request, category):
    category = Category.objects.get(title = category)
    listings = Listing.objects.all().filter(category=category.id).order_by('-created_date')
    return render(request, "auctions/category.html", {
        'category': category,
        'listings': listings
    })

@login_required
def close_listing(request, id):
    # id that comes in is the id of the listing
    listing = Listing.objects.get(id=id)
    comments = Comment.objects.all().filter(for_listing=listing).order_by('-time_added')
    latest_bid = Bid.objects.all().filter(for_listing=listing.id).order_by('-time_added')

    listing.active = False
    listing.save()

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'latest_bid': latest_bid[0] if latest_bid else None,
        'comments': comments
    })