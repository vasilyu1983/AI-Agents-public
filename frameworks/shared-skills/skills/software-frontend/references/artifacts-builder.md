# Single-File HTML Bundle Playbook - React + Tailwind + shadcn/ui

Use this when you need to share a runnable UI prototype as a single `bundle.html` (offline-friendly), while keeping React state/routing and accessible components.

## Quick Start
1) Scaffold: `npm create vite@latest my-bundle -- --template react-ts`  
2) Use the Vite + React template as a baseline: [../assets/vite-react/template-vite-react-ts.md](../assets/vite-react/template-vite-react-ts.md)  
3) Produce a single-file build:
   - Prefer a single-file bundling approach (for example, `vite-plugin-singlefile`) when a single HTML file is a hard constraint.
   - Ensure code-splitting is disabled; otherwise `dist/index.html` will reference additional chunk files.
4) Share: ship `bundle.html` with no external asset dependencies.

## Design Guardrails
- Avoid generic template styling: default purple gradients, over-rounded corners, centered-everything layouts, and mismatched typography.  
- Use purposeful palettes, strong hierarchy, and cohesive typography.  
- Leverage shadcn/ui components already installed; keep accessibility intact.

## Tips
- Keep the bundle self-contained (no external fonts, images, or CDN scripts) unless explicitly allowed.
- Run the shared checklist before sharing: [../../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md](../../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md)
- Use a supported Node.js LTS for tooling stability: https://nodejs.org/en/about/previous-releases

## Optional: AI/Automation

If the bundle is generated for an LLM \"artifact\" environment, treat it as a constrained delivery target:
- Keep file size small; avoid large embedded assets unless required.
- Avoid network calls by default; make URLs explicit and configurable.
- Never embed secrets or tokens in the HTML.
