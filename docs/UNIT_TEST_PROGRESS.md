# Unit Test Coverage Progress

> **Last updated:** 2026-07-25  
> **How to run:** `python3 -m pytest` (in repo root)  
> **How to regenerate this data:** `python3 -m pytest --no-header 2>&1 | grep -E "^src/" | grep -v "100%"`

---

## Current Status

| Metric | Value |
|--------|-------|
| **Total coverage** | **96.04%** |
| **Tests** | 1614 passed, 22 skipped |
| **Source files tracked** | 130 |
| **Files at 100%** | 102 |
| **Files with gaps** | 28 |
| **Target** | 100% |

> Previous sessions documented 52% — that was out-of-date. Actual coverage as of this writing is **96%**.

---

## Files With Gaps (sorted by impact — largest gap first)

Use this table to pick up work in a new session. Check off items as they reach 100%.

### High Priority (large statement gaps)

- [ ] **`src/form/util.py`** — 72% (246 missing stmts)  
  Missing lines: `207-208, 215-216, 303, 309, 457, 466, 497, 601, 747-748, 885-888, 904, 976, 994-997, 1151, 1169, 1188, 1238-1245, 1250, 1305-1376, 1400-1497, 1501-1609, 1626-1685, 1703-1754, 1758-1767, 1782-1839, 1859-1918, 2008, 2021-2030, 2036, 2039, 2042, 2054-2078, 2081, 2088, 2129, 2132-2150, 2152, 2192, 2206-2224`

- [ ] **`src/scouting/admin/util.py`** — 73% (102 missing stmts)  
  Missing lines: `111, 117-125, 173, 229-240, 391-392, 434-435, 469, 520, 534-539, 573-576, 591-597, 692, 696, 702, 707-708, 715-716, 723-724, 767-848, 871`

- [ ] **`src/tba/util.py`** — 79% (38 missing stmts)  
  Missing lines: `254-256, 263-264, 290-291, 368-390, 450-463, 517-521`

- [ ] **`src/alerts/util.py`** — 87% (14 missing stmts)  
  Missing lines: `136, 286, 304-318`

- [ ] **`src/scouting/field/util.py`** — 83% (24 missing stmts)  
  Missing lines: `88-94, 222-228, 252-264, 281, 407, 449-450, 452-453, 455-456`

- [ ] **`src/scouting/strategizing/util.py`** — 85% (24 missing stmts)  
  Missing lines: `51, 127, 155, 179, 188, 195-196, 343-358, 462, 467, 480, 514`

- [ ] **`src/user/util.py`** — 85% (24 missing stmts)  
  Missing lines: `124, 307, 384-388, 401-409, 421, 439-457`

- [ ] **`src/alerts/views.py`** — 82% (13 missing stmts)  
  Missing lines: `167-174, 192-206`

- [ ] **`src/user/views.py`** — 94% (30 missing stmts)  
  Missing lines: `256, 388-393, 396-401, 419, 648, 1217-1226, 1260-1266, 1284-1298`

- [ ] **`src/scouting/admin/views.py`** — 91% (28 missing stmts)  
  Missing lines: `357-364, 398-405, 458-469, 497-508, 534, 537, 568-569, 602, 635-636, 732-733, 749`

### Medium Priority (10–20 missing stmts)

- [ ] **`src/alerts/util_alert_definitions.py`** — 97% (7 missing stmts)  
  Missing lines: `663-667, 670, 679-682`

- [ ] **`src/scouting/strategizing/views.py`** — 93% (10 missing stmts)  
  Missing lines: `70-85, 145-154`

- [ ] **`src/scouting/field/views.py`** — 95% (4 missing stmts)  
  Missing lines: `188-192`

### Low Priority (≤5 missing stmts — easy wins)

- [ ] **`src/admin/views.py`** — 96% (4 missing stmts)  
  Missing lines: `259-262`

- [ ] **`src/attendance/util.py`** — 98% (3 missing stmts)  
  Missing lines: `163, 289-297`

- [ ] **`src/attendance/views.py`** — 97% (2 missing stmts)  
  Missing lines: `84-85`

- [ ] **`src/form/views.py`** — 99% (1 missing stmt)  
  Missing line: `200`

- [ ] **`src/general/cloudinary.py`** — 93% (1 missing stmt)  
  Missing line: `47`

- [ ] **`src/public/competition/views.py`** — 89% (2 missing stmts)  
  Missing lines: `26-27`

- [ ] **`src/scouting/admin.py`** — 0% (1 missing stmt)  
  Missing line: `1`

- [ ] **`src/scouting/field/serializers.py`** — 96% (1 missing stmt)  
  Missing line: `20`

- [ ] **`src/scouting/models.py`** — 99% (4 missing stmts)  
  Missing lines: `231, 279, 291, 303`

- [ ] **`src/scouting/pit/views.py`** — 98% (1 missing stmt)  
  Missing line: `63`

- [ ] **`src/scouting/serializers.py`** — 99% (1 missing stmt)  
  Missing line: `108`

- [ ] **`src/scouting/util.py`** — 99% (2 missing stmts)  
  Missing lines: `620, 628`

- [ ] **`src/scouting/views.py`** — 98% (2 missing stmts)  
  Missing lines: `216-217`

- [ ] **`src/sponsoring/views.py`** — 99% (1 missing stmt)  
  Missing line: `80`

- [ ] **`src/tba/util.py`** — see High Priority above

- [ ] **`src/user/models.py`** — 99% (1 missing stmt)  
  Missing line: `128`

- [ ] **`src/user/views.py`** — see High Priority above (duplicate listed once above)

---

## Session History

| Date | Session Goal | Outcome | Coverage |
|------|-------------|---------|----------|
| 2026-07-25 | Discover actual state, create progress doc | Created this doc; coverage confirmed at 96% | 96.04% |

---

## Recommended Session Workflow

Each new agent session should:

1. **Update coverage numbers** by running:  
   ```bash
   python3 -m pytest --no-header 2>&1 | grep -E "TOTAL|^src/" | grep -v "100%"
   ```

2. **Pick a target** — start with high-priority files (largest gaps).

3. **Inspect the uncovered lines** before writing tests:  
   ```bash
   # Example: view what's on line 1305-1376 of form/util.py
   sed -n '1305,1376p' src/form/util.py
   ```

4. **Add tests** to the appropriate file in `tests/<app>/`.

5. **Verify improvement**:  
   ```bash
   python3 -m pytest tests/<app>/ --no-header 2>&1 | grep "^src/<app>/"
   ```

6. **Update this document**: check off completed items and update the Session History table.

---

## Quick Reference: Test File Locations

| Source module | Test file(s) |
|--------------|-------------|
| `src/form/util.py` | `tests/form/test_form_util_*.py` |
| `src/scouting/admin/util.py` | `tests/scouting/test_scouting_admin_*.py` |
| `src/tba/util.py` | `tests/tba/test_tba_util_*.py` |
| `src/alerts/util.py` | `tests/alerts/test_alerts_*.py` |
| `src/scouting/field/util.py` | `tests/scouting/test_scouting_field_*.py` |
| `src/scouting/strategizing/util.py` | `tests/scouting/test_strategizing_*.py` |
| `src/user/util.py` | `tests/user/test_user_util_*.py` |
| `src/alerts/views.py` | `tests/alerts/test_alerts_*.py` |
| `src/user/views.py` | `tests/user/test_user_views_*.py` |
| `src/scouting/admin/views.py` | `tests/scouting/test_scouting_admin_*.py` |

---

## How to Reach 100%

The remaining 4% (~761 statements) breaks down roughly as:

- **`src/form/util.py`** alone accounts for ~246 stmts (32% of the gap)
- **`src/scouting/admin/util.py`** ~102 stmts (13% of gap)
- **`src/tba/util.py`** ~38 stmts (5% of gap)
- All remaining files combined ~375 stmts (50% of gap)

**Suggested session order:**
1. Easy wins first: knock out all "Low Priority" files in one session (~20 missing stmts total, mostly 1-2 lines each)
2. `src/tba/util.py` — focused session
3. `src/alerts/util.py` + `src/alerts/views.py` — related, do together
4. `src/user/util.py` + `src/user/views.py` — related
5. `src/scouting/strategizing/util.py` + views
6. `src/scouting/field/util.py` + views
7. `src/scouting/admin/util.py` + views — hardest, largest
8. `src/form/util.py` — largest file, needs multiple sessions
