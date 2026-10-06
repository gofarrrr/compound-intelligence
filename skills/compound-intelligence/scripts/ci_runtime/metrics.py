"""Offline per-contract Noul reliability summaries. No training or threshold promotion."""
from __future__ import annotations
from collections import defaultdict
from .common import CIError, bounded_number

GROUP_FIELDS = ('model', 'question_version', 'question_digest', 'state_schema_version', 'question_id', 'split')


def reliability_report(rows: list[dict]) -> dict:
    groups, seen, assignments = defaultdict(list), set(), {}
    required = set(GROUP_FIELDS) | {'case_id', 'probability', 'label', 'primitive'}
    for row in rows:
        if not isinstance(row, dict) or set(row) != required:
            raise CIError('invalid_label_row_fields')
        if row['primitive'] != 'noul' or type(row['label']) is not int or row['label'] not in {0, 1}:
            raise CIError('labels_require_binary_noul_judgments')
        if row['split'] not in {'development', 'test'}:
            raise CIError('invalid_evaluation_split')
        for key in set(GROUP_FIELDS) | {'case_id'}:
            if not isinstance(row[key], str) or not row[key]:
                raise CIError('invalid_evaluation_identifier')
        bounded_number(row['probability'])
        assignment_key = row['case_id']
        if assignment_key in assignments and assignments[assignment_key] != row['split']:
            raise CIError('case_leaks_across_development_and_test')
        assignments[assignment_key] = row['split']
        group_key = tuple(row[k] for k in GROUP_FIELDS)
        unique = group_key + (row['case_id'],)
        if unique in seen:
            raise CIError('duplicate_label_row')
        seen.add(unique)
        groups[group_key].append(row)
    results = []
    for key, entries in sorted(groups.items()):
        n = len(entries)
        brier = sum((r['probability'] - r['label']) ** 2 for r in entries) / n
        bands, ece = [], 0.0
        for i in range(10):
            bucket = [r for r in entries if min(int(r['probability'] * 10), 9) == i]
            if not bucket:
                continue
            mean = sum(r['probability'] for r in bucket) / len(bucket)
            observed = sum(r['label'] for r in bucket) / len(bucket)
            ece += len(bucket) / n * abs(mean - observed)
            bands.append({'lower': i / 10, 'upper': (i + 1) / 10,
                          'n': len(bucket), 'mean_p_yes': mean, 'observed_yes_rate': observed})
        thresholds = []
        total_yes = sum(r['label'] for r in entries)
        for t in (0.5, 0.65, 0.75, 0.85, 0.95):
            accepted = [r for r in entries if r['probability'] >= t]
            true_positive = sum(r['label'] for r in accepted)
            thresholds.append({'threshold': t, 'accepted_n': len(accepted),
                'coverage': len(accepted) / n,
                'precision': true_positive / len(accepted) if accepted else None,
                'recall': true_positive / total_yes if total_yes else None})
        results.append(dict(zip(GROUP_FIELDS, key)) | {'n': n, 'brier_score': brier,
                        'ece_10_equal_width_bins': ece, 'reliability_bands': bands,
                        'threshold_table': thresholds, 'small_sample_warning': n < 100})
    return {'kind': 'offline_noul_reliability_report', 'groups': results,
            'thresholds_fitted': False, 'policy_modified': False,
            'note': 'Labels assess bounded judgments, not causal coaching effectiveness. '
                    'Use development data for tuning and untouched test data for reporting; '
                    'bin estimates are unstable with few examples.'}
