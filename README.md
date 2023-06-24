# Запуск тестов
Переименовываем все env.sample в .env:
```
Async_API_sprint_2/fastapi/.testenv
Async_API_sprint_2/tests/.env
```

## Запуск контейнера
```
cd Async_API_sprint_2/tests/functional
docker-compose -f docker-compose.yml up --build
```
## Адрес репозитория
https://github.com/iliazaraysky/Async_API_sprint_2/
