# Cache System Architecture (n8n pattern)

Redis -> SQLite -> Memory fallback, `CacheService`, `CacheEntry` model, CRUD methods. Moved verbatim out of CLAUDE.md.

### 9. Cache System Architecture (n8n Pattern)
The cache system follows n8n's pattern with automatic fallback:

```
Production (Docker):  Redis → SQLite → Memory
Local Development:    SQLite → Memory (Redis disabled)
```

**Configuration** (`server/.env`):
```bash
REDIS_ENABLED=false           # Local dev: use SQLite
REDIS_URL=redis://redis:6379  # Production: Docker Redis
```

**CacheService** (`server/core/cache.py`):
```python
class CacheService:
    def __init__(self, database: Database, settings: Settings):
        self._database = database
        self._settings = settings
        self._redis: Optional[Redis] = None
        self._memory_cache: Dict[str, Any] = {}

    async def get(self, key: str) -> Optional[str]:
        # Try Redis first (if enabled)
        if self._redis:
            value = await self._redis.get(key)
            if value: return value
        # Fall back to SQLite
        entry = await self._database.get_cache_entry(key)
        if entry: return entry.value
        # Fall back to memory
        return self._memory_cache.get(key)
```

**SQLite Cache Model** (`server/models/cache.py`):
```python
class CacheEntry(SQLModel, table=True):
    __tablename__ = "cache_entries"
    key: str = Field(primary_key=True)
    value: str
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Key Methods** (`server/core/database.py`):
- `get_cache_entry(key)` - Get cache entry by key
- `set_cache_entry(key, value, ttl)` - Set with optional TTL
- `delete_cache_entry(key)` - Delete by key
- `cleanup_expired_cache()` - Remove expired entries
