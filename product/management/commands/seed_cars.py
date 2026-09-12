from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import CustomUser, MANAGER
from category.models import Category
from product.models import Product


# brand, model, year, mileage, price, fuel, transmission, drive, body, color,
# engine volume, horsepower, condition, location
CAR_SPECS = [
    ('BMW', '3 Series 320i', 2022, 28900, 42900, 'petrol', 'automatic', 'rwd', 'sedan', 'Black', '2.0', 184, 'used', 'Berlin'),
    ('BMW', 'X5 xDrive30d', 2021, 41200, 58900, 'diesel', 'automatic', 'awd', 'suv', 'White', '3.0', 286, 'used', 'Munich'),
    ('BMW', 'M4 Competition', 2024, 12800, 74900, 'petrol', 'automatic', 'rwd', 'coupe', 'Blue', '3.0', 510, 'used', 'Hamburg'),
    ('BMW', 'i4 eDrive40', 2023, 15400, 61900, 'electric', 'automatic', 'rwd', 'sedan', 'Green', '0.0', 340, 'used', 'Frankfurt'),
    ('BMW', 'Z4 sDrive30i', 2020, 33700, 39900, 'petrol', 'automatic', 'rwd', 'convertible', 'Red', '2.0', 258, 'used', 'Cologne'),
    ('Mercedes-Benz', 'C 200', 2023, 9400, 51900, 'hybrid', 'automatic', 'rwd', 'sedan', 'Silver', '1.5', 204, 'used', 'Berlin'),
    ('Mercedes-Benz', 'GLC 300', 2022, 22100, 62900, 'petrol', 'automatic', 'awd', 'suv', 'Black', '2.0', 258, 'used', 'Stuttgart'),
    ('Mercedes-Benz', 'EQS 450+', 2024, 5800, 98900, 'electric', 'automatic', 'rwd', 'sedan', 'White', '0.0', 333, 'new', 'Munich'),
    ('Mercedes-Benz', 'AMG GT 53', 2021, 18700, 89900, 'petrol', 'automatic', 'awd', 'coupe', 'Grey', '3.0', 435, 'used', 'Hamburg'),
    ('Mercedes-Benz', 'Vito Tourer', 2020, 54800, 36900, 'diesel', 'automatic', 'rwd', 'van', 'Blue', '2.0', 163, 'used', 'Dusseldorf'),
    ('Audi', 'A4 Avant 40 TDI', 2021, 35700, 37900, 'diesel', 'automatic', 'fwd', 'wagon', 'Grey', '2.0', 204, 'used', 'Berlin'),
    ('Audi', 'Q5 45 TFSI', 2023, 11900, 55900, 'petrol', 'automatic', 'awd', 'suv', 'White', '2.0', 265, 'used', 'Frankfurt'),
    ('Audi', 'RS5 Coupe', 2022, 18800, 69900, 'petrol', 'automatic', 'awd', 'coupe', 'Green', '2.9', 450, 'used', 'Munich'),
    ('Audi', 'e-tron GT', 2024, 4200, 112500, 'electric', 'automatic', 'awd', 'sedan', 'Red', '0.0', 476, 'new', 'Stuttgart'),
    ('Audi', 'A3 Sportback', 2020, 46300, 24900, 'petrol', 'manual', 'fwd', 'hatchback', 'Blue', '1.5', 150, 'used', 'Cologne'),
    ('Toyota', 'Corolla Hybrid', 2023, 7600, 26900, 'hybrid', 'automatic', 'fwd', 'hatchback', 'Silver', '1.8', 140, 'used', 'Berlin'),
    ('Toyota', 'RAV4 Hybrid', 2022, 16300, 34900, 'hybrid', 'automatic', 'awd', 'suv', 'White', '2.5', 222, 'used', 'Leipzig'),
    ('Toyota', 'Camry Hybrid', 2021, 28400, 29900, 'hybrid', 'automatic', 'fwd', 'sedan', 'Black', '2.5', 218, 'used', 'Hamburg'),
    ('Toyota', 'Land Cruiser', 2020, 61700, 57900, 'diesel', 'automatic', 'awd', 'suv', 'Green', '2.8', 204, 'used', 'Munich'),
    ('Toyota', 'GR86', 2024, 2100, 36900, 'petrol', 'manual', 'rwd', 'coupe', 'Red', '2.4', 234, 'new', 'Cologne'),
    ('Lexus', 'NX 350h', 2023, 11200, 52900, 'hybrid', 'automatic', 'awd', 'suv', 'Silver', '2.5', 243, 'used', 'Frankfurt'),
    ('Lexus', 'ES 300h', 2022, 19700, 45900, 'hybrid', 'automatic', 'fwd', 'sedan', 'Blue', '2.5', 218, 'used', 'Berlin'),
    ('Lexus', 'RX 450h+', 2024, 3900, 79900, 'hybrid', 'automatic', 'awd', 'suv', 'White', '2.5', 309, 'new', 'Stuttgart'),
    ('Lexus', 'LC 500', 2021, 15400, 94900, 'petrol', 'automatic', 'rwd', 'coupe', 'Yellow', '5.0', 464, 'used', 'Hamburg'),
    ('Lexus', 'UX 250h', 2020, 42100, 29900, 'hybrid', 'automatic', 'fwd', 'hatchback', 'Grey', '2.0', 184, 'used', 'Dusseldorf'),
    ('Porsche', '911 Carrera', 2023, 8900, 124900, 'petrol', 'automatic', 'rwd', 'coupe', 'Blue', '3.0', 385, 'used', 'Stuttgart'),
    ('Porsche', 'Taycan 4S', 2024, 4200, 112500, 'electric', 'automatic', 'awd', 'sedan', 'White', '0.0', 571, 'new', 'Munich'),
    ('Porsche', 'Cayenne S', 2021, 31800, 73900, 'petrol', 'automatic', 'awd', 'suv', 'Black', '4.0', 440, 'used', 'Berlin'),
    ('Porsche', '718 Boxster', 2022, 12700, 72900, 'petrol', 'manual', 'rwd', 'convertible', 'Red', '2.0', 300, 'used', 'Hamburg'),
    ('Porsche', 'Macan GTS', 2020, 45600, 55900, 'petrol', 'automatic', 'awd', 'suv', 'Grey', '2.9', 380, 'used', 'Frankfurt'),
    ('Tesla', 'Model 3 Long Range', 2023, 15400, 41900, 'electric', 'automatic', 'awd', 'sedan', 'White', '0.0', 498, 'used', 'Berlin'),
    ('Tesla', 'Model Y Performance', 2024, 6300, 52900, 'electric', 'automatic', 'awd', 'suv', 'Black', '0.0', 534, 'new', 'Munich'),
    ('Tesla', 'Model S Plaid', 2022, 22100, 89900, 'electric', 'automatic', 'awd', 'sedan', 'Red', '0.0', 1020, 'used', 'Hamburg'),
    ('Tesla', 'Model X', 2021, 36200, 69900, 'electric', 'automatic', 'awd', 'suv', 'Blue', '0.0', 670, 'used', 'Frankfurt'),
    ('Tesla', 'Model 3 Standard', 2020, 58900, 28900, 'electric', 'automatic', 'rwd', 'sedan', 'Grey', '0.0', 283, 'used', 'Cologne'),
    ('Volkswagen', 'Golf 8', 2022, 17600, 24900, 'petrol', 'automatic', 'fwd', 'hatchback', 'White', '1.5', 150, 'used', 'Berlin'),
    ('Volkswagen', 'Tiguan 2.0 TDI', 2021, 33500, 31900, 'diesel', 'automatic', 'awd', 'suv', 'Black', '2.0', 200, 'used', 'Leipzig'),
    ('Volkswagen', 'ID.4 Pro', 2023, 9800, 39900, 'electric', 'automatic', 'rwd', 'suv', 'Blue', '0.0', 204, 'used', 'Munich'),
    ('Volkswagen', 'Passat Variant', 2020, 52700, 26900, 'diesel', 'automatic', 'fwd', 'wagon', 'Silver', '2.0', 150, 'used', 'Hamburg'),
    ('Volkswagen', 'Amarok', 2024, 3400, 57900, 'diesel', 'automatic', 'awd', 'pickup', 'Green', '3.0', 240, 'new', 'Dusseldorf'),
    ('Hyundai', 'Ioniq 5', 2023, 9800, 39900, 'electric', 'automatic', 'rwd', 'hatchback', 'Green', '0.0', 229, 'used', 'Berlin'),
    ('Hyundai', 'Tucson Hybrid', 2022, 21400, 32900, 'hybrid', 'automatic', 'awd', 'suv', 'White', '1.6', 230, 'used', 'Munich'),
    ('Hyundai', 'Santa Fe', 2021, 29300, 36900, 'diesel', 'automatic', 'awd', 'suv', 'Grey', '2.2', 202, 'used', 'Hamburg'),
    ('Hyundai', 'i30 N', 2020, 38100, 27900, 'petrol', 'manual', 'fwd', 'hatchback', 'Blue', '2.0', 280, 'used', 'Cologne'),
    ('Hyundai', 'Kona Electric', 2024, 1800, 35900, 'electric', 'automatic', 'fwd', 'suv', 'Red', '0.0', 218, 'new', 'Frankfurt'),
    ('Kia', 'EV6 GT-Line', 2023, 12700, 42900, 'electric', 'automatic', 'awd', 'hatchback', 'Black', '0.0', 325, 'used', 'Berlin'),
    ('Kia', 'Sportage Hybrid', 2022, 24300, 30900, 'hybrid', 'automatic', 'fwd', 'suv', 'Silver', '1.6', 230, 'used', 'Munich'),
    ('Kia', 'Sorento', 2021, 35800, 39900, 'diesel', 'automatic', 'awd', 'suv', 'White', '2.2', 202, 'used', 'Hamburg'),
    ('Kia', 'Ceed SW', 2020, 46700, 19900, 'petrol', 'manual', 'fwd', 'wagon', 'Blue', '1.5', 160, 'used', 'Cologne'),
    ('Kia', 'Niro EV', 2024, 2200, 38900, 'electric', 'automatic', 'fwd', 'suv', 'Green', '0.0', 204, 'new', 'Dusseldorf'),
    ('Ford', 'Mustang GT', 2021, 19600, 38900, 'petrol', 'manual', 'rwd', 'coupe', 'Red', '5.0', 450, 'used', 'Berlin'),
    ('Ford', 'Kuga Hybrid', 2023, 8700, 33900, 'hybrid', 'automatic', 'fwd', 'suv', 'White', '2.5', 190, 'used', 'Frankfurt'),
    ('Ford', 'Ranger Wildtrak', 2022, 28700, 46900, 'diesel', 'automatic', 'awd', 'pickup', 'Blue', '2.0', 205, 'used', 'Munich'),
    ('Ford', 'Focus ST', 2020, 41200, 23900, 'petrol', 'manual', 'fwd', 'hatchback', 'Grey', '2.3', 280, 'used', 'Hamburg'),
    ('Ford', 'Transit Custom', 2024, 5100, 49900, 'diesel', 'automatic', 'fwd', 'van', 'Silver', '2.0', 170, 'new', 'Dusseldorf'),
    ('Chevrolet', 'Corvette Stingray', 2022, 7400, 84900, 'petrol', 'automatic', 'rwd', 'coupe', 'Yellow', '6.2', 495, 'used', 'Berlin'),
    ('Chevrolet', 'Camaro SS', 2020, 28900, 45900, 'petrol', 'manual', 'rwd', 'coupe', 'Blue', '6.2', 455, 'used', 'Munich'),
    ('Chevrolet', 'Silverado 1500', 2021, 34600, 55900, 'petrol', 'automatic', 'awd', 'pickup', 'Black', '5.3', 355, 'used', 'Hamburg'),
    ('Chevrolet', 'Bolt EV', 2023, 6100, 29900, 'electric', 'automatic', 'fwd', 'hatchback', 'Green', '0.0', 204, 'used', 'Frankfurt'),
    ('Chevrolet', 'Tahoe', 2019, 68200, 42900, 'petrol', 'automatic', 'awd', 'suv', 'White', '5.3', 355, 'used', 'Cologne'),
    ('Volvo', 'XC60 B5', 2023, 10500, 54900, 'hybrid', 'automatic', 'awd', 'suv', 'Silver', '2.0', 250, 'used', 'Berlin'),
    ('Volvo', 'V90 B4', 2021, 29800, 39900, 'diesel', 'automatic', 'fwd', 'wagon', 'Blue', '2.0', 197, 'used', 'Munich'),
    ('Volvo', 'XC90 Recharge', 2022, 18900, 69900, 'hybrid', 'automatic', 'awd', 'suv', 'Black', '2.0', 455, 'used', 'Hamburg'),
    ('Volvo', 'C40 Recharge', 2024, 2900, 46900, 'electric', 'automatic', 'awd', 'hatchback', 'White', '0.0', 408, 'new', 'Frankfurt'),
    ('Volvo', 'S60 T8', 2020, 41700, 35900, 'hybrid', 'automatic', 'awd', 'sedan', 'Red', '2.0', 390, 'used', 'Cologne'),
    ('Nissan', 'Qashqai e-Power', 2023, 6800, 28900, 'hybrid', 'automatic', 'fwd', 'suv', 'Grey', '1.5', 190, 'used', 'Berlin'),
    ('Nissan', 'Ariya 87 kWh', 2024, 1900, 52900, 'electric', 'automatic', 'awd', 'suv', 'Blue', '0.0', 394, 'new', 'Munich'),
    ('Nissan', 'X-Trail', 2022, 22500, 33900, 'hybrid', 'automatic', 'awd', 'suv', 'White', '1.5', 204, 'used', 'Hamburg'),
    ('Nissan', 'Z Performance', 2021, 12800, 57900, 'petrol', 'manual', 'rwd', 'coupe', 'Yellow', '3.0', 405, 'used', 'Frankfurt'),
    ('Nissan', 'Leaf e+', 2020, 50300, 21900, 'electric', 'automatic', 'fwd', 'hatchback', 'Red', '0.0', 217, 'used', 'Cologne'),
    ('Honda', 'Civic e:HEV', 2022, 13200, 27900, 'hybrid', 'automatic', 'fwd', 'sedan', 'White', '2.0', 184, 'used', 'Berlin'),
    ('Honda', 'CR-V Hybrid', 2023, 9100, 36900, 'hybrid', 'automatic', 'awd', 'suv', 'Black', '2.0', 184, 'used', 'Munich'),
    ('Honda', 'Civic Type R', 2021, 17600, 44900, 'petrol', 'manual', 'fwd', 'hatchback', 'Blue', '2.0', 329, 'used', 'Hamburg'),
    ('Honda', 'HR-V', 2020, 33700, 22900, 'petrol', 'manual', 'fwd', 'suv', 'Grey', '1.5', 130, 'used', 'Frankfurt'),
    ('Honda', 'Jazz', 2024, 1200, 24900, 'hybrid', 'automatic', 'fwd', 'hatchback', 'Red', '1.5', 122, 'new', 'Cologne'),
    ('Mazda', 'CX-5 Skyactiv-G', 2022, 19800, 31900, 'petrol', 'automatic', 'awd', 'suv', 'Red', '2.5', 194, 'used', 'Berlin'),
    ('Mazda', 'MX-5 Roadster', 2021, 14900, 29900, 'petrol', 'manual', 'rwd', 'convertible', 'Blue', '2.0', 184, 'used', 'Munich'),
    ('Mazda', 'Mazda3', 2020, 42700, 21900, 'petrol', 'manual', 'fwd', 'hatchback', 'Grey', '2.0', 122, 'used', 'Hamburg'),
    ('Mazda', 'CX-60 PHEV', 2023, 7600, 48900, 'hybrid', 'automatic', 'awd', 'suv', 'White', '2.5', 327, 'used', 'Frankfurt'),
    ('Mazda', 'CX-30', 2024, 1800, 28900, 'petrol', 'automatic', 'fwd', 'suv', 'Silver', '2.0', 150, 'new', 'Cologne'),
    ('Subaru', 'Outback', 2022, 26700, 35900, 'petrol', 'automatic', 'awd', 'wagon', 'Green', '2.5', 175, 'used', 'Berlin'),
    ('Subaru', 'Forester', 2021, 31400, 32900, 'hybrid', 'automatic', 'awd', 'suv', 'White', '2.0', 150, 'used', 'Munich'),
    ('Subaru', 'BRZ', 2023, 5600, 34900, 'petrol', 'manual', 'rwd', 'coupe', 'Blue', '2.4', 234, 'used', 'Hamburg'),
    ('Subaru', 'Impreza', 2020, 38900, 21900, 'petrol', 'automatic', 'awd', 'hatchback', 'Silver', '2.0', 150, 'used', 'Frankfurt'),
    ('Subaru', 'Solterra', 2024, 1100, 46900, 'electric', 'automatic', 'awd', 'suv', 'Black', '0.0', 218, 'new', 'Cologne'),
    ('Skoda', 'Octavia Combi', 2022, 24400, 26900, 'diesel', 'automatic', 'fwd', 'wagon', 'Blue', '2.0', 150, 'used', 'Berlin'),
    ('Skoda', 'Kodiaq', 2021, 36900, 31900, 'petrol', 'automatic', 'awd', 'suv', 'White', '2.0', 190, 'used', 'Munich'),
    ('Skoda', 'Enyaq iV', 2023, 8700, 42900, 'electric', 'automatic', 'rwd', 'suv', 'Green', '0.0', 204, 'used', 'Hamburg'),
    ('Skoda', 'Fabia', 2020, 41200, 16900, 'petrol', 'manual', 'fwd', 'hatchback', 'Red', '1.0', 110, 'used', 'Frankfurt'),
    ('Skoda', 'Superb', 2024, 1500, 39900, 'hybrid', 'automatic', 'fwd', 'sedan', 'Grey', '1.4', 218, 'new', 'Cologne'),
    ('BYD', 'Atto 3', 2023, 9200, 35900, 'electric', 'automatic', 'fwd', 'suv', 'Blue', '0.0', 204, 'used', 'Berlin'),
    ('BYD', 'Seal AWD', 2024, 3100, 49900, 'electric', 'automatic', 'awd', 'sedan', 'Silver', '0.0', 530, 'new', 'Munich'),
    ('BYD', 'Han', 2022, 18400, 52900, 'electric', 'automatic', 'awd', 'sedan', 'Black', '0.0', 517, 'used', 'Hamburg'),
    ('BYD', 'Dolphin', 2023, 6400, 23900, 'electric', 'automatic', 'fwd', 'hatchback', 'White', '0.0', 204, 'used', 'Frankfurt'),
    ('BYD', 'Tang', 2021, 27800, 45900, 'electric', 'automatic', 'awd', 'suv', 'Red', '0.0', 517, 'used', 'Cologne'),
    ('Land Rover', 'Defender 110', 2022, 23100, 69900, 'diesel', 'automatic', 'awd', 'suv', 'Green', '3.0', 250, 'used', 'Berlin'),
    ('Land Rover', 'Range Rover Sport', 2021, 31800, 89900, 'hybrid', 'automatic', 'awd', 'suv', 'Black', '3.0', 400, 'used', 'Munich'),
    ('Land Rover', 'Discovery', 2020, 47200, 52900, 'diesel', 'automatic', 'awd', 'suv', 'White', '3.0', 249, 'used', 'Hamburg'),
    ('Land Rover', 'Evoque P300e', 2023, 9700, 57900, 'hybrid', 'automatic', 'awd', 'suv', 'Silver', '1.5', 309, 'used', 'Frankfurt'),
    ('Land Rover', 'Defender V8', 2024, 2100, 119900, 'petrol', 'automatic', 'awd', 'suv', 'Blue', '5.0', 525, 'new', 'Cologne'),
]

WMI_BY_BRAND = {
    'BMW': 'WBA', 'Mercedes-Benz': 'WDD', 'Audi': 'WAU', 'Toyota': 'JTN',
    'Lexus': 'JTH', 'Porsche': 'WP0', 'Tesla': '5YJ', 'Volkswagen': 'WVW',
    'Hyundai': 'TMA', 'Kia': 'U5Y', 'Ford': 'WF0', 'Chevrolet': '1G1',
    'Volvo': 'YV1', 'Nissan': 'SJ1', 'Honda': 'JHM', 'Mazda': 'JMZ',
    'Subaru': 'JF1', 'Skoda': 'TMB', 'BYD': 'LGX', 'Land Rover': 'SAL',
}


class Command(BaseCommand):
    help = 'Create deterministic development inventory without deleting user data.'

    def handle(self, *args, **options):
        seller = CustomUser.objects.filter(user_role__in=['seller', MANAGER]).first()
        if seller is None:
            seller = CustomUser.objects.create_user(
                username='motive_inventory',
                email='inventory@motive.local',
                password='ChangeMe123!inventory',
                user_role=MANAGER,
                auth_status='done',
                auth_type='via_email',
            )

        categories = {}
        for body_type in {spec[8] for spec in CAR_SPECS}:
            category, _ = Category.objects.get_or_create(title=body_type.title())
            categories[body_type] = category

        created = 0
        for index, spec in enumerate(CAR_SPECS, start=1):
            (
                brand, model_name, year, mileage, price, fuel_type, transmission,
                drive_type, body_type, color, engine_volume, horsepower, condition,
                location,
            ) = spec
            title = f'{brand} {model_name}'
            vin = f'{WMI_BY_BRAND[brand]}{index:06d}{str(year)[-1]}A{index:06d}'
            defaults = {
                'title': title,
                'short_desc': f'{year} {brand} {model_name}'[:50],
                'desc': f'Inspected {brand} {model_name} with documented service history and transparent pricing.',
                'price': Decimal(str(price)),
                'currency': 'EUR',
                'user': seller,
                'brand': brand,
                'model_name': model_name,
                'year': year,
                'mileage': mileage,
                'fuel_type': fuel_type,
                'transmission': transmission,
                'drive_type': drive_type,
                'body_type': body_type,
                'color': color,
                'engine_volume': Decimal(engine_volume),
                'horsepower': horsepower,
                'condition': condition,
                'location': location,
                'category': categories[body_type],
                'quantity': 1,
                'is_active': True,
                'is_deleted': False,
            }
            _, was_created = Product.objects.get_or_create(vin=vin, defaults=defaults)
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Inventory ready: {created} new cars, {len(CAR_SPECS) - created} already existed.'
            )
        )
