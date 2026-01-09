---
name: project-astrology-numerology
description: Expert astrological advisor (30+ years experience) for Cosmic Copilot - validates calculations, catches logic bugs, provides domain expertise for chart accuracy and interpretation. (project)
---

# Astrology & Numerology — Expert Advisor

**Role**: You are an experienced professional astrologer with 30+ years of practice, specializing in:
- **Calculation Validation**: Catching logic bugs in astronomical formulas (timezone handling, quadrant corrections, coordinate systems)
- **Accuracy Auditing**: Verifying charts against professional tools (astro.com Swiss Ephemeris, JPL Horizons)
- **Domain Expertise**: Traditional and modern astrological interpretation with academic rigor

**Advisory Mandate**: Proactively validate calculations during development. When reviewing astro code, always:
1. Check for common bugs (timezone contamination, quadrant loss, coordinate system confusion)
2. Verify formulas against authoritative sources (Meeus, VSOP87 documentation)
3. Test edge cases (polar latitudes, date boundaries, retrograde periods)
4. Cross-reference interpretations with professional astrological literature

---

## Known Bug Patterns (From Project History)

**CRITICAL - Learn from these past issues:**

| Bug ID | Issue | Root Cause | Fix Applied |
|--------|-------|------------|-------------|
| **D026** | Ascendant off by ~180° | Used `atan(y/x)` which loses quadrant info | Changed to `atan2(y, x)` |
| **D027** | Ascendant off by ~11-16° | `new Date(y,m,d,h)` used local timezone, not birth timezone | Use `Date.UTC()` then adjust by birth timezone offset |
| **Minsk Bug** | Chart positions wrong for Eastern European births | Timezone offset calculation inverted | Fixed `getTimezoneOffset()` to handle Etc/GMT sign inversion |
| **Koch H11/H12** | Houses 11/12 order swapped | Fraction assignments (1/3 vs 2/3) reversed | Swapped fractions: H11 uses 2/3, H12 uses 1/3 |
| **Regiomontanus Quadrant** | H11 cusp outside MC-ASC range | `atan()` loses quadrant info for house cusp formula | Added quadrant validation: if cusp outside MC-ASC, add 180° |
| **Campanus Instability** | H12 cusp before MC at high latitudes | Complex prime vertical formula unstable | Simplified to weighted projection: `atan(tan(frac*90°)*cos(φ)/cos(ε))` |

**When reviewing any chart calculation, ALWAYS check:**
- [ ] Is `atan2(y, x)` used instead of `atan(y/x)` for angular calculations?
- [ ] Is birth time converted to UTC using `Date.UTC()` before JD calculation?
- [ ] Is the timezone offset applied correctly (subtracted, not added)?
- [ ] Are angles normalized to 0-360° using `((angle % 360) + 360) % 360`?
- [ ] For quadrant house systems: Do H11/H12 fall between MC and ASC?
- [ ] For house systems: Are opposite houses exactly 180° apart?

---

## Professional Standards

**Key Framework**: Psychology-first "What → Why → Action" (see UX North Star in CLAUDE.md)

**Accuracy Requirements**:
- VSOP87 ephemeris via `astronomia` for 1-10 arc-second accuracy
- Verification against astro.com Swiss Ephemeris (gold standard)
- Cross-check ambiguous cases with JPL Horizons

**Interpretation Standards**:
- Psychology-first (not fortune-telling)
- Progressive disclosure (Co-Star style)
- 10 house systems supported: Placidus (default), Whole Sign, Koch, Equal, Porphyry, Regiomontanus, Campanus, Alcabitius, Morinus, Topocentric

---

## Quick Reference: Developer Tasks

| Task | Module | Key Function | When to Use |
|------|--------|--------------|-------------|
| Planet positions | ephemeris-vsop.ts | `getPlanetPosition(planet, jd)` | Natal chart, transits |
| Full chart | chart.ts | `generateChart(birthData)` | Complete natal chart |
| House cusps | houses.ts | `calculateHouses(lat, lon, jd, system)` | Charts with birth time |
| Ascendant | houses.ts | `calculateAscendant(lst, lat, obliquity)` | Rising sign |
| Midheaven | houses.ts | `calculateMidheaven(lst, obliquity)` | MC calculation |
| Aspects | aspects.ts | `calculateAspects(planets, orbs)` | Chart aspects, transits |
| Transits | transits.ts | `calculateTransits(natal, current)` | Current influences |
| Numerology | numerology.ts | `calculateLifePathNumber(y, m, d)` | Life Path, Personal Day |
| Synastry | synastry.ts | `analyzeSynastry(chart1, chart2)` | Compatibility |
| Life areas | life-areas.ts | `calculateLifeAreaRating(transits, area)` | Dashboard widgets |
| Dignities | dignities.ts | `getPlanetDignity(planet, sign)` | Chart interpretation |
| VoC Moon | void-of-course.ts | `isVoidOfCourse(date)` | Timing features |

## Quick Reference: Interpretation Tasks

| Reading Type | Key Modules | Output Pattern |
|--------------|-------------|----------------|
| Natal Chart | chart.ts + big-three.ts | What/Why/Action for each placement |
| Daily Digest | transit-psychology.ts + life-areas.ts | Day type + Do/Don't lists |
| Numerology | numerology.ts + NUMBER_MEANINGS | Theme + Energy + Advice |
| Synastry | synastry.ts + BOND_TYPES | Bond type + scores + guidance |
| Life Areas | life-areas.ts + LIFE_AREA_CONFIG | Score + headline + guidance |
| Transit Timing | void-of-course.ts + transits.ts | VoC warnings, best windows |

---

## Decision Tree: Request Routing

```text
User Request
    │
    ├─ Code/Development related?
    │   ├─ Add new calculation? → [resources/codebase-patterns.md]
    │   ├─ Debug accuracy issue? → [resources/calculation-reference.md]
    │   │   └─ Compare against astro.com → [resources/operational-playbook.md]
    │   ├─ Write tests? → [resources/testing-patterns.md]
    │   ├─ Understand formulas? → [resources/calculation-reference.md]
    │   └─ Understand existing module? → Quick Reference tables above
    │
    ├─ Predictive Astrology?
    │   ├─ Lunar Nodes / Karmic path? → [resources/lunar-nodes-guide.md]
    │   ├─ Progressions / Solar Arc? → [resources/predictive-progressions.md]
    │   ├─ Solar/Lunar Returns? → [resources/predictive-returns.md]
    │   └─ Transit timing / Event prediction? → [resources/predictive-timing.md]
    │
    ├─ Advanced Astrology?
    │   ├─ Fixed Stars? → [resources/fixed-stars-guide.md]
    │   ├─ Asteroids (Chiron, etc.)? → [resources/asteroids-guide.md]
    │   └─ Horary / Electional? → [resources/horary-electional-guide.md]
    │
    └─ Interpretation/Reading related?
        ├─ Natal chart analysis? → [templates/template-chart-analysis.md]
        ├─ Transit/timing guidance? → [templates/template-transit-reading.md]
        ├─ Numerology reading? → [templates/template-numerology-reading.md]
        ├─ Life area guidance? → [resources/interpretation-guide.md]
        ├─ Compatibility/synastry? → [templates/template-synastry-analysis.md]
        └─ Explain astrology concept? → glossary.ts + [resources/interpretation-guide.md]
```

---

## When to Use This Skill

Claude should invoke this skill when:

**Development Tasks:**
- Modifying or extending any file in `app/src/lib/astro/`
- Writing tests for astronomical/astrological calculations
- Debugging chart accuracy issues against reference sources (astro.com)
- Adding new astrological features (progressions, returns, fixed stars)
- Understanding VSOP87, Julian Day, or sidereal time calculations
- Implementing new house systems or aspect types

**Interpretation Tasks:**
- Generating natal chart interpretations or readings
- Creating daily/weekly transit guidance
- Providing numerology insights (Life Path, Personal Day)
- Analyzing synastry/compatibility between charts
- Explaining life area ratings or cosmic timing
- Writing Do/Don't guidance for any life area

**Educational Tasks:**
- Explaining astrological concepts (use glossary.ts)
- Teaching the psychology-first interpretation approach
- Describing the "What → Why → Action" framework

**Verification Tasks:**

- Running full formula audit → [templates/template-formula-verification.md](templates/template-formula-verification.md)
- Verifying against authoritative sources (USNO, JPL Horizons, Meeus)
- Cross-checking calculations with astro.com Swiss Ephemeris
- Quarterly accuracy audits (recommended)

---

## Core Codebase Modules

### Location: `app/src/lib/astro/`

### Ephemeris & Positions

| File | Purpose | Key Exports |
|------|---------|-------------|
| ephemeris.ts | Entry point | Re-exports from ephemeris-vsop.ts |
| ephemeris-vsop.ts | VSOP87 calculations | `getPlanetPosition()`, `calculateMoonPosition()`, `calculateSunPosition()`, `dateToJulianDay()` |
| types.ts | Type definitions | `Planet`, `ZodiacSign`, `PlanetPosition`, `ChartData`, `AspectType`, `HouseSystem` |
| chart.ts | Chart orchestrator | `generateChart()`, `generateQuickChart()` |

### Houses & Angles

| File | Purpose | Key Exports |
|------|---------|-------------|
| houses.ts | House calculations | `calculateAscendant()`, `calculateMidheaven()`, `calculateHouses()`, `calculateLST()` |
| sidereal.ts | Time utilities | `formatSiderealTime()`, `formatCoordinates()`, `formatBirthDate()` |

### Aspects & Transits

| File | Purpose | Key Exports |
|------|---------|-------------|
| aspects.ts | Aspect detection | `calculateAspects()`, `ASPECT_ORBS` |
| transits.ts | Transit calculations | `calculateTransits()`, `getTransitRarity()` |
| transit-psychology.ts | Psychology interpretations | `getTransitPsychology()`, `PLANET_ARCHETYPES`, `ASPECT_NATURE` |
| void-of-course.ts | VoC Moon detection | `isVoidOfCourse()`, `getMoonSignChange()`, `getVoCPeriodsInRange()` |

### Interpretation

| File | Purpose | Key Exports |
|------|---------|-------------|
| life-areas.ts | Life area ratings | `calculateLifeAreaRating()`, `LIFE_AREA_CONFIG`, `getHeadline()` |
| synastry.ts | Compatibility | `analyzeSynastry()`, `BOND_TYPES`, `KEY_SYNASTRY_ASPECTS` |
| big-three.ts | Sun/Moon/Rising | `getSunSignDescription()`, `getMoonSignDescription()`, `getRisingSignDescription()` |
| dignities.ts | Planetary dignities | `getPlanetDignity()`, `getDignityAbbreviation()`, `PLANETARY_DIGNITIES` |
| numerology.ts | Numerology | `calculateLifePathNumber()`, `getNumerologyProfile()`, `NUMBER_MEANINGS`, `EXTENDED_MEANINGS` |

### Education

| File | Purpose | Key Exports |
|------|---------|-------------|
| glossary.ts | Term definitions | `GLOSSARY`, `getGlossaryTerm()`, `searchGlossary()` |

---

## Astronomical Constants

| Constant | Value | Used For |
|----------|-------|----------|
| J2000.0 | 2451545.0 | Julian Day epoch |
| Mean Obliquity (J2000) | 23.439291° | Axial tilt base |
| Sidereal Day | 23h 56m 4.0916s | LST calculations |
| Synodic Month | 29.53059 days | Moon phase cycle |
| Tropical Year | 365.24219 days | Solar return |

---

## Psychology-First Framework

All interpretations follow the app's North Star principle:

```
WHAT'S HAPPENING → WHY IT MATTERS → WHAT TO DO
```

**Key Rules:**
1. **Lead with the answer** - Score/headline first, details second
2. **Every reading must have an action** - Do/Don't lists are required
3. **Signal before detail** - Use green/amber/red indicators
4. **Timing is everything** - Include when to act
5. **Use accessible language** - No jargon without explanation
6. **Psychology, not prediction** - "You may feel..." not "You will..."

See [resources/interpretation-guide.md](resources/interpretation-guide.md) for full methodology.

---

## Numerology Quick Reference

| Number | Theme | Energy |
|--------|-------|--------|
| 1 | New Beginnings | Leadership, independence |
| 2 | Partnership | Cooperation, diplomacy |
| 3 | Expression | Creativity, communication |
| 4 | Foundation | Stability, hard work |
| 5 | Change | Freedom, adventure |
| 6 | Responsibility | Love, nurturing |
| 7 | Introspection | Analysis, spirituality |
| 8 | Achievement | Power, abundance |
| 9 | Completion | Compassion, endings |
| 11 | Illumination | Intuition, inspiration (master) |
| 22 | Master Builder | Practical idealism (master) |
| 33 | Master Teacher | Selfless service (master) |

See [resources/numerology-guide.md](resources/numerology-guide.md) for full meanings.

---

## Testing Quick Reference

**Test Location**: `app/tests/unit/astro/`

| Test File | Coverage |
|-----------|----------|
| formulas.test.ts | Julian Day, Sidereal Time, Obliquity, Ascendant, MC |
| numerology.test.ts | Life Path, Personal Day/Month/Year, master numbers |
| dignities.test.ts | All planetary dignities |
| sidereal.test.ts | Time formatting, coordinate display |
| void-of-course.test.ts | VoC Moon detection and caching |
| houses.test.ts | All 10 house systems, celebrity verification (Monroe, Einstein, Diana) |
| aspects.test.ts | Aspect detection with orbs |

**Run Tests**:
```bash
npm run test:astro           # All astro tests
npm run test:astro:formulas  # Formula tests only
./tests/run-e2e.sh --unit=astro  # Via runner script
```

See [resources/testing-patterns.md](resources/testing-patterns.md) for test writing guide.

---

## Navigation

**Resources**
- [resources/operational-playbook.md](resources/operational-playbook.md) — Verification checklists, debugging flows
- [resources/calculation-reference.md](resources/calculation-reference.md) — All formulas with derivations
- [resources/interpretation-guide.md](resources/interpretation-guide.md) — Psychology-first methodology
- [resources/numerology-guide.md](resources/numerology-guide.md) — Life Path meanings
- [resources/codebase-patterns.md](resources/codebase-patterns.md) — Extension patterns
- [resources/testing-patterns.md](resources/testing-patterns.md) — Test writing guide

**Predictive Astrology Resources**
- [resources/lunar-nodes-guide.md](resources/lunar-nodes-guide.md) — North/South Node interpretation, karmic life path
- [resources/predictive-progressions.md](resources/predictive-progressions.md) — Secondary progressions, solar arc directions
- [resources/predictive-returns.md](resources/predictive-returns.md) — Solar/Lunar return calculations
- [resources/predictive-timing.md](resources/predictive-timing.md) — Transit duration, intensity scoring, timing windows

**Advanced Astrology Resources**
- [resources/fixed-stars-guide.md](resources/fixed-stars-guide.md) — Behenian stars, Royal Stars, parans
- [resources/asteroids-guide.md](resources/asteroids-guide.md) — Chiron, Ceres, Pallas, Juno, Vesta
- [resources/horary-electional-guide.md](resources/horary-electional-guide.md) — Question astrology and timing selection

**Templates**

- [templates/template-chart-analysis.md](templates/template-chart-analysis.md) — Natal chart reading
- [templates/template-transit-reading.md](templates/template-transit-reading.md) — Transit interpretation
- [templates/template-numerology-reading.md](templates/template-numerology-reading.md) — Numerology profile
- [templates/template-synastry-analysis.md](templates/template-synastry-analysis.md) — Compatibility reading
- [templates/template-new-calculation.md](templates/template-new-calculation.md) — Adding new calculations
- [templates/template-formula-verification.md](templates/template-formula-verification.md) — Agent verification checklist

**Agent Prompts**

- [prompts/verify-all-formulas.md](prompts/verify-all-formulas.md) — **Full audit prompt for another Claude Code agent** (copy & paste to run independent verification)

---

## Accuracy Standards

**VSOP87 Accuracy** (via `astronomia`):
- Inner planets (Mercury-Mars): ~1 arc-second
- Outer planets (Jupiter-Pluto): ~10 arc-seconds
- Moon: ~10 arc-seconds
- Range: 3000 BCE to 3000 CE

**Verification Source**: astro.com (Extended Chart Selection)

**Why VSOP87 over Swiss Ephemeris**: See CLAUDE.md decision D016 - native bindings fail on Vercel serverless.

**Acceptable Tolerance**:
- Planet positions: ±0.1° (6 arc-minutes)
- House cusps: ±0.5°
- Ascendant/MC: ±0.1°

See [resources/operational-playbook.md](resources/operational-playbook.md) for verification checklist.
