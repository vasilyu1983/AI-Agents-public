#!/usr/bin/env python3
"""WCAG 2.x contrast-ratio calculator for design-spec verification.

Contrast ratios in a spec must come from this script (or an equivalent
calculator), never from estimation: a language model asserting "computed"
ratios it did not compute is fabricating verification. Stdlib only.

Usage:
    # One pair: foreground background
    python3 contrast_check.py "#D97706" "#F8FAFC"

    # Many pairs from stdin, one "fg bg [label]" per line
    printf '#D97706 #F8FAFC severity-high\n#16A34A #F8FAFC ok\n' | \
        python3 contrast_check.py --stdin

    # Every token against every surface (cross product)
    python3 contrast_check.py --tokens "#D97706,#16A34A" \
        --surfaces "#F8FAFC,#FFFFFF"

Colours are #RGB, #RRGGBB, or #RRGGBBAA. A translucent foreground is
composited over its background before measuring (the ratio the user sees);
a translucent background is refused, because the surface it sits on is
unknown: pass the flattened colour instead.

Exit code 1 if any pair fails AA for normal text (4.5:1), else 0.
Exit code 2 when nothing could be checked: bad hex, empty stdin, or a
malformed line. A gate that checked nothing must not report a pass.
"""

import argparse
import sys


def _srgb_channel(v: float) -> float:
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def parse_hex(hex_color: str) -> tuple[int, int, int, float]:
    """Return (r, g, b, alpha) for #RGB / #RRGGBB / #RRGGBBAA.

    Raises ValueError with a readable message on anything else."""
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) not in (6, 8) or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise ValueError(f"bad hex color: {hex_color!r} "
                         "(expected #RGB, #RRGGBB or #RRGGBBAA)")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    alpha = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
    return r, g, b, alpha


def _luminance_rgb(r: float, g: float, b: float) -> float:
    return (0.2126 * _srgb_channel(r)
            + 0.7152 * _srgb_channel(g)
            + 0.0722 * _srgb_channel(b))


def relative_luminance(hex_color: str) -> float:
    r, g, b, _ = parse_hex(hex_color)
    return _luminance_rgb(r, g, b)


def contrast_ratio(fg: str, bg: str) -> float:
    fr, fg_, fb, fa = parse_hex(fg)
    br, bg_, bb, ba = parse_hex(bg)
    if ba < 1.0:
        raise ValueError(f"translucent background {bg!r}: flatten it over "
                         "the surface it renders on and pass that colour")
    if fa < 1.0:  # composite the foreground over the opaque background
        fr, fg_, fb = (fa * c + (1 - fa) * s
                       for c, s in ((fr, br), (fg_, bg_), (fb, bb)))
    l1, l2 = _luminance_rgb(fr, fg_, fb), _luminance_rgb(br, bg_, bb)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def verdicts(ratio: float) -> str:
    aa_normal = "PASS" if ratio >= 4.5 else "FAIL"
    aa_large = "PASS" if ratio >= 3.0 else "FAIL"
    aaa_normal = "PASS" if ratio >= 7.0 else "FAIL"
    nontext = "PASS" if ratio >= 3.0 else "FAIL"
    return (f"AA-normal(4.5) {aa_normal}  AA-large/UI(3.0) {aa_large}  "
            f"AAA-normal(7.0) {aaa_normal}  non-text(3.0/SC1.4.11) {nontext}")


def report(fg: str, bg: str, label: str = "") -> bool:
    ratio = contrast_ratio(fg, bg)
    tag = f"  [{label}]" if label else ""
    print(f"{fg} on {bg}: {ratio:.2f}:1  {verdicts(ratio)}{tag}")
    return ratio >= 4.5


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("colors", nargs="*", help="foreground background")
    parser.add_argument("--stdin", action="store_true",
                        help="read 'fg bg [label]' lines from stdin")
    parser.add_argument("--tokens", help="comma-separated foreground hexes")
    parser.add_argument("--surfaces", help="comma-separated background hexes")
    args = parser.parse_args()

    ok = True
    checked = 0
    try:
        if args.stdin:
            for lineno, line in enumerate(sys.stdin, 1):
                parts = line.split()
                if not parts:
                    continue
                if len(parts) < 2:
                    print(f"error: stdin line {lineno}: expected 'fg bg "
                          f"[label]', got {line.rstrip()!r}", file=sys.stderr)
                    return 2
                ok &= report(parts[0], parts[1], " ".join(parts[2:]))
                checked += 1
        elif args.tokens and args.surfaces:
            for bg in args.surfaces.split(","):
                for fg in args.tokens.split(","):
                    ok &= report(fg.strip(), bg.strip())
                    checked += 1
        elif len(args.colors) == 2:
            ok = report(args.colors[0], args.colors[1])
            checked = 1
        else:
            parser.print_help()
            return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if checked == 0:
        print("error: no colour pairs checked (empty input); refusing to "
              "report a pass", file=sys.stderr)
        return 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
