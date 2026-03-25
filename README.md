# Telegram Shop Platform

Современная экосистема для электронной коммерции, объединяющая панель управления (Django), высокопроизводительного Telegram-бота (Aiogram 3) и отзывчивое веб-приложение (Next.js Mini App).

## 🏗 Архитектура и обоснование решений

Данный проект спроектирован с учетом требований к масштабируемости, отказоустойчивости и минимизации задержек. Ниже приведено обоснование ключевых архитектурных паттернов.

### 1. Взаимодействие WebApp ↔ Django (REST API)
Для взаимодействия фронтенда с бэкендом выбран классический **REST API**.
- **Безопасность**: Использование стандартных механизмов CORS и валидации Telegram `initData` на стороне Django гарантирует защиту данных.
- **State Management**: На фронтенде используется **React Query (TanStack Query)**. Интеграция с REST API позволяет эффективно управлять серверным состоянием, использовать кеширование и механизм "stale-while-revalidate".
- **Разделение ответственности**: Бэкенд остается "безголовым" (headless), что позволяет в будущем легко добавить мобильное приложение или сторонние интеграции без изменения бизнес-логики.

### 2. Взаимодействие Bot ↔ Database (Shared Database Pattern)
В отличие от фронтенда, Telegram-бот взаимодействует с базой данных **напрямую**, минуя REST API. 
*Почему не API?*
- **Минимизация Latency**: Бот обрабатывает тысячи событий в секунду. Лишний HTTP-запрос к API добавил бы накладные расходы на установку соединения и двойную сериализацию/десериализацию JSON.
- **Event Loop Integrity**: Мы используем асинхронные пулы соединений (`psycopg` в асинхронном режиме). Это гарантирует, что `asyncio` loop не будет заблокирован тяжелыми синхронными вызовами, что критично для отзывчивости бота.
- **Shared Schema**: Поскольку бот и админка являются частями одного закрытого контура (back-end), использование общей схемы БД упрощает поддержку консистентности данных без необходимости дублирования DTO в API.

### 3. Управление состоянием и конкурентность
- **Optimistic Locking**: Для управления заказами в админ-панели реализована оптимистичная блокировка. Это предотвращает ситуацию "lost update", когда два менеджера одновременно меняют статус одного и того же заказа. Обновление происходит только в том случае, если текущий статус в БД совпадает с ожидаемым.
- **Redis для FSM и кеширования**: 
    - Состояния диалогов бота (Finite State Machine) хранятся в Redis, что позволяет перезагружать контейнер бота без потери контекста пользователя.
    - Redis также используется как read-through cache для профилей пользователей, предотвращая exhaustion (истощение) пула соединений PostgreSQL при пиковых нагрузках.

---

## 📁 Структура проекта

```text
.
├── admin/                  # Django + DRF (Backend, API, Admin Panel)
│   ├── apps/               # Модульная бизнес-логика
│   │   ├── api/            # Централизованный слой API (Exception handlers, Auth)
│   │   ├── catalog/        # Управление товарами и категориями
│   │   ├── orders/         # Логика заказов и транзакций
│   │   ├── cart/           # Состояние корзин пользователей
│   │   ├── clients/        # База пользователей Telegram
│   │   └── broadcasts/     # Рассылки и уведомления
│   └── config/             # Настройки проекта (Production/Dev, URLS)
├── bot/                    # Aiogram 3.x (Telegram Bot)
│   ├── app/                # Ядро бота
│   │   ├── bot/            # Хендлеры, диалоги (aiogram-dialog), фильтры
│   │   ├── services/       # Бизнес-сервисы (OrderService, ProductService)
│   │   └── infrastructure/ # Репозитории БД, Redis, S3 клиенты
│   ├── alembic/            # Миграции базы данных
│   └── main.py             # Точка входа в event loop
├── webapp/                 # Next.js 15 (Frontend / Mini App)
│   ├── src/                # Архитектура Feature-Sliced Design (FSD)
│   │   ├── app/            # Провайдеры, глобальные стили
│   │   ├── views/          # Страницы каталога и корзины
│   │   ├── widgets/        # Крупные блоки (CatalogGrid, CartList)
│   │   ├── features/       # Интерактивы (AddToCart, PlaceOrder)
│   │   ├── entities/       # Бизнес-сущности (Product, Order, User)
│   │   └── shared/         # Общие UI-компоненты, API-клиент, Hook'и
│   └── public/             # Статика и ассеты
```

---

## ⚙️ Переменные окружения

Создайте файл `.env` в корне проекта, взяв за основу `.env.example`.

| Группа | Переменная | Описание |
|--------|------------|----------|
| **Telegram** | `BOT_TOKEN` | Токен бота от @BotFather |
| **PostgreSQL**| `POSTGRES_DB` | Имя базы данных |
| | `POSTGRES_USER` | Пользователь БД |
| | `POSTGRES_PASSWORD`| Пароль пользователя БД |
| **Redis** | `REDIS_PASSWORD` | Пароль для Redis |
| | `REDIS_USERNAME` | Имя пользователя Redis |
| **MinIO** | `MINIO_ACCESS_KEY` | Ключ доступа S3 |
| | `MINIO_SECRET_KEY` | Секретный ключ S3 |
| | `MINIO_BUCKET_NAME`| Имя бакета для медиа |
| | `MINIO_PUBLIC_URL` | Публичный URL для доступа к медиа-файлам |
| **Django** | `SECRET_KEY` | Секретный ключ Django |
| | `DJANGO_SETTINGS_MODULE`| Путь к настройкам (production/dev) |
| **pgAdmin** | `PGADMIN_PORT` | Порт для pgAdmin |
| | `PGADMIN_DEFAULT_EMAIL` | Email для входа в pgAdmin |
| | `PGADMIN_DEFAULT_PASSWORD`| Пароль для pgAdmin |
| **WebApp** | `NEXT_PUBLIC_API_URL`| URL бэкенда для фронтенда |
| | `WEBAPP_URL` | URL фронтенда (Mini App) |
| **Security** | `CORS_ALLOWED_ORIGINS`| Список разрешенных доменов для CORS |
| | `ALLOWED_HOSTS` | Разрешенные хосты для Django |
| | `CSRF_TRUSTED_ORIGINS`| Доверенные источники для CSRF защиты |

---

## 🚀 Как запустить

### 1. Подготовка
Убедитесь, что у вас установлены **Docker** и **Docker Compose**.

### 2. Запуск инфраструктуры и сервисов
```bash
docker-compose up -d --build
```

### 3. Настройка WebApp (HTTPS Туннель)
Для того чтобы WebApp открылся внутри Telegram, необходим HTTPS-адрес.
1. Запустите любой инструмент туннелирования на порт **3000**:
   - `zrok share public localhost:3000`
   - или `ngrok http 3000`
2. Скопируйте полученную `https://...` ссылку.
3. Вставьте её в переменную `WEBAPP_URL` в вашем `.env`.
4. Перезапустите бота: `docker-compose restart bot`.

### 4. Доступы
После запуска будут доступны:
- **Admin Panel**: [http://localhost:8000/admin](http://localhost:8000/admin)
- **WebApp**: [http://localhost:3000](http://localhost:3000)
- **pgAdmin**: [http://localhost:5050](http://localhost:5050)
- **MinIO**: [http://localhost:9001](http://localhost:9001)

### 3. Создание суперпользователя
```bash
docker-compose exec admin python manage.py createsuperuser
```

---

## 🛠 Стек технологий
- **Backend**: Python 3.12, Django 5, DRF, PostgreSQL, Redis, MinIO (S3).
- **Bot**: Aiogram 3.x, Aiogram-dialog, Psycopg 3.
- **Frontend**: Next.js 15, TypeScript, TanStack Query, Tailwind CSS.
- **DevOps**: Docker, Gunicorn, Nginx (опционально).
