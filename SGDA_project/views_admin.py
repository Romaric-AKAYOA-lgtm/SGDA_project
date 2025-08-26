from django.db.models import Count, F, Value, IntegerField
from django.db.models.functions import ExtractYear
from datetime import date
from django.template.response import TemplateResponse


from Gestion_personnel.employe.models import Employe
from Gestion_personnel.absence.models import Absence
from Gestion_personnel.operation.models import Operation



def get_yearly_counts(model, date_field):
    return (
        model.objects
        .annotate(year=ExtractYear(date_field))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

def get_filtered_yearly_counts(model, date_field, **filters):
    return (
        model.objects
        .filter(**filters)
        .annotate(year=ExtractYear(date_field))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

# Fonction pour récupérer les employés partant à la retraite cette année
def get_employees_retiring_this_year():
    current_year = date.today().year
    retirement_age = 65  # L'âge de la retraite (peut être ajusté si nécessaire)

    return (
        Employe.objects.annotate(
            age=Value(current_year, output_field=IntegerField()) - ExtractYear('date_naissance')
        )
        .filter(age=retirement_age)
        .annotate(year=ExtractYear('date_creation'))  # Si tu veux aussi afficher l'année de leur création
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )

# Fonction pour récupérer les employés progressant vers la retraite
def get_employees_progressing_towards_retirement():
    current_year = date.today().year
    retirement_age = 65  # L'âge de la retraite
    age_range_start = retirement_age - 5  # Tranche d'âge des employés entre 60 et 64 ans

    return (
        Employe.objects.annotate(
            age=Value(current_year, output_field=IntegerField()) - ExtractYear('date_naissance')
        )
        .filter(age__gte=age_range_start, age__lt=retirement_age)
        .annotate(year=ExtractYear('date_creation'))  # Si tu veux aussi afficher l'année de leur création
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )


def dashboard_view(request, admin_site):
    # Données annuelles globales
    employes_par_an = get_yearly_counts(Employe, 'date_creation')
    operations_par_an = get_yearly_counts(Operation, 'date_debut')
    absences_par_an = get_yearly_counts(Absence, 'date_debut')

    # Données spécifiques filtrées
    operation_recrutement_par_an = get_filtered_yearly_counts(Operation, 'date_debut', type_operation='recrutement')
    operation_mutation_par_an = get_filtered_yearly_counts(Operation, 'date_debut', type_operation='mutation')

    operation_recrutement_homme_par_an = get_filtered_yearly_counts(
        Operation, 'date_debut',
        type_operation='recrutement',
        id_employe__sexe='M'
    )
    operation_recrutement_femme_par_an = get_filtered_yearly_counts(
        Operation, 'date_debut',
        type_operation='recrutement',
        id_employe__sexe='F'
    )
    operation_mutation_homme_par_an = get_filtered_yearly_counts(
        Operation, 'date_debut',
        type_operation='mutation',
        id_employe__sexe='M'
    )
    operation_mutation_femme_par_an = get_filtered_yearly_counts(
        Operation, 'date_debut',
        type_operation='mutation',
        id_employe__sexe='F'
    )

    current_year = date.today().year
    # Exemple placeholders pour répartitions par organisation et âge (à adapter)
    operation_repartition_employe_homme_par_organisation_unit_par_an = list(
        Operation.objects.filter(id_employe__sexe='M').annotate(
            year=ExtractYear('date_debut'),
            unite=F('id_organisation_unite__designation')
        ).values('year', 'unite').annotate(count=Count('id')).order_by('year', 'unite')
    )

    operation_repartition_employe_femme_par_organisation_unit_par_an = list(
        Operation.objects.filter(id_employe__sexe='F').annotate(
            year=ExtractYear('date_debut'),
            unite=F('id_organisation_unite__designation')
        ).values('year', 'unite').annotate(count=Count('id')).order_by('year', 'unite')
    )

    operation_repartition_employe_homme_age_par_organisation_unit_par_an = list(
        Operation.objects.annotate(
            age=Value(current_year, output_field=IntegerField()) - ExtractYear('id_employe__date_naissance')
        ).filter(id_employe__sexe='M', age__gte=18, age__lte=35).annotate(
            year=ExtractYear('date_debut'),
            unite=F('id_organisation_unite__designation')
        ).values('year', 'unite').annotate(count=Count('id')).order_by('year', 'unite')
    )

    operation_repartition_employe_femme_age_par_organisation_unit_par_an = list(
        Operation.objects.annotate(
            age=Value(current_year, output_field=IntegerField()) - ExtractYear('id_employe__date_naissance')
        ).filter(id_employe__sexe='F', age__gte=18, age__lte=35).annotate(
            year=ExtractYear('date_debut'),
            unite=F('id_organisation_unite__designation')
        ).values('year', 'unite').annotate(count=Count('id')).order_by('year', 'unite')
    )

    # Ajouter la section des employés partant à la retraite cette année
    employer_parte_retraite_cette_anne_par_an = get_employees_retiring_this_year()

    # Ajouter la progression des employés vers la retraite
    employe_progression_retraite_par_an = get_employees_progressing_towards_retirement()

    sections = []

    def make_section(title, data_qs):
        labels = [str(entry['year']) for entry in data_qs]
        data = [entry['count'] for entry in data_qs]
        return {
            'title': title,
            'labels': labels,
            'data': data,
            'total': sum(data),
            'data_pairs': list(zip(labels, data)),
        }

    # Ajout des sections (ordre chronologique)
    sections.append(make_section("Évolution des Employés", employes_par_an))
    sections.append(make_section("Évolution des Opérations", operations_par_an))

    sections.append(make_section("→ Recrutements", operation_recrutement_par_an))
    sections.append(make_section("→ Recrutements Hommes", operation_recrutement_homme_par_an))
    sections.append(make_section("→ Recrutements Femmes", operation_recrutement_femme_par_an))

    sections.append(make_section("→ Mutations", operation_mutation_par_an))
    sections.append(make_section("→ Mutations Hommes", operation_mutation_homme_par_an))
    sections.append(make_section("→ Mutations Femmes", operation_mutation_femme_par_an))


    sections.append(make_section("Évolution des Absences", absences_par_an))

    # Ajout des répartitions par organisation et âge
    sections.append(make_section("→ Répartition des Hommes par Organisation", operation_repartition_employe_homme_par_organisation_unit_par_an))
    sections.append(make_section("→ Répartition des Femmes par Organisation", operation_repartition_employe_femme_par_organisation_unit_par_an))
    sections.append(make_section("→ Répartition des Hommes (18-35 ans) par Organisation", operation_repartition_employe_homme_age_par_organisation_unit_par_an))
    sections.append(make_section("→ Répartition des Femmes (18-35 ans) par Organisation", operation_repartition_employe_femme_age_par_organisation_unit_par_an))

    # Ajout de la section des employés partant à la retraite cette année
    sections.append(make_section("→ Employés partant à la retraite cette année", employer_parte_retraite_cette_anne_par_an))

    # Ajout de la progression des employés vers la retraite
    sections.append(make_section("→ Progression des employés vers la retraite", employe_progression_retraite_par_an))

    # Liens rapides admin
    quick_links = []
    for model in admin_site._registry.keys():
        meta = model._meta
        url_name = f"myadmin:{meta.app_label}_{meta.model_name}_changelist"
        quick_links.append({
            'url_name': url_name,
            'verbose_name_plural': meta.verbose_name_plural.title(),
        })

    context = dict(admin_site.each_context(request))
    context.update({
        'sections': sections,
        'quick_links': quick_links,
    })

    return TemplateResponse(request, "dashboard1.html", context)
