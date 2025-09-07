
from django.shortcuts import render
from django.db.models import  Sum, Avg
from Gestion_adherent.Cotisation_adherent.models import Cotisation
from Gestion_adherent.Inscription_adherent.adherent.models import Adherent
from Gestion_adherent.Inscription_adherent.suiviTuteurAdherent.models import SuiviTuteurAdherent
from Gestion_adherent.Inscription_adherent.tuteur.models import Tuteur
from Gestion_adherent.Prise_en_charge_adherent.models import PriseEnChargeAdherent
from django.utils import timezone

# Create your views here.
def Gestion_adherent_view(request):
    return render(request, 'Gestion_adherent/home_Gestion_adherent.html')

def statistic_adherent_view(request):
    now = timezone.now()
    # ===============================
    # ADHERENTS
    # ===============================
    adherents = Adherent.objects.filter(
        date_creation__year=now.year,
        date_creation__month=now.month
    )
    adherent_by_id = Adherent.objects.filter(id=1).first()
    adherents_with_pere = Adherent.objects.filter(pere__isnull=False)
    adherents_with_mere_name = Adherent.objects.filter(mere__last_name="Mbemba")
    nb_adherents = Adherent.objects.count()

    adherent_stats = {
        "all": adherents,
        "by_id": adherent_by_id,
        "with_pere": adherents_with_pere,
        "with_mere_name": adherents_with_mere_name,
        "count": nb_adherents,
    }

    # ===============================
    # TUTEURS
    # ===============================
    tuteurs = Tuteur.objects.filter(
        date_creation__year=now.year,
        date_creation__month=now.month
    )
    tuteur_by_id = Tuteur.objects.filter(id=1).first()
    tuteurs_ordered = Tuteur.objects.order_by("last_name")
    nb_tuteurs = Tuteur.objects.count()
    enfants_pere = tuteur_by_id.enfants_pere.all() if tuteur_by_id else []
    enfants_mere = tuteur_by_id.enfants_mere.all() if tuteur_by_id else []

    tuteur_stats = {
        "all": tuteurs,
        "by_id": tuteur_by_id,
        "ordered": tuteurs_ordered,
        "count": nb_tuteurs,
        "enfants_pere": enfants_pere,
        "enfants_mere": enfants_mere,
    }

    # ===============================
    # SUIVI TUTEUR - ADHERENT
    # ===============================
    suivis = SuiviTuteurAdherent.objects.filter(
        date_creation__year=now.year,
        date_creation__month=now.month
    )
    suivis_pere = SuiviTuteurAdherent.objects.filter(statut="pere")
    nb_suivis = SuiviTuteurAdherent.objects.count()

    suivis_stats = {
        "all": suivis,
        "pere": suivis_pere,
        "count": nb_suivis,
    }

    # ===============================
    # COTISATIONS
    # ===============================

    # Cotisations du mois et de l'année en cours
    cotisations = Cotisation.objects.filter(
        date_cotisation__year=now.year,
        #date_cotisation__month=now.month
    )

    cotisations_valides = Cotisation.objects.filter(statut="valide")
    total_cotisations = Cotisation.objects.aggregate(Sum("montant"))["montant__sum"]
    moyenne_mensuelle = Cotisation.objects.filter(type_cotisation="mensuelle").aggregate(Avg("montant"))["montant__avg"]

    cotisation_stats = {
        "all": cotisations,
        "valides": cotisations_valides,
        "total": total_cotisations,
        "moyenne_mensuelle": moyenne_mensuelle,
    }

    # ===============================
    # PRISES EN CHARGE
    # ===============================
    prises = PriseEnChargeAdherent.objects.filter(
        date_creation__year=now.year,
        #date_creation__month=now.month
    )

    last_five_prises = PriseEnChargeAdherent.objects.order_by("-date_creation")[:5]
    prises_with_medecin = PriseEnChargeAdherent.objects.filter(operation_medecin__isnull=False)
    nb_prises = PriseEnChargeAdherent.objects.count()

    prise_en_charge_stats = {
        "all": prises,
        "last_five": last_five_prises,
        "avec_medecin": prises_with_medecin,
        "count": nb_prises,
    }


    # ===============================
    # CONTEXT GLOBAL
    # ===============================
    context = {
        "adherent_stats": adherent_stats,
        "tuteur_stats": tuteur_stats,
        "suivi_stats": suivis_stats,
        "cotisation_stats": cotisation_stats,
        "prise_en_charge_stats": prise_en_charge_stats,
    }

    return render(request, 'Gestion_adherent/statistique_Gestion_adherent.html', context)
