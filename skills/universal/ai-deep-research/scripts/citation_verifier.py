#!/usr/bin/env python3
"""
citation_verifier.py — stdlib-only citation verifier for deep-research workflows.

Reads a JSONL file of {claim, source_url, supporting_quote} entries.
Checks each entry and reports one of:
  - supported: the quote was found (normalized match) in the fetched or
    provided source text, does not negate the claim, every number in the
    claim appears in the quote with a compatible unit, and it overlaps it
  - unsupported: quote not found in the source text ("fabricated"),
    the quote negates the claim ("negated"), a number or unit in the claim
    disagrees with the quote ("numeric mismatch"), or the claim/quote is
    missing or generic
  - unverified: the source text could not be obtained (fetch failed, no
    network, or no source_url/source_text provided) — a "supported" verdict
    is NEVER produced when the source is unavailable
  - needs_review: quote present, found in source, but weak/ambiguous signal:
    low keyword overlap, a claim content word the quote lacks ("children"
    vs "adults"), or a restricting qualifier the quote has and the claim
    dropped ("only", "except", "limited to", ...)

A "supported" verdict requires the supporting_quote to actually appear
(normalized substring match) in the source text. Without that text, the
best this script can say is "unverified" — it never assumes support.

Every check here is lexical: substring/keyword overlap, digit-written
numbers and units, negation-word polarity, and qualifier words. None of it
checks meaning. A quote can pass all of them and still not entail the
claim, so a "supported" verdict on a claim that matters still needs a
human or model entailment read; this script only removes the cheap
failures first.

Numeric agreement (claim vs quote, no source needed): every number written
with digits in the claim must appear in the quote with the same value
(41.90 == 41.9; 1,266 == 1266; "12%" == "12 percent"). When both sides
attach a recognised unit to that number (percent, time units, thousand/
million/billion, data sizes, common currencies) the units must agree, so
"3.5 hours" is not supported by "3.5 days". Limitations, by design: number
words ("eight"), magnitude rewrites ("3 million" vs "3,000,000") and the
pairing of numbers to nouns ("28.4 BLEU on WMT 2014" vs "2014 BLEU on WMT
28.4") are not checked; the check is a fail-closed filter, not entailment.

Usage:
    python3 scripts/citation_verifier.py --input claims.jsonl
    python3 scripts/citation_verifier.py --input claims.jsonl --strict
    python3 scripts/citation_verifier.py --input claims.jsonl --output report.jsonl
    python3 scripts/citation_verifier.py --input claims.jsonl --no-fetch --allow-unverified

Input JSONL format (one JSON object per line):
    {"claim": "...", "source_url": "...", "supporting_quote": "..."}

Optional fields:
    {"claim": "...", "source_url": "...", "supporting_quote": "...",
     "ledger_id": "L001", "evidence_tier": "primary", "date_published": "2025-01-01",
     "source_text": "... full or excerpted source text, bypasses fetch ..."}

`source_text`, when present, is used directly and no network fetch is
attempted — this is how test fixtures verify the logic offline. When it is
absent, the script tries to fetch `source_url` (stdlib `urllib`, short
timeout); any fetch failure, or `--no-fetch`, yields "unverified".

Fetching is SSRF-guarded: only http/https URLs whose resolved addresses are
all public (not loopback, private, link-local/metadata, shared, reserved, or
multicast; IPv4-mapped IPv6 is unwrapped) are fetched, every redirect hop is
re-validated the same way, the connected peer address is re-checked, and
environment proxies are ignored. A blocked
or disallowed URL yields "unverified", the same as any other fetch failure.

Exit codes (the gate contract — a caller may treat 0 as "all citations
verified" and anything else as "do not publish"):
    0 — every claim is "supported". Nothing else exits 0 by default.
    1 — one or more claims are not supported: unsupported (fabricated,
        negated, numeric mismatch, missing/empty claim or quote),
        unverified (source could not be checked), or needs_review (quote
        found but weak overlap). --allow-unverified and --allow-needs-review
        each downgrade that one verdict to "reported, not failing";
        unsupported always exits 1.
    2 — input could not be checked at all: file not found, empty, a line
        that is not valid JSON, or a line that is not a JSON object. The
        script never prints a pass in this case.
"""

import argparse
import http.client
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_QUOTE_WORDS = 5          # Minimum word count for a quote to be considered substantive
GENERIC_QUOTES = {            # Exact or near-exact quotes that add no evidence
    "",
    "see above",
    "see source",
    "n/a",
    "na",
    "none",
    "not available",
    "not provided",
    "todo",
    "tbd",
    "-",
    "...",
}

FETCH_TIMEOUT_SECONDS = 8
FETCH_USER_AGENT = "citation_verifier/1.0 (+deep-research skill)"
ALLOWED_FETCH_SCHEMES = {"http", "https"}  # blocks file://, ftp://, gopher://, etc.

# Negation markers checked at the word level. Deliberately simple (no NLP
# dependency): catches "not", "never", "n't" contractions, and common
# negating verbs/determiners. It flags a MISMATCH in negation polarity
# between the claim and the quote — it does not itself prove entailment.
NEGATION_WORDS = {
    "not", "never", "no", "none", "nobody", "nothing", "nowhere",
    "cannot", "cant", "wont", "dont", "doesnt", "didnt", "isnt", "arent",
    "wasnt", "werent", "havent", "hasnt", "hadnt", "wouldnt", "couldnt",
    "shouldnt", "neither", "nor",
}

# A number written with digits: 41.9, 1,266, 2014, 0.5. The look-arounds stop
# "v2.0.1", "x-4b" or "P100" from contributing partial numbers.
NUMBER_RE = re.compile(r"(?<![\w.])\d(?:[\d,]*\d)?(?:\.\d+)?(?![\w.])")
# The token immediately after a number, if any: "%" or a word.
UNIT_AFTER_RE = re.compile(r"\s*(%|[A-Za-z]+)")

# Recognised units, mapped to a canonical name. A unit outside this table is
# ignored (treated as no unit), so "28.4 BLEU" never causes a false mismatch
# against "28.4 on BLEU". Plural "s" is stripped before lookup.
UNIT_CANON = {
    "%": "percent", "percent": "percent", "pct": "percent", "per": "percent",
    "second": "second", "sec": "second", "minute": "minute", "min": "minute",
    "hour": "hour", "hr": "hour", "day": "day", "week": "week", "wk": "week",
    "month": "month", "mo": "month", "year": "year", "yr": "year",
    "thousand": "thousand", "k": "thousand", "million": "million",
    "mn": "million", "billion": "billion", "bn": "billion", "trillion": "trillion",
    "byte": "byte", "kb": "kb", "mb": "mb", "gb": "gb", "tb": "tb",
    "token": "token", "word": "word", "page": "page",
    "usd": "usd", "dollar": "usd", "eur": "eur", "euro": "eur",
    "gbp": "gbp", "pound": "gbp", "ms": "ms", "km": "km", "kg": "kg",
}


# ---------------------------------------------------------------------------
# Core verification logic
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation from edges."""
    return re.sub(r"\s+", " ", text.strip().lower().strip(".,;:!?"))


def quote_is_substantive(quote: str) -> bool:
    """Return True if the quote meets the minimum content bar."""
    q = normalize(quote)
    if q in GENERIC_QUOTES:
        return False
    word_count = len(q.split())
    return word_count >= MIN_QUOTE_WORDS


def claim_words(claim: str) -> set:
    """Extract meaningful words from a claim (lowercase, no stopwords)."""
    stopwords = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "it", "its",
        "this", "that", "these", "those", "as", "if", "so", "than", "not",
    }
    words = re.findall(r"\b[a-z0-9]+\b", claim.lower())
    return {w for w in words if w not in stopwords and len(w) > 2}


# Words about the act of citing rather than the content cited. A claim may
# say "the paper reports X" where the quote says "we achieve X"; these are
# not content words and their absence from the quote is not a mismatch.
ATTRIBUTION_WORDS = {
    "paper", "report", "reports", "reported", "study", "article", "author",
    "authors", "according", "states", "stated", "said", "says", "found",
    "finds", "shows", "showed", "notes", "noted", "claims", "source", "page",
    "documentation", "docs", "section", "table", "figure", "label",
}

# Restricting qualifiers: when the quote carries one and the claim does not,
# the claim has dropped a limit the source imposed ("safe for adults only"
# quoted for "safe"). Negation words are handled separately by has_negation.
RESTRICTING_QUALIFIERS = {
    "only", "except", "excluding", "exclusively", "solely", "unless",
    "limited", "merely", "partially", "partly", "provided", "restricted",
}


def missing_content_words(claim: str, quote: str) -> List[str]:
    """
    Content words of the claim (no stopwords, no attribution words, no bare
    numbers — those are numeric_mismatch's job) that do not occur in the
    quote. Substring match, so "adult" matches "adults", and a word also
    matches on its stem with a common suffix removed, so "listed" matches
    "lists" and "improves" matches "improvement" instead of flagging every
    change of word form. Any non-empty result means the quote does not state
    something the claim states.
    """
    quote_lower = quote.lower()

    def in_quote(w: str) -> bool:
        if w in quote_lower:
            return True
        for suffix in ("ing", "est", "ed", "es", "er", "ly", "s"):
            if w.endswith(suffix) and len(w) - len(suffix) >= 4:
                return w[:-len(suffix)] in quote_lower
        return False

    return sorted(
        w for w in claim_words(claim)
        if w not in ATTRIBUTION_WORDS and not w.isdigit() and not in_quote(w)
    )


def added_qualifiers(claim: str, quote: str) -> List[str]:
    """Restricting qualifiers present in the quote but absent from the claim."""
    claim_tokens = set(re.findall(r"[a-z]+", claim.lower()))
    quote_tokens = set(re.findall(r"[a-z]+", quote.lower()))
    return sorted((quote_tokens - claim_tokens) & RESTRICTING_QUALIFIERS)


def compute_overlap(claim: str, quote: str) -> float:
    """
    Return the fraction of meaningful claim words present in the quote.
    Range [0.0, 1.0]. A score >= 0.3 is treated as a weak positive signal.
    This is a heuristic — it does not verify semantic accuracy.
    """
    claim_kw = claim_words(claim)
    if not claim_kw:
        return 0.0
    quote_lower = quote.lower()
    matched = sum(1 for w in claim_kw if w in quote_lower)
    return matched / len(claim_kw)


def extract_numbers(text: str) -> List[Tuple[Decimal, Optional[str]]]:
    """
    Return (value, canonical_unit_or_None) for every digit-written number in
    text. Values are Decimals with trailing zeros removed, so 41.90 and 41.9
    compare equal; thousands separators are dropped.
    """
    found = []
    for m in NUMBER_RE.finditer(text):
        try:
            value = Decimal(m.group(0).replace(",", "")).normalize()
        except InvalidOperation:
            continue
        unit = None
        after = UNIT_AFTER_RE.match(text, m.end())
        if after:
            tok = after.group(1).lower()
            if tok == "per" and not text[after.end():].lstrip().lower().startswith("cent"):
                tok = ""  # "per day", not "per cent"
            unit = UNIT_CANON.get(tok) or UNIT_CANON.get(tok.rstrip("s"))
        found.append((value, unit))
    return found


def numeric_mismatch(claim: str, quote: str) -> Optional[str]:
    """
    Return a reason string when a number in the claim is absent from the
    quote or carries a different recognised unit; None when the numbers
    agree (or the claim has none). Compares claim -> quote only: extra
    numbers in the quote are fine, they are context.
    """
    claim_nums = extract_numbers(claim)
    if not claim_nums:
        return None
    quote_nums = extract_numbers(quote)
    quote_values = {v for v, _ in quote_nums}
    fmt = lambda d: format(d, "f")  # noqa: E731 — plain digits, never "2E+1"
    for value, unit in claim_nums:
        if value not in quote_values:
            return (
                f"Claim states {fmt(value)} but the supporting quote does not "
                f"contain that number (quote numbers: "
                f"{', '.join(fmt(v) for v, _ in quote_nums) or 'none'})."
            )
        if unit is None:
            continue
        quote_units = {u for v, u in quote_nums if v == value and u is not None}
        if quote_units and unit not in quote_units:
            return (
                f"Claim states {fmt(value)} {unit} but the quote gives "
                f"{fmt(value)} {'/'.join(sorted(quote_units))} — unit mismatch."
            )
    return None


def has_negation(text: str) -> bool:
    """Return True if text contains a negation marker at the word level."""
    # Drop apostrophes so "didn't" -> "didnt", matching NEGATION_WORDS.
    tokens = re.findall(r"[a-z]+", text.lower().replace("'", ""))
    return any(tok in NEGATION_WORDS for tok in tokens)


def strip_html(html: str) -> str:
    """Very small HTML→text reduction: drop tags/scripts, unescape a few entities."""
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        text = text.replace(ent, ch)
    return re.sub(r"\s+", " ", text).strip()


def _is_unsafe_ip(ip_str: str) -> bool:
    """True unless this address is a globally routable unicast address.

    Blocks loopback, private (RFC 1918 / ULA), link-local (incl. the
    169.254.169.254 cloud-metadata address), shared/CGNAT, reserved,
    multicast and unspecified addresses. IPv4-mapped IPv6 addresses
    (``::ffff:127.0.0.1``) are unwrapped and judged as IPv4, because older
    ``ipaddress`` versions do not classify them as loopback/private.
    """
    try:
        ip = ipaddress.ip_address(ip_str.split("%", 1)[0])  # drop IPv6 zone id
    except ValueError:
        return True  # unparseable — treat as unsafe
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        not ip.is_global
        or ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _resolves_to_safe_addresses(hostname: str) -> bool:
    """
    Resolve `hostname` via getaddrinfo and require every returned address to
    be a safe, public address. Fails closed: DNS errors or an empty result
    are treated as unsafe.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
    except (socket.gaierror, UnicodeError, OSError):
        return False
    if not infos:
        return False
    return all(not _is_unsafe_ip(info[4][0]) for info in infos)


def url_is_safe_to_fetch(url: str) -> bool:
    """
    SSRF guard applied before the initial request AND on every redirect hop.

    Rejects:
      - any scheme other than http/https (blocks file://, ftp://, gopher://, ...)
      - URLs with no hostname component
      - hostnames that resolve (any of their addresses) to a non-public
        address (see _is_unsafe_ip)
    """
    if not url:
        return False
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    if parsed.scheme.lower() not in ALLOWED_FETCH_SCHEMES:
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    return _resolves_to_safe_addresses(hostname)


def _check_connected_peer(sock) -> None:
    """Re-check the address actually connected to (defeats DNS rebinding
    between the pre-flight resolution and the connection)."""
    peer_ip = sock.getpeername()[0]
    if _is_unsafe_ip(peer_ip):
        sock.close()
        raise OSError(f"Blocked connection to non-public address {peer_ip}")


class _GuardedHTTPConnection(http.client.HTTPConnection):
    def connect(self):
        super().connect()
        _check_connected_peer(self.sock)


class _GuardedHTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        super().connect()
        _check_connected_peer(self.sock)


class _GuardedHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_GuardedHTTPConnection, req)


class _GuardedHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_GuardedHTTPSConnection, req, context=self._context)


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-validates every redirect target with url_is_safe_to_fetch before following it."""

    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not url_is_safe_to_fetch(newurl):
            raise urllib.error.URLError(
                f"Blocked redirect to disallowed/unsafe URL: {newurl}"
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_safe_opener() -> urllib.request.OpenerDirector:
    """Opener with no proxies (a proxy would hide the real peer), guarded
    HTTP/HTTPS connections, and redirect re-validation. Only http/https
    handlers are registered, so other schemes have no handler at all."""
    opener = urllib.request.OpenerDirector()
    for handler in (
        urllib.request.ProxyHandler({}),
        urllib.request.UnknownHandler(),
        _GuardedHTTPHandler(),
        _GuardedHTTPSHandler(),
        urllib.request.HTTPDefaultErrorHandler(),
        _SafeRedirectHandler(),
        urllib.request.HTTPErrorProcessor(),
    ):
        opener.add_handler(handler)
    return opener


def fetch_source_text(url: str, timeout: int = FETCH_TIMEOUT_SECONDS) -> Optional[str]:
    """
    Fetch `url` and return normalized-ready plain text, or None on any failure.

    SSRF-guarded: only http/https to a publicly routable address is fetched;
    the check is re-applied on every redirect hop and on the connected peer
    address. Any exception (bad scheme, DNS failure, blocked target, timeout,
    HTTP error, no network access in this environment) is treated as
    "source unavailable" — the caller must NEVER report "supported" when this
    returns None.
    """
    if not url_is_safe_to_fetch(url):
        return None
    try:
        opener = build_safe_opener()
        req = urllib.request.Request(url, headers={"User-Agent": FETCH_USER_AGENT})
        with opener.open(req, timeout=timeout) as resp:  # noqa: S310
            if urllib.parse.urlsplit(resp.geturl()).scheme.lower() not in ALLOWED_FETCH_SCHEMES:
                return None
            raw = resp.read(2_000_000)  # cap to avoid unbounded downloads
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
    except Exception:  # noqa: BLE001 — any fetch failure means "unavailable"
        return None
    return strip_html(html)


def quote_in_source(quote: str, source_text: str) -> bool:
    """Normalized substring check: does the quote actually appear in the source?"""
    q = normalize(quote)
    s = normalize(source_text)
    if not q:
        return False
    return q in s


def verify_entry(entry: dict, strict: bool = False, fetch: bool = True) -> dict:
    """
    Verify a single claim entry.

    Returns a result dict with:
        claim, source_url, verdict, reason, overlap_score, source_status
    Optional passthrough fields: ledger_id, evidence_tier, date_published

    Verdict rules (in order):
      1. Missing claim/quote/generic quote → unsupported
      2. Negation polarity mismatch between claim and quote → unsupported ("negated")
      3. A number in the claim missing from the quote, or with a different
         recognised unit → unsupported ("numeric mismatch")
      4. Source text unavailable (no source_text, fetch disabled/failed) → unverified.
         This NEVER falls through to "supported".
      5. Quote not found in source text (normalized) → unsupported ("fabricated")
      6. Keyword overlap with claim below threshold → needs_review
      7. A claim content word absent from the quote, or a restricting
         qualifier in the quote that the claim lacks → needs_review
      8. Otherwise → supported
    """
    claim = str(entry.get("claim", "")).strip()
    source_url = str(entry.get("source_url", "")).strip()
    quote = str(entry.get("supporting_quote", "")).strip()
    provided_source_text = entry.get("source_text")

    result = {
        "claim": claim,
        "source_url": source_url,
        "supporting_quote": quote,
        "ledger_id": entry.get("ledger_id"),
        "evidence_tier": entry.get("evidence_tier"),
        "date_published": entry.get("date_published"),
        "verdict": None,
        "reason": None,
        "overlap_score": None,
        "source_status": None,
    }

    # --- Guard: empty claim ---
    if not claim:
        result["verdict"] = "unsupported"
        result["reason"] = "Empty claim — there is nothing to verify, so nothing is supported."
        result["overlap_score"] = 0.0
        return result

    # --- Guard: no quote ---
    if not quote:
        result["verdict"] = "unsupported"
        result["reason"] = "No supporting quote provided."
        result["overlap_score"] = 0.0
        return result

    # --- Guard: generic quote ---
    if normalize(quote) in GENERIC_QUOTES:
        result["verdict"] = "unsupported"
        result["reason"] = f"Supporting quote is a generic placeholder: {quote!r}."
        result["overlap_score"] = 0.0
        return result

    # --- Guard: no URL and no inline source text ---
    if not source_url and not provided_source_text:
        result["verdict"] = "unsupported"
        result["reason"] = "No source URL or source_text provided."
        result["overlap_score"] = 0.0
        return result

    # --- Check quote substantiveness ---
    if not quote_is_substantive(quote):
        result["verdict"] = "unsupported"
        result["reason"] = (
            f"Supporting quote is too short ({len(quote.split())} words); "
            f"minimum is {MIN_QUOTE_WORDS} words."
        )
        result["overlap_score"] = 0.0
        return result

    # --- Negation check (claim vs quote; needs no source): polarity must agree ---
    if has_negation(claim) != has_negation(quote):
        result["verdict"] = "unsupported"
        result["reason"] = (
            "The supporting quote's negation polarity does not match the "
            "claim's (one asserts, the other negates) — the quote "
            "contradicts, rather than supports, the claim."
        )
        result["overlap_score"] = 0.0
        return result

    # --- Numeric check (claim vs quote; needs no source): figures must agree ---
    mismatch = numeric_mismatch(claim, quote)
    if mismatch:
        result["verdict"] = "unsupported"
        result["reason"] = f"Numeric mismatch: {mismatch}"
        result["overlap_score"] = 0.0
        return result

    # --- Obtain source text: provided text wins, else fetch, else unavailable ---
    if provided_source_text is not None:
        source_text = str(provided_source_text)
        result["source_status"] = "provided"
    elif fetch:
        source_text = fetch_source_text(source_url)
        result["source_status"] = "fetched" if source_text is not None else "fetch_failed"
    else:
        source_text = None
        result["source_status"] = "fetch_disabled"

    # --- Source unavailable: verdict is ALWAYS unverified, never supported ---
    if not source_text:
        result["verdict"] = "unverified"
        result["reason"] = (
            "Source text could not be obtained (fetch failed, no network, or "
            "--no-fetch was set) — cannot confirm the quote appears in the "
            "source. A quote that cannot be checked is never 'supported'."
        )
        result["overlap_score"] = None
        return result

    # --- Quote must actually appear in the source text ---
    if not quote_in_source(quote, source_text):
        result["verdict"] = "unsupported"
        result["reason"] = (
            "Supporting quote was not found in the source text (normalized "
            "match) — likely fabricated or misquoted."
        )
        result["overlap_score"] = 0.0
        return result

    # --- Compute keyword overlap ---
    overlap = compute_overlap(claim, quote)
    result["overlap_score"] = round(overlap, 3)

    # --- Strict mode: require overlap >= 0.3 ---
    if strict and overlap < 0.3:
        result["verdict"] = "needs_review"
        result["reason"] = (
            f"Overlap score {overlap:.2f} is below 0.30 threshold in strict mode. "
            "Quote may not directly support the claim."
        )
        return result

    # --- Evidence tier check ---
    tier = str(entry.get("evidence_tier", "")).lower()
    if tier == "model-working-notes":
        result["verdict"] = "unsupported"
        result["reason"] = (
            "evidence_tier is 'model-working-notes'; model-generated text "
            "cannot be used as a primary citation."
        )
        return result

    # --- Content-word and qualifier guard (lexical, not entailment) ---
    # "safe for children" vs "safe for adults only" scored 0.67 overlap and
    # passed before this check. Any claim word the quote lacks, or any limit
    # the quote adds that the claim dropped, is a needs_review, never supported.
    missing = missing_content_words(claim, quote)
    added = added_qualifiers(claim, quote)
    if missing or added:
        parts = []
        if missing:
            parts.append(f"claim words absent from the quote: {', '.join(missing)}")
        if added:
            parts.append(f"quote restricts with: {', '.join(added)}")
        result["verdict"] = "needs_review"
        result["reason"] = (
            f"Quote is present in the source but may not say what the claim "
            f"says ({'; '.join(parts)}). This is a lexical check, not an "
            f"entailment check — a human or model must confirm."
        )
        return result

    # --- Passed all checks ---
    if overlap >= 0.3:
        result["verdict"] = "supported"
        result["reason"] = (
            f"Quote was found in the source text, does not negate the claim, "
            f"and overlaps with it (score: {overlap:.2f})."
        )
    else:
        result["verdict"] = "needs_review"
        result["reason"] = (
            f"Quote is present in the source but has low keyword overlap "
            f"with the claim (score: {overlap:.2f}). Manual review recommended."
        )

    return result


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list:
    """Load a JSONL file; return list of dicts. Raises on malformed lines."""
    entries = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"ERROR: malformed JSON on line {lineno}: {exc}", file=sys.stderr)
                sys.exit(2)
            if not isinstance(entry, dict):
                print(
                    f"ERROR: line {lineno} is not a JSON object "
                    f"(got {type(entry).__name__}); each line must be "
                    "{\"claim\": ..., \"source_url\": ..., \"supporting_quote\": ...}.",
                    file=sys.stderr,
                )
                sys.exit(2)
            entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_summary(results: list, strict: bool) -> None:
    """Print a human-readable summary to stdout."""
    total = len(results)
    supported = sum(1 for r in results if r["verdict"] == "supported")
    unsupported = sum(1 for r in results if r["verdict"] == "unsupported")
    needs_review = sum(1 for r in results if r["verdict"] == "needs_review")
    unverified = sum(1 for r in results if r["verdict"] == "unverified")

    mode = "strict" if strict else "standard"
    print(f"\n=== Citation Verifier Report ({mode} mode) ===")
    print(f"Total claims:    {total}")
    print(f"  Supported:     {supported}")
    print(f"  Unsupported:   {unsupported}")
    print(f"  Needs review:  {needs_review}")
    print(f"  Unverified:    {unverified}")
    print()

    if unsupported or needs_review or unverified:
        print("--- Issues ---")
        for r in results:
            if r["verdict"] in ("unsupported", "needs_review", "unverified"):
                ledger = f" [{r['ledger_id']}]" if r.get("ledger_id") else ""
                tier = f" (tier: {r['evidence_tier']})" if r.get("evidence_tier") else ""
                print(f"\n[{r['verdict'].upper()}]{ledger}{tier}")
                print(f"  Claim:  {r['claim'][:120]}")
                print(f"  URL:    {r['source_url'][:100]}")
                print(f"  Reason: {r['reason']}")
    else:
        print("All claims are supported.")


def write_report(results: list, output_path: Path) -> None:
    """Write results as JSONL to output_path."""
    with output_path.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nReport written to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Verify citations in a JSONL file of {claim, source_url, supporting_quote}.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--input", "-i",
        required=True,
        metavar="FILE",
        help="Path to input JSONL file.",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Optional path for JSONL report output.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Require keyword overlap >= 0.30 for 'supported' verdict.",
    )
    p.add_argument(
        "--no-fetch",
        action="store_true",
        default=False,
        help=(
            "Do not fetch source_url over the network; rely only on inline "
            "source_text. Entries without source_text are reported as "
            "'unverified' (never 'supported')."
        ),
    )
    p.add_argument(
        "--allow-unverified",
        action="store_true",
        default=False,
        help=(
            "Do not fail the gate on claims whose source could not be checked "
            "(they are still reported). By default unverified claims exit 1."
        ),
    )
    p.add_argument(
        "--allow-needs-review",
        action="store_true",
        default=False,
        help=(
            "Do not fail the gate on needs_review claims (quote found but weak "
            "overlap; they are still reported). By default they exit 1."
        ),
    )
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    entries = load_jsonl(input_path)
    if not entries:
        print("ERROR: input file is empty — nothing to verify.", file=sys.stderr)
        sys.exit(2)

    results = [
        verify_entry(entry, strict=args.strict, fetch=not args.no_fetch)
        for entry in entries
    ]

    print_summary(results, strict=args.strict)

    if args.output:
        write_report(results, Path(args.output))

    # Exit 0 only when every claim is "supported". Unsupported always fails;
    # unverified and needs_review fail unless the matching --allow-* flag
    # downgrades them to "reported only".
    failing = {"unsupported", "unverified", "needs_review"}
    if args.allow_unverified:
        failing.discard("unverified")
    if args.allow_needs_review:
        failing.discard("needs_review")
    has_issues = any(r["verdict"] in failing for r in results)
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
