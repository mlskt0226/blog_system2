-- Скрипт создания всех таблиц
\i 01_users.sql
\i 02_categories.sql
\i 03_posts.sql
\i 04_comments.sql
\i 05_favorites.sql
\i 06_subscriptions.sql

-- Комментарий для проверки
SELECT 'Все таблицы успешно созданы' AS message;