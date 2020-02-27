import hashlib
import json
import re
import urllib

import requests


class Utils:

    @staticmethod
    def parse_group_elements(group_elements, s, headers):
        max_users_count = None
        group_datas = []
        for group_element in group_elements:
            # parse group data
            group_data = Utils.parse_group_tag(group_tag=group_element, session=s, headers=headers)
            if group_data is not None:
                group_datas.append(group_data)
                if max_users_count is None:
                    max_users_count = group_data['users_count']
                else:
                    max_users_count = max(max_users_count, group_data['users_count'])

        uids = ''
        for group_data in group_datas:
            if group_data is not None:
                if len(uids) > 0:
                    uids = uids + ','
                uids = uids + '{}'.format(group_data['groupId'])

        if len(uids) > 0:
            # OK API
            application_id = '512000025985'
            client_key = 'CCIGGFJGDIHBABABA'
            client_secret = '9CF17E8FE80499EBF9689343'
            access_token = 'tkn1UivsiIJu3S2kQIGbRznqxG4msFox4uKZJo6adQcwBXkidpybEg9mLKWfRiIzrN8y3'
            # API_SERVER = 'https://api.ok.ru/api'
            API_SERVER = 'https://api.ok.ru/fb.do'

            params = {
                'method': 'group.getInfo',
                'format': 'json',
                'uids': uids,
                'fields': 'admin_id,uid',
            }

            secret_key = hashlib.md5((access_token + client_secret).encode('utf8')).hexdigest()
            application_key = 'application_key=' + client_key + 'fields=admin_id,uidformat=jsonmethod=group.getInfo' \
                              + 'uids=' + uids + secret_key
            sig = hashlib.md5(application_key.encode('utf8')).hexdigest()
            uidparam = urllib.parse.quote(uids)
            api_request = 'https://api.ok.ru/fb.do' \
                          '?application_key={}' \
                          '&fields=admin_id%2Cuid' \
                          '&format=json' \
                          '&method=group.getInfo' \
                          '&uids={}' \
                          '&sig={}' \
                          '&access_token={}' \
                .format(client_key, uidparam, sig, access_token)

            res = requests.get(api_request).text
            results = json.loads(res)

            for result in results:
                group_id = result['uid']
                for group_data in group_datas:
                    if group_data is not None and group_id == group_data['groupId']:
                        try:
                            group_data['admin_id'] = result['admin_id']
                        except KeyError:
                            print('ERROR ---- no group admin')
                            group_datas.remove(group_data)
            if len(group_datas) > 0:
                request = 'https://www.advertising-orange.com/?action=addOkGroup'
                res = requests.post(request, json=group_datas)

        return max_users_count

    @staticmethod
    def parse_group_tag(group_tag, session, headers):
        group_data = {}

        title_tag = group_tag.find('a', attrs={"class": "gs_result_i_t_name o"})
        title = title_tag['title']
        group_data['title'] = title

        link = 'https://ok.ru{}'.format(str(title_tag['href']))
        group_data['link'] = link

        group_id = None
        try:
            hrefattrs = str(title_tag['hrefattrs'])
            splits = re.split("&", hrefattrs)
        except KeyError:
            splits = re.split("&", link)
        for split in splits:
            if split.__contains__('st.groupId'):
                group_id_splits = re.split("=", str(split))
                group_id = int(group_id_splits[1])
        if group_id is not None:
            group_data['groupId'] = group_id

        group_users_tag = group_tag.find('div', attrs={"class": "gs_group_users lp-t"})
        users_count_text = group_users_tag.getText()
        splits = re.split(" ", users_count_text)
        users_count_text = splits[0]
        if users_count_text.__contains__('K'):
            splits = re.split("K", users_count_text)
            total_count = int(splits[0]) * 1000
        elif users_count_text.__contains__("M"):
            splits = re.split("M", users_count_text)
            total_count = int(splits[0]) * 1000000
        else:
            total_count = int(users_count_text)
        if total_count < Constants.OK_GROUP_MAX_USERS_COUNT:
            group_data['users_count'] = total_count
        else:
            return None

        try:
            group_descr_tag = group_tag.find('div', attrs={"class": "textWrap invisible js-group-description-full"})
            group_descr_text = str(group_descr_tag.getText())
        except AttributeError:
            group_descr_text = ''
        group_data['descr'] = group_descr_text

        return group_data


class Constants:
    OK_GROUP_MAX_USERS_COUNT = 1000
    OK_SESSION_COOKIES_FILE_NAME = 'cookies.txt'
    DEMO_KEY_WORDS = [
        "Маникюр"
    ]
    KEY_WORDS = [
        "Маникюр", "Педикюр", "магазин", "Студия", "Массаж", "Бахилы", "Наращивание ресниц"
        , "Brow", "Одежд", "Ремонт", "Салон", "Торт"
        , "цветы", "Визажист", "гель", "Макияж", "Свадебное", "Товар", "брендовой"
        , "тату", "ногти", "Бижутерия", "стрижк", "Массажист", "Ручная работа"
        , "заказ", "ручной работы", "парикмахер", "прическ", "Съедобн", "Букет", "Шиномонтаж"
        , "шугаринг", "ванн", "Сумк", "Тамада", "Ведущий", "Доставка", "Парфюм"
        , "коляски", "Мебель", "косметика", "обувь", "лак", "кафе"
        , "Тренер", "фитнес", "Питание", "Похудание", "Стилист", "Аниматор", "Фокусник"
        , "Установка", "Волосы", "Фотограф", "Декор", "Потолки", "Покраска", "Флорист"
        , "Имидж", "На праздник", "Лазер", "Косметолог", "Пирсинг", "Хной", "Tatto"
        , "Bust up", "Выправление", "Ламинирование", "Милирование", "Брови", "Ресницы", "Кожа"
        , "Мех", "Шубы", "Дед мороз", "Снегурочка", "Подарки", "Корпоратив", "Юбилей"
        , "Грим", "Визажист", "Проект", "Бизнес", "Семинар", "Развитие", "Парикмахер"
        , "Архитектор", "Выпечк", "Перевозки", "Капкейки", "Рецепт", "Карепрост", "Продажа щенков"
        , "Окрашивание", "Пилинг", "Lashmaker", "Коррекция"
        , "Организатор", "Кератин", "BOOST UP", "beauty"
        , "отоплени", "квартир", "кухн", "утепление", "новостройка"
        , "здоровье", "красота", "услуги", "нарощування", "послуги", "строительство", "биохимия"
        , "реабилитолог", "терапия", "процедур", "лечение", "акварель", "покрытие", "studio"
        , "мастер", "design", "дизайн", "манiкюр", "завивка", "полировка"
        , "депиляци", "сервис", "релакс", "профессионал", "обслуживани"
        , "персонал", "антистрес", "подаро", "лечебн", "укрепление", "расслабляющ", "медицинск"
        , "специалист", "доктор", "оздоровительн", "аренда", "аксессуар", "недвижимост", "материалы"
        , "оборудование", "техника", "отдых", "купить", "коммерческ", "электроника", "запчасти"
        , "велосипеды", "швеи", "инструменты", "продукты", "строительн", "трикотаж", "такси"
        , "аукцион", "изделия", "продается", "прибор", "сельскохозяйствен", "станок", "восстановление"
        , "масаж", "дорого", "delivery", "запись", "антицелюл", "предложения", "оздоровчий"
        , "транспорт", "дешев", "доступн", "сиворотка", "полиграфия", "развлечени", "прокат"
        , "омолаживающ", "частн", "монтаж", "интерьер", "элитн", "отделка"
        , "строительные", "сантехн", "скидки", "консультаци", "эксперт", "клиент"
        , "выполним", "сделаем", "менеджер", "детал", "договор", "штукатурк", "жилье"
        , "машин", "реконструкция", "линолеум", "ламинат", "инженер", "гаранти", "компетентны"
        , "пеноблок", "проектирование", "кондитер", "конфеты", "Шоколад", "мармелад", "Мороженое"
        , "пирог", "повар", "пирожное", "печенье", "пицца", "рулет", "бисквит"
        , "застоль", "ресторан", "десерт", "мясн", "гарнир", "обеды"
        , "блюдо", "блюда", "банкет", "деликатес", "жилет", "меховы", "пошив", "распродажа"
        , "шапк", "куртк", "штаны", "полушубок", "пальто", "рюкзак"
        , "наушники", "шиншилла", "изготовление", "дубленк", "пуховик", "ветровк"
        , "убор", "хутр", "оплата", "продукция", "текстиль", "кашемир", "каталог"
        , "ассортимент", "перчатки", "кошельки", "косметички"
        , "шарфы", "ботинки", "кроссовки", "сапоги", "туфли", "угги", "антенны"
        , "рубашки", "брюки", "свитеры", "джинсы", "платья", "юбки", "толстовки"
        , "костюмы", "купальники", "блузки", "пиджаки", "костюмы", "белье", "футболки"
        , "майки", "топы", "платья", "сарафаны", "шорты", "мокасины", "кеды"
        , "покупки", "средства", "свадьба", "букеты", "флористика", "торжеств"
        , "видеооператор", "артисты", "музыканты", "видеосъемка", "кортеж", "фейерверки", "салюты"
        , "каравай", "франшиза", "целебный", "шоумен", "браслеты", "кулоны", "серьги"
        , "кольца", "сумки", "часы", "брошки", "термосы", "колье", "расчески"
        , "чехлы", "фурнитура", "сережки", "украшени", "игрушки", "самоцветы", "драгоценные камни"
        , "топаз", "янтарь", "малахит", "платина", "кимберлитовые"
        , "турмалин", "драгоценный камень", "сапфир", "канцтовары", "напитки", "ноутбуки", "компьютеры"
        , "диваны", "столы", "шкафы", "кровати", "кресла", "матрасы", "комоды"
        , "стулья", "столики", "спальни", "стульчики", "комплекты", "стеллажи", "каркасы"
        , "бассейны", "табуреты", "пуфики", "рассрочка", "наборы", "посуда", "коврики"
        , "ковры", "гобелены", "бытовая", "принадлежности", "аккумуляторы", "палатки", "колонки"
        , "шины", "устройства", "холодильники", "туристические", "акустика", "самокаты", "велосипедны"
        , "телевизоры", "мангалы", "тренажеры", "колготки", "чулки", "носки", "полотенца"
        , "антенны", "дезодоранты", "кондиционеры", "инвентарь", "аквариумистика", "сноуборды", "снасти"
        , "чемоданы", "джойстики", "килими", "ковролин", "шелк", "дорожки", "синтетические"
        , "шерстяные", "боксерские", "пояса", "груши", "кимоно", "шлемы", "капы"
        , "экипировка", "щитки", "скакалки", "бандажи", "наколенники", "борцовки", "снаряжение"
        , "термобелье", "налокотники", "ремни", "фонари", "кобуры", "крепления", "бронежилеты"
        , "ателье", "акриловы", "алмазн", "авиалинии", "Автоматическ", "автомасла", "адвокат"
        , "аудиторс", "акушер", "AliExpress для", "автомаляр"
        , "Автострахование", "Агент по недвижимости", "автомойка", "автосалон"
        , "барахолка", "Бурение скважин", "бумажники", "багеты", "батареи"
        , "билеты", "бюро", "буфет", "бассейны", "батуты", "брокер", "бухгалтер"
        , "бизнес-тренер", "БУ авто", "бумажные скульптуры", "ВЕНТИЛЯЦИЯ"
        , "воздушные шарики", "восточные сладости", "витражист", "ветеринарная клиника"
        , "вакансии", "врач педиатр", "Выкройки", "Всё для Pole", "Вебинар", "Врач психотерапевт"
        , "гантели", "горны", "диетолог", "девелопер", "дрессировщик"
        , "декоративн", "дайвинг", "дипломные", "оптика", "обмен валют"
        , "отел", "ортопедическ", "оружейная", "охотовед", "офтальмолог"
        , "оптометрист", "ОПТОМ", "сауна", "салон краси", "страхование"
        , "стартовые", "спорттовары", "спортпит", "стоматология", "сендвич", "солярий"
        , "СПОРТИНВЕНТАРЬ", "Спортивный врач", "Спортивный психолог", "Страховой агент"
        , "Спичрайтер", "Супервайзер", "тренажоры", "Тренинг-менеджер", "тренинг"
        , "Телохранитель", "парилки", "препараты", "подъемники", "Пушистые пледы"
        , "пневматика", "продюсер", "паркет", "памятники", "Пластическая хирургия"
        , "перетяжка", "Программист 1С", "ревизоры", "рефераты", "реферальная"
        , "Реставратор", "Риэлтор", "Ресторатор", "из перья", "аксесуар"
        , "Автоцентр", "Вязанные", "Орифлейм", "ORIFLAME", "коррекци"
        , "ЕвроБетон", "Оратор", "камины", "Экскурсия", "Жилые комплексы"
        , "Жилой комплекс", "Детская ярмарка", "Аквариумные рыбки", "Поездка", "вязаные"
        , "Детский клуб", "Цветочная корзинка", "Цветочная корзина", "ноготки", "Мебели"
        , "Юридическая помощь", "хореография", "БАТЭЛЬ", "Batel", "Продажа"
        , "фасадных", "термопанелей", "AVON", "БОРТИКИ", "КОНВЕРТЫ"
        , "ОДЕЯЛКИ", "Всё для деток", "нижнее бельё", "Эпиляция", "бровей"
        , "английский", "Бетон", "Прачечная"
        , "Токарные работы", "двери", "сейфы", "пекарня", "Наращивание"
        , "ногтей", "ресничек", "Стеклопластиковая", "арматура"

        , "Manicure", "Pedicure", "shop", "Studio", "Massage", "Eyelash"
        , "Brow", "Clothes", "Repair", "Salon", "Cake"
        , "flowers", "gel", "Make-up", "Wedding", "Goods", "brand"
        , "nails", "jewelry", "haircut", "Masseur"
        , "order", "handmade", "hairdresser", "hairstyle", "bouquet"
        , "shugaring", "baths", "Bag", "Tamada", "Leading", "Delivery", "Perfume"
        , "strollers", "Furniture", "cosmetics", "shoes", "lacquer", "cafe"
        , "Coach", "fitness", "Nutrition", "Weight Loss", "Stylist", "Animator", "Magician"
        , "Installation", "Hair", "Photographer", "Decor", "Ceilings", "Paint", "Florist"
        , "Image", "Laser", "Cosmetologist", "Piercing", "Henna"
        , "Straightening", "Laminating", "Milling", "Eyebrows", "Eyelashes", "Skin"
        , "Fur", "Santa Claus", "Snow Maiden", "Gifts", "Corporate", "Jubilee"
        , "Makeup", "Project", "Business", "Seminar", "Development", "Hairdresser"
        , "Architect", "Bake", "Carriage", "Recipe", "Kareprost", "Sale of puppies"
        , "Coloring", "Peeling", "Lashmaker", "Correction"
        , "Organizer", "Keratin"
        , "heating", "apartments", "kitchens", "warming"
        , "health", "construction", "biochemistry"
        , "rehabilitator", "therapy", "procedures", "treatment", "watercolor", "cover"
        , "master", "curling", "polishing"
        , "depilation", "service", "relax", "professional", "personnel", "antistress", "medical"
        , "strengthening", "relaxing", "medical"
        , "specialist", "doctor", "healthier", "rent", "accessory", "real estate", "materials"
        , "equipment", "rest", "buy", "commercial", "electronics", "parts"
        , "bicycles", "seamstresses", "tools", "products", "construction", "knitwear", "taxi"
        , "auction", "products", "sold", "appliance", "agricultural", "machine", "restoration"
        , "massage", "expensive", "delivery", "record", "anti-cellulite", "suggestions", "health"
        , "transport", "cheap", "available", "serum", "polygraphy", "entertainment", "rental"
        , "rejuvenating", "private", "installation", "interior", "elite", "decoration"
        , "construction", "plumbing", "discounts", "consulting", "expert", "client"
        , "manager", "details", "contract", "plaster", "housing"
        , "machines", "reconstruction", "linoleum", "laminate", "engineer", "guarantee", "competent"
        , "design", "confectioner", "candy", "Chocolate", "marmalade", "Ice cream"
        , "pie", "cook", "cake", "cookies", "pizza", "roll", "biscuit"
        , "feast", "restaurant", "dessert", "meat", "garnish", "lunches"
        , "dish", "banquet", "delicacy", "vest", "sewing", "sale"
        , "cap", "jacket", "pants", "coat", "backpack"
        , "headphones", "chinchilla", "making", "down jacket", "wind"
        , "payment", "products", "textiles", "cashmere", "catalog"
        , "assortment", "clothes", "shoes", "gloves", "wallets", "beauticians"
        , "scarves", "boots", "sneakers", "antennas"
        , "shirt", "trousers", "sweaters", "jeans", "skirts", "hoodies"
        , "suits", "blouses", "jackets", "wear"
        , "T-shirts", "tops", "dresses", "sarafans", "shorts", "moccasins"
        , "wedding", "bouquets", "floristics", "celebrations"
        , "videographer", "artists", "musicians", "video", "tuple", "fireworks", "salutes"
        , "franchise", "curative", "showman", "bracelets", "pendants", "earrings"
        , "rings", "bags", "watches", "brooches", "thermoses", "necklaces", "combs"
        , "cases", "accessories", "earrings", "decorations", "toys", "gems", "precious stones"
        , "topaz", "amber", "malachite", "platinum", "kimberlite"
        , "tourmaline", "precious stone", "sapphire", "stationery", "drinks", "laptops", "computers"
        , "sofas", "tables", "cabinets", "beds", "chairs", "mattresses"
        , "tables", "bedrooms", "racks", "skeletons"
        , "swimming pools", "stools", "installments", "sets", "dishes", "rugs"
        , "carpets", "tapestries", "household", "accessories", "batteries", "tents", "columns"
        , "tires", "devices", "refrigerators", "tourist", "acoustics", "scooters", "bicycles"
        , "TVs", "braziers", "trainers", "pantyhose", "stockings", "socks", "towels"
        , "aerials", "deodorants", "conditioners", "inventory", "aquarium", "snowboards", "tackles"
        , "suitcases", "joysticks", "kilimi", "carpet", "silk", "paths", "synthetic"
        , "woolen", "boxing", "belt", "pear", "kimono", "helmets", "kapy"
        , "shields", "skipping ropes", "bandages", "knee pads", "wrestlers", "equipment"
        , "thermal underwear", "elbow pads", "belts", "flashlights", "holsters", "bindings", "bulletproof vests"
        , "atelier", "acrylic", "diamond", "airline", "automatic", "auto", "lawyer"
        , "auditors", "obstetrician", "AliExpress for", "automaton"
        , "Auto Insurance", "Real Estate Agent", "car wash"
        , "flea market", "Drilling wells", "wallets", "baguettes", "batteries"
        , "tickets", "bureau", "buffet", "pools", "trampolines", "broker", "accountant"
        , "business coach", "paper sculptures", "VENTILATION"
        , "balloons", "oriental sweets", "stained-glass window", "veterinary clinic"
        , "vacancies", "doctor pediatrician", "Patterns", "Everything for Pole", "Webinar", "Doctor therapist"
        , "dumbbells", "horns", "dietician", "developer", "trainer"
        , "decorative", "diving", "diploma", "optics", "currency exchange"
        , "calving", "orthopedic", "weapon", "hunting specialist", "ophthalmologist"
        , "optometrist", "OPTOM", "sauna", "beauty salon", "insurance"
        , "starting", "sport goods", "sportspit", "stomatology", "sandwich", "solarium"
        , "Sports doctor", "Sports psychologist", "Insurance agent"
        , "Speech Reciter", "Supervisor", "simulators", "Training Manager", "training"
        , "Bodyguard", "steam room", "preparations", "lifts", "Fluffy blankets"
        , "pneumatics", "producer", "parquet", "monuments", "Plastic surgery"
        , "developer", "programmer", "auditors", "abstracts", "referral"
        , "Restorer", "Realtor", "Restaurateur", "feathers", "accessories"
    ]
