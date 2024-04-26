# Sorex Bot

## Технологии
- **Python** - язык программирования
- **aiohttp\aiogram** - взаимодействие с API и работа телеграмбота
- **PostgreSQL** - система управления базами данных
- **Docker** - для контейнеризации и упрощения развертывания

## Установка и запуск

### Предварительные требования
- Установленные Docker и Docker Compose
- Python версии 3.10 или выше

### Конфигурация

Перед запуском необходимо отредактировать файлы конфигурации для корректной работы приложения:

1. Файл [.env](.env)

    Этот файл содержит переменные окружения, используемые приложением для настройки его параметров.

2. Файл [docker-compose.yml](docker-compose.yml)

   Этот файл используется для определения и запуска многоконтейнерных Docker приложений.

### Шаги для запуска
```bash
    git clone https://github.com/likimiad/sorex-bot.git
    cd sorex-bot
    pip install -r requirements.txt
    make docker-build
```

## Как работает

Прописываем комманду `/start` выбираем валюту, указываем минимальный и максимальный порог для каждой валюты. Для изменения надо снова прописать `/start` и выбрать что интересует.

Каждые 4 минуты после старта бота, бот отправляет сообщения(alerts) если они удовлетворяют условиям. 
