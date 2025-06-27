#!/usr/bin/env python3
"""
Phase 6.3 Test Execution Script

This script executes the comprehensive testing suite for Phase 6.3 requirements.
It runs all tests, generates coverage reports, and provides detailed analysis.

Usage:
    python run_phase6_tests.py
    python run_phase6_tests.py --quick    # Skip slow tests
    python run_phase6_tests.py --coverage # Include coverage report
    python run_phase6_tests.py --report   # Generate detailed report
"""

import sys
import argparse
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase6TestRunner:
    """Comprehensive test runner for Phase 6.3 requirements."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_smoke_tests(self) -> bool:
        """Run quick smoke tests to verify basic functionality."""
        logger.info("Running smoke tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "smoke",
            "-v",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            success = result.returncode == 0
            
            self.test_results['smoke'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                logger.info("✅ Smoke tests passed")
            else:
                logger.error("❌ Smoke tests failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to run smoke tests: {e}")
            return False
    
    def run_unit_tests(self) -> bool:
        """Run unit tests with coverage."""
        logger.info("Running unit tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "unit",
            "-v",
            "--cov=services",
            "--cov=utils",
            "--cov-report=term-missing",
            "--cov-report=json:coverage_unit.json",
            "--junit-xml=test-results-unit.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            success = result.returncode == 0
            
            self.test_results['unit'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                logger.info("✅ Unit tests passed")
            else:
                logger.error("❌ Unit tests failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to run unit tests: {e}")
            return False
    
    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        logger.info("Running integration tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "integration",
            "-v",
            "--tb=long",
            "--junit-xml=test-results-integration.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            success = result.returncode == 0
            
            self.test_results['integration'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                logger.info("✅ Integration tests passed")
            else:
                logger.error("❌ Integration tests failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to run integration tests: {e}")
            return False
    
    def run_phase6_specific_tests(self) -> bool:
        """Run Phase 6 specific tests."""
        logger.info("Running Phase 6 specific tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_phase6_integration.py",
            "-v",
            "--tb=long",
            "--junit-xml=test-results-phase6.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            success = result.returncode == 0
            
            self.test_results['phase6'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                logger.info("✅ Phase 6 tests passed")
            else:
                logger.error("❌ Phase 6 tests failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to run Phase 6 tests: {e}")
            return False
    
    def run_performance_tests(self) -> bool:
        """Run performance and slow tests."""
        logger.info("Running performance tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "slow or performance",
            "-v",
            "--tb=short",
            "--junit-xml=test-results-performance.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            success = result.returncode == 0
            
            self.test_results['performance'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                logger.info("✅ Performance tests passed")
            else:
                logger.error("❌ Performance tests failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to run performance tests: {e}")
            return False
    
    def run_comprehensive_tests(self, include_slow: bool = True) -> bool:
        """Run all tests with comprehensive coverage."""
        logger.info("Running comprehensive test suite...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--cov=services",
            "--cov=utils",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage_comprehensive.json",
            "--junit-xml=test-results-comprehensive.xml",
            "--tb=short"
        ]
        
        if not include_slow:
            cmd.extend(["-m", "not slow"])
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            success = result.returncode == 0
            
            self.test_results['comprehensive'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            
            if success:
                logger.info("✅ Comprehensive tests passed")
            else:
                logger.error("❌ Comprehensive tests failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to run comprehensive tests: {e}")
            return False
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report."""
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("PHASE 6.3 COMPREHENSIVE TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            report_lines.append(f"Total Duration: {duration:.2f} seconds")
        
        report_lines.append("")
        
        # Test Results Summary
        report_lines.append("TEST RESULTS SUMMARY")
        report_lines.append("-" * 40)
        
        total_suites = len(self.test_results)
        passed_suites = sum(1 for result in self.test_results.values() if result['success'])
        
        report_lines.append(f"Test Suites Run: {total_suites}")
        report_lines.append(f"Test Suites Passed: {passed_suites}")
        report_lines.append(f"Test Suites Failed: {total_suites - passed_suites}")
        report_lines.append(f"Overall Success Rate: {(passed_suites/total_suites)*100:.1f}%" if total_suites > 0 else "No tests run")
        report_lines.append("")
        
        # Individual Test Suite Results
        for suite_name, results in self.test_results.items():
            report_lines.append(f"{suite_name.upper()} TESTS")
            report_lines.append("-" * 30)
            status = "✅ PASSED" if results['success'] else "❌ FAILED"
            report_lines.append(f"Status: {status}")
            
            if results.get('output'):
                # Extract key metrics from pytest output
                output_lines = results['output'].split('\\n')
                for line in output_lines:
                    if "passed" in line and "failed" in line:
                        report_lines.append(f"Details: {line.strip()}")
                        break
                    elif "passed" in line and line.count('=') > 5:
                        report_lines.append(f"Details: {line.strip()}")
                        break
            
            if not results['success'] and results.get('errors'):
                report_lines.append("Errors:")
                error_lines = results['errors'].split('\\n')[:5]  # First 5 lines
                for error_line in error_lines:
                    if error_line.strip():
                        report_lines.append(f"  {error_line.strip()}")
            
            report_lines.append("")
        
        # Coverage Information
        coverage_file = self.project_root / "coverage_comprehensive.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                report_lines.append("CODE COVERAGE")
                report_lines.append("-" * 30)
                
                totals = coverage_data.get('totals', {})
                report_lines.append(f"Overall Coverage: {totals.get('percent_covered', 0):.1f}%")
                report_lines.append(f"Lines Covered: {totals.get('covered_lines', 0)}")
                report_lines.append(f"Lines Missing: {totals.get('missing_lines', 0)}")
                report_lines.append(f"Total Statements: {totals.get('num_statements', 0)}")
                report_lines.append("")
                
                # File-level coverage
                files = coverage_data.get('files', {})
                if files:
                    report_lines.append("FILE COVERAGE BREAKDOWN")
                    report_lines.append("-" * 30)
                    for filename, file_data in list(files.items())[:10]:  # Top 10 files
                        coverage_pct = file_data.get('summary', {}).get('percent_covered', 0)
                        report_lines.append(f"{filename}: {coverage_pct:.1f}%")
                    report_lines.append("")
                
            except Exception as e:
                report_lines.append(f"Error reading coverage data: {e}")
                report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 30)
        
        all_passed = all(result['success'] for result in self.test_results.values())
        
        if all_passed:
            report_lines.append("🎉 All tests passed! The application is ready for Phase 6.4 deployment.")
            
            # Coverage-based recommendations
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    coverage_pct = coverage_data.get('totals', {}).get('percent_covered', 0)
                    
                    if coverage_pct >= 90:
                        report_lines.append("✨ Excellent test coverage! No coverage improvements needed.")
                    elif coverage_pct >= 80:
                        report_lines.append("📈 Good test coverage. Consider adding tests for edge cases.")
                    else:
                        report_lines.append("⚠️ Consider improving test coverage before production deployment.")
                        
                except Exception:
                    pass
        else:
            report_lines.append("❌ Some tests failed. Address the following before proceeding:")
            failed_suites = [name for name, result in self.test_results.items() if not result['success']]
            for suite in failed_suites:
                report_lines.append(f"  • Fix {suite} test failures")
            
            report_lines.append("")
            report_lines.append("💡 Check the detailed output above for specific error information.")
            report_lines.append("🔄 Re-run tests after making fixes to verify resolution.")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\\n".join(report_lines)
    
    def save_report(self, filename: str = "phase6_test_report.txt") -> None:
        """Save the test report to a file."""
        report = self.generate_test_report()
        report_path = self.project_root / filename
        
        try:
            with open(report_path, 'w') as f:
                f.write(report)
            logger.info(f"Test report saved to {report_path}")
        except Exception as e:
            logger.error(f"Failed to save test report: {e}")
    
    def run_test_suite(self, quick: bool = False, coverage: bool = False) -> bool:
        """
        Run the complete Phase 6.3 test suite.
        
        Args:
            quick: Skip slow/performance tests
            coverage: Include detailed coverage reporting
            
        Returns:
            True if all tests passed, False otherwise
        """
        self.start_time = time.time()
        
        logger.info("🚀 Starting Phase 6.3 Comprehensive Testing")
        logger.info(f"Quick mode: {quick}")
        logger.info(f"Coverage reporting: {coverage}")
        logger.info("-" * 50)
        
        all_passed = True
        
        # Run test suites in order
        test_suites = [
            ("Smoke Tests", self.run_smoke_tests),
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("Phase 6 Specific Tests", self.run_phase6_specific_tests),
        ]
        
        if not quick:
            test_suites.append(("Performance Tests", self.run_performance_tests))
        
        for suite_name, test_function in test_suites:
            logger.info(f"Running {suite_name}...")
            try:
                passed = test_function()
                if not passed:
                    all_passed = False
                    logger.error(f"{suite_name} failed!")
                else:
                    logger.info(f"{suite_name} completed successfully")
            except Exception as e:
                logger.error(f"Error running {suite_name}: {e}")
                all_passed = False
            
            logger.info("")
        
        # Run comprehensive test if coverage requested
        if coverage:
            logger.info("Running comprehensive tests with coverage...")
            comp_passed = self.run_comprehensive_tests(include_slow=not quick)
            if not comp_passed:
                all_passed = False
        
        self.end_time = time.time()
        
        # Generate and display report
        report = self.generate_test_report()
        print("\\n" + report)
        
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Phase 6.3 Comprehensive Test Runner")
    parser.add_argument("--quick", action="store_true", help="Skip slow tests for faster execution")
    parser.add_argument("--coverage", action="store_true", help="Include detailed coverage reporting")
    parser.add_argument("--report", action="store_true", help="Save detailed report to file")
    parser.add_argument("--output", default="phase6_test_report.txt", help="Report output filename")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = Phase6TestRunner()
    
    # Run tests
    success = runner.run_test_suite(quick=args.quick, coverage=args.coverage)
    
    # Save report if requested
    if args.report:
        runner.save_report(args.output)
    
    # Exit with appropriate code
    if success:
        logger.info("🎉 All Phase 6.3 tests passed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some Phase 6.3 tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()