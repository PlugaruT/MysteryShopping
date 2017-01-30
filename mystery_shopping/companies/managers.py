from django.db.models import QuerySet


class CompanyElementQuerySet(QuerySet):
    def has_evaluations_for_project(self, pk, project):
        """
        method for checking weather a company element has evaluations defined
        for the given project.

        :param pk: company element
        :param project: project to query info for
        :return: boolean
        """
        try:
            return self.get(pk=pk).evaluations.filter(project=project).exists()
        except:
            return False

    def get_list_of_non_editable_places(self, project):
        places = project.research_methodology.company_elements.all()
        id_list = list()
        for place in places:
            if self.has_evaluations_for_project(pk=place.pk, project=project):
                id_list.append(place.pk)
        return id_list

    def get_company_elements_not_in_project(self, project):
        all_company_elements = set(project.company.get_descendants(include_self=False).values_list('id', flat=True))
        company_elements_in_project = set(project.research_methodology.company_elements.values_list('id', flat=True))
        return list(all_company_elements - company_elements_in_project)
