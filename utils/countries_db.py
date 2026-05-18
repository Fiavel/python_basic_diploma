from py_countries_states_cities_database import get_all_cities, get_all_countries
from translate import Translator



translator = Translator(from_lang="russian", to_lang="english")
cities = get_all_cities()
countries = get_all_countries()


def find_country_by_code(code: str) -> tuple[str, str] | None:
    """
    Поиск страны по коду
    Searching country using its code
    """
    for country in countries:
        if country['iso2'] == code:
            return country['name'], country['iso2']
    return None


def find_city_and_country_exact(city_name: str) -> str:
    """
    Поиск стран по названию города
    Searching country using its name
    """
    city_name_en = translator.translate(city_name)
    matches = [city for city in cities if city['name'].lower() == city_name_en.lower()]

    if not matches:
        return ''

    results = []
    for city in matches:
        country_info = find_country_by_code(city['country_code'])
        if country_info:
            results.append(f"{city['name']}, {country_info[0]}, {country_info[1]}")

    return "\n".join(list(set(results)))