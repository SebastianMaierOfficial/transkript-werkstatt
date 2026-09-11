"""Explicit, session-only literal rules, applied once against the original text."""
import re
import unicodedata
from detection import literal, person_pattern


def validate_rules(rules):
    if not isinstance(rules, list) or len(rules) > 200:
        raise ValueError('Maximal 200 Ausnahmeregeln möglich.')
    clean, seen = [], {}
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError('Ungültige Ausnahmeregel.')
        source, action, target = rule.get('source'), rule.get('action'), rule.get('target', '')
        if not isinstance(source, str) or not isinstance(target, str) or action not in ('keep', 'replace'):
            raise ValueError('Ausnahmeregel: Suchausdruck und Aktion prüfen.')
        source, target = (unicodedata.normalize('NFC', value.strip()) for value in (source, target))
        if not source or len(source) > 200 or any(c in source for c in '\r\n'):
            raise ValueError('Ausnahmeregel: Suchausdruck mit 1 bis 200 Zeichen erforderlich.')
        if action == 'replace' and (not target or len(target) > 200 or any(c in target for c in '\r\n')):
            raise ValueError('Ausnahmeregel: Ersatztext mit 1 bis 200 Zeichen erforderlich.')
        target = target if action == 'replace' else ''
        key = ' '.join(source.casefold().split())
        value = (action, target)
        if key in seen:
            if seen[key] != value:
                raise ValueError('Derselbe Suchausdruck hat widersprüchliche Ausnahmeregeln.')
            continue
        seen[key] = value
        clean.append({'source': source, 'action': action, 'target': target})
    return clean


def rule_spans(text, rules):
    matches = []
    for rule in rules:
        source = rule['source']
        for match in re.finditer(person_pattern(source), text, re.I):
            target = match.group() if rule['action'] == 'keep' else rule['target']
            if rule['action'] == 'replace' and not re.fullmatch(literal(source), match.group(), re.I):
                # Preserve simple possessives without inflecting invented role labels.
                target += "'" if target[-1:].casefold() in ('s', 'x', 'z', 'ß') else 's'
            matches.append((match.start(), match.end(), target))
    # A longer, more specific expression wins, independent of row order.
    accepted = []
    for span in sorted(matches, key=lambda h: (-(h[1]-h[0]), h[0])):
        if not any(span[0] < end and span[1] > start for start, end, _ in accepted):
            accepted.append(span)
    return sorted(accepted)


def prioritize(text, hits, overrides):
    """Split automatic spans at explicit rules; don't expose unmatched surname parts."""
    remaining = []
    for start, end, label in hits:
        pieces = [(start, end)]
        for left, right, _ in overrides:
            pieces = [(a, b) for lo, hi in pieces
                      for a, b in ((lo, min(hi, left)), (max(lo, right), hi)) if a < b] if any(lo < right and hi > left for lo, hi in pieces) else pieces
        for lo, hi in pieces:
            # Keep separators between an explicit role and the residual masked name.
            if (lo, hi) != (start, end):
                while lo < hi and text[lo].isspace(): lo += 1
                while hi > lo and text[hi-1].isspace(): hi -= 1
            if lo < hi: remaining.append((lo, hi, label))
    return remaining + overrides
