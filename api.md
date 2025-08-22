# Fanbase API Documentation

## Общие сведения
- Базовый URL: `http://domain/api/v1/`
- Все ответы возвращаются в формате JSON
- В случае ошибки возвращается код статуса HTTP и JSON с описанием ошибки
- API использует асинхронную архитектуру (Quart framework)
- Все эндпойнты поддерживают CORS для веб-приложений

## 1. Цитаты

### 1.1 Получение цитат персоны
`GET /get_quotes`

#### Параметры
- `person_id` (обязательный): ID персоны

#### Пример запроса
```
/api/v1/get_quotes?person_id=1
```

#### Ответ
```json
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
```

#### Ошибки
- `400 Bad Request`: "person_id is required" - не указан ID персоны
- `404 Not Found`: "No quotes found for this person" - цитаты для персоны не найдены

### 1.2 Получение всех цитат
`GET /get_all_quote`

#### Параметры
Отсутствуют

#### Пример запроса
```
/api/v1/get_all_quote
```

#### Ответ
```json
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
```

#### Ошибки
- `404 Not Found`: "No quotes found" - цитаты не найдены

### 1.3 Получение информации о персоне
`GET /get_person`

#### Параметры
- `person_id` (обязательный): ID персоны
или
- `full_name` (обязательный): полное имя персоны

#### Примеры запросов
```
/api/v1/get_person?person_id=1      # Детали персоны по ID
/api/v1/get_person?full_name=Иванов # Детали персоны по имени
```

#### Ответ
```json
{
    "person": [
        {
            "id": 1,
            "full_name": "Иванов"
        }
    ],
    "status": 200
}
```

#### Ошибки
- `400 Bad Request`: "full_name or person_id is required" - не указан ни ID, ни имя персоны
- `404 Not Found`: "No found person" - персона не найдена

## 2. Wiki

### 2.1 Получение Wiki
`GET /wiki/{wiki_id}`

#### Параметры
- `wiki_id` (обязательный): ID wiki записи

#### Пример запроса
```
/api/v1/wiki/1
```

#### Ответ
```json
{
    "wiki": {
        "id": 1,
        "person_id": 1,
        "description": "Описание персоны",
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:00:00",
        "created_by": "user",
        "images": [
            {
                "id": 1,
                "filename": "abc123.jpg",
                "original_filename": "photo.jpg",
                "file_size": 1024000,
                "mime_type": "image/jpeg",
                "uploaded_at": "2024-01-01T12:00:00",
                "uploaded_by": "user"
            }
        ]
    },
    "status": 200
}
```

### 2.2 Обновление Wiki
`PUT /wiki/{wiki_id}`

#### Параметры
- `wiki_id` (обязательный): ID wiki записи

#### Тело запроса
```json
{
    "description": "Новое описание",
    "updated_by": "user"
}
```

#### Ответ
```json
{
    "message": "Wiki updated successfully",
    "wiki": {
        "id": 1,
        "description": "Новое описание",
        "updated_at": "2024-01-01T12:00:00",
        "created_by": "user"
    },
    "status": 200
}
```

## 3. Изображения Wiki

### 3.1 Загрузка изображения
`POST /wiki/{wiki_id}/images`

#### Параметры
- `wiki_id` (обязательный): ID wiki записи

#### Тело запроса (multipart/form-data)
- `image` (обязательный): файл изображения
- `uploaded_by` (опциональный): имя загрузившего (по умолчанию "anonymous")

#### Поддерживаемые форматы
- JPG, JPEG, PNG, GIF, WebP
- Максимальный размер: 10MB

#### Меры безопасности
- Валидация расширения файла
- Проверка MIME-типа
- Анализ содержимого файла (магические числа)
- Блокировка вредоносного контента (PHP, JavaScript, HTML)
- Блокировка исполняемых файлов
- Генерация безопасных имен файлов (UUID)
- Изоляция загруженных файлов в отдельной папке

#### Ответ
```json
{
    "message": "Image uploaded successfully",
    "image": {
        "id": 1,
        "filename": "abc123.jpg",
        "original_filename": "photo.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "uploaded_at": "2024-01-01T12:00:00",
        "uploaded_by": "user"
    },
    "status": 200
}
```

### 3.2 Получение изображения
`GET /wiki/images/{image_id}/file`

#### Параметры
- `image_id` (обязательный): ID изображения

#### Пример запроса
```
/api/v1/wiki/images/1/file
```

#### Ответ
- Возвращает файл изображения с соответствующим MIME-типом
- В случае ошибки возвращает JSON с описанием ошибки

### 3.3 Получение списка изображений
`GET /wiki/{wiki_id}/images`

#### Параметры
- `wiki_id` (обязательный): ID wiki записи

#### Пример запроса
```
/api/v1/wiki/1/images
```

#### Ответ
```json
{
    "images": [
        {
            "id": 1,
            "filename": "abc123.jpg",
            "original_filename": "photo.jpg",
            "file_size": 1024000,
            "mime_type": "image/jpeg",
            "uploaded_at": "2024-01-01T12:00:00",
            "uploaded_by": "user"
        }
    ],
    "status": 200
}
```

### 3.4 Удаление изображения
`DELETE /wiki/images/{image_id}`

#### Параметры
- `image_id` (обязательный): ID изображения

#### Пример запроса
```
DELETE /api/v1/wiki/images/1
```

#### Ответ
```json
{
    "message": "Image deleted successfully",
    "status": 200
}
```

## Безопасность

### Меры защиты от эксплойтов

#### 1. Валидация файлов
- **Расширение файла**: Проверяется соответствие разрешенным типам
- **MIME-тип**: Проверяется заголовок Content-Type
- **Содержимое**: Анализируются магические числа файла

#### 2. Блокировка вредоносного контента
- **PHP код**: Блокируются `<?php`, `<?=` теги
- **JavaScript**: Блокируются `<script>` теги и `javascript:` протокол
- **HTML**: Блокируются HTML документы
- **Исполняемые файлы**: Блокируются PE, ELF, shell скрипты

#### 3. Изоляция файлов
- **Безопасные имена**: UUID вместо оригинальных имен
- **Отдельная папка**: Загрузки изолированы от основного кода
- **Ограничения доступа**: Файлы доступны только через API

#### 4. Дополнительные проверки
- **Размер файла**: Ограничение 10MB
- **Тип контента**: Только изображения
- **Логирование**: Все загрузки логируются

### Рекомендации по безопасности

1. **Регулярно обновляйте** зависимости и систему
2. **Мониторьте логи** загрузок на подозрительную активность
3. **Ограничьте доступ** к папке uploads через веб-сервер
4. **Используйте HTTPS** для защиты передаваемых данных
5. **Настройте firewall** для блокировки подозрительных IP

## Коды ошибок

### Общие ошибки
- `400 Bad Request`: Неверные параметры запроса
- `404 Not Found`: Ресурс не найден
- `500 Internal Server Error`: Внутренняя ошибка сервера

**Примечание**: Все ошибки возвращают JSON ответ с полями `error` (описание ошибки) и `status` (код статуса).

### Специфичные ошибки для изображений
- `400 Bad Request`: "File type not allowed" - неподдерживаемый формат файла
- `400 Bad Request`: "File too large" - файл превышает максимальный размер (10MB)
- `400 Bad Request`: "No image file provided" - файл не предоставлен
- `400 Bad Request`: "File is not a valid image. Content validation failed." - файл не прошел валидацию содержимого
- `400 Bad Request`: "File contains potentially dangerous content. Security check failed." - файл содержит опасный контент
- `404 Not Found`: "Image file not found" - файл изображения не найден на диске

### Специфичные ошибки для Wiki
- `400 Bad Request`: "Description is required" - описание не предоставлено
- `404 Not Found`: "Wiki not found" - wiki запись не найдена

```
