# 🚀 ПОШАГОВАЯ ИНСТРУКЦИЯ ДЛЯ НАСТРОЙКИ ПРОДАКШЕН СЕРВЕРА

## 📋 Краткая Справка
- **Сервер**: 95.217.84.234:8000
- **Проблема**: SmartFilter блокирует обработку из-за отсутствия переменных окружения
- **Решение**: Установить переменные окружения и перезапустить сервис

---

## 🔑 Шаг 1: Подключение к серверу

```bash
# Подключитесь к серверу (замените user на ваше имя пользователя)
ssh user@95.217.84.234

# Перейдите в директорию с AI сервисом
cd /path/to/ai-service  # Замените на правильный путь
```

---

## ⚙️ Шаг 2: Создать файл с переменными окружения

Выполните эту команду **одним блоком**:

```bash
cat > .env << 'EOF'
# Production Environment Variables for AI Service
# Активация всех ключевых функций для санкционного скрининга

# AC Pattern Search - КРИТИЧЕСКИ ВАЖНО!
ENABLE_AHO_CORASICK=true
AHO_CORASICK_CONFIDENCE_BONUS=0.3

# SmartFilter Configuration
ENABLE_SMART_FILTER=true
ALLOW_SMART_FILTER_SKIP=true

# Search Functionality
ENABLE_SEARCH=true
ENABLE_VECTOR_FALLBACK=true

# Other Features
ENABLE_VARIANTS=true
ENABLE_EMBEDDINGS=true
ENABLE_DECISION_ENGINE=true
ENABLE_METRICS=true

# Performance
PRIORITIZE_QUALITY=true
ENABLE_FAISS_INDEX=true

# Feature Flags
ENABLE_AC_TIER0=true
EOF
```

**Проверьте что файл создан:**
```bash
cat .env
```

---

## 🔄 Шаг 3: Перезапустить сервис

### Вариант A: Если используется systemd
```bash
sudo systemctl restart ai-service
sudo systemctl status ai-service
```

### Вариант B: Если запускается вручную
```bash
# Остановить существующие процессы
pkill -f 'python.*main.py'

# Подождать 2 секунды
sleep 2

# Запустить сервис в фоне с логированием
nohup python -m src.ai_service.main > service.log 2>&1 &

# Проверить что запустился
ps aux | grep python
```

### Вариант C: С загрузкой .env файла
```bash
pkill -f 'python.*main.py'
sleep 2

# Загрузить переменные из .env и запустить
source .env && nohup python -m src.ai_service.main > service.log 2>&1 &
```

---

## 🧪 Шаг 4: Проверить что сервис работает

### Базовая проверка работоспособности:
```bash
curl http://localhost:8000/health
```

**Ожидаемый результат:** `{"status": "healthy"}`

### Проверка исправления SmartFilter:
```bash
curl -X POST http://localhost:8000/process \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Ковриков Роман Валерійович",
    "options": {
      "enable_advanced_features": true,
      "enable_search": true
    }
  }'
```

**Ожидаемый результат ПОСЛЕ исправления:**
```json
{
  "decision": {
    "risk_level": "high",
    "decision_details": {
      "smartfilter_should_process": true  ← ДОЛЖНО БЫТЬ true!
    }
  },
  "search_results": {
    "total_hits": 4  ← ДОЛЖНО БЫТЬ > 0!
  }
}
```

**Если видите `"smartfilter_should_process": false` - переменные не загрузились!**

---

## 🔍 Шаг 5: Диагностика проблем

### Если SmartFilter все еще блокирует:

1. **Проверить переменные в процессе:**
```bash
ps aux | grep python
# Найти PID процесса

# Проверить переменные окружения процесса (замените PID)
cat /proc/PID/environ | tr '\0' '\n' | grep ENABLE_AHO_CORASICK
```

2. **Перезапустить с явным экспортом:**
```bash
pkill -f 'python.*main.py'

export ENABLE_AHO_CORASICK=true
export ENABLE_SEARCH=true
export ENABLE_SMART_FILTER=true
export ALLOW_SMART_FILTER_SKIP=true

python -m src.ai_service.main
```

3. **Проверить логи:**
```bash
tail -f service.log
# Ищите строки с "SERVICE_CONFIG" или "SmartFilter"
```

---

## ✅ Шаг 6: Финальная проверка

После успешной настройки тестируем несколько случаев:

```bash
# Тест 1: Санкционное лицо (должен найти)
curl -X POST http://localhost:8000/process \
  -H 'Content-Type: application/json' \
  -d '{"text": "Петро Порошенко", "options": {"enable_search": true}}'

# Тест 2: Обычное имя (должен обработать без блокировки)
curl -X POST http://localhost:8000/process \
  -H 'Content-Type: application/json' \
  -d '{"text": "Иван Иванов", "options": {"enable_search": true}}'
```

**Критерии успеха:**
- ✅ `smartfilter_should_process: true` для всех запросов
- ✅ `search_results.total_hits > 0` для санкционных лиц
- ✅ Время ответа < 1 секунды

---

## 🚨 Важные Замечания

1. **Файл .env должен быть в корневой директории проекта**
2. **Переменные должны быть экспортированы ДО запуска сервиса**
3. **Если используется контейнер Docker, переменные нужно передавать через docker run -e**
4. **При использовании systemd, добавьте переменные в unit файл сервиса**

---

## 🔧 Альтернативный метод через systemd unit

Если используется systemd, добавьте переменные в unit файл:

```bash
sudo nano /etc/systemd/system/ai-service.service
```

Добавьте в секцию `[Service]`:
```ini
[Service]
Environment=ENABLE_AHO_CORASICK=true
Environment=ENABLE_SEARCH=true
Environment=ENABLE_SMART_FILTER=true
Environment=ALLOW_SMART_FILTER_SKIP=true
...
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ai-service
```

---

## 📞 Контакты для поддержки

Если возникают проблемы, проверьте:
1. Логи сервиса: `tail -f service.log`
2. Статус процессов: `ps aux | grep python`
3. Переменные окружения: `printenv | grep ENABLE`

**После выполнения всех шагов система будет работать "как часы"! 🎯**