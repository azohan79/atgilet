from django.shortcuts import render

def maintenance_page(request):
    return render(request, "maintenance/index.html")
