"""Theory and insights scheduler for student learning."""
import logging
import asyncio
import discord
import random

logger = logging.getLogger("teaching-assistant")

INSIGHTS = {
    "web_dev": [
        {
            "type": "deep",
            "title": "React Server Components: Streaming & Suspense",
            "content": "RSC bukan cuma soal 'server vs client' — ini soal streaming HTML.\n\n\n你没有意识到: Suspense boundaries bisa di-nested, dan React akan streaming HTML secara gradual. user see content secepat-it loads, bukan nunggu semua.\n\nIni yang bikin RSC + Suspense outperform traditional SSR.",
            "code": None
        },
        {
            "type": "deep",
            "title": "React useEffect Cleanup = Critical",
            "content": "Setiap useEffect dengan async operation 郑明: cleanup function必须执行.\n\n❌ fetch data tanpa abort controller\n✅ useEffect(() => { const ac = new AbortController(); fetch(url, { signal: ac.signal }); return () => ac.abort(); }, [])\n\nTanpa cleanup = memory leak + stale state updates + race conditions.",
            "code": "useEffect(() => {\n  const controller = new AbortController();\n  fetch(url, { signal: controller.signal })\n    .then(res => res.json())\n    .then(setData);\n  return () => controller.abort();\n}, [url]);"
        },
        {
            "type": "deep",
            "title": "TypeScript: Covariance & Contravariance",
            "content": "Ini yang bikin banyak senior bingung:\n\n- **Covariant**: tipe boleh 'kurang specific' di output\n- **Contravariant**: tipe boleh 'kurang specific' di input\n- **Invariant**: harus exact match\n\nTypeScript function parameters are contravariant by default. That知 否?",
            "code": "type Animal = { name: string }\ntype Dog = { name: string; breed: string }\n\n// Error! Dog[] is not assignable to Animal[]\n// because arrays are invariant in TypeScript\nfunction makeAnimals(dogs: Dog[]): Animal[] {\n  return dogs; // This WILL error\n}"
        },
        {
            "type": "deep",
            "title": "Next.js Middleware: Edge != Serverless",
            "content": "Next.js Middleware runs di Edge Runtime — bukan berarti sama dengan serverless.\n\nEdge = V8 isolates, no Node.js APIs, cold start < 1ms\nServerless = Node.js, cold start 100ms-1s\n\nMiddleware itu Edge — cocok untuk auth check, redirect, geolocation. Bukan untuk: database queries berat, file operations.",
            "code": None
        },
        {
            "type": "deep",
            "title": "JavaScript Event Loop: Microtasks vs Macrotasks",
            "content": "setTimeout(fn, 0) !== setImmediate(fn)\n\nExecution order:\n1. Synchronous code first\n2. All microtasks (Promise.then, queueMicrotask)\n3. ONE macrotask (setTimeout, setInterval, I/O)\n4. Repeat\n\nPromise.resolve().then() adalah microtask — dia执行before setTimeout!\n\n这造成race condition yang surprising.",
            "code": "console.log('1');\nsetTimeout(() => console.log('2'), 0);\nPromise.resolve().then(() => console.log('3'));\n// Output: 1, 3, 2"
        },
        {
            "type": "deep",
            "title": "React useMemo: Dependencies Trap",
            "content": "useMemo yang dependencies-nya salah = subtle bugs.\n\n❌ const result = useMemo(() => expensiveCalc(a, b), [a])\n\nJikab bergantung juga sama b, tapi lupa include — kamu dapet stale value.\n\nUse ESLint rule `react-hooks/exhaustive-deps` — tapi perlu understand kenapa, not just blindly add semua.",
            "code": None
        },
        {
            "type": "deep",
            "title": "CSS Container Queries: Game Changer",
            "content": "Media queries check viewport. Container queries check parent.\n\nArtinya: komponen yang SAME component bisa beda tampilan tergantung container-nya — tanpa JavaScript!\n\nIni重构以前的组件封装方式.",
            "code": ".card-container {\n  container-type: inline-size;\n}\n@container (min-width: 400px) {\n  .card { flex-direction: row; }\n}"
        },
        {
            "type": "deep",
            "title": "Web Performance: Core Web Vitals Secrets",
            "content": "LCP (Largest Contentful Paint):\n- Optimize hero image dengan `fetchpriority=\"high\"`\n- Preload fonts, bukan preload everything\n\nCLS (Cumulative Layout Shift):\n- Selalu set `width` dan `height` pada gambar\n- Reserved space untuk ads\n\nINP (Interaction to Next Paint):\n- Long tasks di main thread = jank\n- Break up dengan `scheduler.yield()` atau `setTimeout(fn, 0)`",
            "code": "<img src='hero.jpg' fetchpriority='high' width='800' height='400' />"
        },
    ],
    "software_engineering": [
        {
            "type": "deep",
            "title": "Cargo Cult Programming",
            "content": "Senior devs juga bisa jadi korban: copy-paste pattern tanpa understand why.\n\nTanda-tanda cargo cult:\n- 'Pake always useEffect' — padahal mungkin tidak perlu\n- 'Pake Redux' — padahal Context cukup\n- 'Pake microservices' — padahal monolith cukup\n\nSeniority 不是关于工具, 是关于知道何时不使用工具.",
            "code": None
        },
        {
            "type": "deep",
            "title": "The Law of Leaky Abstractions",
            "content": "All non-trivial abstractions are leaky.\n\nORM meng-abstract SQL — tapi suatu saat kamu harus understand SQL untuk debug performance.\n\nNext.js meng-abstract HTTP — tapi suatu saat kamu harus understand HTTP untuk debug caching.\n\nDon't fight the abstraction. Learn what's underneath.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Premature Optimization is Evil... But",
            "content": "Knuth: 'Premature optimization is the root of all evil'\n\nTapi ada nuance: design decisions itu expensive untuk ubah later.\n\nYang boleh dioptimize dari awal:\n- Data model design (hard to migrate)\n- API contract (breaking changes costly)\n- Security (can't add retroactively)\n\n\nYang boleh ditunda: micro-optimizations, caching layers.",
            "code": None
        },
        {
            "type": "deep",
            "title": "The Fallacy of Golden Path",
            "content": "'Gak pake framework, gak professional'\n\n工具不等于专业精神. Kadang vanilla JS/Node lebih tepat — особенно untuk:\n- Microservices kecil\n- CLI tools\n- Embedded systems\n- Learning purposes\n\nRails/Django/Next.js = productive untuk 80% cases. Tapi 20%你需要自定义.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Technical Debt is NOT Always Bad",
            "content": "Technical debt itu seperti credit card — BERBAYAR, tapi sometimes right untuk leverage.\n\nAccept debt when:\n- Startup fase, speed matters\n- MVP untuk validate hypothesis\n- Temporary solution untuk buy time\n\nPay debt when:\n- Feature baru butuh refactor anyway\n- Debt rate (bug rate, slow development) > interest\n- Team cukup成熟untuk handle it",
            "code": None
        },
        {
            "type": "deep",
            "title": "Conway's Law: Org Structure = System Design",
            "content": "Organizations which design systems are constrained to produce systems which mirror their communication structures.\n\n— Melvin Conway, 1968\n\nKalau 3 teambau backend → akan ada 3 microservices.\nKalau tim frontend suka buat komponen independently → akan ada 微服务 frontend yang tidak coalesce.\n\nDesign org structure duluan, baru design system.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Sunk Cost Fallacy in Code",
            "content": "'Sudah 6 bulan kita bangun这套system, gak mungkin throw away'\n\nKalau codebase-nya sudah unsalvageable — rewrite sometimes是正确的选择.\n\nWarning signs:\n- Setiap feature butuh 3x waktu正常人\n- Tests tidak可靠—— kamu takut refactor\n- Senior devsavoid certain parts\n- Onboarding untuk new dev > 2 weeks\n\nCost of rewrite < cost of continue maintaining.",
            "code": None
        },
        {
            "type": "deep",
            "title": "The Single Source of Truth Problem",
            "content": "Data di:- Database- Redis cache- localStorage- Context/Redux- Component state\n\nKalau inconsistent → bugs.\n\nSenior devs design systems dengan clear ownership:\n- Database = source of truth\n- Cache = read-only acceleration\n- localStorage = user preferences only\n- State managers = UI state, bukan source of truth\n\nJika kamu find yourself syncing state across places — design flaw.",
            "code": None
        },
    ],
    "backend": [
        {
            "type": "deep",
            "title": "PostgreSQL: Indexes Are Not Free",
            "content": "Index mempercepat READ, tapi memperlambat WRITE.\n\nSetiap INSERT/UPDATE → semua indexes di table tersebut harus di-update.\n\n\nGuidelines:\n- Index columns yang ada di WHERE, JOIN, ORDER BY\n-Jangan index everything 'just in case'\n- Monitor dengan `pg_stat_user_indexes`\n- Composite index order matters: equal columns first\n\n`CREATE INDEX idx ON users(email, created_at)` — email untuk equality, created_at untuk range.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Database Transactions: Serialization vs Isolation",
            "content": "Isolation level yang lebih tinggi = lebih 'safe', tapi lebih lambat.\n\n- READ UNCOMMITTED: bisa read uncommitted data (dirty reads) — almost never use\n- READ COMMITTED: default di PostgreSQL\n- REPEATABLE READ: consistent view throughout transaction\n- SERIALIZABLE: fully isolated, bisa fail dengan serialization errors\n\nSERIALIZABLE bukan berarti 'lebih baik' — kadang perlu retry logic karena serialize failures.",
            "code": None
        },
        {
            "type": "deep",
            "title": "API Versioning: The Hard Parts",
            "content": "Versioning bukan soal `/v1/users` vs `/v2/users`.\n\nMasalah sebenar:\n- Field removal = BREAKING (perlu major version)\n- Field addition = non-breaking (bisa minor version)\n- Field semantics change = BREAKING (even if name sama)\n- Response format change = BREAKING\n\nBetter approach: evolution instead of versioning.\n- Add fields, don't remove\n- Deprecate dengan `Sunset` header\n- 301 redirect untuk major breaks\n\nAPI versioning is a commitment.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Caching: Invalidation is Harder Than Cache Creation",
            "content": "There are only two hard things in Computer Science: cache invalidation and naming things.\n\n— Phil Karlton\n\nCache strategies:\n- TTL-based: simple, but data bisa stale\n- Event-based: complex, but accurate\n- Write-through: consistent, but slower\n\nGeneral rule: don't cache data yang berubah frequently. Cache computations, bukan sources of truth.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Message Queues: At-Least-Once vs Exactly-Once",
            "content": "Distributed systems不可能同时拥有both.\n\nAt-least-once (Kafka, RabbitMQ):\n- Messages pasti di-deliver >= 1 times\n- Consumer harus handle duplicates (idempotency)\n- More common, more scalable\n\nExactly-once (Kafka transactions):\n- Expensive, complex\n- Use cases: billing, financial transactions\n\nDesign decision: idempotent consumers更重要.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Idempotency: The Design Principle Nobody Teaches",
            "content": "Idempotent = effect yang same即使执行一次或多次.\n\nAPI endpoints yang idempotent:\n- GET (天然 idempotent)\n- PUT (replace resource)\n- DELETE (天然 idempotent)\n- POST dengan幂等键 (deduplication)\n\nKenapa penting: retry logic, network failures, load balancers bisa cause duplicate requests.\n\nDesign: setiap mutation endpoint harus idempotent atau punya deduplication mechanism.",
            "code": "POST /payments\n{ \"order_id\": \"123\", \"idempotency_key\": \"abc-123\" }\n// Server check idempotency_key, return cached response if exists"
        },
        {
            "type": "deep",
            "title": "Rate Limiting: Token Bucket vs Sliding Window",
            "content": "Token Bucket: simple, burst-friendly\n- 100 requests/minute, bucket holds 100 tokens\n- Setiap request consume 1 token\n- Token refill continuously\n\nSliding Window: more accurate, harder to implement\n- Hit rate over continuous time window\n- Smoother, better untuk APIs yang steady traffic\n\nSliding window implementation: Redis ZSET dengan timestamps.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Circuit Breaker Pattern: Beyond Hello World",
            "content": "Circuit breaker states:\n1. CLOSED: normal operation, semua request through\n2. OPEN: fail fast, requests langsung rejected\n3. HALF_OPEN:试探恢复, allow some requests through\n\nKey metrics untuk transition:\n- Failure threshold (e.g., >50% errors dalam 10s)\n- Recovery timeout (e.g., 30s sebelum half-open)\n- Success threshold (e.g., >3 successes before close)\n\n不要 naive implementation. Consider:\n- Partial failures (timeout vs error)\n- Slow failures (slow responses)\n- Resource exhaustion (connection pool full)",
            "code": None
        },
    ],
    "devops": [
        {
            "type": "deep",
            "title": "Docker: Layer Caching Secrets",
            "content": "Docker layers hanya re-built jika layer tersebut berubah.\n\nBest practice order:\n1. Dependencies di-copy pertama (rarely change)\n2. Source code di-copy terakhir (frequently change)\n\n❌ COPY . .\nRUN npm ci\n✅ COPY package*.json .\nRUN npm ci\nCOPY . .\n\nIni leverage build cache — dependency installation hanya re-runs kalau package.json berubah.",
            "code": "FROM node:20-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm ci --only=production\nCOPY . .\nCMD [\"node\", \"index.js\"]"
        },
        {
            "type": "deep",
            "title": "Kubernetes: Liveness vs Readiness Probes",
            "content": "Liveness probe: 'Is this container alive? If not, restart'\nReadiness probe: 'Can this container accept traffic? If not, remove from load balancer'\n\nCommon mistake: use same probe untuk keduanya.\n\n正确的做法:\n- Liveness: `/healthz` yang simple, fast\n- Readiness: `/ready` yang check dependencies (DB, cache, downstream APIs)\n\nJika app butuh 30s untuk start, liveness should allow 30s startup.",
            "code": "livenessProbe:\n  httpGet:\n    path: /healthz\n    port: 8080\n  initialDelaySeconds: 30\nreadinessProbe:\n  httpGet:\n    path: /ready\n    port: 8080\n  initialDelaySeconds: 5"
        },
        {
            "type": "deep",
            "title": "GitOps: The Declarative Infrastructure Trap",
            "content": "GitOps = source of truth di Git, automated sync ke cluster.\n\nTemptation: push EVERYTHING to Git.\nReality: drift happens, reconciliation fails, dan kamu stuck.\n\nPractical GitOps:\n- App configs di Git ✓\n- Secrets: NOT in Git (use Sealed Secrets, Vault)\n- Sensitive infra: manual approval process\n- Drift detection yang regular\n\nGitOps is tool, not substitute untuk understanding infrastructure.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Observability: Metrics vs Logs vs Traces",
            "content": "Three pillars, different use cases:\n\nMetrics (Prometheus):\n- 'How many errors per minute?'\n- Aggregated, compressible, long retention\n- Good untuk alerting, dashboards\n\nLogs (ELK, Loki):\n- 'What happened at 3:00 PM?'\n- High cardinality, expensive to store\n- Good untuk debugging specific events\n\nTraces (Jaeger, Tempo):\n- 'Why is this request slow?'\n- Request-scoped, connected across services\n- Good untuk distributed debugging\n\n你不需要 all three dari day one. Start dengan metrics.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Database Migrations: Zero-Downtime Strategy",
            "content": "Zero-downtime migration itu complex tapi doable.\n\nExpand-Contract pattern:\n1. Add new column (expand)\n2. Deploy code yang write ke both old dan new column\n3. Backfill data\n4. Deploy code yang read dari new column\n5. Remove old column (contract)\n\n这意味着: 每个migration步骤must be independently deployable. Big migrations必须拆分.",
            "code": None
        },
        {
            "type": "deep",
            "title": "CI/CD: Test Pyramid Realization",
            "content": "Test Pyramid:\n- Many unit tests (fast, cheap)\n- Some integration tests (medium)\n- Few E2E tests (slow, expensive)\n\nReality check:\n- Unit tests catch logic bugs\n- Integration tests catch API contract bugs\n- E2E tests catch critical user flows ONLY\n\n若你的E2E tests > 20% — 太慢了, 你们等太久.\n若你的unit tests < 60% — 你们缺少fast feedback.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Incident Management: The Uncomfortable Truth",
            "content": "Incident = bukan about Blame, about Learning.\n\n但: 'No blame' culture doesn't mean 'No accountability'.\n\n\nGood incident process:\n1. Detect (alerting must be actionable)\n2. Respond (SRE playbook)\n3. Resolve (temporary fix vs permanent fix)\n4. Review (blameless postmortem)\n5. Improve (action items, tracked)\n\nPostmortem bukan总结报告,是改进计划.",
            "code": None
        },
        {
            "type": "deep",
            "title": "Cost Optimization: The AWS Bill Horror Show",
            "content": "Common cost mistakes:\n- Reserved instances untuk intermittent workloads\n- EBS volumes yang idle但charging\n- NAT Gateway untuk infrequent traffic\n- Multi-AZ untuk dev environments\n- No lifecycle policies untuk S3\n\nCloud costs itu fractal — selalu有surprise di细节.\n\nTools: AWS Cost Explorer, Kubecost untuk K8s, Datadog APM untuk compute.\n\nRule of thumb: if you're not looking at your bill monthly, you're overspending.",
            "code": None
        },
    ]
}

def get_random_insight() -> dict:
    """Get a random insight from random category."""
    category = random.choice(list(INSIGHTS.keys()))
    insight = random.choice(INSIGHTS[category])
    return {**insight, "category": category}

def format_insight(insight: dict) -> str:
    """Format insight for Discord."""
    category_emoji = {
        "web_dev": "⚛️",
        "software_engineering": "🔧",
        "backend": "🗄️",
        "devops": "🐳"
    }
    type_emoji = {
        "tip": "💡",
        "quiz": "❓",
        "deep": "📚",
        "fun_fact": "🤓"
    }

    emoji_cat = category_emoji.get(insight["category"], "📌")
    emoji_type = type_emoji.get(insight["type"], "📌")

    title = insight["title"]
    content = insight["content"]
    insight_type = insight["type"]

    lines = [
        f"**{emoji_cat} {title}** {emoji_type}\n",
        f"{content}\n"
    ]

    if insight.get("code"):
        lines.append(f"```\n{insight['code']}\n```")

    if insight_type == "quiz":
        lines.append(f"\n*Jawaban: ||{insight['answer']}||*")

    return "".join(lines)

def get_insight_message() -> str:
    """Generate insight message for posting."""
    insight = get_random_insight()
    formatted = format_insight(insight)

    message = f"""
📚 **Insight Per Jam — Web Programming**

{formatted}

---
💡 Mau topik tertentu? Ketik `!insight [web|se|backend|devops]` untuk minta insight spesifik!
"""
    return message.strip()

async def send_insight_to_channel(bot, channel_name: str = "umum"):
    """Send insight to specified channel."""
    guild = bot.client.get_guild(bot.guild_id)
    if not guild:
        return False

    channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not channel:
        return False

    message = get_insight_message()
    await channel.send(message)
    return True

async def start_insight_scheduler(bot, interval_hours: int = 1):
    """Start the insight scheduler."""
    logger.info(f"Insight scheduler started - posting every {interval_hours} hour(s)")

    while True:
        try:
            guild = bot.client.get_guild(bot.guild_id)
            if guild:
                channel = discord.utils.get(guild.text_channels, name="umum")
                if channel:
                    message = get_insight_message()
                    await channel.send(message)
                    logger.info("Insight posted to #umum")
                else:
                    logger.warning("Channel #umum not found")
            else:
                logger.warning("Guild not found")
        except Exception as e:
            logger.error(f"Error posting insight: {e}")

        await asyncio.sleep(interval_hours * 3600)