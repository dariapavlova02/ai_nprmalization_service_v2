# Система профилирования AI Service Normalization Factory

Полнофункциональная система профилирования производительности для выявления узких мест в factory-пути нормализации.

## 🎯 Цель

Пропрофилировать factory-путь нормализации на коротких строках и найти "горячие точки" для оптимизации:
- Убрать лишние аллокации/копии строк
- Кэшировать морф-парсы и токен-классы
- Предоставить конкретные рекомендации по оптимизации

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
make -f Makefile.profile install-profile-deps
```

### 2. Демонстрация системы

```bash
python scripts/demo_profiling.py
```

### 3. Полное профилирование

```bash
make -f Makefile.profile profile
```

### 4. Просмотр результатов

```bash
make -f Makefile.profile show-profile
```

## 📁 Структура системы

```
scripts/
├── profile_normalization.py          # cProfile + pstats профилирование
├── profile_normalization_pyinstrument.py  # pyinstrument HTML-отчёты
├── generate_profile_report.py        # Генерация markdown-отчёта
├── test_profiling.py                 # Тестирование системы
└── demo_profiling.py                 # Демонстрация возможностей

src/ai_service/utils/
└── profiling.py                      # Утилиты профилирования

docs/
└── PROFILING_README.md               # Детальная документация

artifacts/                            # Результаты профилирования
├── profile_stats.prof               # cProfile бинарные данные
├── profile_async.html               # pyinstrument HTML (async)
├── profile_sync.html                # pyinstrument HTML (sync)
├── profile_detail_*.html            # Детальные HTML-отчёты
└── profile_report.md                # Markdown-отчёт с рекомендациями
```

## 🔧 Компоненты системы

### 1. Скрипты профилирования

#### `profile_normalization.py`
- **Назначение**: Профилирование с cProfile + pstats
- **Выход**: TOP-50 функций по cumtime/tottime
- **Использование**: `python scripts/profile_normalization.py [iterations]`

#### `profile_normalization_pyinstrument.py`
- **Назначение**: Детальные HTML-отчёты с визуализацией
- **Выход**: `artifacts/profile_*.html`
- **Использование**: `python scripts/profile_normalization_pyinstrument.py [iterations]`

#### `generate_profile_report.py`
- **Назначение**: Анализ результатов и генерация рекомендаций
- **Выход**: `artifacts/profile_report.md`
- **Использование**: `python scripts/generate_profile_report.py`

### 2. Утилиты профилирования (`profiling.py`)

#### `PerformanceCounter`
- Дешёвый счётчик времени выполнения
- Метрики: p50, p95, p99, среднее, минимум, максимум
- Thread-safe для многопоточности

#### `MemoryTracker`
- Трекинг памяти с tracemalloc
- Пиковое использование, аллокации, снимки
- Интеграция с контекстными менеджерами

#### `ProfilingManager`
- Централизованное управление метриками
- Сбор статистик со всех компонентов
- Экспорт в различных форматах

#### Декораторы и контекстные менеджеры
```python
@profile_function("component.method")
async def method():
    pass

with profile_time("operation"):
    # код

with profile_memory("allocation"):
    # код
```

### 3. Интеграция в сервисы

Профилирование интегрировано в ключевые компоненты:

- **`TokenProcessor.strip_noise_and_tokenize`** - токенизация
- **`MorphologyProcessor.normalize_slavic_token`** - морфология
- **`RoleClassifier.tag_tokens`** - классификация ролей
- **`NormalizationFactory.normalize_text`** - основной процесс

## 📊 Тестовые данные

Система использует фиксированный набор из 20 фраз:

### Русские имена
- "Іван Петров"
- "ООО 'Ромашка' Иван И."
- "Анна Сергеевна Иванова"
- "Петр Петрович Петров"
- "Мария Александровна Сидорова"

### Украинские имена
- "Петро Порошенко"
- "Володимир Зеленський"
- "Олена Піддубна"
- "ТОВ 'Київ' Олександр О."
- "Наталія Вікторівна Коваленко"

### Английские имена
- "John Smith"
- "Mary Johnson"
- "Robert Brown"
- "Elizabeth Davis"
- "Michael Wilson"

### Смешанные случаи
- "Dr. John Smith"
- "Prof. Maria Garcia"
- "Mr. Петр Петров"
- "Ms. Анна Иванова"
- "Іван I. Петров"

## 🎯 Типы горячих точек

### 1. Tokenization (токенизация)
- **Симптомы**: Высокое время в `strip_noise_and_tokenize`
- **Причины**: Множественные regex, split() в циклах
- **Рекомендации**: Предкомпиляция regex, батчевая обработка

### 2. Morphology (морфология)
- **Симптомы**: Высокое время в `normalize_slavic_token`
- **Причины**: Повторные вызовы pymorphy3
- **Рекомендации**: LRU кэш, кэширование результатов

### 3. Role Classification (классификация ролей)
- **Симптомы**: Высокое время в `tag_tokens`
- **Причины**: Линейный поиск в словарях
- **Рекомендации**: Set вместо list, кэширование

### 4. Normalization (нормализация)
- **Симптомы**: Высокое время в `normalize_text`
- **Причины**: Повторные вычисления, неэффективные алгоритмы
- **Рекомендации**: Кэширование, оптимизация алгоритмов

### 5. Regex (регулярные выражения)
- **Симптомы**: Высокое время в regex функциях
- **Причины**: Компиляция в каждом вызове
- **Рекомендации**: Предкомпиляция на уровне модуля

## 📈 Рекомендации по оптимизации

### 1. Кэширование морфологического анализа

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def _morph_nominal_cached(token: str, language: str) -> str:
    # Кэшированная версия морфологического анализа
    pass
```

**Ожидаемый эффект**: -30-50% времени

### 2. Предкомпиляция регулярных выражений

```python
import re

# На уровне модуля
TOKEN_SPLIT_PATTERN = re.compile(r"([,])")
INITIALS_PATTERN = re.compile(r"^((?:[A-Za-zА-Яа-яІЇЄҐіїєґ]\.){2,})([A-Za-zА-Яа-яІЇЄҐіїєґ].*)$")
```

**Ожидаемый эффект**: -10-20% времени

### 3. Оптимизация поиска в словарях

```python
# Использовать set вместо list для O(1) поиска
STOP_WORDS_SET = set(STOP_ALL)
```

**Ожидаемый эффект**: -5-15% времени

### 4. Кэширование результатов классификации ролей

```python
from functools import lru_cache

@lru_cache(maxsize=500)
def _classify_token_cached(token: str, language: str) -> str:
    # Кэшированная классификация роли
    pass
```

**Ожидаемый эффект**: -20-40% времени

## 🛠 Команды Makefile

```bash
# Полное профилирование
make -f Makefile.profile profile

# Только cProfile
make -f Makefile.profile profile-cprofile

# Только pyinstrument
make -f Makefile.profile profile-pyinstrument

# Быстрое профилирование
make -f Makefile.profile profile-quick

# Профилирование с памятью
make -f Makefile.profile profile-memory

# Генерация отчёта
make -f Makefile.profile profile-report

# Показать результаты
make -f Makefile.profile show-profile

# Очистка результатов
make -f Makefile.profile clean-profile

# Установка зависимостей
make -f Makefile.profile install-profile-deps
```

## 📋 Критерии приёмки

- ✅ Есть два скрипта профилирования; локально работают без ES/сетей
- ✅ Генерится `artifacts/profile.html` и `artifacts/profile_report.md`
- ✅ В отчёте явно перечислены 3–5 горячих мест с конкретными действиями
- ✅ Система не ломает внешний контракт `NormalizationResult`
- ✅ Путь legacy не затронут
- ✅ Никаких глобальных сайд-эффектов: профилирование запускается только в `scripts/*`

## 🔍 Интерпретация результатов

### HTML-отчёты pyinstrument
1. Откройте `artifacts/profile_async.html` в браузере
2. Изучите flame graph для визуализации call stack
3. Обратите внимание на функции с наибольшим временем выполнения
4. Ищите узкие места в критическом пути

### Markdown-отчёт
1. Откройте `artifacts/profile_report.md`
2. Изучите таблицу TOP-10 горячих точек
3. Обратите внимание на рекомендации по оптимизации
4. Следуйте приоритизации (high/medium/low priority)

## 🚨 Ограничения и предупреждения

1. **Профилирование влияет на производительность** - не используйте в production
2. **Результаты могут варьироваться** - запускайте несколько раз для стабильности
3. **Память** - pyinstrument может потреблять много памяти на больших наборах данных
4. **Зависимости** - убедитесь, что все опциональные зависимости установлены

## 🔧 Troubleshooting

### Ошибка "pyinstrument не установлен"
```bash
pip install pyinstrument
```

### Ошибка "ModuleNotFoundError"
```bash
# Убедитесь, что вы в корневой директории проекта
cd /path/to/ai-service
python scripts/profile_normalization.py
```

### Нет результатов профилирования
```bash
# Очистите кэш и перезапустите
make -f Makefile.profile clean-profile
make -f Makefile.profile profile
```

## 📚 Дополнительные ресурсы

- [Детальная документация](docs/PROFILING_README.md)
- [cProfile документация](https://docs.python.org/3/library/profile.html)
- [pyinstrument документация](https://pyinstrument.readthedocs.io/)
- [Python profiling best practices](https://docs.python.org/3/library/profile.html#profile-stats)

## 🎉 Заключение

Система профилирования готова к использованию и предоставляет:

1. **Детальный анализ производительности** с помощью cProfile и pyinstrument
2. **Конкретные рекомендации по оптимизации** с ожидаемыми эффектами
3. **Интеграцию в ключевые компоненты** без нарушения внешнего API
4. **Удобные инструменты** для запуска и анализа результатов

Запустите `python scripts/demo_profiling.py` для быстрого знакомства с системой!
