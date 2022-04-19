# Проектная работа 5 спринта

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить во втором спринте модуля "Сервис Async API".

Как и в прошлом спринте, мы оценили задачи в стори поинтах.

Вы можете разбить эти задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**

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
