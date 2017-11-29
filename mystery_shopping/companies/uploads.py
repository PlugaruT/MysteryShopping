from mystery_shopping.companies.models import Industry, SubIndustry


def handle_csv_with_uploaded_sub_industries(csv_file, has_header=False):
    """
        Parse the .csv file and save the industries to the database.
        The .csv file should have the following columns:
        ---------------------------
        | Industry | Sub-Industry |
        ---------------------------
    """
    data = csv_file.read()
    data = data.decode('utf8')
    data = data.strip().split('\n')
    # Remove first line if file has header
    if has_header:
        data.pop(0)

    for industry_data in data:
        industry_name, sub_industry_name = extract_industry_details(industry_data)
        industry, _ = Industry.objects.get_or_create(name=industry_name)
        sub_industry, _ = SubIndustry.objects.get_or_create(name=sub_industry_name, industry=industry)
        sub_industry.save()
    return False


def extract_industry_details(industry_data):
    industry_list = industry_data.split('[],')
    return industry_list[0].strip(), industry_list[1].strip()
