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

Exit code 1 if any pair fails AA for normal text (4.5:1), else 0.
"""

import argparse
import sys


def _srgb_channel(v: float) -> float:
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"bad hex color: {hex_color!r}")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.2126 * _srgb_channel(r)
            + 0.7152 * _srgb_channel(g)
            + 0.0722 * _srgb_channel(b))


def contrast_ratio(fg: str, bg: str) -> float:
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
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
    if args.stdin:
        for line in sys.stdin:
            parts = line.split()
            if len(parts) >= 2:
                ok &= report(parts[0], parts[1],
                             " ".join(parts[2:]))
    elif args.tokens and args.surfaces:
        for bg in args.surfaces.split(","):
            for fg in args.tokens.split(","):
                ok &= report(fg.strip(), bg.strip())
    elif len(args.colors) == 2:
        ok = report(args.colors[0], args.colors[1])
    else:
        parser.print_help()
        return 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
