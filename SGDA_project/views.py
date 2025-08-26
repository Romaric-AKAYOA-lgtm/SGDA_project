from django.shortcuts import render

# 1. Consulter
def home_view(request):
    return render(request, 'home.html')

def base_html(request):
    return render(request, "base.html")  # Remplace par le bon chemin si nécessaire
