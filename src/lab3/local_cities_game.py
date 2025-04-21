from load_cities import load_russian_cities

cities_list = load_russian_cities()

used_cities = []
current_letter = None

print("Игра в города (локальная версия)")
while True:
    city = input("Введите город: ").strip().lower()
    if city in used_cities:
        print("Этот город уже был.")
        continue
    if city not in cities_list:
        print("Такого города нет в списке.")
        continue
    if current_letter and not city.startswith(current_letter):
        print(f"Город должен начинаться на букву '{current_letter.upper()}'.")
        continue
    used_cities.append(city)
    last_letter = city[-1].lower()
    current_letter = city[-2].lower() if last_letter in ['ь', 'ъ', 'ы'] else last_letter