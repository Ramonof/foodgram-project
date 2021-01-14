![yamdb_workflow Action Status](https://github.com/Ramonof/foodgram-project/workflows/foodgram%20workflow/badge.svg)
# Сайт «Продуктовый помощник»
Онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
# Запуск
Запустить docker-compose:

docker-compose up

Выполнить миграции:

docker-compose exec web python manage.py migrate

Чтобы загрузить список ингредиентов в БД:

docker-compose exec web python manage.py loaddata ingredients.json
