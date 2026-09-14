"""
Benchmarking framework for comparing Malta P-Systems to conventional approaches.

Usage:
    from benchmarks import BenchmarkSuite, ComparisonReport
    suite = BenchmarkSuite.load("cec2017")
    results = suite.run(malta_algorithm, xgboost_baseline)
    report = ComparisonReport(results)
    report.publish("reports/cec2017_comparison.pdf")
"""
