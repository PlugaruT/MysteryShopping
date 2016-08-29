from mystery_shopping.companies.models import Industry
from mystery_shopping.companies.models import SubIndustry


def handle_csv_with_uploaded_sub_industries(csv_file, has_header=True):
    """
        Parse the .csv file and save the industries to the database.

          The .csv file should have the following columns:
          ---------------------------------------------------
          | Industry | Sub-Industry |
          ---------------------------------------------------
    """
    data = csv_file.read()
    data = data.decode('utf8')
    data = data.strip().split('\n')
    # Remove first line if file has header
    if has_header:
        data.pop(0)

    for industry_data in data:
        industry_list = industry_data.split(',')
        industry_name = industry_list[0].strip()
        sub_industry_name = industry_list[1].strip()

        industry, _ = Industry.objects.get_or_create(name=industry_name)
        sub_industry, _ = SubIndustry.objects.get_or_create(name=sub_industry_name, industry=industry)
        sub_industry.save()
    return True
