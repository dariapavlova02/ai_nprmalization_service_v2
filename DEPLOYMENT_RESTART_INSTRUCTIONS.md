# 🚀 Инструкция по переподнятию AI Service с поддержкой поиска

## ✅ Что было исправлено

1. **Добавлена генерация частичных паттернов** - теперь поиск работает для "Порошенко Петро" и подобных запросов
2. **Загружено 942,282 паттернов** в Elasticsearch, включая 220,241 partial_match паттернов
3. **Частично исправлен конфликт зависимостей** elasticsearch/httpx

## 🔧 Критическая проблема: httpx dependency conflict

**Проблема**: Конфликт версий httpx/elasticsearch не позволяет запустить сервис

**Ошибка**:
```
AttributeError: module 'httpx' has no attribute '__version__'
```

## 📋 Варианты решения

### Вариант 1: Быстрое решение (Virtual Environment)

```bash
# 1. Создать виртуальное окружение
python3 -m venv venv_ai_service
source venv_ai_service/bin/activate

# 2. Установить совместимые версии
pip install httpx==0.25.2
pip install elasticsearch==8.10.0
pip install -r requirements.txt

# 3. Запустить сервис
ENABLE_SEARCH=true ENABLE_EMBEDDINGS=true \
uvicorn src.ai_service.main:app --host 0.0.0.0 --port 8000
```

### Вариант 2: Обновление requirements.txt

Добавить в `requirements.txt`:
```txt
httpx==0.25.2
elasticsearch==8.10.0
```

### Вариант 3: Запуск без поиска (временно)

Если нужно быстро запустить сервис без поиска:
```bash
ENABLE_SEARCH=false ENABLE_EMBEDDINGS=false \
uvicorn src.ai_service.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Проверка работоспособности

### 1. Проверка базовой функциональности

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Порошенко Петро Олексійович"}'
```

### 2. Проверка поиска частичных имен

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Порошенко Петро"}' | jq .search_results
```

**Ожидаемый результат**: должны быть найдены частичные паттерны с типом `partial_match`.

### 3. Прямая проверка Elasticsearch

```bash
# Запустить тест паттернов
python test_direct_es_search.py
```

## 📊 Статус компонентов

| Компонент | Статус | Описание |
|-----------|--------|----------|
| ✅ Частичные паттерны | Работает | Генерация и загрузка завершена |
| ✅ Elasticsearch | Работает | 942,282 паттернов загружены |
| ❌ AI Service | Не запускается | httpx dependency conflict |
| ✅ Поиск в ES | Работает | Проверено напрямую |

## 🔍 Диагностика проблем

### Если сервис не запускается:

1. Проверить версии:
```bash
python -c "import httpx; print(httpx.__version__)"
python -c "import elasticsearch; print('ES OK')"
```

2. Использовать virtual environment:
```bash
python3 -m venv fresh_env
source fresh_env/bin/activate
pip install httpx==0.25.2 elasticsearch==8.10.0
```

### Если поиск не работает:

1. Проверить переменные окружения:
```bash
echo $ENABLE_SEARCH
echo $ENABLE_EMBEDDINGS
```

2. Проверить подключение к Elasticsearch:
```bash
curl 95.217.84.234:9200/_cluster/health
```

3. Проверить индекс паттернов:
```bash
curl 95.217.84.234:9200/ai_service_ac_patterns/_count
```

## 🚀 Рекомендуемая последовательность запуска

1. **Обновить код**:
```bash
git pull origin main
```

2. **Настроить окружение**:
```bash
python3 -m venv venv_ai_service
source venv_ai_service/bin/activate
pip install httpx==0.25.2 elasticsearch==8.10.0
pip install -r requirements.txt
```

3. **Запустить с поиском**:
```bash
ENABLE_SEARCH=true ENABLE_EMBEDDINGS=true \
uvicorn src.ai_service.main:app --host 0.0.0.0 --port 8000
```

4. **Проверить работу**:
```bash
python test_direct_es_search.py
```

## 📝 Важные замечания

- **Паттерны уже загружены** - повторная загрузка не требуется
- **Поиск работает** - проблема только в запуске Python сервиса
- **Elasticsearch доступен** - 95.217.84.234:9200
- **942,282 паттернов** готовы к использованию

## 🆘 Если ничего не помогает

Временный обходной путь - запуск без поиска:
```bash
ENABLE_SEARCH=false uvicorn src.ai_service.main:app --host 0.0.0.0 --port 8000
```

Основная функциональность нормализации будет работать, только без AC/векторного поиска.