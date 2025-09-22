# Golden Test Suite для E2E Верификации

Компактный набор golden-кейсов для end-to-end верификации всех слоёв обработки, кроме нормализации (которая тестируется отдельно).

## 📋 Структура

```
tests/golden_e2e/
├── README.md                    # Этот файл
├── golden_suite.json            # Полный набор тестов (32 кейса)
├── simple_golden_runner.py      # Демо-раннер (работающий)
├── test_golden_suite.py         # Полный pytest-совместимый раннер
├── generate_layer_files.py      # Генератор файлов по слоям
└── layer_*.json                 # Тесты по слоям (7 файлов)
```

## 🎯 Покрытие слоев

1. **Ingest** (3 кейса) - парсинг входа, языковая детекция
2. **Smart Filter** (5 кейсов) - очистка текста, удаление шума
3. **Pattern Builder** (6 кейсов) - генерация вариантов, TIERы
4. **Signals** (5 кейсов) - матчинг и скоринг
5. **Decision Engine** (5 кейсов) - бизнес-логика решений
6. **Post Export Sanitizer** (5 кейсов) - очистка выходных данных
7. **Report Assembler** (3 кейсов) - сборка финального отчёта

## 🚀 Запуск

### Демо (работающий)
```bash
python simple_golden_runner.py
```

### Полный набор тестов
```bash
python test_golden_suite.py
```

### Конкретный слой
```bash
python test_golden_suite.py ingest
```

### Через pytest
```bash
pytest test_golden_suite.py -v
```

## 📊 Формат тестов

Каждый тест содержит:

```json
{
  "id": "G-ING-01",
  "layer": "ingest",
  "description": "базовый EN с шумом",
  "input": { /* входные данные */ },
  "expect": { /* ожидаемые точные значения */ },
  "assert": [ /* булевые проверки */ ]
}
```

## ✅ Типы проверок

- **expect**: точные значения полей
- **assert**: регулярные выражения, диапазоны, логические условия
- **includes**: проверка вхождения в массивы
- **includes_any**: проверка любого из элементов

## 🔧 Интеграция с реальными слоями

В production версии замените мок-функции в `_mock_layer_output()` на вызовы реальных слоев:

```python
# Вместо мока
if layer == "ingest":
    return mock_ingest_output(test_input)

# Используйте реальный слой
if layer == "ingest":
    return real_ingest_service.process(test_input)
```

## 📈 Примеры кейсов

### G-ING-01: Ingest - Английское имя с подсказкой языка
```json
{
  "input": {
    "full_name": "Dr. John A. Smith Jr.",
    "source_lang_hint": "en"
  },
  "expect": {
    "ingest.lang": "en"
  },
  "assert": [
    "ingest.lang == 'en'"
  ]
}
```

### G-SF-01: Smart Filter - Удаление титулов/суффиксов
```json
{
  "input": {
    "full_name_raw": "Dr. John A. Smith Jr.",
    "lang": "en"
  },
  "expect": {
    "sf.cleaned_name": "John Smith"
  },
  "assert": [
    "sf.cleaned_name == 'John Smith'"
  ]
}
```

### G-SIG-01: Signals - Exact match по TIN
```json
{
  "input": {
    "query": "782611846337",
    "index": {"tin": ["782611846337"]}
  },
  "expect": {
    "signal": "exact",
    "confidence": 1.0
  },
  "assert": [
    "score.exact >= 0.99"
  ]
}
```

## 🎨 Конфигурация

### Критерии успеха
- **Passed**: все expect и assert выполнены
- **Failed**: любая проверка не прошла
- **Error**: исключение во время выполнения

### Метрики качества
- Coverage: >= 0.9
- Precision/Recall: по порогам в assert
- Performance: время выполнения слоя

## 🔄 CI/CD Интеграция

Добавьте в `.github/workflows/`:

```yaml
- name: Run Golden E2E Tests
  run: |
    python tests/golden_e2e/test_golden_suite.py
    pytest tests/golden_e2e/test_golden_suite.py -v --tb=short
```

## 📝 Добавление новых тестов

1. Добавьте тест в `golden_suite.json`
2. Обновите мок-логику в раннере (если нужно)
3. Регенерируйте файлы по слоям:
   ```bash
   python generate_layer_files.py
   ```

## 🎯 Принципы

- ✅ **Атомарность**: каждый тест проверяет один слой
- ✅ **Детерминизм**: одинаковый input → одинаковый output
- ✅ **Изоляция**: тесты не влияют друг на друга
- ✅ **Полнота**: покрытие ключевых сценариев
- ✅ **Читаемость**: понятные ожидания и проверки

## 🚨 Анти-паттерны

- ❌ Тесты, зависящие от внешних сервисов
- ❌ Хардкод временных значений
- ❌ Каскадные падения (один тест ломает другие)
- ❌ Магические числа без объяснения

---

**Статус**: 🟢 Ready for production integration
**Последнее обновление**: 2025-01-22