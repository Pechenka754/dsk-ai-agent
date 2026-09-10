from ai_parser import (
    parse_user_request,
    generate_clarifying_question,
    parse_complex_selection,
    parse_apartment_selection,
    detect_intent,
    find_information_target,
    generate_information_answer,
    compare_complexes_by_criterion,
    compare_apartments_by_criterion,
    is_context_reference_request,
    parse_context_selection,
    is_complex_reference_request,
    is_last_object_reference
)

from database import (
    create_database,
    add_test_apartments,
    search_apartments,
    search_nearest_apartments,
    get_complexes_for_filters,
    get_complexes_by_ids,
    get_complex_names_by_apartments,
    get_complex_by_id,
    get_all_complexes
)


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================================

def is_request_complete(filters):
    """Проверяет, достаточно ли параметров для поиска."""

    return filters.get("rooms") is not None


def print_filters(filters):
    """Красиво выводит текущие параметры поиска."""

    print()
    print("Текущие параметры поиска:")

    rooms = filters.get("rooms")
    min_area = filters.get("min_area")
    max_area = filters.get("max_area")
    max_price = filters.get("max_price")
    max_floor = filters.get("max_floor")

    if rooms is None:
        print("  Комнаты: не указано")
    else:
        print(f"  Комнаты: {rooms}")

    if min_area is None:
        print("  Минимальная площадь: не указана")
    else:
        print(f"  Минимальная площадь: {min_area:g} м²")

    if max_area is None:
        print("  Максимальная площадь: не указана")
    else:
        print(f"  Максимальная площадь: {max_area:g} м²")

    if max_price is None:
        print("  Максимальная цена: не указана")
    else:
        print(
            f"  Максимальная цена: "
            f"{max_price:,.0f} ₽".replace(",", " ")
        )

    if max_floor is None:
        print("  Максимальный этаж: не указан")
    else:
        print(f"  Максимальный этаж: {max_floor}")


def print_manager_context(filters, last_request, selected_ids):
    """Показывает менеджеру контекст запроса пользователя."""

    print()
    print("Информация для менеджера:")
    print()

    rooms = filters.get("rooms")
    min_area = filters.get("min_area")
    max_area = filters.get("max_area")
    max_price = filters.get("max_price")
    max_floor = filters.get("max_floor")

    if rooms is None:
        print("  Комнаты: не указано")
    else:
        print(f"  Комнаты: {rooms}")

    if min_area is None:
        print("  Минимальная площадь: не указана")
    else:
        print(f"  Минимальная площадь: {min_area:g} м²")

    if max_area is None:
        print("  Максимальная площадь: не указана")
    else:
        print(f"  Максимальная площадь: {max_area:g} м²")

    if max_price is None:
        print("  Максимальный бюджет: не указан")
    else:
        print(
            f"  Максимальный бюджет: "
            f"{max_price:,.0f} ₽".replace(",", " ")
        )

    if max_floor is None:
        print("  Максимальный этаж: не указан")
    else:
        print(f"  Максимальный этаж: {max_floor}")

    if selected_ids:
        selected_complexes = get_complexes_by_ids(
            selected_ids
        )

        print()
        print("  Выбранные ЖК:")

        for complex_data in selected_complexes:
            print(f"    - {complex_data[1]}")

    if last_request:
        print()
        print(
            f"  Последний запрос пользователя: "
            f"«{last_request}»"
        )


def print_apartment_details(apartment):
    """Выводит подробную информацию о квартире."""

    if not apartment:
        return

    (
        apartment_id,
        complex_id,
        rooms,
        area,
        price,
        floor,
        finishing,
        balcony,
        image,
        booking_status,
        booking_type,
        booking_until
    ) = apartment

    complex_data = get_complex_by_id(
        complex_id
    )

    complex_name = "Не указан"

    if complex_data:
        complex_name = complex_data[1]

    print()
    print("Информация о квартире:")
    print()
    print(f"ID: {apartment_id}")
    print(f"Жилой комплекс: {complex_name}")
    print(f"Количество комнат: {rooms}")
    print(f"Площадь: {area} м²")
    print(f"Цена: {price:,.0f} ₽")
    print(f"Этаж: {floor}")
    print(f"Отделка: {finishing}")
    print(f"Балкон: {balcony}")
    print(f"Статус бронирования: {booking_status}")


def print_complexes(complexes):
    """Выводит список подходящих ЖК."""

    print()
    print("Подходящие жилые комплексы:")
    print()

    for index, complex_data in enumerate(complexes, start=1):

        (
            complex_id,
            name,
            district,
            housing_class,
            completion_year,
            description,
            infrastructure,
            parking,
            apartment_count
        ) = complex_data

        print(f"{index}. {name}")
        print(f"   Район: {district}")
        print(f"   Класс: {housing_class}")
        print(f"   Сдача: {completion_year}")
        print(f"   Описание: {description}")
        print(f"   Инфраструктура: {infrastructure}")
        print(f"   Парковка: {parking}")
        print(f"   Подходящих квартир: {apartment_count}")
        print()


def print_apartments(apartments):
    """Выводит найденные квартиры."""

    if not apartments:
        return

    complex_names = get_complex_names_by_apartments(apartments)

    print("Подходящие квартиры:")

    for apartment in apartments:

        (
            apartment_id,
            complex_id,
            rooms,
            area,
            price,
            floor,
            finishing,
            balcony,
            image,
            booking_status,
           booking_type,
            booking_until
        ) = apartment

        complex_name = complex_names.get(
            complex_id,
            f"ЖК #{complex_id}"
        )

        print(
            f"ID: {apartment_id} | "
            f"{complex_name} | "
            f"{rooms}-комнатная | "
            f"{area:g} м² | "
            f"{price:,.0f} ₽ | "
            f"{floor} этаж | "
            f"{finishing}"
        )


def print_apartment_comparison(apartments):
    """Выводит сравнительную таблицу квартир."""

    if not apartments or len(apartments) < 2:
        print()
        print(
            "Агент: Для сравнения нужно выбрать "
            "как минимум две квартиры."
        )
        return

    print()
    print("Сравнение квартир:")
    print()

    headers = [
        "Параметр",
        "Квартира 1",
        "Квартира 2"
    ]

    rows = []

    for apartment in apartments[:2]:

        (
            apartment_id,
            complex_id,
            rooms,
            area,
            price,
            floor,
            finishing,
            balcony,
            image,
            booking_status,
            booking_type,
            booking_until
        ) = apartment

        complex_data = get_complex_by_id(
            complex_id
        )

        complex_name = "Не указан"

        if complex_data:
            complex_name = complex_data[1]

        rows.append(
            {
                "id": apartment_id,
                "complex": complex_name,
                "rooms": rooms,
                "area": area,
                "price": f"{price:,.0f} ₽",
                "floor": floor,
                "finishing": finishing
            }
        )

    apartment_1 = rows[0]
    apartment_2 = rows[1]

    print(
        f"{headers[0]:<20}"
        f"{headers[1]:<25}"
        f"{headers[2]:<25}"
    )

    print("-" * 70)

    print(
        f"{'ID':<20}"
        f"{str(apartment_1['id']):<25}"
        f"{str(apartment_2['id']):<25}"
    )

    print(
        f"{'ЖК':<20}"
        f"{apartment_1['complex']:<25}"
        f"{apartment_2['complex']:<25}"
    )

    print(
        f"{'Комнаты':<20}"
        f"{str(apartment_1['rooms']):<25}"
        f"{str(apartment_2['rooms']):<25}"
    )

    print(
        f"{'Площадь':<20}"
        f"{str(apartment_1['area']) + ' м²':<25}"
        f"{str(apartment_2['area']) + ' м²':<25}"
    )

    print(
        f"{'Цена':<20}"
        f"{apartment_1['price']:<25}"
        f"{apartment_2['price']:<25}"
    )

    print(
        f"{'Этаж':<20}"
        f"{str(apartment_1['floor']):<25}"
        f"{str(apartment_2['floor']):<25}"
    )

    print(
        f"{'Отделка':<20}"
        f"{apartment_1['finishing']:<25}"
        f"{apartment_2['finishing']:<25}"
    )


def print_comparison(complexes):
    """Выводит сравнительную таблицу ЖК."""

    if not complexes:
        return

    print()
    print("=" * 120)
    print("Сравнение жилых комплексов")
    print("=" * 120)

    headers = [
        "Характеристика"
    ]

    for complex_data in complexes:
        headers.append(complex_data[1])

    rows = [
        ("Район", 2),
        ("Класс", 3),
        ("Сдача", 4),
        ("Описание", 5),
        ("Инфраструктура", 6),
        ("Парковка", 7)
    ]

    column_widths = [22]

    for complex_data in complexes:
        values = [
            str(complex_data[1]),
            str(complex_data[2]),
            str(complex_data[3]),
            str(complex_data[4]),
            str(complex_data[5]),
            str(complex_data[6]),
            str(complex_data[7])
        ]

        max_width = max(
            len(value)
            for value in values
        )

        column_widths.append(
            min(max(max_width, 20), 45)
        )

    # Заголовок
    for index, header in enumerate(headers):
        width = column_widths[index]

        if index == 0:
            print(
                f"{header:<{width}}",
                end=" | "
            )
        else:
            print(
                f"{header:<{width}}",
                end=" | "
            )

    print()

    print("-" * 120)

    # Строки
    for row_name, data_index in rows:

        print(
            f"{row_name:<{column_widths[0]}}",
            end=" | "
        )

        for index, complex_data in enumerate(complexes):

            value = str(complex_data[data_index])

            width = column_widths[index + 1]

            # Чтобы очень длинное описание
            # не разорвало таблицу
            if len(value) > width:
                value = value[:width - 3] + "..."

            print(
                f"{value:<{width}}",
                end=" | "
            )

        print()

    print("=" * 120)


def print_alternatives(
    filters,
    exclude_ids=None
):
    """Выводит ближайшие варианты, если точных совпадений нет."""

    alternatives = search_nearest_apartments(
        filters,
        limit=5,
        exclude_ids=exclude_ids
    )

    if not alternatives:
        print()
        print(
            "К сожалению, подходящих вариантов "
            "в базе пока нет."
        )

        return []

    print()
    print(
        "Точных совпадений не найдено. "
        "Но я подобрал наиболее близкие варианты:"
    )
    print()

    print_apartments(alternatives)

    return alternatives


def print_next_actions():
    """Показывает возможные следующие действия."""

    print()
    print("Агент: Вы можете:")
    print("- изменить параметры поиска;")
    print("- выбрать ЖК для сравнения;")
    print("- попросить подобрать другие варианты;")
    print("- узнать подробнее о конкретном ЖК;")
    print("- обратиться к менеджеру.")


def print_information_help():
    """Подсказка для информационных запросов."""

    print()
    print(
        "Например, вы можете спросить:"
    )
    print(
        "«Расскажи подробнее про ЖК Парковый»"
    )
    print(
        "«Какая инфраструктура у ЖК Парковый?»"
    )
    print(
        "«Какая парковка в ЖК Парковый?»"
    )


# ==========================================================
# ОСНОВНОЙ ЗАПУСК
# ==========================================================

create_database()
add_test_apartments()


# ==========================================================
# СОСТОЯНИЕ ДИАЛОГА
# ==========================================================

current_filters = {
    "rooms": None,
    "max_price": None,
    "min_area": None,
    "max_area": None,
    "max_floor": None
}

last_user_request = ""

last_complexes = []
selected_complex_ids = []

last_apartments = []
shown_apartment_ids = set()

selected_apartments = []

last_selected_apartment = None
last_selected_complex_id = None

last_context_type = None

print()
print("=" * 70)
print("AI-агент подбора квартир")
print("=" * 70)
print()
print("Введите запрос или напишите «выход» для завершения.")
print()


# ==========================================================
# ЦИКЛ ДИАЛОГА
# ==========================================================

while True:

    user_text = input("Вы: ").strip()

    if not user_text:
        continue

    last_user_request = user_text

    if user_text.lower() in [
        "выход",
        "exit",
        "quit"
    ]:
        print()
        print("Агент: Хорошего дня!")
        break

    # ======================================================
    # ОПРЕДЕЛЯЕМ НАМЕРЕНИЕ
    # ======================================================

    intent = detect_intent(
        user_text,
        last_complexes
    )

    # ======================================================
    # МЕНЕДЖЕР
    # ======================================================

    if intent == "manager":

        print()
        print(
            "Агент: Конечно. "
            "Передаю ваш запрос менеджеру."
        )

        print_manager_context(
            current_filters,
            last_user_request,
            selected_complex_ids
        )

        print()
        print("[MANAGER_REQUEST]")

        continue

    if is_complex_reference_request(user_text):

        selected = parse_context_selection(
            user_text,
            last_complexes
        )

        if selected:

            selected_complex_ids = [
                complex_data[0]
                for complex_data in selected
            ]

            last_selected_complex_id = selected[-1][0]

            print()
            print("Агент: Вы выбрали:")

            print_complexes(
                selected
            )

            continue

    if (
        is_context_reference_request(user_text)
        and intent not in ["information", "comparison"]
    ):

        # Если контекст — квартиры
        if last_context_type == "apartment":

            selected = parse_context_selection(
                user_text,
                last_apartments
            )

            if selected:

                for apartment in selected:
                    if apartment not in selected_apartments:
                        selected_apartments.append(apartment)

                last_selected_apartment = selected[-1]

                print()
                print("Агент: Вы выбрали:")

                print_apartments(
                    selected
                )

                continue

        if any(
            phrase in user_text.lower()
            for phrase in [
                "этот",
                "эта",
                "это",
                "эту",
                "данный",
                "данная",
                "данное",
                "данную"
            ]
        ):

            if last_selected_apartment:

                selected_apartments = [
                    last_selected_apartment
                ]

                print()
                print("Агент: Речь идёт об этом варианте:")

                print_apartments(
                    selected_apartments
                )

                continue

        # Если контекст — ЖК
        if last_context_type == "complex":

            selected = parse_context_selection(
                user_text,
                last_complexes
            )
    
            if selected:

                selected_complex_ids = [
                    complex_data[0]
                    for complex_data in selected
                ]

                last_selected_complex_id = selected[-1][0]

                print()
                print("Агент: Вы выбрали:")

                print_complexes(
                    selected
                )

                continue

    if (
        last_selected_apartment
        and any(
            phrase in user_text.lower()
            for phrase in [
                "расскажи подробнее",
                "расскажи про",
                "расскажи о",
                "подробнее про",
                "подробнее о",
                "что это за вариант",
                "что это за квартира",
                "информация про",
                "информация о"
            ]
        )
        and is_last_object_reference(user_text)
    ):

        print()
        print(
            "Агент: Конечно. Вот подробная информация "
            "по выбранному варианту:"
        )

        print_apartment_details(
            last_selected_apartment
        )

        continue

    # --------------------------------------------------
    # Ссылка на последний выбранный объект
    # --------------------------------------------------

    if is_last_object_reference(user_text):

        text_lower = user_text.lower()

        # Если пользователь задаёт вопрос об объекте, это должен обработать intent "information", а не обычная ссылка.
        information_words = [
            "расскажи",
            "подробнее",
            "что это",
            "что за",
            "информация",
            "описание",
            "характеристик",
            "характеристика"
        ]

        is_information_request_about_object = any(
            word in text_lower
            for word in information_words
        )

        if not is_information_request_about_object:

            if last_selected_apartment:

                selected_apartments = [
                    last_selected_apartment
                ]

                print()
                print(
                    "Агент: Речь идёт об этом варианте:"
                )

                print_apartments(
                    selected_apartments
                )

                continue

            if last_selected_complex_id:

                complex_data = get_complex_by_id(
                    last_selected_complex_id
                )

                if complex_data:

                    print()
                    print(
                        "Агент: Речь идёт об этом ЖК:"
                    )

                    print_complexes(
                        [complex_data]
                    )

                    continue

            print()
            print(
                "Агент: Пока не удалось определить, "
                "какой именно вариант вы имеете в виду."
            )

            continue

    if intent == "alternative":

        if not current_filters.get("rooms"):
            print()
            print(
                "Агент: Сначала давайте определимся, "
                "сколько комнат вам нужно."
            )
            continue

        excluded_ids = shown_apartment_ids

        alternatives = search_nearest_apartments(
            current_filters,
            limit=5,
            exclude_ids=excluded_ids
        )

        if not alternatives:
            print()
            print(
                "Агент: Я показал все доступные "
                "подходящие или наиболее близкие варианты."
            )

            print()
            print(
                "Агент: Можно изменить параметры поиска "
                "или обратиться к менеджеру."
            )

            continue

        last_apartments = alternatives
        last_context_type = "apartment"

        # Запоминаем эти квартиры, чтобы больше их не показывать
        for apartment in alternatives:
            shown_apartment_ids.add(
                apartment[0]
            )

        print()
        print(
            "Агент: Конечно. Вот другие варианты:"
        )
        
        print()

        print_apartments(
            alternatives
        )

        print_next_actions()

        continue

    # ======================================================
    # ВЫБОР КВАРТИРЫ
    # ======================================================

    if intent == "apartment":

        if not last_apartments:
            print()
            print(
                "Агент: Сейчас нет списка квартир, "
                "из которого можно выбрать."
            )
            print(
                "Сначала выполните поиск квартир."
            )
            continue

        newly_selected_apartments = parse_apartment_selection(
            user_text,
            last_apartments
        )

        if not newly_selected_apartments:
            print()
            print(
                "Агент: Я не смог определить, "
                "какую квартиру вы выбрали."
            )
            print(
                "Например: «первый вариант» "
                "или «квартира ID 13»."
            )
            continue

        # Добавляем новые квартиры к уже выбранным
        for apartment in newly_selected_apartments:
            if apartment not in selected_apartments:
                selected_apartments.append(apartment)

        last_selected_apartment = selected_apartments[-1]

        print()
        print("Агент: Вы выбрали:")

        print_apartments(
            selected_apartments
        )

        continue

    # ======================================================
    # СРАВНЕНИЕ ЖК
    # ======================================================

    if intent == "comparison":

        # --------------------------------------------------
        # Сначала проверяем выбранные квартиры
        # --------------------------------------------------

        if selected_apartments and len(selected_apartments) >= 2:

            criterion = compare_apartments_by_criterion(
                user_text,
                selected_apartments
            )

            # Если пользователь указал конкретный критерий
            if criterion == "cheapest":

                cheapest = min(
                    selected_apartments,
                    key=lambda apartment: apartment[4]
                )

                print()
                print("Агент: Самый дешёвый вариант:")

                print_apartments(
                    [cheapest]
                )

                continue

            if criterion == "most_expensive":

                most_expensive = max(
                    selected_apartments,
                    key=lambda apartment: apartment[4]
                )

                print()
                print("Агент: Самый дорогой вариант:")

                print_apartments(
                    [most_expensive]
                )

                continue

            if criterion == "largest_area":

                largest = max(
                    selected_apartments,
                    key=lambda apartment: apartment[3]
                )

                print()
                print("Агент: Вариант с наибольшей площадью:")

                print_apartments(
                    [largest]
                )

                continue

            if criterion == "smallest_area":

                smallest = min(
                    selected_apartments,
                    key=lambda apartment: apartment[3]
                )

                print()
                print("Агент: Вариант с наименьшей площадью:")

                print_apartments(
                    [smallest]
                )

                continue

            if criterion == "highest_floor":

                highest = max(
                    selected_apartments,
                    key=lambda apartment: apartment[5]
                )

                print()
                print("Агент: Вариант на самом высоком этаже:")

                print_apartments(
                    [highest]
                )

                continue

            if criterion == "lowest_floor":

                lowest = min(
                    selected_apartments,
                    key=lambda apartment: apartment[5]
                )

                print()
                print("Агент: Вариант на самом низком этаже:")

                print_apartments(
                    [lowest]
                )

                continue

            # Если конкретный критерий не указан —
            # показываем полное сравнение квартир

            print_apartment_comparison(
                selected_apartments
            )

            continue

        # --------------------------------------------------
        # Если квартир не выбрано — сравниваем ЖК
        # --------------------------------------------------

        if not selected_complex_ids:

            print()
            print(
                "Агент: Сначала выберите ЖК или квартиры, "
                "которые хотите сравнить."
            )

            print()
            print("Например:")
            print("«первый и пятый ЖК»")
            print("или")
            print("«ID 13 и ID 3»")

            continue

        complexes = get_complexes_by_ids(
            selected_complex_ids
        )

        if not complexes:

            print()
            print(
                "Агент: Не удалось найти выбранные ЖК."
            )

            continue

        criterion = compare_complexes_by_criterion(
            user_text,
            complexes
        )

        if criterion:

            print()
            print(
                "Агент: Сравнение по выбранному критерию:"
            )

            print()

            print_comparison(
                complexes
            )

            continue

        print_comparison(
            complexes
        )

        continue
    
    # ======================================================
    # ИНФОРМАЦИЯ О ЖК
    # ======================================================

    if intent == "information":

            # Информация о последней выбранной квартире
        if (
            last_selected_apartment
            and is_last_object_reference(user_text)
        ):

            print()
            print(
                "Агент: Конечно. Вот подробная информация "
                "по выбранному варианту:"
            )

            print_apartment_details(
                last_selected_apartment
            )

            continue

        # ----------------------------------------------
        # Сначала пытаемся найти ЖК среди последних
        # показанных пользователю
        # ----------------------------------------------

        target_complex_id = find_information_target(
            user_text,
            last_complexes
        )

        # ----------------------------------------------
        # Если среди последних не нашли,
        # ищем среди всех ЖК
        # ----------------------------------------------

        if target_complex_id is None:

            all_complexes = get_all_complexes()

            target_complex_id = find_information_target(
                user_text,
                all_complexes
            )

        # ----------------------------------------------
        # Если всё равно не нашли
        # ----------------------------------------------

        if target_complex_id is None:

            print()
            print(
                "Агент: Уточните, пожалуйста, "
                "про какой ЖК вы хотите узнать."
            )

            if last_complexes:
                print()
                print("Недавно найденные ЖК:")

                for index, complex_data in enumerate(
                    last_complexes,
                    start=1
                ):
                    print(
                        f"{index}. {complex_data[1]}"
                    )

            print_information_help()

            continue

        # ----------------------------------------------
        # Получаем данные из SQLite
        # ----------------------------------------------

        complex_data = get_complex_by_id(
            target_complex_id
        )

        if complex_data is None:

            print()
            print(
                "Агент: К сожалению, "
                "информация об этом ЖК не найдена."
            )

            continue

        # ----------------------------------------------
        # Генерируем ответ
        # ----------------------------------------------

        answer = generate_information_answer(
            user_text,
            complex_data
        )

        print()
        print(f"Агент: {answer}")

        print()
        print(
            "Агент: Если хотите, могу также "
            "показать квартиры в этом ЖК "
            "или сравнить его с другим."
        )

        continue

    # ======================================================
    # ВЫБОР ЖК
    # ======================================================

    if intent == "complex":

        if not last_complexes:

            print()
            print(
                "Агент: Сейчас нет списка ЖК, "
                "из которого можно выбрать."
            )

            print(
                "Сначала задайте параметры поиска."
            )

            continue

        selected_ids = parse_complex_selection(
            user_text,
            last_complexes
        )

        if not selected_ids:

            print()
            print(
                "Агент: Я не смог определить, "
                "какие ЖК вы выбрали."
            )

            print(
                "Например: «первый, пятый и седьмой»."
            )

            continue

        selected_complex_ids = selected_ids

        selected_complexes = get_complexes_by_ids(
            selected_complex_ids
        )

        print()
        print("Агент: Вы выбрали:")

        for complex_data in selected_complexes:
            print(
                f"- {complex_data[1]}"
            )

        print()
        print(
            "Агент: Что хотите сделать "
            "с выбранными ЖК?"
        )

        print(
            "Например: «Чем они отличаются?»"
        )

        continue

    # ======================================================
    # ПОИСК КВАРТИР / ИЗМЕНЕНИЕ ФИЛЬТРОВ
    # ======================================================

    if intent == "filter":

        parsed = parse_user_request(
            user_text,
            current_filters
        )

        updates = parsed.get(
            "updates",
            {}
        )

        clear_fields = parsed.get(
            "clear_fields",
            []
        )

        # ----------------------------------------------
        # Если пользователь ничего не задал
        # ----------------------------------------------

        if not updates and not clear_fields:

            print()
            print(
                "Агент: Я не совсем понял, "
                "какие параметры вы хотите изменить."
            )

            print()
            print(
                "Например:"
            )
            print(
                "«Хочу двушку до 15 миллионов»"
            )
            print(
                "«Нужна квартира от 55 м²»"
            )
            print(
                "«Ищу однушку не выше 5 этажа»"
            )

            continue

        # ----------------------------------------------
        # Обновляем параметры
        # ----------------------------------------------

        for field, value in updates.items():

            if field in current_filters:
                current_filters[field] = value

        # ----------------------------------------------
        # Очищаем параметры
        # ----------------------------------------------

        for field in clear_fields:

            if field in current_filters:
                current_filters[field] = None

        # ----------------------------------------------
        # Показываем текущие параметры
        # ----------------------------------------------

        print_filters(
            current_filters
        )

        # ----------------------------------------------
        # Проверяем, хватает ли параметров
        # ----------------------------------------------

        if not is_request_complete(
            current_filters
        ):

            print()
            print(
                f"Агент: "
                f"{generate_clarifying_question(current_filters)}"
            )

            continue

        # ----------------------------------------------
        # Начинаем новый поиск
        # ----------------------------------------------

        shown_apartment_ids = set()

        # ----------------------------------------------
        # Ищем квартиры
        # ----------------------------------------------

        apartments = search_apartments(
        current_filters
        )

        # ----------------------------------------------
        # Если ничего не нашли
        # --------------------------ы--------------------

        if not apartments:
            last_apartments = print_alternatives(
                current_filters,
                exclude_ids=shown_apartment_ids
            )

            for apartment in last_apartments:
                shown_apartment_ids.add(
                    apartment[0]
                )

            print_next_actions()
            continue

        # Запоминаем последние показанные квартиры
        last_apartments = apartments
        last_context_type = "apartment"

        # Запоминаем все показанные квартиры
        for apartment in apartments:
            shown_apartment_ids.add(
                apartment[0]
            )

        # ----------------------------------------------
        # Ищем ЖК
        # ----------------------------------------------

        complexes = get_complexes_for_filters(
            current_filters
        )

        # Запоминаем последние ЖК
        last_complexes = complexes

        # После нового поиска старый выбор
        # лучше сбросить
        selected_complex_ids = []

        # ----------------------------------------------
        # Показываем ЖК
        # ----------------------------------------------

        print_complexes(
            complexes
        )

        # ----------------------------------------------
        # Показываем квартиры
        # ----------------------------------------------

        print()
        print_apartments(
            apartments
        )

        print_next_actions()

        continue

    # ======================================================
    # НЕИЗВЕСТНЫЙ ЗАПРОС
    # ======================================================

    print()
    print(
        "Агент: Я не совсем понял запрос."
    )

    print(
        "Я специализируюсь на подборе квартир "
        "и жилых комплексов."
    )

    print()
    print("Например, вы можете:")

    print(
        "• «Хочу двушку до 15 миллионов»"
    )

    print(
        "• «Хочу однушку от 40 м²»"
    )

    print(
        "• «Расскажи подробнее про ЖК Парковый»"
    )

    print(
        "• «Какая парковка в ЖК Речной?»"
    )

    print(
        "• «Сравни первый, третий и пятый ЖК»"
    )


