# Lag & Rolling Feature Template

Define lag and window-based features for forecasting.

---

## 1. Lag Features

lags:
1
7
14
28

(Optional)
hourly_lags:
1
24
48

---

## 2. Rolling Windows

rolling:
windows:

- 7
- 14
- 30
metrics:
- mean
- std
- min
- max
- sum

---

## 3. Target Leakage Checks

- [ ] Lags only reference past timestamps  
- [ ] Rolling windows computed on historical data  
- [ ] Seasonal lags added when needed
