# AI Coding Tools ROI Calculator

**Last Updated**: {{DATE}}
**Owner**: {{NAME}}
**Version**: {{VERSION}}

---

Purpose: calculate return on investment for AI coding tool adoption. Fill in the input variables, apply the formulas, and use the sensitivity table to stress-test assumptions. Designed to be transferred directly into a spreadsheet.

## How to Use

1. Fill in the **Input Variables** table with your organization's numbers.
2. Walk through the **Calculation Formulas** step by step.
3. Use the **Sensitivity Analysis** to present conservative, moderate, and optimistic scenarios.
4. Determine the **Break-Even** point to set minimum adoption targets.

---

## Input Variables

| Variable | Symbol | Conservative | Moderate | Optimistic | Your Value |
|----------|--------|-------------|----------|------------|------------|
| Number of developers | `N` | {{N}} | {{N}} | {{N}} | {{N}} |
| Average fully-loaded cost ($/year) | `C_dev` | {{150000}} | {{175000}} | {{200000}} | {{VALUE}} |
| Effective hourly cost ($/hour) | `C_hour` | = C_dev / 2080 | = C_dev / 2080 | = C_dev / 2080 | {{VALUE}} |
| AI tool cost per seat ($/month) | `C_seat` | {{19}} | {{19}} | {{19}} | {{VALUE}} |
| Training cost per developer ($, one-time) | `C_train` | {{500}} | {{1000}} | {{1500}} | {{VALUE}} |
| Hours saved per developer per week | `H_saved` | {{2}} | {{4}} | {{6}} | {{VALUE}} |
| Working weeks per year | `W` | 48 | 48 | 48 | {{VALUE}} |
| Quality improvement (% reduction in bug-fix time) | `Q_improve` | {{5%}} | {{10%}} | {{15%}} | {{VALUE}} |
| Annual bug-fix hours per developer | `H_bugfix` | {{200}} | {{200}} | {{200}} | {{VALUE}} |
| Annual developer turnover rate (%) | `R_turnover` | {{15%}} | {{15%}} | {{15%}} | {{VALUE}} |
| Retention improvement (% reduction in turnover) | `R_improve` | {{5%}} | {{10%}} | {{15%}} | {{VALUE}} |
| Replacement cost per developer ($) | `C_replace` | {{75000}} | {{100000}} | {{125000}} | {{VALUE}} |
| Overhead factor (implementation, admin) | `F_overhead` | 15% | 15% | 15% | {{VALUE}} |

---

## Calculation Formulas

Work through these in order. Each formula uses the symbols from the input table.

### Costs

```
Annual tool cost         = N x C_seat x 12
Annual training cost     = N x C_train
Overhead                 = (Annual tool cost + Annual training cost) x F_overhead
Total annual cost        = Annual tool cost + Annual training cost + Overhead
```

| Cost Component | Formula | Your Calculation |
|---------------|---------|-----------------|
| Annual tool cost | {{N}} x {{C_seat}} x 12 | = ${{VALUE}} |
| Annual training cost | {{N}} x {{C_train}} | = ${{VALUE}} |
| Overhead (15%) | (tool + training) x 0.15 | = ${{VALUE}} |
| **Total annual cost** | sum of above | = **${{TOTAL_COST}}** |

### Benefits

```
Time savings value       = N x H_saved x W x C_hour
Quality savings          = N x H_bugfix x Q_improve x C_hour
Retention savings        = N x R_turnover x R_improve x C_replace
Total annual benefit     = Time savings + Quality savings + Retention savings
```

| Benefit Component | Formula | Your Calculation |
|------------------|---------|-----------------|
| Time savings value | {{N}} x {{H_saved}} x {{W}} x {{C_hour}} | = ${{VALUE}} |
| Quality savings | {{N}} x {{H_bugfix}} x {{Q_improve}} x {{C_hour}} | = ${{VALUE}} |
| Retention savings | {{N}} x {{R_turnover}} x {{R_improve}} x {{C_replace}} | = ${{VALUE}} |
| **Total annual benefit** | sum of above | = **${{TOTAL_BENEFIT}}** |

### Returns

```
Net annual benefit       = Total annual benefit - Total annual cost
ROI (%)                  = (Net annual benefit / Total annual cost) x 100
Payback period (months)  = Total annual cost / (Net annual benefit / 12)
```

| Return Metric | Formula | Your Calculation |
|--------------|---------|-----------------|
| Net annual benefit | {{TOTAL_BENEFIT}} - {{TOTAL_COST}} | = ${{NET_BENEFIT}} |
| ROI (%) | ({{NET_BENEFIT}} / {{TOTAL_COST}}) x 100 | = {{ROI}}% |
| Payback period | {{TOTAL_COST}} / ({{NET_BENEFIT}} / 12) | = {{MONTHS}} months |

---

## Sensitivity Analysis

ROI (%) at different adoption rates and time-saved scenarios. Assume all other inputs held constant.

| | 2 hrs/wk saved | 4 hrs/wk saved | 6 hrs/wk saved | 8 hrs/wk saved |
|---|----------------|----------------|----------------|----------------|
| **25% adoption** | {{ROI}}% | {{ROI}}% | {{ROI}}% | {{ROI}}% |
| **50% adoption** | {{ROI}}% | {{ROI}}% | {{ROI}}% | {{ROI}}% |
| **75% adoption** | {{ROI}}% | {{ROI}}% | {{ROI}}% | {{ROI}}% |
| **100% adoption** | {{ROI}}% | {{ROI}}% | {{ROI}}% | {{ROI}}% |

How to calculate each cell:
- Effective developers = N x adoption_rate
- Recalculate Total annual benefit using effective developers
- Costs remain fixed (all seats licensed regardless of adoption)
- ROI = (adjusted_benefit - total_cost) / total_cost x 100

---

## Break-Even Analysis

The minimum adoption rate at which the program pays for itself.

```
Break-even adoption rate = Total annual cost / Max annual benefit (at 100% adoption)
```

| Scenario | Total Cost | Max Benefit (100%) | Break-Even Adoption |
|----------|-----------|-------------------|-------------------|
| Conservative (2 hrs/wk) | ${{VALUE}} | ${{VALUE}} | {{VALUE}}% |
| Moderate (4 hrs/wk) | ${{VALUE}} | ${{VALUE}} | {{VALUE}}% |
| Optimistic (6 hrs/wk) | ${{VALUE}} | ${{VALUE}} | {{VALUE}}% |

**Decision rule**: if current adoption rate > break-even rate at the conservative scenario, the investment is justified.

---

## Assumptions and Caveats

- Hours saved are self-reported unless validated by controlled experiment (see experiment-design-template).
- Quality and retention improvements are harder to attribute; use conservative estimates.
- Training cost is year-one only; subsequent years use a lower refresher cost.
- Overhead factor (15%) covers admin time, integration maintenance, and security review.
- This model does not capture second-order effects (e.g., faster time-to-market revenue impact).

---

## Presentation Tips

- Lead with the moderate scenario; use conservative as the floor.
- Show the sensitivity table to demonstrate range of outcomes.
- Highlight the break-even adoption rate: it shifts the question from "should we invest?" to "can we achieve X% adoption?"
- Pair with survey data (adoption-survey-template) for credibility.
