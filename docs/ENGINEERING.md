# Engineering Notes

The v3 trend layer uses ordinary least-squares regression and EWMA because they are deterministic, inspectable and appropriate as short-history operational heuristics. If a historical baseline has zero variance, a matching sample returns z=0 while a departure returns positive/negative infinity so abrupt changes are not hidden.

SLO error budgets are based on good/bad service events rather than CPU or memory. This is an intentional reliability-engineering distinction.

Fleet aggregation accepts plain snapshot mappings and tolerates hosts with different sensor sets. The HTML report has no external JavaScript/CSS dependency, generates inline SVG sparklines and escapes text.
