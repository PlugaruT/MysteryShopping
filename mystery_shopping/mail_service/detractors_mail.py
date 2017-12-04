from mystery_shopping.mail_service.mail import EmailDispatcher, get_text_and_html_content


def send_email_when_new_detractor(recipients):
    subject_line = 'New detractor in the --place name--'

    context = {
        'random': 'random'
    }

    text_content, html_content = get_text_and_html_content('detractors/new_detractor', context)

    service = EmailDispatcher(recipients=recipients, text_content=text_content, html_content=html_content,
                              subject=subject_line)
    service.build_and_send()


def send_email_when_new_detractor_case(recipients, place):
    subject_line = 'New detractor case in the {}'.format(place)

    context = {
        'random': 'random'
    }

    text_content, html_content = get_text_and_html_content('detractors/new_detractor_case', context)

    service = EmailDispatcher(recipients=recipients, text_content=text_content, html_content=html_content,
                              subject=subject_line)
    service.build_and_send()


def send_notification_email_for_follow_up(case):
    subject_line = 'Follow up date for a detractor case is today!'
    recipients = case.follow_up_user.email

    context = {
        'case_url': _build_case_url(case)
    }

    text_content, html_content = get_text_and_html_content('detractors/follow_up', context)

    service = EmailDispatcher(recipients=recipients, text_content=text_content, html_content=html_content,
                              subject=subject_line)
    service.build_and_send()


def _build_case_url(case):
    domain = 'cxi.dapi.solutions'
    company_id = case.get_company().id
    project_id = case.get_project().id
    respondent_id = case.respondent.id

    return 'https://{domain}/company/{company}/project/{project}/respondents/{respondent}/detail?withCase=true'.format(
        domain=domain, company=company_id, project=project_id, respondent=respondent_id)
