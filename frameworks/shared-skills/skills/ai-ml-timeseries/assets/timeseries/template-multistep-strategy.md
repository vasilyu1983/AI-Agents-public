# Multi-Step Forecasting Strategy Template

Use this to declare how a model produces multiple future steps.

```yaml
multistep_strategy:
  strategy: "direct" # direct | recursive | dirrec | seq2seq
  horizon: 28
  known_future_covariates: []
  direct:
    horizons:
      - 1
      - 7
      - 14
      - 28
  recursive:
    refit_each_step: false
  seq2seq:
    encoder_length: 56
    decoder_length: 28
```

Checklist:

- [ ] Strategy aligned with horizon length
- [ ] Error propagation checked
- [ ] Covariates aligned with the forecast range
