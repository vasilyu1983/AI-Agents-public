# Completed synthetic measurement audit

All data below are invented for illustrating the audit; they are not a study result.

**Interpretation:** a benchmark score estimates the ability of an agent system to complete bounded spreadsheet tasks under configuration v1. **Use:** compare two configurations locally; no claim about unrestricted autonomy. **Population:** the task family represented by 40 synthetic tasks. **Instrument:** task set v1, execution scaffold v1, and rubric v1 with exact checks and human review.

**Observation:** configuration A passes 30/40 tasks; B passes 32/40. These are sample proportions, not proof that B is better in the target population. Both use the same tools and budget. The task set covers formulas and formatting but omits macros and corrupted inputs. Human review has no independent second rating.

**Validity:** conditional for bounded formula/formatting completion; insufficient for general spreadsheet competence. **Reliability:** unknown across fresh runs, task samples, and raters. **Scale:** pass fractions permit comparisons within this instrument; a score of 0.8 does not imply twice the underlying capability of 0.4. **Error:** task sampling, nondeterministic runs, and scorer disagreements remain unquantified. **Calibration:** scorer agreement with adjudicated outcomes has not been measured. **Comparability:** no configuration or instrument changes within the sample; future versions require an overlap/anchor study.

**Verdict:** conditional descriptive comparison for v1 tasks; insufficient for a population superiority claim. Next evidence: repeated paired runs on held-out representative tasks, blinded independent scoring with adjudication, and reporting sampling/run uncertainty through statistical inference. No numerical superiority threshold is invented.
