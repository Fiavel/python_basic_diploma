import json
import requests
from typing import Dict, List
from config_data.config import API_KEY

BASE_URL = "https://booking-com15.p.rapidapi.com/api/v1"


def search_destination(city: str):
    """
    Поиск ID назначения по названию города
    Search destination id using city name
    """
    url = f"{BASE_URL}/hotels/searchDestination"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    params = {"query": city}

    response = requests.get(url, headers=headers, params=params)
    data_to_use = json.loads(response.text)
    return data_to_use


def search_hotels(params: Dict) -> requests.Response:
    """
    Поиск отелей по параметрам
    Search hotels using parameters
    """
    url = f"{BASE_URL}/hotels/searchHotels"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=params)
    return response


def parse_hotels_response(response: requests.Response, country_code) -> List[Dict]:
    """
    Парсинг ответа API отелей
    Parser for API response
    """
    obj = json.loads(response.text)
    hotels = obj.get('data', {}).get('hotels', [])
    result = []

    for hotel in hotels:
        prop = hotel.get('property', {})
        hotel_info = {
            'name': prop.get('name', 'No name'),
            'booking_link' : generate_booking_link(
                hotel_name=prop.get('name', 'No name'),
                country_code=country_code,
                checkin_date=prop.get('checkinDate', 'N/A'),
                checkout_date=prop.get('checkoutDate', 'N/A')
            ),
            'description': hotel.get('accessibilityLabel', 'No description'),
            'price': f"{round(float(prop.get('priceBreakdown', {}).get('grossPrice', {}).get('value', 0)), 2)} {prop.get('priceBreakdown', {}).get('grossPrice', {}).get('currency', '')}",
            'checkin_date': prop.get('checkinDate', 'N/A'),
            'checkout_date': prop.get('checkoutDate', 'N/A'),
            'photos': prop.get('photoUrls', []),
            'coordinates': (prop.get('latitude', 'N/A'), prop.get('longitude', 'N/A'))
        }
        result.append(hotel_info)

    return result


def generate_booking_link(hotel_name: str, country_code: str, checkin_date: str, checkout_date: str) -> str:
    """
    Генерация ссылки на Booking.com
    Additional link generator for Booking.com, since API gives broken links
    """
    hotel_name_clean = hotel_name.lower().replace(' ', '-')
    return (f"https://www.booking.com/hotel/{country_code.lower()}/{hotel_name_clean}.html"
            f"?checkin={checkin_date}&checkout={checkout_date}")