# Lovinaland

Сайт агентства эксклюзивной земли и островов в Индонезии. Django 5.2 LTS, Postgres/SQLite, EN · RU · TR.

## Запуск на localhost

```bash
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py compile_translations
.venv\Scripts\python manage.py seed_demo
.venv\Scripts\python manage.py runserver
```

- Сайт: http://localhost:8000 (язык по браузеру; `/en/`, `/ru/`, `/tr/`)
- Админка: http://localhost:8000/manage/ — тестовые аккаунты admin/partner в `.env` (`DEV_*`)
- Тесты: `.venv\Scripts\python manage.py test listings`

По умолчанию локально используется SQLite. Для Postgres укажите `DATABASE_URL` в `.env`
(или поднимите `docker compose up -d db`).

## Роли

| | Админ (superuser) | Партнёр (группа *Partners*, `is_staff`) |
|---|---|---|
| Объекты, фото, видео, регионы | ✓ | ✓ |
| Заявки, ссылки | ✓ | ✓ |
| Пользователи, настройки сайта, страницы, услуги | ✓ | — |

Новый партнёр: Админка → Пользователи → добавить → отметить «Статус персонала» и группу *Partners*.
Чтобы партнёр получал заявки в Telegram, укажите его `Telegram chat ID`.

## Объекты

- **Статусы**: черновик · опубликован · только по ссылке · продан.
- **Фото**: поле «Add photos» принимает много файлов сразу; всё конвертируется в WebP. Порядок меняется перетаскиванием, обложка отмечается галочкой.
- **Видео**: ссылка YouTube/Vimeo (можно unlisted) или mp4-файл.
- **Ссылки** `/s/<token>/`: у каждого объекта есть приватная ссылка (кнопка «copy» в списке).
  Дополнительно можно создать ссылки для партнёров и клиентов: метка, язык, срок действия. Видно число просмотров,
  а заявки по такой ссылке записываются на её владельца.
- **Автоперевод**: панель «Auto-translate» над формой. Выберите язык-источник и нажмите *Translate*: заполнятся
  пустые поля других языков. Проверьте текст, отметьте «RU/TR text checked» и сохраните.
  С ключом `DEEPL_API_KEY` (DeepL API Free, 500k символов/мес.) перевод заметно лучше, без ключа используется MyMemory.

## Тексты страниц

*Site content*: настройки сайта (контакты, hero, ключевые цифры), страницы `about`, `how-to-buy`, `privacy`,
`terms`, услуги и отзывы. Разметка в текстах: пустая строка — абзац, `## ` — заголовок, `- ` — список, `**жирный**`.

Строки интерфейса лежат в `locale/<lang>/LC_MESSAGES/django.po`. После правки выполните `manage.py compile_translations`.

## Деплой на VPS (Docker)

1. Скопируйте проект на сервер и создайте `.env`: `DEBUG=False`, длинный `SECRET_KEY`, `ALLOWED_HOSTS=lovinaland.com,www.lovinaland.com`,
   `CSRF_TRUSTED_ORIGINS=https://lovinaland.com,https://www.lovinaland.com`, `SITE_URL=https://lovinaland.com`, `POSTGRES_PASSWORD`,
   `ADMIN_URL` (неочевидный путь), ключи Telegram/DeepL.
2. `docker compose --profile prod up -d --build`
3. `docker compose exec web python manage.py createsuperuser`
4. nginx: `deploy/nginx.conf` + `certbot --nginx`.
