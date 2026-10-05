"""Bounded executable contract models; no agent calls or execution authority."""
from collections import Counter
import unittest

def opinion(panel, responses):
    if len(set(panel)) != len(panel):
        raise ValueError('duplicate panel identity')
    by_judge = {}
    for judge, verdict in responses:
        if judge not in panel:
            raise ValueError('unauthorized judge')
        if judge in by_judge and by_judge[judge] != verdict:
            raise ValueError('conflicting vote')
        by_judge[judge] = verdict
    counts = Counter(by_judge.values())
    winners = [v for v, n in counts.items() if n >= len(panel)//2 + 1]
    return winners[0] if len(winners) == 1 else None

def merge(records):
    events = {}
    for identity, payload, deps in records:
        if identity in events and events[identity] != (payload, deps):
            raise ValueError('immutable identity collision')
        events[identity] = (payload, deps)
    return events

def synthesize(events, required):
    needed = set(required)
    for payload, deps in events.values():
        needed.update(deps)
    if not needed.issubset(events):
        raise ValueError('incomplete dependencies or final versions')
    latest = {}
    for (task, writer, seq), (payload, _) in sorted(events.items()):
        latest[(task, writer)] = payload
    return latest

class Contracts(unittest.TestCase):
    def test_agreement_is_original_panel_majority(self):
        panel = list('abcde')
        self.assertIsNone(opinion(panel, [('a','yes'),('b','yes'),('c','no')]))
        self.assertIsNone(opinion(panel, [('a','yes')]*3))
        self.assertEqual('yes', opinion(panel, [('a','yes'),('b','yes'),('c','yes')]))
        with self.assertRaises(ValueError):
            opinion(panel, [('a','yes'),('a','no')])
        with self.assertRaises(ValueError):
            opinion(panel, [('outsider','yes')])

    def test_reorder_duplicate_and_collision(self):
        first = (('task','a',1), ('finding-a',), ())
        second = (('task','a',2), ('finding-a','finding-b'), (first[0],))
        forward = merge([first,second])
        backward = merge([second,first,second])
        self.assertEqual(forward, backward)
        self.assertEqual(('finding-a','finding-b'), synthesize(backward, [second[0]])[('task','a')])
        with self.assertRaises(ValueError):
            merge([first, (first[0], ('conflicting',), ())])

    def test_required_versions_and_dependency_gaps(self):
        first = (('task','a',1), ('a',), ())
        final = (('task','b',2), ('b',), (('task','a',2),))
        with self.assertRaises(ValueError):
            synthesize(merge([first,final]), [final[0]])
        with self.assertRaises(ValueError):
            synthesize(merge([first]), [('task','a',2)])

if __name__ == '__main__':
    unittest.main()
