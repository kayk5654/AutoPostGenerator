"""
Test Runner for Phase 6.3: Comprehensive Testing

This module provides comprehensive test execution capabilities including:
- Test discovery and execution
- Coverage reporting
- Performance testing
- Test result analysis
- Automated test reporting

Usage:
    python tests/test_runner.py --all
    python tests/test_runner.py --unit
    python tests/test_runner.py --integration
    python tests/test_runner.py --performance
"""

import sys
import argparse
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase6TestRunner:
    """Comprehensive test runner for the Auto Post Generator project."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize test runner.
        
        Args:
            project_root: Root directory of the project. Defaults to parent of tests directory.
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
        self.results = {}
        
    def run_unit_tests(self) -> Dict[str, Any]:
        """
        Run unit tests with coverage reporting.
        
        Returns:
            Dict containing test results and metrics
        """
        logger.info("Running unit tests...")
        
        start_time = time.time()
        
        # Run pytest with coverage for unit tests
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "-m", "unit",
            "-v",
            "--cov=services",
            "--cov=utils",
            "--cov-report=term-missing",
            "--cov-report=json:coverage.json",
            "--junit-xml=test-results-unit.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            elapsed_time = time.time() - start_time
            
            # Parse coverage data
            coverage_data = self._parse_coverage_data()
            
            return {
                "type": "unit",
                "status": "passed" if result.returncode == 0 else "failed",
                "duration": elapsed_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "coverage": coverage_data
            }
            
        except Exception as e:
            logger.error(f"Unit tests failed: {str(e)}")
            return {
                "type": "unit",
                "status": "error",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """
        Run integration tests.
        
        Returns:
            Dict containing test results and metrics
        """
        logger.info("Running integration tests...")
        
        start_time = time.time()
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "-m", "integration",
            "-v",
            "--junit-xml=test-results-integration.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            elapsed_time = time.time() - start_time
            
            return {
                "type": "integration",
                "status": "passed" if result.returncode == 0 else "failed",
                "duration": elapsed_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Integration tests failed: {str(e)}")
            return {
                "type": "integration",
                "status": "error",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """
        Run performance tests.
        
        Returns:
            Dict containing test results and metrics
        """
        logger.info("Running performance tests...")
        
        start_time = time.time()
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "-m", "slow",
            "-v",
            "--junit-xml=test-results-performance.xml"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            elapsed_time = time.time() - start_time
            
            return {
                "type": "performance",
                "status": "passed" if result.returncode == 0 else "failed",
                "duration": elapsed_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Performance tests failed: {str(e)}")
            return {
                "type": "performance",
                "status": "error",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all tests with comprehensive reporting.
        
        Returns:
            Dict containing all test results and summary
        """
        logger.info("Running comprehensive test suite...")
        
        start_time = time.time()
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "-v",
            "--cov=services",
            "--cov=utils",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=json:coverage.json",
            "--junit-xml=test-results-all.xml",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            elapsed_time = time.time() - start_time
            
            # Parse coverage data
            coverage_data = self._parse_coverage_data()
            
            return {
                "type": "comprehensive",
                "status": "passed" if result.returncode == 0 else "failed",
                "duration": elapsed_time,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "coverage": coverage_data
            }
            
        except Exception as e:
            logger.error(f"Comprehensive tests failed: {str(e)}")
            return {
                "type": "comprehensive",
                "status": "error",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def _parse_coverage_data(self) -> Optional[Dict[str, Any]]:
        """
        Parse coverage data from coverage.json file.
        
        Returns:
            Dict containing coverage metrics or None if not available
        """
        coverage_file = self.project_root / "coverage.json"
        
        if not coverage_file.exists():
            return None
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            # Extract summary metrics
            totals = coverage_data.get('totals', {})
            
            return {
                "percent_covered": totals.get('percent_covered', 0),
                "num_statements": totals.get('num_statements', 0),
                "missing_lines": totals.get('missing_lines', 0),
                "covered_lines": totals.get('covered_lines', 0),
                "files": list(coverage_data.get('files', {}).keys())
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse coverage data: {str(e)}")
            return None
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive test report.
        
        Args:
            results: Test results from test execution
            
        Returns:
            Formatted test report as string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("AUTO POST GENERATOR - COMPREHENSIVE TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Test Summary
        report_lines.append("TEST SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Test Type: {results.get('type', 'Unknown')}")
        report_lines.append(f"Status: {results.get('status', 'Unknown').upper()}")
        report_lines.append(f"Duration: {results.get('duration', 0):.2f} seconds")
        report_lines.append(f"Return Code: {results.get('return_code', 'N/A')}")
        report_lines.append("")
        
        # Coverage Information
        coverage = results.get('coverage')
        if coverage:
            report_lines.append("COVERAGE METRICS")
            report_lines.append("-" * 40)
            report_lines.append(f"Overall Coverage: {coverage['percent_covered']:.1f}%")
            report_lines.append(f"Total Statements: {coverage['num_statements']}")
            report_lines.append(f"Covered Lines: {coverage['covered_lines']}")
            report_lines.append(f"Missing Lines: {coverage['missing_lines']}")
            report_lines.append(f"Files Analyzed: {len(coverage['files'])}")
            report_lines.append("")
        
        # Test Output
        if results.get('stdout'):
            report_lines.append("TEST OUTPUT")
            report_lines.append("-" * 40)
            report_lines.append(results['stdout'])
            report_lines.append("")
        
        # Errors (if any)
        if results.get('stderr'):
            report_lines.append("ERRORS/WARNINGS")
            report_lines.append("-" * 40)
            report_lines.append(results['stderr'])
            report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 40)
        
        if results.get('status') == 'passed':
            report_lines.append("✅ All tests passed successfully!")
            
            if coverage and coverage['percent_covered'] < 80:
                report_lines.append("📈 Consider improving test coverage (currently {:.1f}%)".format(coverage['percent_covered']))
            elif coverage and coverage['percent_covered'] >= 90:
                report_lines.append("🎉 Excellent test coverage ({:.1f}%)!".format(coverage['percent_covered']))
        else:
            report_lines.append("❌ Some tests failed. Please review the output above.")
            report_lines.append("💡 Fix failing tests before deploying to production.")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\\n".join(report_lines)
    
    def save_report(self, results: Dict[str, Any], filename: str = "test_report.txt") -> None:
        """
        Save test report to file.
        
        Args:
            results: Test results from test execution
            filename: Name of the report file
        """
        report = self.generate_test_report(results)
        report_path = self.project_root / filename
        
        try:
            with open(report_path, 'w') as f:
                f.write(report)
            logger.info(f"Test report saved to {report_path}")
        except Exception as e:
            logger.error(f"Failed to save test report: {str(e)}")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner for Auto Post Generator")
    
    parser.add_argument("--all", action="store_true", help="Run all tests with coverage")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--report", default="test_report.txt", help="Test report filename")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize test runner
    runner = Phase6TestRunner()
    
    # Determine which tests to run
    if args.unit:
        results = runner.run_unit_tests()
    elif args.integration:
        results = runner.run_integration_tests()
    elif args.performance:
        results = runner.run_performance_tests()
    else:  # Default to all tests
        results = runner.run_all_tests()
    
    # Generate and display report
    report = runner.generate_test_report(results)
    print(report)
    
    # Save report to file
    runner.save_report(results, args.report)
    
    # Exit with appropriate code
    if results.get('status') == 'passed':
        logger.info("All tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()