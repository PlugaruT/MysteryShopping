from datetime import datetime
from urllib.parse import urlencode

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from mystery_shopping.factories.respondents import RespondentCaseFactory
from mystery_shopping.factories.users import UserFactory
from mystery_shopping.respondents.models import Respondent, RespondentCase, RespondentCaseState
from mystery_shopping.users.roles import UserRole
from mystery_shopping.users.tests.user_authentication import AuthenticateUser


class RespondentsAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        RespondentCase.objects.all().delete()
        Respondent.objects.all().delete()

    def test_get_respondents_with_cases(self):
        case = RespondentCaseFactory()
        params = {
            'project': case.respondent.evaluation.project_id
        }
        response = self.client.get('{}?{}'.format(reverse('respondentswithcases-list'), urlencode(params)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), case.respondent.id)


class RespondentCasesAPITestCase(APITestCase):
    def setUp(self):
        self.authentication = AuthenticateUser()
        self.client = self.authentication.client

        RespondentCase.objects.all().delete()

    def test_start_analysis(self):
        case = RespondentCaseFactory()
        case.assign(self.authentication.user)
        case.save()

        response = self.client.post(path=reverse('respondentcases-start-analysis', args=(case.id,)))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.ANALYSIS)

    def test_escalate(self):
        case = RespondentCaseFactory()
        case.assign(self.authentication.user)
        case.save()

        response = self.client.post(path=reverse('respondentcases-escalate', args=(case.id,)),
                                    data={'reason': 'because'})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.ESCALATED)
        self.assertEqual(read_case.comments.first().text, 'because')
        self.assertEqual(read_case.comments.first().author, self.authentication.user)

    def test_analyse(self):
        case = RespondentCaseFactory(state=RespondentCaseState.ANALYSIS)

        response = self.client.post(path=reverse('respondentcases-analyse', args=(case.id,)),
                                    data={'issue': 'because', 'issue_tags': ['valera']})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)

        self.assertEqual(read_case.state, RespondentCaseState.IMPLEMENTATION)
        self.assertEqual(read_case.issue, 'because')
        self.assertEqual(read_case.issue_tags.first().name, 'valera')

    def test_implement_with_no_date_and_user(self):
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)

        response = self.client.post(path=reverse('respondentcases-implement', args=(case.id,)),
                                    data={'solution': 'because', 'solution_tags': ['tag1', ]})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.SOLVED)
        self.assertEqual(read_case.solution, 'because')
        self.assertEqual(read_case.solution_tags.first().name, 'tag1')

    def test_implement_with_no_user(self):
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)

        response = self.client.post(path=reverse('respondentcases-implement', args=(case.id,)),
                                    data={'solution': 'because', 'solution_tags': ['tag1', ],
                                          'follow_up_date': '10-10-2017'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_implement(self):
        user = UserFactory()
        case = RespondentCaseFactory(state=RespondentCaseState.IMPLEMENTATION)

        response = self.client.post(path=reverse('respondentcases-implement', args=(case.id,)),
                                    data={'solution': 'because', 'solution_tags': ['tag1', ],
                                          'follow_up_user': user.id, 'follow_up_date': '10-10-2017'})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)

        self.assertEqual(read_case.state, RespondentCaseState.PLANNED_FOR_FOLLOW_UP)
        self.assertEqual(read_case.solution, 'because')
        self.assertEqual(read_case.solution_tags.first().name, 'tag1')
        self.assertEqual(read_case.follow_up_date, datetime.strptime('10-10-2017', '%d-%m-%Y').date())

    def test_start_follow_up(self):
        case = RespondentCaseFactory(state=RespondentCaseState.PLANNED_FOR_FOLLOW_UP)

        response = self.client.post(path=reverse('respondentcases-start-follow-up', args=(case.id,)))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.FOLLOW_UP)

    def test_follow_up(self):
        case = RespondentCaseFactory(state=RespondentCaseState.FOLLOW_UP)

        response = self.client.post(path=reverse('respondentcases-follow-up', args=(case.id,)),
                                    data={'follow_up': 'because', 'follow_up_tags': ['tag1', ]})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)
        self.assertEqual(read_case.state, RespondentCaseState.SOLVED)
        self.assertEqual(read_case.follow_up, 'because')
        self.assertEqual(read_case.follow_up_tags.first().name, 'tag1')

    def test_assign(self):
        assign_user = UserFactory()
        case = RespondentCaseFactory(state=RespondentCaseState.ESCALATED)

        response = self.client.post(path=reverse('respondentcases-assign', args=(case.id,)),
                                    data={'comment': 'because', 'user': assign_user.id})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)

        self.assertEqual(read_case.state, RespondentCaseState.ASSIGNED)
        self.assertEqual(read_case.responsible_user, assign_user)
        self.assertEqual(read_case.comments.first().text, 'because')
        self.assertEqual(read_case.comments.first().author, self.authentication.user)

    def test_re_assign_without_permissions(self):
        assign_user = UserFactory()
        case = RespondentCaseFactory(state=RespondentCaseState.CLOSED)

        response = self.client.post(path=reverse('respondentcases-reassign', args=(case.id,)),
                                    data={'comment': 'because', 'user': assign_user.id})

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_re_assign(self):
        self._set_user_as_client_project_manager()
        assign_user = UserFactory()
        case = RespondentCaseFactory(state=RespondentCaseState.CLOSED)

        response = self.client.post(path=reverse('respondentcases-reassign', args=(case.id,)),
                                    data={'comment': 'because', 'user': assign_user.id})

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        read_case = RespondentCase.objects.get(id=case.id)

        self.assertEqual(RespondentCaseState.ASSIGNED, read_case.state)
        self.assertEqual(assign_user, read_case.responsible_user)
        self.assertEqual('because', read_case.comments.first().text)
        self.assertEqual(self.authentication.user, read_case.comments.first().author)

    def test_close(self):
        case = RespondentCaseFactory()
        case.assign(self.authentication.user)
        case.save()

        response = self.client.post(path=reverse('respondentcases-close', args=(case.id,)),
                                    data={'reason': 'because'})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)

        self.assertEqual(read_case.state, RespondentCaseState.CLOSED)
        self.assertEqual(read_case.comments.first().text, 'because')
        self.assertEqual(read_case.comments.first().author, self.authentication.user)

    def test_add_comment(self):
        case = RespondentCaseFactory()
        case.assign(self.authentication.user)
        case.save()

        response = self.client.post(path=reverse('respondentcases-add-comment', args=(case.id,)),
                                    data={'comment': 'this is cool'})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        read_case = RespondentCase.objects.get(id=case.id)

        self.assertEqual(read_case.comments.first().text, 'this is cool')
        self.assertEqual(read_case.comments.first().author, self.authentication.user)

    def _set_user_as_client_project_manager(self):
        group, _ = Group.objects.get_or_create(name=UserRole.CLIENT_PROJECT_MANAGER_GROUP)
        group.user_set.add(self.authentication.user)
