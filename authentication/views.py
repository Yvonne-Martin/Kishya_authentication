
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = token.get("userinfo")

    user = User.objects.filter(email=user_info["email"]).first()

    if user:
        login(request, user)
        return redirect(request.build_absolute_uri(reverse("index")))
    else:
        messages.error(request, "Account does not exist. Do you want to sign up?")
        return redirect("register")

def register(request):
    user_info = request.session.get("user_info")

    if request.method == "POST":
        username = user_info["email"]
        password = User.objects.make_random_password()

        user, created = User.objects.get_or_create(username=username, email=user_info["email"])
        if created:
            user.set_password(password)
            user.save()
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "User already exists.")
            return redirect("login")

    return render(request, "authentication/register.html", {"user_info": user_info})

def logout(request):
    request.session.clear()
    return redirect(
        f"http://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def index(request):
    return render(
        request,
        "authentication/index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

