from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Watchlist


def index(request):
    listing = Listing.objects.filter(active=True)
    
    return render(request, "auctions/index.html", {
        "listings": listing
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

    cuser = request.user
    if request.method == "POST":
        # Get data from create_listing form 
        title = request.POST['title']
        description = request.POST['description']
        start_bid = int(request.POST['bid'])
        image = request.POST['image']
        
        category = request.POST['category']
        if category == "none":
            category = None

        # Add listing to Lisging model.
        user = User.objects.get(id=cuser.id)
        new_listing = Listing.objects.create(name=title, category=category, top_bid=start_bid, description=description, image=image, lister=user, active=True)
        new_listing.save()

        # Add start bid to Bid model.
        auction = Listing.objects.get(pk=new_listing.id)
        bid = Bid.objects.create(bid=start_bid, bidder=user, auction=auction)
        bid.save()

        # Return to the auction view page after successfully creating the auction
        return HttpResponseRedirect(reverse(f"index"))
    else:
        if cuser.is_authenticated:
            return render(request, "auctions/create_listing.html")
        else:
            return render(request, "auctions/login.html", {
                "message": "You need to login to add any auction listing."
            })

def listing(request, auction_id):
   
    listing = Listing.objects.get(pk=int(auction_id))

    try:
        comments = Comment.objects.filter(post=listing)
    except: 
        comments = None

    # Throws error if expected listing does not exist.
    try:
        bid_count = Bid.objects.filter(auction=listing).count()
        highest_bid = Bid.objects.filter(auction=listing).latest('id')
    except:
        return render(request, "auctions/fourerror.html", {
            "message": "404 Page not found"
        })

    if request.method == "POST":
        # Updating Bid.
        new_bid = request.POST['bid']
        user = request.user
    
        if float(highest_bid.bid) < float(new_bid):
            if user.is_authenticated:
            
                # Full Success of bid updating
                bid = Bid.objects.create(bid=new_bid, bidder=user, auction=listing)
                bid.save()
                highest_bid = float((Bid.objects.filter(auction=listing).latest('id')).bid)
                bid_count =  Bid.objects.filter(auction=listing).count()

                # Updating top bid on Auction Model
                listing.top_bid = highest_bid
                listing.save()

                return HttpResponseRedirect(reverse("listing", args=[auction_id]))
            else:
                return render(request, 'acutions/login.html', {
                    "message": "You must be loged in to bid."
                })    
        else:
            return HttpResponseRedirect(reverse("listing", args=[auction_id]))
    
    else:
        try:
            watch = Watchlist.objects.filter(watcher=request.user, watchpost=listing)
        except:
            watch = None
        # GET listing Page
        print(highest_bid.bidder)
        print(request.user)
        return render(request, "auctions/listing.html", {
            "user": request.user,
            "listings": listing,
            "highest_bid": highest_bid,
            "bid_count": bid_count,
            "watch": watch,
            "comments": comments
        })

@login_required
def watchlist(request):
    user = request.user
    watches = Watchlist.objects.filter(watcher=user)   

    if request.method == "POST":
        auction_id = int(request.POST['x'])
        auction = Listing.objects.get(id=auction_id)
        watch = request.POST['watch']
        
        if watch == 'false':
            new_watch = Watchlist.objects.create(watcher=user, watchpost=auction)
            new_watch.save()
        elif watch == 'true':
            print("i was here")
            old_watch = Watchlist.objects.get(watcher=user, watchpost=auction)
            old_watch.delete()

        return HttpResponseRedirect(reverse("listing", args=[auction_id]))
    else:
        return render(request, 'auctions/watches.html', {
            "watches": watches
        })

def close_list(request, auction_id):
    if request.method == 'POST':
        auction = Listing.objects.get(id=auction_id)
        auction.active = False
        auction.save()
    
    return HttpResponseRedirect(reverse("listing", args=[auction_id]))
        
def comment(request, auction_id):
    if request.method == "POST":
        comment = request.POST['comment']
        commenter = request.user
        post = Listing.objects.get(id=auction_id)

        Comment.objects.create(comment=comment, commenter=commenter, post=post).save()
    
    return HttpResponseRedirect(reverse("listing", args=[auction_id]))
    
def categories(request):
    categories = set(Listing.objects.values_list('category'))
    cats = []
    for category in categories:
        if category[0]:
            cats.append(category[0].capitalize())

    print(cats)
    return render(request, "auctions/categories.html", {
        "categories": cats
    })

def category(request, cat):
    try:
        listings = Listing.objects.filter(category=cat.lower(), active=True)
    except:
        return HttpResponseRedirect(reverse("categories"))

    return render(request, "auctions/category.html", {
        "listings": listings
    })
    