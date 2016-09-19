from mystery_shopping.common.models import Country
from mystery_shopping.common.models import CountryRegion
from mystery_shopping.common.models import County
from mystery_shopping.common.models import City


def handle_csv_with_uploaded_localities(csv_file, has_header=True):
    """Parse the .csv file and save the localities to the database.

    The .csv file should have the following columns:
    ---------------------------------------------------
    | Country | Region | County | Locality | ZIP Code |
    ---------------------------------------------------
    | Moldova | South  | Cahul  | Hutulu   | MD-3922  |
    ---------------------------------------------------
    | ...     | ...    | ...    | ...      | ...      |
    ---------------------------------------------------
    """
    data = csv_file.read()
    data = data.decode('utf8')
    data = data.strip().split('\n')

    # Remove first line if file has header
    if has_header:
        data.pop(0)

    for locality_data in data:
        locality_list = locality_data.split(',')
        country_name = locality_list[0].strip()
        region_name = locality_list[1].strip()
        county_name = locality_list[2].strip()
        locality_name = locality_list[3].strip()
        zip_code = locality_list[4].strip()

        country, _ = Country.objects.get_or_create(name=country_name)
        region, _ = CountryRegion.objects.get_or_create(country=country, name=region_name)
        county, _ = County.objects.get_or_create(country=country, country_region=region, name=county_name)
        locality, locality_created = City.objects.get_or_create(county=county, name=locality_name)

        locality.zip_code = zip_code
        locality.save()

    return True


def handle_csv_with_uploaded_countries(csv_file, has_header=True):
    """
        Parse the .csv file and save the countries to the database.
        The .csv file should have the following columns:
        -----------
        | Country |
        -----------
    """
    data = csv_file.read()
    data = data.decode('utf8')
    data = data.strip().split('\n')
    # Remove first line if file has header
    if has_header:
        data.pop(0)

    for country_name in data:
        Country.objects.create(name=country_name.strip())
