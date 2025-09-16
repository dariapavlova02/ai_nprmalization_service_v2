# 🚀 AI Service - Unified Architecture

**Clean, consolidated AI service** for normalization and structured extraction from sanctions data with support for multiple languages (English, Russian, Ukrainian).

## ✨ **Unified Architecture Benefits**

🎯 **Single Orchestrator** - Replaced 3+ duplicate implementations with one clean `UnifiedOrchestrator`
📋 **CLAUDE.md Compliant** - Exact 9-layer specification implementation
🔍 **Structured Signals** - Persons, organizations, IDs, dates with full traceability
⚡ **Performance Optimized** - ≤10ms for short strings, comprehensive caching
🧪 **Comprehensive Testing** - 12 real payment scenarios, contract validation

## 🏗️ **9-Layer Architecture**

```
1. Validation & Sanitization  →  Basic input validation
2. Smart Filter              →  Pre-processing decision
3. Language Detection        →  ru/uk/en identification
4. Unicode Normalization     →  Text standardization
5. Name Normalization (CORE) →  Person names + org cores
6. Signals                   →  Structured extraction
7. Variants (optional)       →  Spelling alternatives
8. Embeddings (optional)     →  Vector representation
9. Decision & Response       →  Final result assembly
```

## 🎯 **Core Features**

- **📝 Text Normalization**: Morphological analysis with token-level tracing
- **🏢 Structured Extraction**: Persons with DOB/IDs, organizations with legal forms
- **🌍 Multi-language Support**: Russian, Ukrainian, English with mixed-script handling
- **🔍 Smart Filtering**: Pre-processing optimization with signal detection
- **📊 Signal Analysis**: Legal forms, payment contexts, document numbers
- **🎯 Variant Generation**: Transliteration, phonetic, morphological variants
- **⚡ High Performance**: Caching, async processing, performance monitoring

## 🔮 **Embeddings**

The EmbeddingService provides pure vector generation capabilities using multilingual sentence transformers:

### **Model Choice & Architecture**
- **Default Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Why L12 v2**: Balanced performance (384-dim) with multilingual support (ru/uk/en)
- **Output**: 32-bit float vectors, ready for downstream similarity analysis
- **Preprocessing**: Automatically removes dates/IDs - only names/organizations are embedded

### **Why Dates/IDs Are Excluded**
- **Separation of Concerns**: Names → semantic similarity, Dates/IDs → exact matching
- **Downstream Processing**: Signals layer handles structured data, Decision layer does exact matching
- **Performance**: Cleaner embeddings without noise from structured data

### **API Usage**
```python
from ai_service.config import EmbeddingConfig
from ai_service.layers.embeddings.embedding_service import EmbeddingService

# Initialize service
config = EmbeddingConfig()
service = EmbeddingService(config)

# Single text encoding
vector = service.encode_one("Ivan Petrov")  # 384 floats

# Batch encoding (recommended)
vectors = service.encode_batch(["Ivan Petrov", "Anna Smith"])  # 2x384 floats

# Multilingual support
ru_vector = service.encode_one("Иван Петров")
uk_vector = service.encode_one("Іван Петров") 
en_vector = service.encode_one("Ivan Petrov")
# All vectors are comparable for similarity analysis
```

### **Model Switching**
```python
# Switch models via configuration
config = EmbeddingConfig(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    extra_models=["sentence-transformers/all-MiniLM-L6-v2"]
)
service = EmbeddingService(config)
```

### **Performance SLA**
- **Latency**: < 15ms single text, < 200ms for 1000 texts (p95)
- **Memory**: ~80MB model + ~1MB per 100 texts
- **Throughput**: ~100 texts/sec (CPU), ~500 texts/sec (GPU)

### **Important Notes**
- **No Indexing**: Pure vector generation - indexing handled downstream
- **No Similarity Search**: Vector similarity calculations done by other services  
- **Lazy Loading**: Models loaded only when first needed
- **Batch Processing**: Optimized for processing multiple texts efficiently

📖 **Detailed Documentation**: See [docs/embeddings.md](docs/embeddings.md) for complete usage guide

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry for dependency management
- Docker (optional)

### Local Development

1. **Install dependencies**:
   ```bash
   make install-dev
   ```

2. **Start the service**:
   ```bash
   make start
   ```

3. **Run tests**:
   ```bash
   make test
   ```

### Docker Deployment

1. **Build the image**:
   ```bash
   make docker-build
   ```

2. **Run production container**:
   ```bash
   make docker-run
   ```

3. **Run development container**:
   ```bash
   make docker-dev
   ```

## API Endpoints

### Core Endpoints

- `POST /process` - Complete text processing
- `POST /normalize` - Text normalization
- `POST /process-batch` - Batch text processing
- `POST /search-similar` - Similarity search
- `POST /analyze-complexity` - Text complexity analysis

### Administrative Endpoints (Protected)

- `POST /clear-cache` - Clear cache (requires API key)
- `POST /reset-stats` - Reset statistics (requires API key)

### Information Endpoints

- `GET /health` - Service health check
- `GET /stats` - Processing statistics
- `GET /languages` - Supported languages
- `GET /` - Service information

## Configuration

The service uses environment variables for configuration:

- `APP_ENV`: Environment (development, staging, production)
- `WORKERS`: Number of worker processes (production only)
- `DEBUG`: Enable debug mode

### Security

Administrative endpoints are protected with API key authentication. Set the key in `config.py`:

```python
SECURITY_CONFIG = {
    'admin_api_key': 'your-secure-api-key-here'
}
```

## Development

### Project Structure

```
src/ai_service/
├── services/           # Core services
│   ├── orchestrator_service.py
│   ├── normalization_service.py
│   ├── variant_generation_service.py
│   └── ...
├── data/              # Data files and templates
├── config/            # Configuration files
└── utils/             # Utility functions

tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── e2e/              # End-to-end tests
```

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test file
poetry run pytest tests/unit/test_orchestrator_service.py -v

# Test collection only (verify configuration)
poetry run pytest --collect-only -q

# Run specific test markers
poetry run pytest -m unit -v
poetry run pytest -m integration -v
poetry run pytest -m skip_heavy_deps -v
```

### Pytest Configuration

The project uses `pytest.ini` for test configuration with the following features:

- **Timeout**: 300 seconds per test (configurable via `timeout = 300`)
- **Markers**: Support for `unit`, `integration`, `slow`, `performance`, `skip_heavy_deps`
- **Async Support**: Automatic async test detection (`asyncio_mode = auto`)
- **Warning Filters**: Deprecation and user warnings are filtered out
- **Test Discovery**: Automatically finds tests in `tests/` directory

**Note**: Some tests require heavy dependencies (ML libraries). Use `-m skip_heavy_deps` to skip these tests if dependencies are not installed.

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Clean up
make clean
```

## Deployment

### Production

1. **Set environment**:
   ```bash
   export APP_ENV=production
   export WORKERS=4
   ```

2. **Install dependencies**:
   ```bash
   make install
   ```

3. **Start service**:
   ```bash
   make start-prod
   ```

### Docker Compose

```bash
# Production
docker-compose up ai-service

# Development
docker-compose --profile dev up ai-service-dev
```

## CI/CD

The project includes GitHub Actions workflow for automated testing:

- Runs on push to `main` and `develop` branches
- Runs on pull requests
- Installs dependencies with Poetry
- Runs tests with coverage
- Uploads coverage to Codecov

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Statistics

```bash
curl http://localhost:8000/stats
```

## 🔍 **Hybrid Search System**

The AI Service now includes a comprehensive hybrid search system combining Aho-Corasick (AC) lexical search with kNN vector search for optimal performance and accuracy.

### **Key Features**
- **AC Search**: Exact, phrase, and ngram matching for precise lexical search
- **Vector Search**: Semantic similarity using dense vectors (384-dimensional)
- **Hybrid Fusion**: Intelligent combination of AC and vector results
- **Elasticsearch Integration**: Scalable search backend with monitoring
- **Performance Monitoring**: Comprehensive metrics and alerting

### **Quick Start with Search**

1. **Start the monitoring stack**:
   ```bash
   docker-compose -f monitoring/docker-compose.monitoring.yml up -d
   ```

2. **Load sample data**:
   ```bash
   python scripts/bulk_loader.py --input sample_entities.jsonl --entity-type person --upsert
   ```

3. **Test search functionality**:
   ```bash
   python scripts/quick_test_search.py --test all
   ```

4. **Check system health**:
   ```bash
   ./scripts/health_check.sh
   ```

### **Search API Endpoints**
- `POST /search` - Hybrid search with AC and vector fusion
- `POST /search/ac` - AC-only search (exact, phrase, ngram)
- `POST /search/vector` - Vector-only search (kNN)
- `GET /search/health` - Search system health check

### **Monitoring Dashboards**
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### **Emergency Procedures**
```bash
# Check system health
./scripts/emergency_procedures.sh health

# Emergency restart
./scripts/emergency_procedures.sh restart

# Enable fallback mode
./scripts/emergency_procedures.sh fallback
```

📖 **Complete Documentation**: See [docs/hybrid-search-runbook.md](docs/hybrid-search-runbook.md) for comprehensive SRE and developer procedures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

@ Daria Pavlova