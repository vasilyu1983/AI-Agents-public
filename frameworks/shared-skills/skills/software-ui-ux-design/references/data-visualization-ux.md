# Data Visualization UX

Comprehensive guide to designing effective, accessible, and interactive data visualizations. Covers chart type selection, dashboard layout patterns, accessibility requirements, interaction design, mobile considerations, and common anti-patterns. Good data viz reduces cognitive load and surfaces insight; bad data viz misleads and confuses.

**Last Updated**: March 2026

---

## Chart Type Selection Guide

Choosing the right chart type is the most consequential data viz decision. Match the chart to the analytical task, not the data shape.

### By Analytical Task

| Task | Recommended Chart | Avoid |
|------|------------------|-------|
| **Compare values** | Bar chart (vertical or horizontal) | Pie chart with many slices |
| **Show trends over time** | Line chart, area chart | Bar chart for continuous time series |
| **Show part-to-whole** | Stacked bar, treemap, pie (max 5 slices) | Donut with > 6 segments |
| **Show distribution** | Histogram, box plot, violin plot | Bar chart with arbitrary bins |
| **Show correlation** | Scatter plot, bubble chart | Dual-axis line chart |
| **Show ranking** | Horizontal bar chart (sorted) | Vertical bar with angled labels |
| **Show geographic patterns** | Choropleth, dot density map | 3D globe for comparison tasks |
| **Show flow/process** | Sankey diagram, funnel chart | Pie chart |
| **Show composition over time** | Stacked area chart, 100% stacked bar | Multiple pie charts |
| **Show deviation** | Diverging bar chart, bullet chart | Line chart without baseline reference |

### Decision Tree

```text
What question are you answering?
  |
  +-- "How much?" (comparison)
  |     +-- Few categories (< 8) --> Bar chart
  |     +-- Many categories (8+) --> Horizontal bar, sorted
  |     +-- Two values per item --> Grouped bar or bullet chart
  |
  +-- "How has it changed?" (trend)
  |     +-- One series --> Line chart
  |     +-- 2-4 series --> Multi-line chart
  |     +-- 5+ series --> Small multiples (sparklines)
  |     +-- Cumulative --> Area chart
  |
  +-- "What is the breakdown?" (composition)
  |     +-- At one point --> Pie (< 5 slices), treemap (5+)
  |     +-- Over time --> Stacked bar or stacked area
  |
  +-- "Is there a relationship?" (correlation)
  |     +-- Two variables --> Scatter plot
  |     +-- Three variables --> Bubble chart (size = 3rd var)
  |     +-- Many variables --> Heatmap or parallel coordinates
  |
  +-- "What is the spread?" (distribution)
        +-- One variable --> Histogram or density plot
        +-- Compare distributions --> Box plot or violin
        +-- Over categories --> Ridgeline plot
```

### Bar Chart Best Practices

| Guideline | Rationale |
|-----------|-----------|
| Always start y-axis at zero | Truncated axes exaggerate differences |
| Sort bars by value (unless categorical order matters) | Easier to compare and rank |
| Use horizontal bars for long labels | Prevents angled or rotated text |
| Limit to 12-15 bars maximum | Beyond this, filter or group |
| Single color unless encoding a variable | Gratuitous color adds noise |

### Line Chart Best Practices

| Guideline | Rationale |
|-----------|-----------|
| Use for continuous data (time series) | Lines imply interpolation between points |
| Limit to 4-5 lines per chart | More lines become unreadable |
| Label lines directly (not just legend) | Reduces eye travel |
| Use consistent time intervals on x-axis | Irregular spacing misleads |
| Highlight the most important line | Use color weight or thickness |

---

## Dashboard Layout Patterns

### Information Hierarchy

Structure dashboards with a clear visual hierarchy: overview first, then details on demand.

```text
DASHBOARD LAYOUT (Z-pattern reading):
+-----------------------------------------------+
|  KPI SUMMARY BAR                              |  <-- Level 1: Key metrics
|  [Metric 1]  [Metric 2]  [Metric 3]  [M4]    |      at a glance
+-----------------------------------------------+
|                           |                    |
|  PRIMARY CHART            |  SECONDARY CHART   |  <-- Level 2: Main
|  (largest area, key       |  (supporting       |      visualizations
|   trend or comparison)    |   context)         |
|                           |                    |
+---------------------------+--------------------+
|                           |                    |
|  DETAIL TABLE / LIST      |  FILTERS /         |  <-- Level 3: Detail
|  (drill-down data)        |  CONTROLS          |      and interaction
|                           |                    |
+---------------------------+--------------------+
```

### KPI Card Design

```html
<!-- KPI summary card -->
<div class="kpi-card" role="group" aria-label="Monthly Revenue">
  <span class="kpi-label">Monthly Revenue</span>
  <span class="kpi-value">$1.24M</span>
  <span class="kpi-trend kpi-trend--positive" aria-label="Up 12% from last month">
    +12%
  </span>
  <span class="kpi-comparison">vs $1.11M last month</span>
</div>
```

```css
.kpi-card {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1.25rem;
  border-radius: 8px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
}
.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
}
.kpi-trend--positive { color: var(--color-success); }
.kpi-trend--negative { color: var(--color-error); }
.kpi-comparison {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}
```

### Card Grid Layout

| Layout Pattern | Best For | Grid Structure |
|---------------|----------|---------------|
| **Equal cards** | Homogeneous metrics | `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` |
| **Featured + supporting** | Primary chart with context | `grid-template-columns: 2fr 1fr` |
| **Full-width rows** | Time series, wide tables | Single column, stacked |
| **Sidebar + main** | Filters alongside charts | `grid-template-columns: 260px 1fr` |

### Responsive Dashboard Strategy

```css
.dashboard-grid {
  display: grid;
  gap: 1rem;
  /* Desktop: 3-column layout */
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 1024px) {
  .dashboard-grid {
    /* Tablet: 2-column layout */
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .dashboard-grid {
    /* Mobile: single column, stacked */
    grid-template-columns: 1fr;
  }
  .kpi-bar {
    /* Horizontal scroll for KPI cards on mobile */
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
  }
  .kpi-card {
    scroll-snap-align: start;
    min-width: 200px;
  }
}
```

---

## Accessible Data Visualization

### Color-Blind Safe Palettes

Approximately 8% of males and 0.5% of females have some form of color vision deficiency. Never rely on color alone to convey information.

| Palette Type | Colors | Use Case |
|-------------|--------|----------|
| **Categorical (qualitative)** | Blue, orange, green, purple, brown, pink | Distinct categories (max 6-8) |
| **Sequential** | Single hue light-to-dark (e.g., light blue to navy) | Ordered values, density |
| **Diverging** | Two hues from a neutral midpoint (e.g., blue-white-red) | Values above/below a reference |
| **Color-blind safe set** | `#0072B2`, `#E69F00`, `#009E73`, `#CC79A7`, `#D55E00`, `#56B4E9`, `#F0E442` | Wong palette -- safe for all CVD types |

| Reinforcement Technique | Implementation |
|------------------------|---------------|
| Pattern fills | Stripes, dots, crosshatch in addition to color |
| Shape encoding | Different marker shapes per series (circle, square, triangle) |
| Direct labeling | Label data points or series directly on the chart |
| Texture and dashing | Dashed, dotted, solid lines for different series |
| Value annotations | Show numeric values on bars or key points |

### ARIA for Charts

```html
<!-- SVG chart with accessibility -->
<figure role="figure" aria-labelledby="chart-title" aria-describedby="chart-desc">
  <figcaption>
    <h3 id="chart-title">Monthly Revenue by Region (2025)</h3>
    <p id="chart-desc">
      Bar chart showing revenue across 4 regions. North leads at $4.2M,
      followed by West at $3.1M, South at $2.8M, and East at $2.4M.
    </p>
  </figcaption>

  <svg role="img" aria-labelledby="chart-title chart-desc"
       viewBox="0 0 600 400">
    <!-- Chart content -->
    <g role="list" aria-label="Revenue by region">
      <g role="listitem">
        <title>North: $4.2M</title>
        <rect x="50" y="80" width="80" height="280" fill="#0072B2" />
        <text x="90" y="70" text-anchor="middle">$4.2M</text>
      </g>
      <!-- Additional bars -->
    </g>
  </svg>
</figure>
```

### Alt Text for Data Visualizations

| Chart Complexity | Alt Text Strategy |
|-----------------|-------------------|
| Simple (1-3 data points) | Summarize all values: "Bar chart: Q1 $2M, Q2 $3.1M, Q3 $2.8M" |
| Moderate (4-10 data points) | State trend and extremes: "Line chart showing upward trend from $1M in Jan to $4.2M in Dec, with a dip in July" |
| Complex (many data points) | Describe pattern and link to data table: "Scatter plot showing positive correlation between ad spend and conversions. See data table below." |

### Data Table Fallback

Always provide a visually hidden (or toggled) data table as an alternative to charts.

```html
<details>
  <summary>View data as table</summary>
  <table>
    <caption>Monthly Revenue by Region (2025)</caption>
    <thead>
      <tr>
        <th scope="col">Region</th>
        <th scope="col">Revenue</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>North</td><td>$4,200,000</td></tr>
      <tr><td>West</td><td>$3,100,000</td></tr>
      <tr><td>South</td><td>$2,800,000</td></tr>
      <tr><td>East</td><td>$2,400,000</td></tr>
    </tbody>
  </table>
</details>
```

---

## Interactive Visualization Patterns

### Tooltips

| Guideline | Implementation |
|-----------|---------------|
| Show on hover (desktop) and tap (mobile) | `mouseenter`/`mouseleave` + `touchstart` |
| Position near the data point, not center of chart | Offset tooltip by 8-12px from cursor |
| Include relevant context (value, label, % of total) | Not just the raw number |
| Keep tooltip concise (2-4 lines max) | Avoid paragraph-length tooltips |
| Dismiss on `Escape` key | Keyboard accessibility |
| Avoid covering the data point being inspected | Flip tooltip position if near edges |

```javascript
// React tooltip pattern (Recharts example)
<Tooltip
  content={({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="chart-tooltip" role="status" aria-live="polite">
        <p className="tooltip-label">{label}</p>
        {payload.map((entry) => (
          <p key={entry.name} style={{ color: entry.color }}>
            {entry.name}: {formatCurrency(entry.value)}
          </p>
        ))}
      </div>
    );
  }}
/>
```

### Drill-Down

```text
DRILL-DOWN HIERARCHY:
  Overview (all regions)
    --> Click region --> Region detail (monthly breakdown)
      --> Click month --> Monthly detail (daily breakdown)
        --> Click day --> Transaction list

NAVIGATION:
  [Breadcrumb: All Regions > North > March 2025]
  [Back button always visible]
  [Animated transition between levels]
```

| Drill-Down Principle | Rationale |
|---------------------|-----------|
| Provide breadcrumb navigation | Users must know where they are and how to go back |
| Animate transitions between levels | Maintain spatial orientation |
| Preserve filter state across levels | Do not reset filters on drill-down |
| Offer "back to overview" shortcut | One-click escape from deep levels |

### Filtering and Time Series Controls

```html
<!-- Filter bar for dashboard -->
<div class="filter-bar" role="toolbar" aria-label="Chart filters">
  <div role="group" aria-label="Time range">
    <button aria-pressed="false">7D</button>
    <button aria-pressed="true">30D</button>
    <button aria-pressed="false">90D</button>
    <button aria-pressed="false">1Y</button>
    <button aria-pressed="false">Custom</button>
  </div>

  <select aria-label="Region filter">
    <option value="all">All Regions</option>
    <option value="north">North</option>
    <option value="south">South</option>
  </select>
</div>
```

| Filter Pattern | Best For |
|---------------|----------|
| Toggle buttons (7D / 30D / 90D) | Predefined time ranges |
| Date range picker | Custom time ranges |
| Multi-select dropdown | Category filtering (regions, products) |
| Search-as-filter | Large category lists (100+ items) |
| Slider | Numeric range (price, quantity) |
| Brush selection on chart axis | Zoom into a sub-range of time series |

### Cross-Filtering

When a dashboard has multiple charts showing related data, clicking a segment in one chart should filter the others.

```javascript
// Cross-filter state management pattern
const [filters, setFilters] = useState({
  region: null,
  timeRange: '30d',
  category: null,
});

// Clicking a bar in the region chart sets the region filter
function onRegionClick(region) {
  setFilters(prev => ({
    ...prev,
    region: prev.region === region ? null : region, // toggle
  }));
}

// All charts consume the same filter state
<RevenueChart data={filteredData} />
<CategoryBreakdown data={filteredData} />
<TransactionTable data={filteredData} />
```

---

## Mobile Data Visualization

### Constraints and Adaptations

| Constraint | Adaptation |
|-----------|------------|
| Small viewport (320-428px) | Simplify charts: fewer data points, larger touch targets |
| No hover state | Replace tooltips with tap-to-reveal or always-visible labels |
| Fat finger accuracy | Minimum 44px tap targets for interactive elements |
| Limited bandwidth | Reduce data resolution, lazy-load charts below the fold |
| Portrait orientation | Stack charts vertically; use full-width single-column |

### Mobile Chart Patterns

| Desktop Pattern | Mobile Alternative |
|----------------|-------------------|
| Multi-series line chart (5+ lines) | Small multiples or series selector dropdown |
| Wide data table | Horizontal scroll with sticky first column |
| Side-by-side charts | Stacked vertically with tab navigation |
| Hover tooltips | Tap to select data point; detail panel below chart |
| Complex dashboard grid | Scrollable card list with KPI summary at top |

```css
/* Responsive chart container */
.chart-container {
  width: 100%;
  aspect-ratio: 16 / 9;
}

@media (max-width: 640px) {
  .chart-container {
    aspect-ratio: 4 / 3; /* Taller on mobile for readability */
  }
  .chart-legend {
    /* Move legend below chart on mobile */
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
}
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| **3D charts** | Distort perception of values; rear bars are occluded | Always use 2D charts |
| **Dual y-axes** | Users conflate unrelated scales; easy to manipulate correlation | Use two separate charts or normalize values |
| **Truncated y-axis** | Exaggerates small differences to appear dramatic | Start bar charts at zero; annotate scale breaks on line charts |
| **Pie chart with > 5 slices** | Small slices become indistinguishable | Use horizontal bar chart instead |
| **Rainbow color palette** | Not perceptually ordered; color-blind hostile | Use sequential or diverging single-hue palettes |
| **Decorative chart junk** | Gridlines, gradients, shadows reduce data-ink ratio | Maximize data-ink ratio (Tufte principle) |
| **Unlabeled axes** | Users cannot interpret values without context | Always label axes with units |
| **Animated transitions without purpose** | Distract from data comprehension | Animate only to show change or draw attention to updates |
| **Auto-refreshing without indication** | Data changes surprise the user | Show "Last updated" timestamp and refresh indicator |
| **Legend far from chart** | Forces eye travel and memorization | Label data directly or place legend adjacent to data |

---

## Tools Reference

| Library | Framework | Strengths | Best For |
|---------|-----------|-----------|----------|
| **D3.js** | Vanilla JS | Full control, bindable to any DOM element, vast ecosystem | Custom visualizations, complex interactions |
| **Observable Plot** | Vanilla JS | Concise API, built on D3, sensible defaults | Exploratory analysis, quick charts |
| **Recharts** | React | Declarative, composable components, good defaults | React dashboards, standard chart types |
| **Victory** | React / React Native | Cross-platform, animation support | React and React Native projects |
| **Chart.js** | Vanilla JS (wrappers for React, Vue) | Simple API, canvas-based (performant for large datasets) | Quick charts, lightweight needs |
| **Visx** | React | Low-level React + D3 primitives, fully customizable | Design-system-integrated charts |
| **Nivo** | React | Rich chart types, built-in theming, server-side rendering | Themed dashboards, SSR requirements |

### D3 Accessibility Pattern

```javascript
// D3: Adding ARIA to an SVG bar chart
const svg = d3.select('#chart')
  .append('svg')
  .attr('role', 'img')
  .attr('aria-labelledby', 'chart-title chart-desc');

svg.append('title').attr('id', 'chart-title').text('Revenue by Region');
svg.append('desc').attr('id', 'chart-desc')
  .text('Bar chart showing North leading at $4.2M, West $3.1M, South $2.8M, East $2.4M');

const bars = svg.selectAll('.bar')
  .data(data)
  .enter()
  .append('g')
  .attr('role', 'listitem');

bars.append('rect')
  .attr('aria-label', d => `${d.region}: ${formatCurrency(d.value)}`);
```

### Recharts Responsive Setup

```jsx
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

function RevenueChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <XAxis dataKey="region" />
        <YAxis tickFormatter={(v) => `$${v / 1e6}M`} />
        <Tooltip formatter={(v) => `$${v.toLocaleString()}`} />
        <Bar dataKey="revenue" fill="var(--color-interactive)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

---

## Data Viz Accessibility Checklist

- [ ] Color is not the only means of conveying information (use shapes, patterns, labels)
- [ ] Palette tested with color-blindness simulators (deuteranopia, protanopia, tritanopia)
- [ ] All chart text meets WCAG 4.5:1 contrast ratio
- [ ] Charts have descriptive alt text or `aria-label` summarizing key insight
- [ ] Data table alternative provided for all charts
- [ ] Interactive elements have minimum 44px touch targets on mobile
- [ ] Tooltips accessible via keyboard (Tab/Enter to activate)
- [ ] Animated transitions respect `prefers-reduced-motion`
- [ ] Axes are labeled with units
- [ ] Legend is proximate to the chart, not separated by whitespace

---

## References

- [Tufte, Edward. The Visual Display of Quantitative Information. Graphics Press, 2001.](https://www.edwardtufte.com/tufte/books_vdqi)
- [Few, Stephen. Information Dashboard Design. Analytics Press, 2013.](https://www.perceptualedge.com)
- [W3C WAI — Accessible Data Visualizations](https://www.w3.org/WAI/WCAG22/Understanding/)
- [Chartability — An Accessibility Framework for Data Viz](https://chartability.github.io/POUR-CAF/)
- [Observable Plot Documentation](https://observablehq.com/plot/)
- [Recharts Documentation](https://recharts.org/)
- [D3.js Documentation](https://d3js.org/)
- [Wong, Bang. "Points of View: Color Blindness." Nature Methods, 2011.](https://www.nature.com/articles/nmeth.1618)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and interaction checklist
- [wcag-accessibility.md](wcag-accessibility.md) — WCAG 2.2 contrast and non-text content requirements
- [dark-mode-theming.md](dark-mode-theming.md) — Theming charts for dark mode
- [mobile-ux-patterns.md](mobile-ux-patterns.md) — Mobile touch targets and responsive patterns
- [design-systems.md](design-systems.md) — Design token integration for chart colors
