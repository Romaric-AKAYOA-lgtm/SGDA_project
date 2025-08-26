from django.shortcuts import render

# 1. Consulter
def referentiel_view(request):
    return render(request, 'referentiel/home_view.html')
