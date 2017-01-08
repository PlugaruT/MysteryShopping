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

    def get_list_of_editable_places(self, project):
        places = project.research_methodology.company_elements.all()
        id_list = list()
        for place in places:
            if not self.has_evaluations_for_project(pk=place.pk, project=project):
                id_list.append(place.pk)

        return id_list
