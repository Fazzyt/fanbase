# Fanbase API Documentation

## Общие сведения
- Базовый URL: `http://domain/api/v1/`
- Все ответы возвращаются в формате JSON
- В случае ошибки возвращается код статуса HTTP и JSON с описанием ошибки

### 1. Получение цитат
`GET /get_quotes`

#### Параметры
- `person_id` (обязательный): ID персоны

#### Примеры запросов
/api/v1/get_quotes?person_id=1      # Цитаты персоны по ID

### Ответ
{
"quotes": [
        {
            "id": 1,
            "quote": "Текст цитаты",
            "person_id": 1
        }
    ],
    "status": 200
}

### 2. Получение цитируемых
`GET /get_person`

#### Параметры
- `person_id` (обязательный): ID персоны
или
- `full_name` (обязательный): полное имя персоны

#### Примеры запросов
/api/v1/get_person?person_id=1      # Детали персоны по ID
/api/v1/get_person?full_name=Иванов # Детали персоны по имени

### Ответ
{
    "person": [
        {
            "full_name": "Иванов",
            "id": 1
        }
    ],
    "status": 200
}
