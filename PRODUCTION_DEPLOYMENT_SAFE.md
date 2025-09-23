# 🚀 Безопасный деплой поиска в продакшен

## ⚠️ ВАЖНО: Сохранение данных Elasticsearch

Этот деплой добавляет поиск **БЕЗ потери существующих данных** в Elasticsearch. Все ваши индексы и данные будут сохранены.

## 🔄 Что происходит при деплое

### ✅ Безопасные операции:
- ✅ Обновление кода AI Service
- ✅ Добавление нового поля `search_results` в API
- ✅ Создание нового индекса `watchlist` (если не существует)
- ✅ Сохранение всех существующих индексов и данных

### ❌ НЕ затрагивается:
- ❌ Существующие индексы Elasticsearch НЕ изменяются
- ❌ Данные НЕ удаляются
- ❌ Конфигурация ES НЕ меняется
- ❌ Перезапуск Elasticsearch НЕ требуется

## 📋 Пошаговая инструкция

### Шаг 1: Подключение к серверу

```bash
ssh ваш-продакшн-сервер
cd /path/to/ai-service  # Путь к вашему проекту
```

### Шаг 2: Создание бэкапов (ОБЯЗАТЕЛЬНО!)

```bash
# 1. Бэкап текущей конфигурации
cp env.production env.production.backup.$(date +%Y%m%d_%H%M%S)

# 2. Бэкап состояния докера
docker-compose ps > docker-state.backup.$(date +%Y%m%d_%H%M%S)

# 3. Проверка здоровья Elasticsearch ПЕРЕД деплоем
curl -s http://localhost:9200/_cluster/health | jq .
curl -s http://localhost:9200/_cat/indices?v

# 4. Сохранить вывод для сравнения ПОСЛЕ деплоя
curl -s http://localhost:9200/_cat/indices?v > elasticsearch-indices.before.txt
```

### Шаг 3: Получение обновленного кода

```bash
# Проверить текущую ветку
git branch

# Получить последние изменения
git pull origin main

# Проверить что получили commit 48c08d2
git log --oneline -5
```

### Шаг 4: Подготовка конфигурации

```bash
# Проверить что файл конфигурации существует
ls -la env.production.search

# ВАЖНО: Сравнить конфигурации перед применением
echo "=== ТЕКУЩАЯ КОНФИГУРАЦИЯ ==="
cat env.production | grep -E "(ENABLE_|ES_)" || echo "Нет поисковых настроек"

echo "=== НОВАЯ КОНФИГУРАЦИЯ ==="
cat env.production.search | grep -E "(ENABLE_|ES_)"

# Применить новую конфигурацию
cp env.production.search env.production

echo "✅ Конфигурация обновлена"
```

### Шаг 5: Безопасный перезапуск сервиса

```bash
# Проверить текущие контейнеры
docker ps | grep ai

# Остановить ТОЛЬКО ai-service (Elasticsearch НЕ трогаем!)
docker-compose -f docker-compose.prod.yml stop ai-service

# НЕ делать docker-compose down - это может затронуть ES!

# Пересобрать образ с новым кодом
docker-compose -f docker-compose.prod.yml build --no-cache ai-service

# Запустить сервис с новой конфигурацией
docker-compose -f docker-compose.prod.yml up -d ai-service

echo "✅ Сервис перезапущен"
```

### Шаг 6: Проверка здоровья системы

```bash
echo "🔍 Проверка здоровья системы..."

# 1. Проверить что AI Service запустился
echo "=== AI SERVICE STATUS ==="
docker ps | grep ai-service
docker logs ai-service-prod --tail 20

# 2. Проверить что Elasticsearch НЕ пострадал
echo "=== ELASTICSEARCH STATUS ==="
curl -s http://localhost:9200/_cluster/health | jq .

# 3. Сравнить индексы ДО и ПОСЛЕ
echo "=== ELASTICSEARCH INDICES ==="
curl -s http://localhost:9200/_cat/indices?v > elasticsearch-indices.after.txt
diff elasticsearch-indices.before.txt elasticsearch-indices.after.txt || echo "Индексы изменились (это нормально)"

# 4. Проверить API здоровье
echo "=== AI SERVICE HEALTH ==="
curl -s http://localhost:8000/health | jq .
```

### Шаг 7: Тестирование поиска

```bash
echo "🧪 Тестирование поисковой функциональности..."

# Тест 1: Проверить что search_results появились в ответе
echo "=== ТЕСТ 1: Поле search_results ==="
curl -s -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Порошенко Петр", "generate_variants": false}' \
  | jq 'keys[]' | grep search_results

if [ $? -eq 0 ]; then
    echo "✅ Поле search_results найдено"
else
    echo "❌ Поле search_results НЕ найдено!"
fi

# Тест 2: Проверить структуру search_results
echo "=== ТЕСТ 2: Структура search_results ==="
curl -s -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Иванов Иван", "generate_variants": false}' \
  | jq '.search_results'

# Тест 3: Проверить что нормализация всё ещё работает правильно
echo "=== ТЕСТ 3: Нормализация ==="
curl -s -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Порошенка Петенька", "generate_variants": false}' \
  | jq -r '.normalized_text'
```

### Шаг 8: Настройка Elasticsearch (опционально)

```bash
# Запустить настройку ES для полной функциональности поиска
echo "🔧 Настройка Elasticsearch..."

cd scripts
python3 setup_elasticsearch.py
cd ..

echo "✅ Elasticsearch настроен"
```

## 🔍 Ожидаемые результаты

### ✅ Успешный деплой:

1. **AI Service работает**:
   ```bash
   curl http://localhost:8000/health
   # Status: 200, "status": "healthy"
   ```

2. **search_results в ответе**:
   ```json
   {
     "normalized_text": "Порошенко Петр",
     "search_results": {
       "query": "Порошенко Петр",
       "results": [],
       "total_hits": 0,
       "search_type": "similarity_mock"
     }
   }
   ```

3. **Elasticsearch не пострадал**:
   ```bash
   curl http://localhost:9200/_cluster/health
   # "status": "green" или "yellow"
   ```

4. **Все данные сохранены**:
   ```bash
   curl http://localhost:9200/_cat/indices
   # Все ваши индексы на месте + возможно новый "watchlist"
   ```

## 🚨 План отката (если что-то пошло не так)

### Быстрый откат конфигурации:
```bash
# Вернуть старую конфигурацию
cp env.production.backup.YYYYMMDD_HHMMSS env.production

# Перезапустить сервис
docker-compose -f docker-compose.prod.yml restart ai-service

echo "✅ Откат конфигурации выполнен"
```

### Полный откат кода:
```bash
# Вернуться к предыдущему коммиту
git reset --hard d01bbf8  # предыдущий коммит

# Пересобрать и перезапустить
docker-compose -f docker-compose.prod.yml stop ai-service
docker-compose -f docker-compose.prod.yml build --no-cache ai-service
docker-compose -f docker-compose.prod.yml up -d ai-service

echo "✅ Полный откат выполнен"
```

## 📊 Мониторинг после деплоя

### В течение первого часа проверять:

```bash
# Каждые 5 минут проверять логи
watch -n 300 'docker logs ai-service-prod --tail 10'

# Проверять производительность
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/process \
  -d '{"text":"test"}'

# Мониторить Elasticsearch
watch -n 300 'curl -s http://localhost:9200/_cluster/health | jq .'
```

## ✅ Чек-лист успешного деплоя

- [ ] Бэкапы созданы
- [ ] AI Service запущен и отвечает на `/health`
- [ ] `search_results` поле появилось в API ответах
- [ ] Elasticsearch здоров (статус green/yellow)
- [ ] Все существующие индексы сохранены
- [ ] Нормализация работает корректно
- [ ] Производительность в норме (<100ms на запрос)

## 🎉 После успешного деплоя

Поиск будет работать в режиме mock service с пустыми результатами до тех пор, пока не будут загружены реальные данные в watchlist индекс.

**Деплой безопасен и не влияет на существующие данные Elasticsearch!** 🔒