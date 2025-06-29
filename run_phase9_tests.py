#!/usr/bin/env python3
"""
Phase 9 Test Runner: Dynamic Model Selection

Comprehensive test runner for Phase 9 implementation following Linear issues:
- ASS-23: Phase 9.1 - Model Discovery Service  
- ASS-24: Phase 9.2 - Configuration Updates
- ASS-25: Phase 9.3 - UI Model Selection Interface
- ASS-26: Phase 9.4 - LLM Service Integration

This runner executes all Phase 9 tests and provides detailed reporting
on test coverage, performance, and implementation readiness.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

def run_command(command: List[str], timeout: int = 300) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return 1, "", f"Error running command: {str(e)}"


def run_phase9_tests(verbose: bool = False, coverage: bool = False) -> Dict:
    """Run all Phase 9 tests and collect results."""
    print("🚀 Running Phase 9: Dynamic Model Selection Tests")
    print("=" * 60)
    
    test_files = [
        "tests/test_phase9_model_discovery.py",
        "tests/test_phase9_configuration.py", 
        "tests/test_phase9_ui_model_selection.py",
        "tests/test_phase9_llm_service_integration.py",
        "tests/test_phase9_integration.py"
    ]
    
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'test_files': {},
        'coverage_report': None,
        'performance_metrics': {},
        'start_time': time.time()
    }
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        
        # Build pytest command
        cmd = ["python", "-m", "pytest", test_file]
        if verbose:
            cmd.extend(["-v", "-s"])
        if coverage:
            cmd.extend(["--cov=services", "--cov=config", "--cov=app"])
        cmd.extend(["--tb=short", "--disable-warnings"])
        
        start_time = time.time()
        exit_code, stdout, stderr = run_command(cmd)
        end_time = time.time()
        
        # Parse test results
        file_results = parse_pytest_output(stdout, stderr)
        file_results['execution_time'] = end_time - start_time
        file_results['exit_code'] = exit_code
        
        results['test_files'][test_file] = file_results
        results['total_tests'] += file_results.get('total', 0)
        results['passed_tests'] += file_results.get('passed', 0)
        results['failed_tests'] += file_results.get('failed', 0)
        results['skipped_tests'] += file_results.get('skipped', 0)
        
        # Print file summary
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        print(f"   {status} - {file_results.get('total', 0)} tests in {file_results['execution_time']:.2f}s")
        
        if exit_code != 0 and verbose:
            print(f"   Error output: {stderr}")
    
    results['end_time'] = time.time()
    results['total_execution_time'] = results['end_time'] - results['start_time']
    
    return results


def parse_pytest_output(stdout: str, stderr: str) -> Dict:
    """Parse pytest output to extract test statistics."""
    results = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'errors': []}
    
    # Parse test summary line
    for line in stdout.split('\n'):
        if 'passed' in line or 'failed' in line or 'skipped' in line:
            # Look for pattern like "5 passed, 2 failed, 1 skipped"
            parts = line.split()
            for i, part in enumerate(parts):
                if part.isdigit():
                    count = int(part)
                    if i + 1 < len(parts):
                        status = parts[i + 1].replace(',', '')
                        if status == 'passed':
                            results['passed'] = count
                        elif status == 'failed':
                            results['failed'] = count
                        elif status == 'skipped':
                            results['skipped'] = count
    
    results['total'] = results['passed'] + results['failed'] + results['skipped']
    
    # Extract error details
    if stderr:
        results['errors'].append(stderr)
    
    return results


def generate_phase9_report(results: Dict) -> str:
    """Generate comprehensive Phase 9 test report."""
    report = []
    report.append("Phase 9: Dynamic Model Selection - Test Report")
    report.append("=" * 60)
    report.append("")
    
    # Overall summary
    total = results['total_tests']
    passed = results['passed_tests']
    failed = results['failed_tests']
    skipped = results['skipped_tests']
    success_rate = (passed / total * 100) if total > 0 else 0
    
    report.append(f"📊 OVERALL SUMMARY")
    report.append(f"   Total Tests: {total}")
    report.append(f"   Passed: {passed} ✅")
    report.append(f"   Failed: {failed} ❌")
    report.append(f"   Skipped: {skipped} ⏭️")
    report.append(f"   Success Rate: {success_rate:.1f}%")
    report.append(f"   Total Time: {results['total_execution_time']:.2f}s")
    report.append("")
    
    # Phase 9 component breakdown
    component_mapping = {
        "test_phase9_model_discovery.py": "Phase 9.1: Model Discovery Service",
        "test_phase9_configuration.py": "Phase 9.2: Configuration Updates", 
        "test_phase9_ui_model_selection.py": "Phase 9.3: UI Model Selection",
        "test_phase9_llm_service_integration.py": "Phase 9.4: LLM Service Integration",
        "test_phase9_integration.py": "Phase 9 Integration Tests"
    }
    
    report.append("🔍 COMPONENT BREAKDOWN")
    for test_file, file_results in results['test_files'].items():
        component_name = component_mapping.get(Path(test_file).name, Path(test_file).name)
        file_total = file_results.get('total', 0)
        file_passed = file_results.get('passed', 0)
        file_success_rate = (file_passed / file_total * 100) if file_total > 0 else 0
        status_icon = "✅" if file_results['exit_code'] == 0 else "❌"
        
        report.append(f"   {status_icon} {component_name}")
        report.append(f"      Tests: {file_passed}/{file_total} ({file_success_rate:.1f}%)")
        report.append(f"      Time: {file_results['execution_time']:.2f}s")
        report.append("")
    
    # Implementation readiness assessment
    report.append("🎯 IMPLEMENTATION READINESS")
    readiness_score = success_rate
    
    if readiness_score >= 90:
        readiness_status = "🟢 READY FOR IMPLEMENTATION"
        recommendation = "All tests passing. Phase 9 is ready for implementation."
    elif readiness_score >= 75:
        readiness_status = "🟡 MOSTLY READY"
        recommendation = "Most tests passing. Review failed tests before implementation."
    elif readiness_score >= 50:
        readiness_status = "🟠 NEEDS WORK"
        recommendation = "Significant test failures. Address issues before implementation."
    else:
        readiness_status = "🔴 NOT READY"
        recommendation = "Major test failures. Substantial work needed before implementation."
    
    report.append(f"   Status: {readiness_status}")
    report.append(f"   Score: {readiness_score:.1f}%")
    report.append(f"   Recommendation: {recommendation}")
    report.append("")
    
    # Next steps
    report.append("📋 NEXT STEPS")
    if failed > 0:
        report.append("   1. Review and fix failing tests")
        report.append("   2. Implement missing functionality")
        report.append("   3. Re-run tests to verify fixes")
        report.append("   4. Proceed with Phase 9 implementation")
    else:
        report.append("   1. All tests passing - ready for Phase 9 implementation")
        report.append("   2. Begin with Phase 9.1: Model Discovery Service")
        report.append("   3. Continue with subsequent phases in order")
        report.append("   4. Run integration tests after each phase")
    
    return "\n".join(report)


def save_test_results(results: Dict, output_file: str = "phase9_test_results.json"):
    """Save test results to JSON file."""
    try:
        # Convert to JSON-serializable format
        json_results = json.dumps(results, indent=2, default=str)
        with open(output_file, 'w') as f:
            f.write(json_results)
        print(f"📄 Results saved to {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Phase 9 Test Runner")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("-c", "--coverage", action="store_true",
                       help="Enable coverage reporting")
    parser.add_argument("-o", "--output", default="phase9_test_results.json",
                       help="Output file for results")
    parser.add_argument("--report-only", action="store_true",
                       help="Only generate report from existing results")
    
    args = parser.parse_args()
    
    if args.report_only and Path(args.output).exists():
        # Load existing results and generate report
        try:
            with open(args.output, 'r') as f:
                results = json.load(f)
            report = generate_phase9_report(results)
            print(report)
        except Exception as e:
            print(f"❌ Failed to load existing results: {e}")
            return 1
    else:
        # Run tests and generate report
        results = run_phase9_tests(verbose=args.verbose, coverage=args.coverage)
        
        # Generate and display report
        report = generate_phase9_report(results)
        print("\n" + report)
        
        # Save results
        save_test_results(results, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())