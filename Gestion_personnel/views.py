from django.utils import timezone
from django.shortcuts import render

from Gestion_personnel.absence.models import Absence

from Gestion_personnel.employe.models import Employe
from Gestion_personnel.operation.models import Operation

# 1. Consulter
def Gestion_personnel_view(request):
    return render(request, 'Gestion_personnel/home_Gestion_personnel.html')



def statistic_personnel_view(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year
    # ---------------------------
    # Employés
    # ---------------------------
    employes = Employe.objects.filter(
        date_creation__year=current_year,
        #date_creation__month=current_month
    ).order_by('-date_creation')
    employes=employes.order_by('-date_creation')
    employes_actifs = employes.filter(statut="actif")

    # Année en cours
    current_year = timezone.now().year

    # Employés qui partent à la retraite cette année (âge 60 par exemple)
    employes_retraite = employes.filter(date_naissance__year=current_year - 60)

    employes_stats = {
        'total_employes': employes.count(),
        'total_actifs': employes_actifs.count(),
        'employes_tries': employes.order_by('last_name'),
        'employes_values': employes.values('first_name','last_name','matricule','grade','categorie','statut','date_creation'),
        'employes_actifs_triees': employes_actifs.order_by('last_name').values('first_name','last_name','matricule','grade','categorie'),
        'employes_retraite': employes_retraite.values('first_name','last_name','matricule','date_naissance','grade','categorie'),
    }


    # ---------------------------
    # Opérations
    # ---------------------------
    operations = Operation.objects.filter(
        date_debut__year=current_year,
       # date_debut__month=current_month
    ).order_by('-date_debut')
    operations_recentes = operations.order_by('-date_creation')[:5]

    operations_stats = {
        'operations': operations,
        'operations_recentes': operations_recentes,
        'operations_confirmees': operations.filter(statut='confirme'),
        'operations_annulees': operations.filter(statut='annule'),
        'operations_recrutement': operations.filter(type_operation='affectation'),
        'operations_mutation': operations.filter(type_operation='mutation'),
        'operations_date_debut': operations.filter(date_debut__gte=timezone.now()),
        'operations_date_fin': operations.filter(date_fin__lte=timezone.now()),
        'operations_tries': operations.order_by('-date_creation'),
        'operations_values': operations.values('id','numero_fiche','numero_note','type_operation','statut','id_employe__first_name','id_employe__last_name','id_fonction__designation','id_organisation_unite__designation','date_debut','date_fin','date_creation'),
        'total_operations': operations.count(),
        'total_confirmees_operations': operations.filter(statut='confirme').count(),
        'total_recentes_operations': operations_recentes.count(),
    }

    # ---------------------------
    # Absences
    # ---------------------------
    absences = Absence.objects.filter(
        date_creation__year=current_year,
       # date_creation__month=current_month
    ).order_by('-date_creation')
    absences_recentes = absences.order_by('-date_creation')[:5]

    absences_stats = {
        'absences': absences,
        'absences_recentes': absences_recentes,
        'absences_conge_annuel': absences.filter(type_absence='conge_annuel'),
        'absences_imprevue': absences.filter(type_absence='absence_imprevue'),
        'absences_confirmees': absences.filter(statut='confirme'),
        'absences_annulees': absences.filter(statut='annule'),
        'absences_en_cours': absences.filter(statut='en_cours'),
        'absences_terminees': absences.filter(statut='termine'),
        'absences_date_debut': absences.filter(date_debut__gte=timezone.now()),
        'absences_date_retour': absences.filter(date_retour__lte=timezone.now()),
        'absences_tries': absences.order_by('-date_creation'),
        'absences_values': absences.values(
            'id',
            'type_absence',
            'statut',
            'date_debut',
            'duree',
            'date_retour',
            'lieu',
            'motif',
            'numero_note',
            'numero_fiche',
            'id_absence_operation_employe__id_employe__first_name',
            'id_absence_operation_employe__id_employe__last_name',
            'id_absence_operation_employe_respensable__id_employe__first_name',
            'id_absence_operation_employe_respensable__id_employe__last_name',
            'id_absence_operation_employe_enregistre__id_employe__first_name',
            'id_absence_operation_employe_enregistre__id_employe__last_name'
        ),
        'total_absences': absences.count(),
        'total_confirmees_absences': absences.filter(statut='confirme').count(),
        'total_recentes_absences': absences_recentes.count(),
    }

    # ---------------------------
    # Fusion de tous les contextes
    # ---------------------------
    context = {**employes_stats, **operations_stats, **absences_stats}

    return render(request, 'Gestion_personnel/statistique_personnel.html', context)
