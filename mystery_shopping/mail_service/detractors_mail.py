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
