# MUI Integration Notes

Durable rules for building on MUI (Material UI). Library selection lives in [software-ui-ux-design/references/component-library-comparison.md](../../software-ui-ux-design/references/component-library-comparison.md). MUI's APIs move between majors, so copy code only from the docs at [mui.com](https://mui.com/) for the major you install, and check `npm view @mui/material version` before scaffolding.

## Setup

- Install `@mui/material` with its styling-engine peers (`@emotion/react`, `@emotion/styled` by default); a missing peer fails at runtime, not at install.
- Icons (`@mui/icons-material`) are a separate package; import per icon path or rely on verified tree-shaking so the whole icon set does not ship.
- For server-rendered React (Next.js App Router and similar), follow MUI's framework integration guide (the `@mui/material-nextjs` package and its cache provider) so styles are emitted on the server and do not flash or mismatch on hydration.
- Load the brand font yourself (self-hosted or the framework's font loader) and set it in the theme's `typography.fontFamily`; MUI does not load fonts.

## Theme as the Single Token Source

- `createTheme` is the one place for palette, typography, spacing, breakpoints, shape and component default overrides. Map design tokens into it; do not scatter hex values or pixel sizes through components.
- Use `theme.spacing()` and the `sx` prop's spacing shorthand instead of raw px, and breakpoint objects (`{ xs: …, md: … }`) instead of hand-written media queries.
- Put recurring component tweaks in `theme.components.<Name>.styleOverrides` / `defaultProps`, not in per-instance `sx`.
- Handle dark mode through the theme's colour-scheme and CSS-variable support for your installed major (it avoids a flash of the wrong scheme on SSR). Test both schemes for contrast; Material's default palettes do not guarantee AA for every custom brand colour.

## Components

- `IconButton` and any icon-only control need an `aria-label`; `Dialog` needs `aria-labelledby` (and `aria-describedby` when there is body text). Test them with the ARIA contract tests in [software-accessibility/references/remediation-playbook.md](../../software-accessibility/references/remediation-playbook.md).
- The Grid component's import path and responsive-prop API changed between majors; use `Stack` for one-dimensional layout and copy Grid examples only from the docs for your installed version.
- MUI X (Data Grid, Date and Time Pickers, Charts, Tree View) has a free community tier plus commercially licensed tiers. Check the MUI X licensing page before you depend on a feature, and treat a licence-key warning as a release blocker.
- Date pickers need an explicit date-adapter library and a `LocalizationProvider`; pick the adapter the app already uses.
- With React Hook Form, wrap MUI inputs in `Controller` (they are controlled components) and pass `error` and `helperText` from the field state so errors reach assistive tech.

## Performance

- Measure the route payload with and without MUI X widgets; lazy-load grids, charts and pickers on routes that need them.
- Heavy per-render `sx` objects on long lists cost style recalculation; hoist static styles into `styled()` components or theme overrides.

## Migration

Use the official migration guide and codemods for each major (`npx @mui/codemod …`). Upgrade one major at a time and re-run visual and accessibility checks; theme structure and component props have changed across majors before.
