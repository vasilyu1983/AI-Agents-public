# Device Matrix

## Tier Definitions

- **Tier 1**: Top 70-80% of user traffic. Must pass before release. Run in CI on every PR.
- **Tier 2**: Next 15-20% of traffic. Run before major releases. Manual or nightly CI.
- **Tier 3**: Long tail devices. Exploratory testing only. Monitor crash reports.

## Selection Criteria

Use analytics to identify top devices by:

- Active users per device model
- OS version distribution
- Screen size / resolution clusters
- Market-specific devices (regional variants)

## Example Matrix

Replace examples with your actual analytics (device model, OS distribution, and regional mix).

| Platform | Device | OS Version | Tier | Notes |
| --- | --- | --- | --- | --- |
| iOS | Latest Pro iPhone | Latest iOS | 1 | Default simulator target for PR smoke |
| iOS | Popular iPhone (N-1) | Latest iOS | 1 | High-volume "normal" screen |
| iOS | Small iPhone (SE/mini) | Latest iOS | 2 | Small screen edge cases |
| iOS | iPad (if supported) | Latest iPadOS | 2 | Tablet layout testing |
| Android | Pixel (latest) | Latest Android | 1 | Reference device |
| Android | Samsung Galaxy S-series | Latest Android | 1 | Top OEM skin |
| Android | Samsung Galaxy A-series | Latest Android | 1 | Mid-range high volume |
| Android | OEM skin variant (Xiaomi/OnePlus/etc.) | Latest-1 Android | 2 | OEM skin variations |
| Android | Budget/low-end device | Latest-1 Android | 2 | Performance constraints |
| Android | Tablet (if supported) | Latest Android | 2 | Tablet layout testing |

## OS Version Coverage

| Platform | Min Supported | Target | Notes |
| --- | --- | --- | --- |
| iOS | N-2 (typical) | N | Decide based on App Store distribution + product policy |
| Android | N-4 (typical) | N | Decide based on Play distribution, OEM mix, and app constraints |

## Update Cadence

- Review matrix quarterly or after major OS releases.
- Update Tier 1 when analytics show traffic shifts.
- Archive devices dropping below 1% traffic.
