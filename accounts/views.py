from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect("dashboard")

            # Redirect to the next URL if it exists, otherwise redirect to a default URL
            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")
