# Calendar Feature Template

Standardized calendar & event features for time series.

---

## 1. Calendar Features

calendar:
day_of_week: true
day_of_month: true
week_of_year: true
month: true
quarter: true
is_weekend: true

---

## 2. Holiday/Event Features

events:
holiday_calendar: "<country_or_custom>"
special_days:

- "black_friday"
- "cyber_monday"
- "end_of_quarter"

---

## 3. Weather (Optional)

weather:
include: true
lag_hours: 24
variables:

- temperature
- precipitation
- humidity

---

## 4. Checklist

- [ ] Timezone aligned  
- [ ] Event features region-specific  
- [ ] Weather features lagged (no leakage)  
