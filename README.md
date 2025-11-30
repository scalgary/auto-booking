# Automated Pickleball Court Booking System

*Because I'd rather spend time playing pickleball than refreshing a booking page at ungodly hours.*

## The Problem

High-demand pickleball courts at my local gym open for booking at... well, that's the issue. The rules keep changing:
- Started at midnight
- Changed to 8:00 AM  
- Changed back to midnight
- Who knows what's next?

Slots fill within 10-30 seconds. Manual booking means setting alarms, refreshing frantically, and competing with hundreds of players. **I needed automation that could adapt to constant rule changes.**

## Rule #0: Never Hardcode Anything

The gym changes booking policies constantly. My solution had to survive these changes without code refactoring.

**Every configurable parameter lives in:**
- Environment variables (workflow-level timing)
- JSON config files (booking details)
- Command-line arguments (runtime parameters)
- Python constants (performance tuning)

**Result**: When booking time changed from midnight → 8am, I edited one workflow variable. No code changes. No redeployment.

## Core Technical Challenges

### 1. Unreliable Scheduling on Free Infrastructure

**The Problem**: GitHub Actions free tier doesn't guarantee cron execution times. A job scheduled for 7:59 AM might run at 7:59... or 8:02... or 8:07. When slots disappear in 10 seconds, this is catastrophic.

**My Solution**: Multi-schedule reliability window with smart deduplication
```yaml
schedule:
  - cron: '45 14 * * *'  # 7:45 AM Calgary (4 attempts)
  - cron: '52 14 * * *'  # 7:52 AM
  - cron: '56 14 * * *'  # 7:56 AM  
  - cron: '59 14 * * *'  # 7:59 AM
```

**Deduplication Strategy**:
1. First successful run creates a Git tag: `his-booking-06-Dec-25`
2. Subsequent runs check for tag and abort
3. Concurrency groups **queue** (don't cancel) to handle race conditions

**Why This Works**:
- Guaranteed at least one attempt within 15 minutes of target time
- Tag-based deduplication is git-native (no external state)
- Queueing preserves all attempts for audit trail
- Simple enough to debug at 2 AM when things break

**Alternative Rejected**: Complex retry logic in a single workflow would hit GitHub Actions timeout limits and be harder to debug.

### 2. Dynamic Content Without Page Refreshes

**The Problem**: The gym website pre-loads all slots in the DOM but shows them as "Unavailable" until exactly 8:00 AM. The HTML exists, but the "Book Now" button doesn't appear until opening time.

**Naive Solution** (what I tried first):
```python
# Refresh page every 2 seconds
while not_bookable:
    driver.refresh()
    time.sleep(2)
    check_if_bookable()
```
**Problems**: Slow (6-8s per refresh), resource-heavy, misses the exact moment slots open.

**Smart Solution**: DOM polling with high-frequency checks
```python
WebDriverWait(driver, timeout=3, poll_frequency=0.1).until(
    lambda d: len(parent.find_elements(
        By.XPATH, ".//*[contains(text(), 'Book Now')]"
    )) > 0
)
```

**Performance Impact**:
- Old approach: ~2-4 second delay after slots open
- New approach: ~100-300ms delay after slots open
- **10-20x faster response time**

**Key Insight**: Modern web apps update DOM without full page reloads. Polling the DOM is orders of magnitude faster than refreshing the entire page.

### 3. Production Debugging Without Access to Production

**The Problem**: When the bot fails at 8:00 AM, I'm asleep. When I wake up at 10:00 AM, GitHub Actions shows "❌ Failed" with no useful context. I have zero visibility into what actually happened.

**My Solution**: Comprehensive diagnostic logging system

**Dual-Output Strategy**:
```python
# Console: INFO level (what happened)
logger.info("🔍 Recherche du slot correspondant...")

# File: DEBUG level (why it happened)  
logger.debug(f"Bouton {i}: {class_name} | Date match: {date_match}")
```

**Performance Instrumentation**:
```python
start = time.perf_counter()
# ... operation ...
logger.info(f"⏱️ Login total: {time.perf_counter() - start:.3f}s")
```

**Element Diagnostics** (when clicks fail):
```python
logger.info(f"📍 Position: {button.location}")
logger.info(f"👁️ Visible: {button.is_displayed()}")
logger.info(f"✅ Enabled: {button.is_enabled()}")

# What's actually blocking the click?
top_element = driver.execute_script("""
    var rect = arguments[0].getBoundingClientRect();
    var centerX = rect.left + rect.width / 2;
    var centerY = rect.top + rect.height / 2;
    return document.elementFromPoint(centerX, centerY);
""", button)
```

**Conditional Debug Screenshots**:
```python
if self.debug_mode:
    filename = f"debug_{step_name}_{date}.png"
    driver.save_screenshot(filename)
```

**Real Impact**: 
- Before: Spend 30 minutes reproducing issues locally
- After: Read log file, understand exact failure point, fix in 5 minutes
- Bonus: Performance data reveals bottlenecks (page loads dominate at 5-8s)

### 4. Flexible Configuration for Changing Requirements

**The Challenge**: Support multiple users, multiple time slots, changing gym rules, and ad-hoc bookings.

**Architecture**:

**Workflow Level** (timing control):
```yaml
env:
  TARGET_UTC_HOUR: 15              # Changes when gym changes rules
  TAG_PREFIX: 'his'                # Separate streams for different users
  REGISTRATION_JSON_FILE: 'his_registrations.json'
```

**JSON Config** (weekly planning):
```json
{
  "date": "06-Dec-25",
  "time": "18:00",
  "level": "Advanced",
  "name": "Player Name"
}
```

**Command-Line** (testing):
```bash
python bot_execution_sleep.py "06-Dec-25" "18:00" "Advanced" "Player"
```

**Runtime Tuning** (performance):
```python
time_sleep = 3              # Balance speed vs reliability
poll_frequency = 0.1        # How often to check DOM changes
web_wait_time = 3           # Max wait for elements
implicit_wait = 0.5         # Driver-level element search timeout
```

**Why This Matters**: 
- Gym changes booking time → Edit one env var
- Want to book for a friend → Use different JSON config
- Testing new slot → Manual workflow dispatch
- Performance tuning → Adjust constants, no architecture changes

## Technical Implementation

### Code Evolution (3 Phases)

**Phase 1: `execution.py`** - Proof of Concept
- Functional/procedural approach
- Hard-coded values everywhere
- Basic screenshots
- Question: "Can this even be automated?"

**Phase 2: `bot_execution.py`** - Production Readiness  
- Object-oriented design with `TennisBookingBot` class
- Encapsulated state and configuration
- WebDriverWait for reliability
- Question: "How do we make this maintainable?"

**Phase 3: `bot_execution_sleep.py`** - Performance & Observability
- `time.perf_counter()` instrumentation everywhere
- Dual console/file logging with DEBUG mode
- Smart polling (DOM observation vs page refresh)
- Detailed element diagnostics
- Question: "How do we make this fast and debuggable?"

### Docker Strategy

**Development**: 
- `docker-compose` with full debugging stack
- Works in GitHub Codespaces for cloud development
- All the tools I need to iterate quickly

**Production**:
- Custom lightweight image: `scalgary/selenium-env:latest`
- Optimized for GitHub Actions cold start time
- Just enough packages to run headless Chrome + Selenium

**Trade-off**: Development convenience vs production speed. Both environments coexist peacefully.

### GitHub Actions Workflow Design

**3 Workflows, 3 Purposes**:

1. **`docker-build.yml`**: Manual trigger to build/push Docker images when dependencies change

2. **`registrations.yml`**: The production workhorse
   - 4 cron schedules (reliability window)
   - Tag-based deduplication (Git tags as free state storage)
   - Manual dispatch form (ad-hoc bookings)
   - Concurrency queue (preserve audit trail)
   - Bot commits successful bookings with tag

3. **`clever_registration.yml`**: Experimental variations (testing ground)

**Key GitHub Actions Learnings**:
- Free tier cron is unreliable → compensate with multiple attempts
- Concurrency control: queue vs cancel matters for audit trail
- Tags are free, persistent, git-native state storage
- Manual dispatch is invaluable for testing
- Permissions must be explicit (`contents:write` for bot commits)

### Performance Metrics

**Typical End-to-End**: 8-15 seconds from cold start to confirmed booking

**Breakdown**:
- Driver setup: 1-2s
- Login: 3-5s
- Navigate to planning: 2-3s
- Find matching slot: 0.5-1s
- Poll for "Book Now": 0.5-3s (variable based on timing)
- Click + select player: 2-3s
- Confirm: 1-2s

**Bottleneck Identified**: Page loads dominate (5-8s combined). Selenium operations are sub-second each. Can't optimize network/rendering time, but DOM polling minimizes waiting.

## Project Structure
```
.
├── execution.py                    # Phase 1: Functional proof-of-concept
├── bot_execution.py                # Phase 2: OOP refactor
├── bot_execution_sleep.py          # Phase 3: Production (current)
├── reminder.py                     # Calendar sync automation
├── his_registrations.json          # Booking config (Player 1)
├── my_registrations.json           # Booking config (Player 2)
├── Dockerfile                      # Lightweight production image
├── docker-compose.yml              # Full dev environment
└── .github/workflows/
    ├── docker-build.yml            # Image builder (manual)
    ├── registrations.yml           # Main booking workflow (4 crons)
    └── clever_registration.yml     # Experimental playground
```

## Configuration Examples

### Secrets (GitHub Actions)
```bash
YOUR_SECRET_EMAIL=user@example.com
YOUR_SECRET_PASSWORD=***
YOUR_SECRET_LOGON_URL=https://gym.example.com/login
YOUR_SECRET_PLANNING_URL=https://gym.example.com/schedule
YOUR_SECRET_MY_NAME=Player1
YOUR_SECRET_HIS_NAME=Player2
```

### Workflow Environment Variables
```yaml
env:
  TARGET_UTC_HOUR: 15              # 8:00 AM Calgary = 15:00 UTC
  MAX_WAIT_SECONDS: 500            # Safety timeout
  ADVANCE_SECONDS: 2               # Click buffer time
  TAG_PREFIX: 'his'                # Namespace for this booking stream
  REGISTRATION_JSON_FILE: 'his_registrations.json'
```

### Weekly Booking Config (JSON)
```json
{
  "date": "06-Dec-25",
  "time": "18:00",
  "level": "Advanced",
  "name": "Player Name"
}
```

**Workflow**: Every Sunday, I update the JSON with next week's desired slots. Bot handles the rest automatically.

## Running It

**Local Development**:
```bash
# Full dev environment
docker-compose up

# Direct execution with arguments
python bot_execution_sleep.py "06-Dec-25" "18:00" "Advanced" "Player"
```

**Production**: 
- Automatic: GitHub Actions cron triggers
- Manual: Actions tab → Run workflow → Fill form

## Key Learnings

### Problem-Solving Over Elegance
The 4-cron approach is "inelegant" by computer science standards. A single workflow with perfect retry logic would be more sophisticated. But:
- 4 crons is trivially simple to understand
- Debugging is straightforward (each run is independent)
- No complex state management needed
- **It works 100% of the time when slots are available**

Lesson: Pragmatic solutions beat theoretical purity.

### Observability is Worth the Investment
Time spent building the logging infrastructure (dual output, performance tracking, element diagnostics) paid back 10x when debugging production failures. You can't fix what you can't see.

### Parameters > Hard-Coding
When external systems change frequently (gym rules, booking times), parameterized code survives. Hard-coded values create technical debt. Rule #0 saved me from multiple refactoring cycles.

### Docker: Dev vs Prod is a Real Trade-off
Development needs debugging tools. Production needs fast startup. Both are valid. Maintain both environments separately.

### GitHub Actions Quirks
- Free tier cron is unreliable → design around it
- Concurrency control is subtle → queue vs cancel has implications
- Tags are free state storage → use them
- Manual dispatch is invaluable → always include it

### Iterative Refinement Beats Planning
I didn't architect the perfect system upfront. I (with Claude's help):
1. Made it work (execution.py)
2. Made it maintainable (bot_execution.py)  
3. Made it debuggable (bot_execution_sleep.py)

Each phase solved real problems I discovered in the previous phase.

## Results

**6 months of operation**:
- Success rate: 100% (when slots are available)
- Zero missed bookings due to timing
- Zero duplicate bookings despite parallel runs
- Total time saved: ~50 hours of manual booking attempts
- Sleep quality: Significantly improved 😴

## Future Improvements

1. Being a better pickleball player (highest priority)

---

*Built because I'd rather write code once than refresh a webpage for 6 months.*

**Runtime**: 8-25 seconds from cold start to confirmed booking  
**Success Rate**: 99.9% when slots are available  
**Hours of Sleep Saved**: Countless
**Hours of Coding**: Countless