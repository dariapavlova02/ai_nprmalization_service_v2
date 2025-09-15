# 🔧 Техническая Реализация AI Service

## 📁 Структура Проекта

```
src/ai_service/
├── contracts/              # Контракты и схемы данных
│   ├── base_contracts.py   # Основные контракты
│   └── decision_contracts.py # Контракты для принятия решений
├── core/                   # Ядро системы
│   ├── unified_orchestrator.py # Главный оркестратор
│   ├── decision_engine.py  # Движок принятия решений
│   └── orchestrator_factory.py # Фабрика оркестраторов
├── layers/                 # 9-слойная архитектура
│   ├── validation/         # Слой 1: Валидация
│   ├── smart_filter/       # Слой 2: Умный фильтр
│   ├── language/           # Слой 3: Детекция языка
│   ├── unicode/            # Слой 4: Unicode нормализация
│   ├── normalization/      # Слой 5: Нормализация имен
│   ├── signals/            # Слой 6: Извлечение сигналов
│   ├── variants/           # Слой 7: Генерация вариантов
│   ├── embeddings/         # Слой 8: Эмбеддинги
│   └── decision/           # Слой 9: Принятие решений
├── config/                 # Конфигурация
│   └── settings.py         # Настройки системы
├── data/                   # Данные и словари
│   ├── dicts/              # Словари для обработки
│   └── patterns/           # Паттерны для поиска
└── utils/                  # Утилиты
    ├── logging_config.py   # Настройка логирования
    └── response_formatter.py # Форматирование ответов
```

## 🏗️ Ключевые Компоненты

### 1. UnifiedOrchestrator (Главный Оркестратор)

**Назначение**: Координирует работу всех 9 слоев обработки

**Ключевые методы**:
```python
async def process(
    text: str,
    generate_variants: bool = True,
    generate_embeddings: bool = False,
    remove_stop_words: bool = True,
    preserve_names: bool = True,
    enable_advanced_features: bool = True
) -> UnifiedProcessingResult
```

**Особенности**:
- Асинхронная обработка
- Кэширование результатов
- Обработка ошибок
- Метрики производительности

### 2. SmartFilterService (Умный Фильтр)

**Назначение**: Предварительная оценка релевантности текста

**Детекторы**:
- `NameDetector` - детекция имен
- `CompanyDetector` - детекция организаций  
- `DocumentDetector` - детекция документов
- `TerrorismDetector` - детекция террористических терминов

**Алгоритм работы**:
1. Анализ капитализации
2. Поиск юридических форм
3. Детекция дат и ID
4. Скоринг уверенности
5. Принятие решения о дальнейшей обработке

### 3. NormalizationService (Нормализация)

**Назначение**: Морфологический анализ и нормализация имен

**Технологии**:
- **PyMorphy3** - морфологический анализ
- **SpaCy** - NLP обработка
- **Custom rules** - специфичные правила

**Процесс**:
1. Токенизация текста
2. Классификация ролей токенов
3. Морфологический анализ
4. Нормализация в именительный падеж
5. Трассировка каждого токена

### 4. SignalsService (Извлечение Сигналов)

**Назначение**: Структурирование извлеченных данных

**Экстракторы**:
- `PersonExtractor` - извлечение персон
- `OrganizationExtractor` - извлечение организаций
- `IdentifierExtractor` - извлечение ID
- `BirthdateExtractor` - извлечение дат рождения

**Результат**:
```python
@dataclass
class SignalsResult:
    persons: List[SignalsPerson]
    organizations: List[SignalsOrganization]
    extras: SignalsExtras
    confidence: float
```

### 5. DecisionEngine (Движок Решений)

**Назначение**: Взвешенная оценка риска

**Алгоритм скоринга**:
```python
score = (
    w_smartfilter * smartfilter_confidence +
    w_person * person_confidence +
    w_org * org_confidence +
    w_similarity * similarity_score +
    bonus_date_match * date_match +
    bonus_id_match * id_match
)
```

**Уровни риска**:
- **SKIP** (0.0-0.65): Низкий риск
- **REVIEW** (0.65-0.85): Средний риск  
- **AUTO_HIT** (0.85-1.0): Высокий риск

## 🔄 Поток Обработки Данных

### 1. Входные Данные
```python
{
    "text": "Оплата ТОВ 'ПРИВАТБАНК' Ивану Петрову",
    "generate_variants": true,
    "generate_embeddings": false
}
```

### 2. Валидация (Слой 1)
- Проверка длины текста
- Санитизация входных данных
- Валидация формата

### 3. Smart Filter (Слой 2)
```python
SmartFilterResult(
    should_process=True,
    confidence=0.75,
    classification="high_risk_organization",
    detected_signals=["company", "person", "payment"]
)
```

### 4. Детекция Языка (Слой 3)
```python
{
    "language": "ru",
    "confidence": 0.95,
    "mixed_script": False
}
```

### 5. Unicode Нормализация (Слой 4)
```python
"Оплата ТОВ 'ПРИВАТБАНК' Ивану Петрову" 
→ "Оплата ТОВ 'ПРИВАТБАНК' Ивану Петрову"
```

### 6. Нормализация Имен (Слой 5)
```python
NormalizationResult(
    normalized="оплата тов приватбанк иван петров",
    tokens=["оплата", "тов", "приватбанк", "иван", "петров"],
    trace=[...]  # Детальная трассировка
)
```

### 7. Извлечение Сигналов (Слой 6)
```python
SignalsResult(
    persons=[
        SignalsPerson(
            core=["иван", "петров"],
            full_name="Иван Петров",
            confidence=0.85
        )
    ],
    organizations=[
        SignalsOrganization(
            core="приватбанк",
            legal_form="ТОВ",
            full_name="ТОВ 'ПРИВАТБАНК'",
            confidence=0.90
        )
    ]
)
```

### 8. Генерация Вариантов (Слой 7, опционально)
```python
[
    "оплата тов приватбанк иван петров",
    "оплата тов приватбанк иван петров",
    "оплата тов приватбанк иван петров"
]
```

### 9. Эмбеддинги (Слой 8, опционально)
```python
[0.123, -0.456, 0.789, ...]  # 384-мерный вектор
```

### 10. Принятие Решения (Слой 9)
```python
DecisionOutput(
    risk=RiskLevel.AUTO_HIT,
    score=0.87,
    reasons=["high_org_confidence", "valid_id_present"],
    details={...}
)
```

## ⚡ Оптимизации Производительности

### 1. Кэширование
- **LRU Cache** с TTL
- **Ключи кэша**: MD5 хеш нормализованных параметров
- **Размер кэша**: 10,000 записей
- **Hit rate**: 80%+

### 2. Асинхронная Обработка
- **FastAPI** для async HTTP
- **asyncio** для параллельной обработки
- **Batch processing** для множественных запросов

### 3. Ленивая Загрузка
- **Модели загружаются** только при первом использовании
- **Кэширование моделей** в памяти
- **Оптимизированные размеры** моделей

### 4. Раннее Прерывание
- **Smart Filter** может пропустить дорогую обработку
- **Пороги уверенности** для быстрых решений
- **Таймауты** для защиты от зависания

## 🧪 Тестирование

### Стратегия Тестирования
```
tests/
├── unit/                   # Unit тесты (95%+ покрытие)
│   ├── test_normalization.py
│   ├── test_smart_filter.py
│   └── test_decision_engine.py
├── integration/            # Интеграционные тесты
│   ├── test_pipeline_end2end.py
│   └── test_api_risk_response.py
└── e2e/                   # End-to-end тесты
    ├── test_full_pipeline_risk.py
    └── test_sanctions_screening_pipeline.py
```

### Типы Тестов
- **Unit тесты**: Тестирование отдельных компонентов
- **Integration тесты**: Тестирование взаимодействия слоев
- **E2E тесты**: Полные сценарии обработки
- **Performance тесты**: Нагрузочное тестирование
- **Contract тесты**: Проверка API контрактов

## 📊 Мониторинг и Метрики

### Prometheus Метрики
```python
# Основные метрики
ai_service_requests_total
ai_service_requests_successful_total
ai_service_processing_time_avg_seconds
ai_service_cache_hit_rate
ai_service_component_available
```

### Логирование
- **Структурированные логи** (JSON)
- **Уровни**: DEBUG, INFO, WARNING, ERROR
- **Контекстная информация** в каждом логе
- **Ротация логов** по размеру и времени

### Health Checks
- **Проверка зависимостей** (SpaCy модели)
- **Проверка конфигурации**
- **Проверка производительности**
- **Статистика работы**

## 🔧 Конфигурация

### Environment Variables
```bash
# Основные настройки
APP_ENV=production
DEBUG=false
WORKERS=4

# Feature flags
ENABLE_SMART_FILTER=true
ENABLE_VARIANTS=false
ENABLE_EMBEDDINGS=false
ENABLE_DECISION_ENGINE=true

# Производительность
MAX_INPUT_LENGTH=10000
CACHE_SIZE=10000
CACHE_TTL=3600

# Безопасность
ADMIN_API_KEY=your-secure-key
RATE_LIMIT_ENABLED=true
```

### Конфигурационные Классы
```python
@dataclass
class ServiceConfig:
    max_input_length: int = 10000
    enable_smart_filter: bool = True
    enable_variants: bool = False
    enable_embeddings: bool = False
    enable_decision_engine: bool = True
```

## 🚀 Развертывание

### Docker
```dockerfile
FROM python:3.12-slim

# Установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование кода
COPY src/ /app/src/
WORKDIR /app

# Запуск приложения
CMD ["uvicorn", "src.ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  ai-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - WORKERS=4
    volumes:
      - ./logs:/app/logs
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-service
  template:
    spec:
      containers:
      - name: ai-service
        image: ai-service:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## 📈 Масштабирование

### Горизонтальное Масштабирование
- **Stateless архитектура** - легко масштабируется
- **Load balancer** - распределение нагрузки
- **Health checks** - автоматическое восстановление
- **Auto-scaling** - автоматическое масштабирование

### Вертикальное Масштабирование
- **Memory optimization** - оптимизация использования памяти
- **CPU optimization** - оптимизация CPU
- **Caching strategies** - стратегии кэширования
- **Resource monitoring** - мониторинг ресурсов

---

*Документ подготовлен: Дарья Павлова*  
*Дата: Декабрь 2024*  
*Версия: 1.0*
