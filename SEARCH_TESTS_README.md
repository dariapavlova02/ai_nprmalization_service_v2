# Комплексные тесты поисковой интеграции

Создан полный набор тестов для поисковой интеграции с использованием pytest, Docker Compose и изоляцией тестов.

## 🎯 Цели тестирования

- **Unit**: маппинг трансформаций ES hit → Candidate, нормализация порогов, слияние скорингов
- **Integration**: создание временного индекса, индексация 5-10 сущностей (ru/uk/en), проверка всех типов поиска
- **Performance**: 1k запросов, p95 < 80мс end-to-end

## 📁 Структура тестов

```
tests/
├── conftest.py                           # Pytest конфигурация и фикстуры
├── requirements_test.txt                 # Зависимости для тестов
├── unit/                                 # Unit тесты
│   ├── test_search_contracts.py         # Тесты контрактов поиска
│   ├── test_search_integration.py       # Тесты интеграции поиска
│   └── test_decision_engine_with_search.py # Тесты Decision Engine с поиском
├── integration/                          # Integration тесты
│   └── test_elasticsearch_search.py     # Тесты Elasticsearch поиска
├── performance/                          # Performance тесты
│   └── test_search_performance.py       # Тесты производительности поиска
└── README.md                            # Подробная документация
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Установить зависимости для тестов
pip install -r tests/requirements_test.txt

# Или через make
make -f Makefile.test install-test-deps
```

### 2. Unit тесты (без внешних зависимостей)

```bash
# Все unit тесты
pytest tests/unit/ -m "unit" -v

# Или через make
make -f Makefile.test test-unit
```

### 3. Integration тесты (требует Docker)

```bash
# Запустить Elasticsearch
docker-compose -f docker-compose.test.yml up -d

# Дождаться готовности
curl -f http://localhost:9200/_cluster/health

# Запустить integration тесты
pytest tests/integration/ -m "integration" -v

# Или через make
make -f Makefile.test test-integration
```

### 4. Performance тесты

```bash
# Запустить performance тесты
pytest tests/performance/ -m "performance" -v

# Или через make
make -f Makefile.test test-performance
```

### 5. Все тесты автоматически

```bash
# Установить, запустить тесты и очистить
make -f Makefile.test test-with-docker
```

## 🧪 Типы тестов

### Unit тесты (`@pytest.mark.unit`)

**Файлы:**
- `test_search_contracts.py` - Контракты данных поиска
- `test_search_integration.py` - Функции интеграции поиска
- `test_decision_engine_with_search.py` - Decision Engine с поиском

**Покрытие:**
- ✅ Маппинг трансформаций ES hit → Candidate
- ✅ Нормализация порогов
- ✅ Слияние скорингов
- ✅ Контракты данных (SearchOpts, SearchMode, ACScore, VectorHit, Candidate, SearchInfo)
- ✅ Функции интеграции (extract_search_candidates, create_search_info)
- ✅ Decision Engine с весами поиска

### Integration тесты (`@pytest.mark.integration`)

**Файлы:**
- `test_elasticsearch_search.py` - Elasticsearch поиск

**Покрытие:**
- ✅ **Exact поиск**: находит только при точном `normalized_name`
- ✅ **Phrase поиск**: ловит «Иван Иванов»
- ✅ **N-gram поиск**: дает слабый сигнал
- ✅ **kNN поиск**: возвращает релевант при отсутствии AC
- ✅ **Fusion**: консенсус поднимает в топ
- ✅ Фильтрация по стране и мета-данным
- ✅ Множественные кандидаты
- ✅ Обработка ошибок

### Performance тесты (`@pytest.mark.performance`)

**Файлы:**
- `test_search_performance.py` - Производительность поиска

**Критерии:**
- ✅ **1k запросов**: p95 < 80мс end-to-end
- ✅ **Успешность**: > 95%
- ✅ **Память**: < 200MB увеличение
- ✅ **Concurrent**: 1, 5, 10, 20 параллельных запросов
- ✅ **Error handling**: обработка ошибок

## 🔧 Конфигурация

### Переменные окружения

Тесты автоматически устанавливают:

```bash
# Поиск
ENABLE_HYBRID_SEARCH=true
ES_URL=http://localhost:9200
ES_AUTH=
ES_VERIFY_SSL=false

# Веса поиска для Decision Engine
AI_DECISION__W_SEARCH_EXACT=0.3
AI_DECISION__W_SEARCH_PHRASE=0.25
AI_DECISION__W_SEARCH_NGRAM=0.2
AI_DECISION__W_SEARCH_VECTOR=0.15

# Пороги поиска
AI_DECISION__THR_SEARCH_EXACT=0.8
AI_DECISION__THR_SEARCH_PHRASE=0.7
AI_DECISION__THR_SEARCH_NGRAM=0.6
AI_DECISION__THR_SEARCH_VECTOR=0.5

# Бонусы поиска
AI_DECISION__BONUS_MULTIPLE_MATCHES=0.1
AI_DECISION__BONUS_HIGH_CONFIDENCE=0.05
```

### Pytest маркеры

- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.integration` - Integration тесты (требуют Elasticsearch)
- `@pytest.mark.performance` - Performance тесты
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.docker` - Тесты, требующие Docker

## 🎭 Фикстуры

### Основные фикстуры

- `elasticsearch_container` - Docker контейнер Elasticsearch
- `elasticsearch_client` - HTTP клиент для Elasticsearch
- `test_indices` - Тестовые индексы с данными
- `mock_hybrid_search_service` - Мок HybridSearchService
- `mock_signals_result` - Мок SignalsResult
- `mock_normalization_result` - Мок NormalizationResult
- `sample_query_vector` - Образец вектора запроса

### Тестовые данные

**Персоны:**
- `иван петров` (RU) - точное совпадение
- `мария сидорова` (UA) - фраза
- `john smith` (US) - n-gram

**Организации:**
- `ооо приватбанк` (UA) - точное совпадение
- `apple inc` (US) - фраза

## 📊 Критерии успеха

### Unit тесты
- ✅ Все контракты данных работают корректно
- ✅ Трансформации ES hit → Candidate
- ✅ Нормализация порогов
- ✅ Слияние скорингов
- ✅ Decision Engine с поиском

### Integration тесты
- ✅ Exact поиск находит только точные совпадения
- ✅ Phrase поиск ловит фразы
- ✅ N-gram поиск дает слабые сигналы
- ✅ kNN поиск возвращает релевантные результаты
- ✅ Fusion поднимает консенсус в топ

### Performance тесты
- ✅ 1k запросов, p95 < 80мс end-to-end
- ✅ Успешность > 95%
- ✅ Память < 200MB увеличение
- ✅ Concurrent запросы работают стабильно

## 🐛 Отладка

### Проблемы с Docker

```bash
# Проверить статус контейнеров
docker ps

# Посмотреть логи Elasticsearch
docker logs ai-service-test-es

# Очистить все контейнеры
make -f Makefile.test clean-test-env
```

### Проблемы с тестами

```bash
# Запустить с подробным выводом
pytest tests/unit/test_search_contracts.py -v -s

# Запустить конкретный тест
pytest tests/unit/test_search_contracts.py::TestSearchOpts::test_default_values -v

# Запустить с отладкой
pytest tests/unit/test_search_contracts.py --pdb
```

### Проблемы с импортами

```bash
# Проверить PYTHONPATH
echo $PYTHONPATH

# Запустить из корня проекта
cd /path/to/ai-service
pytest tests/unit/ -v
```

## 📈 Расширение тестов

### Добавление новых unit тестов

1. Создайте файл в `tests/unit/`
2. Используйте маркер `@pytest.mark.unit`
3. Добавьте фикстуры из `conftest.py`

### Добавление новых integration тестов

1. Создайте файл в `tests/integration/`
2. Используйте маркер `@pytest.mark.integration`
3. Используйте фикстуры `elasticsearch_client` и `test_indices`

### Добавление новых performance тестов

1. Создайте файл в `tests/performance/`
2. Используйте маркер `@pytest.mark.performance`
3. Измеряйте производительность и проверяйте пороги

## 🔄 CI/CD

Тесты можно интегрировать в CI/CD пайплайн:

```yaml
# GitHub Actions example
- name: Run unit tests
  run: make -f Makefile.test test-unit

- name: Run integration tests
  run: make -f Makefile.test test-with-docker
```

## 📋 Чек-лист готовности

- [x] Unit тесты для контрактов данных
- [x] Unit тесты для функций интеграции
- [x] Unit тесты для Decision Engine с поиском
- [x] Integration тесты для Elasticsearch
- [x] Performance тесты с 1k запросов
- [x] Docker Compose для тестов
- [x] Makefile для удобного запуска
- [x] Подробная документация
- [x] Изоляция тестов
- [x] Автоматическая очистка
- [x] Стабильные пороги
- [x] Обработка ошибок

## 🎉 Результат

Создан комплексный набор тестов, который:

1. **Покрывает все аспекты** поисковой интеграции
2. **Изолирован** и не влияет на другие тесты
3. **Автоматически** настраивает и очищает окружение
4. **Проверяет производительность** с четкими критериями
5. **Легко расширяется** для новых тестов
6. **Готов к CI/CD** интеграции

Тесты готовы к использованию и обеспечивают высокое качество поисковой интеграции! 🚀
