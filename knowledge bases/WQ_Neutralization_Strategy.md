# Neutralization Strategy Guide by Data Category

This guide tells Gemini which neutralization setting to use for each data category.
Sourced from WorldQuant seminars, jglazar/notes, and empirical testing.

## Rules by Category

### Price Volume
- **Neutralize by: MARKET or NONE**
- Price volume ideas work for all instruments — do NOT neutralize by industry or subindustry
- No neutralization is extremely strong for price reversion (you can long/short the whole market)
- Neutralizing by MARKET instead of SUBINDUSTRY can reduce Sharpe but greatly increases fitness
- For mean reversion alphas specifically, try NONE first

### Fundamental
- **Neutralize by: INDUSTRY**
- Fundamentals affect price differently in different industries
- Compare companies to industry peers, not the whole market
- Examples: sales/assets, debt/equity, inventory_turnover, retained_earnings

### Analyst / Estimates
- **Neutralize by: INDUSTRY**
- Analyst data estimates future fundamental data
- Consensus estimates are most meaningful within the same industry
- Examples: est_eps, mdf_pec, mdf_eg3, fam_est_eps_rank

### Model (mdf_*, mdl_*, fam_*)
- **Neutralize by: varies — experiment with SECTOR and INDUSTRY**
- Model datasets vary wildly with subcategory
- Start with SECTOR, then try INDUSTRY
- For model scores that are already cross-sectional (like fam_roe_rank), SUBINDUSTRY works

### News
- **Neutralize by: SUBINDUSTRY**
- News impacts companies differently based on their subindustry
- High-count news = momentum signal, low-count = reversion signal
- Use ts_rank or ts_decay to smooth high turnover from news data

### Social Media / Sentiment
- **Neutralize by: SUBINDUSTRY or INDUSTRY**
- Social media impact is company-dependent
- Sentiment scores (snt_*, scl12_*) should be neutralized granularly
- Volume-weighted sentiment is more robust than raw sentiment

### Options
- **Neutralize by: MARKET or SECTOR**
- Options have consistent impact across industries
- Put-call ratio, implied volatility work at a broad level
- Don't over-neutralize — market-level captures the signal best

### Short Interest
- **Neutralize by: INDUSTRY**
- Short interest is relative to sector norms
- Experiment with SUBINDUSTRY as well

### Insider / Institutional
- **Neutralize by: SECTOR or INDUSTRY**
- Institution data depends on type and provider
- Insider news is company-dependent — try INDUSTRY or SUBINDUSTRY

### Earnings
- **Neutralize by: INDUSTRY**
- Earnings is like fundamentals — compare within industry
- Earnings surprise signals work best with MARKET neutralization
- Post-earnings drift: momentum for 2 days, then reversal for 5 days

### Credit Risk
- **Neutralize by: SECTOR**
- Credit risk varies by sector (financial vs. tech vs. energy)
- Rating probabilities are meaningful within the same sector

### Macro / Sector / Industry data
- **Neutralize by: MARKET**
- These are already macro-level signals
- Don't neutralize by subindustry — it removes the signal

## General Tips

1. **Smaller universe (TOP200) + broader neutralization (MARKET)** = lower turnover
2. **Larger universe (TOP3000) + tighter neutralization (SUBINDUSTRY)** = more signal but higher turnover
3. When in doubt, test SUBINDUSTRY first (it's the WQ default) then try INDUSTRY and MARKET
4. `group_neutralize(alpha, group)` can be used inside expressions for fine-grained control
5. No neutralization is sometimes the best choice for pure price reversion
6. Fitness problems (turnover too high) can often be fixed by switching from SUBINDUSTRY to MARKET

## Neutralization + Universe Combinations That Work

| Category | TOP3000 | TOP200 |
|----------|---------|--------|
| Price Volume | MARKET or NONE | MARKET or NONE |
| Fundamental | INDUSTRY | SUBINDUSTRY |
| Analyst | INDUSTRY | SUBINDUSTRY |
| Model | SECTOR | INDUSTRY |
| Sentiment | SUBINDUSTRY | INDUSTRY |
| Options | MARKET | MARKET |
| Credit Risk | SECTOR | SECTOR |
