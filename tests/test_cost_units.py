"""Offline regressions: monetary units follow column names, not magnitude."""
import unittest
from google_ads_intent_mcp.intent import analyze_search_terms, classify_search_term


class CostUnitsTests(unittest.TestCase):
    def test_micros_small_boundary_and_large(self):
        for key in ('cost_micros', 'Cost micros'):
            for value in (0, 1, 50000, 100000, 100001, 200000000000):
                with self.subTest(key=key, value=value):
                    result = analyze_search_terms([{'search_term': 'free robux generator', key: value}], llm=False)
                    self.assertEqual(result['terms'][0]['metrics']['cost'], value / 1000000)
                    self.assertEqual(result['summary']['wasted_cost'], round(value / 1000000, 2))

    def test_currency_large_boundary_and_formatted(self):
        for key in ('cost', 'Cost'):
            for value, expected in [(100000, 100000), (100001, 100001), ('$200,000', 200000), ('12.50', 12.5)]:
                with self.subTest(key=key, value=value):
                    result = analyze_search_terms([{'search_term': 'free robux generator', key: value}], llm=False)
                    self.assertEqual(result['terms'][0]['metrics']['cost'], expected)
                    self.assertEqual(result['summary']['wasted_cost'], expected)

    def test_currency_precedence_and_blank_fallback(self):
        for cost, expected in [(0, 0), ('', .05), (None, .05), (200000, 200000)]:
            result = analyze_search_terms([{'search_term': 'free robux generator', 'cost': cost, 'cost_micros': 50000}], llm=False)
            self.assertEqual(result['terms'][0]['metrics']['cost'], expected)

    def test_direct_classification_uses_same_units(self):
        low = classify_search_term('free robux generator', {'cost_micros': 50000}, llm=False)
        equivalent = classify_search_term('free robux generator', {'cost': '.05'}, llm=False)
        self.assertEqual(low['scores'], equivalent['scores'])
        high = classify_search_term('free robux generator', {'cost': 200000}, llm=False)
        equivalent = classify_search_term('free robux generator', {'cost_micros': 200000000000}, llm=False)
        self.assertEqual(high['scores'], equivalent['scores'])

    def test_nonfinite_metrics_rejected_with_clear_error(self):
        for field in ('cost', 'Cost', 'cost_micros', 'Cost micros', 'clicks', 'conversions', 'impressions'):
            for value in ('NaN', 'sNaN', 'Infinity', '-Infinity', float('nan'), float('inf')):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, 'finite numbers'):
                        analyze_search_terms([{'search_term': 'synthetic', field: value}], llm=False)
        for field in ('cost', 'cost_micros', 'conversions'):
            with self.assertRaisesRegex(ValueError, 'finite numbers'):
                classify_search_term('synthetic', {field: 'NaN'}, llm=False)

    def test_negative_credits_and_missing_values(self):
        for row, expected in [({'cost_micros': -50000}, -.05), ({'cost': -200000}, -200000), ({}, 0), ({'cost': ''}, 0), ({'cost': None}, 0)]:
            with self.subTest(row=row):
                result = analyze_search_terms([{'search_term': 'free robux generator', **row}], llm=False)
                self.assertEqual(result['terms'][0]['metrics']['cost'], expected)
