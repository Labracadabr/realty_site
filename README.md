# Bali Islands — bali-islands.com

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

По умолчанию локально используется SQLite. Для Postgres укажите `DATABASE_URL` в `.env`.

## Роли

| | Админ (superuser) | Партнёр (группа *Partners*, `is_staff`) |
|---|---|---|
| Объекты, фото, видео, регионы | ✓ | ✓ |
| Заявки, ссылки | ✓ | ✓ |
| Пользователи, настройки сайта, страницы, услуги | ✓ | — |

Новый партнёр: Админка → Пользователи → добавить → отметить «Статус персонала» и группу *Partners*.
Чтобы партнёр получал заявки в Telegram, укажите его `Telegram chat ID`.

## Защита входа в админку

После 5 неверных паролей с одного IP вход с этого IP блокируется на час (django-axes).
Пользователь не блокируется по логину, поэтому посторонний не сможет «запереть» вас, подбирая пароль к вашему аккаунту.
Разблокировать вручную: `python manage.py axes_reset` (всех) или `axes_reset_ip <ip>`.
Журнал попыток: Админка → Axes.

## Объекты

- **Статусы**: черновик · опубликован · только по ссылке · продан.
- **Фото**: поле «Add photos» принимает много файлов сразу; всё конвертируется в WebP. Порядок меняется перетаскиванием, обложка отмечается галочкой.
- **Место на карте**: вставьте в поле «Google Maps link» любую ссылку Google Maps (в том числе короткую `maps.app.goo.gl` из кнопки «Поделиться») или координаты, скопированные правым кликом по карте. Широта и долгота заполнятся при сохранении, проверить точку можно по ссылке «open pin».
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

Сайт работает в двух контейнерах: Django (gunicorn) и собственный Postgres, который наружу не публикуется.
nginx на хосте проксирует запросы на `127.0.0.1:8010` и сам раздаёт `/media/` из `/var/www/bali-islands/media`.

```bash
cp deploy/env.production.example .env      # заполнить
sudo mkdir -p /var/www/bali-islands/media
docker compose up -d --build
docker compose exec web python manage.py seed_demo --content-only
docker compose exec web python manage.py createsuperuser
sudo cp deploy/nginx.conf /etc/nginx/sites-available/bali-islands
sudo ln -s /etc/nginx/sites-available/bali-islands /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d bali-islands.com -d www.bali-islands.com
```

Обновление: `git pull && docker compose up -d --build`.
Бэкап БД: `docker compose exec db pg_dump -U baliislands baliislands > backup.sql`.
