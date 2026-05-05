import os
import django
import random
import urllib.request
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vgoru.settings')
django.setup()

from django.contrib.auth.models import User
from mountains_roads.models import MountainRoute, RouteReview, UserProfile


def download_image(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"Помилка завантаження фото {url}: {e}")
        return None


def populate():
    print("Починаємо наповнення бази реальними даними...")

    users_data = [
        ('taras_shevchenko', 'Тарас', 'Шевченко'),
        ('lesya_ukrainka', 'Леся', 'Українка'),
        ('ivan_franko', 'Іван', 'Франко'),
        ('bogdan_hmel', 'Богдан', 'Хмельницький'),
        ('lina_kostenko', 'Ліна', 'Костенко'),
        ('vasyl_stus', 'Василь', 'Стус'),
        ('grigoriy_skovoroda', 'Григорій', 'Сковорода'),
        ('marusya_churay', 'Маруся', 'Чурай')
    ]

    users = []
    for username, first, last in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@example.com', 'first_name': first, 'last_name': last}
        )
        if created:
            user.set_password('password123')
            user.save()
            UserProfile.objects.create(user=user, bio=f"Привіт! Я {first}, люблю Карпати.")
        users.append(user)

    print(f"Користувачі: {len(users)} шт.")

    routes_data = [
        {
            "name": "Говерла",
            "region": "Івано-Франківська обл.",
            "height": 2061,
            "difficulty": "medium",
            "duration": 6.0,
            "distance": 14.5,
            "desc": "Найвища точка України. Маршрут з бази 'Заросляк'. Популярний, але кам'янистий підйом.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Hoverla_View.jpg/800px-Hoverla_View.jpg"
        },
        {
            "name": "Озеро Синевир",
            "region": "Закарпатська обл.",
            "height": 989,
            "difficulty": "easy",
            "duration": 2.5,
            "distance": 4.0,
            "desc": "Найбільше гірське озеро України, 'Морське Око' Карпат. Легка прогулянка навколо озера серед смерек.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Synevir_lake_from_above.jpg/800px-Synevir_lake_from_above.jpg"
        },
        {
            "name": "Піп Іван Чорногірський",
            "region": "Івано-Франківська обл.",
            "height": 2028,
            "difficulty": "hard",
            "duration": 9.0,
            "distance": 22.0,
            "desc": "Сходження до обсерваторії 'Білий Слон'. Один з наймальовничіших та найважчих маршрутів Чорногори.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Pip_Ivan_Chornohora_observatory.jpg/800px-Pip_Ivan_Chornohora_observatory.jpg"
        },
        {
            "name": "Скелі Довбуша",
            "region": "Івано-Франківська обл.",
            "height": 668,
            "difficulty": "easy",
            "duration": 3.0,
            "distance": 5.0,
            "desc": "Унікальний скельний комплекс у буковому лісі. Місце сили та історії про опришків.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Dovbush_rocks_2.jpg/800px-Dovbush_rocks_2.jpg"
        },
        {
            "name": "Петрос",
            "region": "Закарпатська обл.",
            "height": 2020,
            "difficulty": "hard",
            "duration": 8.0,
            "distance": 16.0,
            "desc": "Дуже стрімкий підйом та спуск. Чудова панорама на Говерлу. Небезпечний у погану погоду.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Petros_mountain.jpg/800px-Petros_mountain.jpg"
        },
        {
            "name": "Гимба та водоспад Шипіт",
            "region": "Закарпатська обл.",
            "height": 1491,
            "difficulty": "medium",
            "duration": 5.0,
            "distance": 10.0,
            "desc": "Популярний маршрут на Боржаві. Можна піднятися на витягу, а далі пішки по хребту.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Shypit_waterfall_2019.jpg/800px-Shypit_waterfall_2019.jpg"
        },
        {
            "name": "Шпиці",
            "region": "Івано-Франківська обл.",
            "height": 1863,
            "difficulty": "medium",
            "duration": 7.0,
            "distance": 14.0,
            "desc": "Скелі, схожі на вежі готичного замку. Неймовірно фотогенічне місце в масиві Чорногора.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Spitsi_mountain.jpg/800px-Spitsi_mountain.jpg"
        },
        {
            "name": "Хом'як",
            "region": "Івано-Франківська обл.",
            "height": 1542,
            "difficulty": "easy",
            "duration": 4.5,
            "distance": 9.0,
            "desc": "Ідеальна гора для початківців. Серпантинна стежка через ліс, а на вершині статуя Матері Божої.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Gorgany_Synyak.jpg/800px-Gorgany_Synyak.jpg"
        },
        {
            "name": "Озеро Несамовите",
            "region": "Івано-Франківська обл.",
            "height": 1750,
            "difficulty": "medium",
            "duration": 6.0,
            "distance": 14.0,
            "desc": "Одне з найвищих озер. Легенди кажуть, що якщо кинути камінь у воду — піде дощ.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Nesamovyte_lake.jpg/800px-Nesamovyte_lake.jpg"
        },
        {
            "name": "Парашка",
            "region": "Львівська обл.",
            "height": 1268,
            "difficulty": "medium",
            "duration": 6.0,
            "distance": 13.0,
            "desc": "Найвища вершина Сколівських Бескидів. Чудовий варіант для одноденного походу зі Львова.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Parashka_mountain.jpg/800px-Parashka_mountain.jpg"
        },
        {
            "name": "Полонина Руна",
            "region": "Закарпатська обл.",
            "height": 1479,
            "difficulty": "easy",
            "duration": 5.0,
            "distance": 12.0,
            "desc": "Величезне плато, рівне як стіл. Тут є залишки старої радарної станції.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Borzhava_Range.jpg/800px-Borzhava_Range.jpg"
        },
        {
            "name": "Явірник-Горган",
            "region": "Івано-Франківська обл.",
            "height": 1467,
            "difficulty": "medium",
            "duration": 5.5,
            "distance": 11.0,
            "desc": "Класичні Ґоргани з камінням, вкритим зеленим мохом. Дуже атмосферно.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Yavirnyk-Gorgan.jpg/800px-Yavirnyk-Gorgan.jpg"
        },
        {
            "name": "Пікуй",
            "region": "Львівська обл.",
            "height": 1408,
            "difficulty": "medium",
            "duration": 6.5,
            "distance": 12.5,
            "desc": "Найвища точка Львівщини. Гостра вершина з чудовими краєвидами на Польщу.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Pikuy_mountain.jpg/800px-Pikuy_mountain.jpg"
        },
        {
            "name": "Бребенескул",
            "region": "Івано-Франківська обл.",
            "height": 2035,
            "difficulty": "hard",
            "duration": 8.0,
            "distance": 18.0,
            "desc": "Друга за висотою вершина України. Поруч знаходиться найвисокогірніше озеро.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Brebeneskul_lake.jpg/800px-Brebeneskul_lake.jpg"
        },
        {
            "name": "Ґут-Томнатик",
            "region": "Івано-Франківська обл.",
            "height": 2016,
            "difficulty": "hard",
            "duration": 8.5,
            "distance": 19.0,
            "desc": "Одна з вершин двотисячників. Менш людна, ніж Говерла, але дуже красива.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Hoverla_View.jpg/800px-Hoverla_View.jpg"
        }
    ]

    created_count = 0
    for data in routes_data:
        route, created = MountainRoute.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['desc'],
                'difficulty': data['difficulty'],
                'height': data['height'],
                'duration_hours': data['duration'],
                'distance_km': data['distance'],
                'region': data['region'],
                'map_coordinates': '48.15, 24.50',
                'rating': 0
            }
        )

        # Завантажуємо фото, якщо його немає
        if created or not route.image:
            print(f"Завантажую фото для {route.name}...")
            img_content = download_image(data['image_url'])
            if img_content:
                route.image.save(f"route_{route.id}.jpg", ContentFile(img_content), save=True)
            created_count += 1
        else:
            print(f"{route.name} вже існує")

    print(f"Маршрути: оновлено/створено {created_count} з {len(routes_data)}")

    comments = [
        ("Це було неймовірно! Краєвиди просто космос.", 5),
        ("Маршрут важчий, ніж я думав, але воно того варте.", 4),
        ("Дуже багато людей, не вдалося побути в тиші.", 3),
        ("Обов'язково беріть зручне взуття і воду!", 5),
        ("Найкращий похід у моєму житті.", 5),
        ("Погода зіпсувалася, нічого не побачили :(", 2),
        ("Добре маркований маршрут, заблукати важко.", 5),
        ("Рекомендую йти восени, кольори лісу чарівні.", 5),
        ("Трохи нудно на підйомі, але вершина супер.", 4),
        ("Дуже крутий підйом, коліна боліли.", 4)
    ]

    all_routes = list(MountainRoute.objects.all())

    RouteReview.objects.all().delete()

    review_count = 0
    for _ in range(40):
        user = random.choice(users)
        route = random.choice(all_routes)
        text, rating = random.choice(comments)

        final_rating = max(1, min(5, rating + random.randint(-1, 1)))

        if not RouteReview.objects.filter(user=user, route=route).exists():
            RouteReview.objects.create(
                user=user,
                route=route,
                rating=final_rating,
                title=text[:20] + "...",
                text=text,
                helpful_count=random.randint(0, 15)
            )
            review_count += 1

    print(f"Відгуки: створено {review_count} шт.")

    for route in all_routes:
        avg = route.get_average_rating()
        if avg > 0:
            route.rating = avg
            route.save()

    print("Рейтинги перераховано.")
    print("ВСЕ ГОТОВО! Можна запускати сервер.")


if __name__ == '__main__':
    populate()