# WQ Brain — Alpha Database

Three files make up the alpha research database:

| File | Format | Purpose |
|------|--------|---------|
| `fields_tracker.csv` | CSV | All 1,731 WQ Brain fields with status and notes |
| `results.csv` | CSV | All 164 tested alphas with sharpe/fitness/corr/score |
| `wq_alpha.db` | SQLite | Same data queryable via SQL — useful views included |

## SQLite Views

```sql
-- Submitted and submittable alphas
SELECT * FROM submittable;

-- All untested mdl177 model fields
SELECT * FROM v_untested_fields WHERE field LIKE 'mdl177%';

-- Dead fields — do not retest
SELECT * FROM v_dead_fields;

-- Fields flagged for testing soon
SELECT * FROM v_test_soon;
```

## Quick Query Examples

```bash
# Open DB
sqlite3 wq_alpha.db

# Find untested fangma siblings
SELECT field FROM v_untested_fields WHERE field LIKE 'mdl177_fangma%';

# Best submitted alphas by sharpe
SELECT alpha_id, name, sharpe, fitness, max_corr FROM submittable ORDER BY sharpe DESC;

# All rejected alphas and why
SELECT alpha_id, name, rejection_reason FROM results WHERE alpha_status = '❌ Rejected';
```

## Updating

After each batch run, export from `WQ_Brain_Tracker_Session_XX.xlsx`:
- Results tab → `results.csv`
- Fields Tracker tab → `fields_tracker.csv`

Then rebuild the DB:
```bash
python3 scripts/rebuild_db.py
```
