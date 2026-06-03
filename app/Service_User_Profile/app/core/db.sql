-- 1. Создание таблицы профилей
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY,
    first_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NULL,
    city VARCHAR(100) NULL,

    -- Ограничения на диапазоны чисел (Constraint) для защиты от некорректных значений
    age INTEGER CHECK (age >= 0 AND age <= 120) NULL,
    children_count INTEGER CHECK (children_count >= 0 AND children_count <= 50) NULL,

    -- Поля аудита времени с поддержкой часовых поясов (timezone)
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Создание функции для автоматического обновления поля updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Создание триггера, который будет вызываться автоматически при операции UPDATE
DROP TRIGGER IF EXISTS set_user_profiles_updated_at ON user_profiles;

CREATE TRIGGER set_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Создание индексов для ускорения поиска по часто запрашиваемым полям
CREATE INDEX IF NOT EXISTS idx_user_profiles_city ON user_profiles(city);