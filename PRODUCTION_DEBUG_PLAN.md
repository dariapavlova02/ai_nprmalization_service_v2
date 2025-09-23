# 🚨 КРИТИЧНЫЕ ПРОБЛЕМЫ ПРОДАКШН СЕРВЕРА

## Обнаруженные проблемы

### 1. ❌ Неправильная нормализация украинских имен

**Кейс 1**: "Порошенка Петенька"
- 🔴 **Продакшн**: `"Порошенка | Петро"`
- ✅ **Ожидаем**: `"Порошенко Петро"`
- 🐛 **Проблема**: Морфология выдает женскую форму "Порошенка" вместо мужской "Порошенко"

**Кейс 2**: "Павлової Дарʼї Юріївни"
- 🔴 **Продакшн**: `"Павлов | Юріївна"` (потеряли имя!)
- ✅ **Ожидаем**: `"Павлова Дарʼя Юріївна"`
- 🐛 **Проблемы**:
  - Павлової → Павлов (мужская форма)
  - Дарʼї отфильтровалось как unknown

### 2. ❌ Поиск не работает
- SmartFilter возвращает `"risk_level": "skip"`
- Elasticsearch search не происходит

## Диагностика

### ✅ Локальные тесты работают правильно:
```bash
Павлової → Павлова ✅ (женская форма сохраняется)
Порошенка → Порошенко ✅ (правильная морфология)
Дарʼї → Дарʼї ✅ (сохраняется)
```

### 🔍 Root Cause Analysis

**Гипотеза 1: Неправильные feature flags на проде**
```json
// Возможные проблемные флаги:
"preserve_feminine_surnames": false  // Должно быть true
"enable_enhanced_gender_rules": false  // Должно быть true
"preserve_feminine_suffix_uk": false  // Должно быть true
```

**Гипотеза 2: Language detection**
- Продакшн trace показывает `"language": "uk"` ✅
- Но возможны проблемы с FSM role classification для украинского

**Гипотеза 3: Кеш/версия кода**
- Продакшн может использовать старую версию кода
- Или кешированные результаты с неправильными настройками

## План исправлений

### 🚨 НЕМЕДЛЕННО (Critical):

1. **Проверить feature flags на проде**:
```bash
# Эти флаги ОБЯЗАТЕЛЬНО должны быть true:
PRESERVE_FEMININE_SUFFIX_UK=true
ENABLE_ENHANCED_GENDER_RULES=true
PRESERVE_FEMININE_SURNAMES=true
ENABLE_FSM_TUNED_ROLES=true
```

2. **Проверить Smart Filter конфигурацию**:
```bash
# Поиск должен работать:
ENABLE_SMART_FILTER=true
ALLOW_SMART_FILTER_SKIP=false  # Не пропускать обработку
ENABLE_AHO_CORASICK=true
ENABLE_VECTOR_FALLBACK=true
```

3. **Перезапустить сервис** с очисткой кеша

### 🔧 Дополнительно:

4. **Проверить Elasticsearch**:
   - Индекс ac-patterns загружен?
   - Elasticsearch доступен?

5. **Логирование на проде**:
   - Включить debug_tracing=true
   - Проверить полные trace для понимания где ломается

6. **Версия кода**:
   - Убедиться что продакшн использует последний код
   - Проверить что исправления из отладки применены

## Команды для диагностики

```bash
# 1. Проверить статус Elasticsearch
curl "http://localhost:9200/_cluster/health"

# 2. Проверить количество паттернов
curl "http://localhost:9200/ac-patterns/_count"

# 3. Проверить переменные окружения
env | grep -E "(PRESERVE|GENDER|FSM|SMART)"

# 4. Перезапуск с правильными флагами
docker-compose restart ai-service
```

## Expected Results после исправления:

```json
// "Порошенка Петенька"
{
  "normalized_text": "Порошенко Петро",
  "decision": {"risk_level": "medium"}  // не skip!
}

// "Павлової Дарʼї Юріївни"
{
  "normalized_text": "Павлова Дарʼя Юріївна",
  "decision": {"risk_level": "medium"}  // не skip!
}
```