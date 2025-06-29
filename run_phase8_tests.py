#!/usr/bin/env python3
"""
Test Runner for Phase 8: Advanced Prompt Customization
Executes comprehensive tests for custom instructions functionality.

Covers Linear issues:
- ASS-20: Phase 8.1 UI Enhancement for Custom Instructions  
- ASS-21: Phase 8.2 Prompt System Enhancement
- ASS-22: Phase 8.3 Workflow Integration for Custom Instructions

Usage:
    python run_phase8_tests.py                    # Run all Phase 8 tests
    python run_phase8_tests.py --mode ui          # Run only UI tests
    python run_phase8_tests.py --mode prompt      # Run only prompt tests
    python run_phase8_tests.py --mode workflow    # Run only workflow tests
    python run_phase8_tests.py --mode integration # Run only integration tests
    python run_phase8_tests.py --coverage         # Run with coverage report
    python run_phase8_tests.py --fast             # Run fast tests only
    python run_phase8_tests.py --verbose          # Verbose output
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def run_pytest_command(args, test_markers=None, test_files=None):
    """Run pytest with specified arguments and markers."""
    cmd = ['python', '-m', 'pytest']
    
    # Add test files or default to Phase 8 test file
    if test_files:
        cmd.extend(test_files)
    else:
        cmd.append('tests/test_phase8_custom_instructions.py')
    
    # Add markers if specified
    if test_markers:
        for marker in test_markers:
            cmd.extend(['-m', marker])
    
    # Add common arguments
    cmd.extend([
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings',  # Disable warnings
        '--durations=10'  # Show 10 slowest tests
    ])
    
    # Add additional arguments
    cmd.extend(args)
    
    return cmd

def run_phase8_ui_tests(args):
    """Run Phase 8.1 UI Enhancement tests."""
    print("🖥️  Running Phase 8.1: UI Enhancement for Custom Instructions Tests")
    print("=" * 70)
    
    markers = ['phase8', 'ui']
    cmd = run_pytest_command(args, test_markers=markers)
    cmd.extend(['-k', 'TestCustomInstructionsUI'])
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_phase8_prompt_tests(args):
    """Run Phase 8.2 Prompt System Enhancement tests."""
    print("🔤 Running Phase 8.2: Prompt System Enhancement Tests")
    print("=" * 70)
    
    markers = ['phase8', 'prompt']
    cmd = run_pytest_command(args, test_markers=markers)
    cmd.extend(['-k', 'TestPromptSystemEnhancement'])
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_phase8_workflow_tests(args):
    """Run Phase 8.3 Workflow Integration tests."""
    print("⚙️  Running Phase 8.3: Workflow Integration for Custom Instructions Tests")
    print("=" * 70)
    
    markers = ['phase8', 'workflow']
    cmd = run_pytest_command(args, test_markers=markers)
    cmd.extend(['-k', 'TestWorkflowIntegration'])
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_phase8_integration_tests(args):
    """Run Phase 8 integration tests."""
    print("🔗 Running Phase 8: Integration Tests")
    print("=" * 70)
    
    markers = ['phase8', 'integration']
    cmd = run_pytest_command(args, test_markers=markers)
    cmd.extend(['-k', 'TestPhase8Integration'])
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_phase8_fast_tests(args):
    """Run fast Phase 8 tests only."""
    print("⚡ Running Phase 8: Fast Tests Only")
    print("=" * 70)
    
    markers = ['phase8']
    cmd = run_pytest_command(args, test_markers=markers)
    cmd.extend(['-k', 'not slow and not performance'])
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_phase8_performance_tests(args):
    """Run Phase 8 performance tests."""
    print("📊 Running Phase 8: Performance Tests")
    print("=" * 70)
    
    markers = ['phase8', 'performance']
    cmd = run_pytest_command(args, test_markers=markers)
    cmd.extend(['-k', 'performance'])
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_all_phase8_tests(args):
    """Run all Phase 8 tests."""
    print("🚀 Running All Phase 8: Advanced Prompt Customization Tests")
    print("=" * 70)
    
    markers = ['phase8']
    cmd = run_pytest_command(args, test_markers=markers)
    
    return subprocess.run(cmd, cwd=PROJECT_ROOT)

def run_with_coverage(args):
    """Run tests with coverage report."""
    print("📈 Running Phase 8 Tests with Coverage Report")
    print("=" * 70)
    
    # Check if coverage is installed
    try:
        import coverage
    except ImportError:
        print("❌ Coverage.py not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'])
    
    # Run tests with coverage
    cmd = run_pytest_command(args, test_markers=['phase8'])
    cmd.extend([
        '--cov=app',
        '--cov=services', 
        '--cov=utils',
        '--cov-report=html:htmlcov/phase8',
        '--cov-report=term-missing',
        '--cov-fail-under=80'
    ])
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print("\n📊 Coverage report generated in htmlcov/phase8/")
    
    return result

def validate_environment():
    """Validate that the test environment is properly set up."""
    print("🔍 Validating test environment...")
    
    # Check if we're in the right directory
    if not (PROJECT_ROOT / 'app.py').exists():
        print("❌ Error: app.py not found. Make sure you're in the project root.")
        return False
    
    # Check if test file exists
    test_file = PROJECT_ROOT / 'tests' / 'test_phase8_custom_instructions.py'
    if not test_file.exists():
        print(f"❌ Error: Test file not found: {test_file}")
        return False
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ Error: pytest not installed. Run: pip install pytest")
        return False
    
    print("✅ Test environment validated")
    return True

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description='Run Phase 8: Advanced Prompt Customization Tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_phase8_tests.py                    # Run all Phase 8 tests
  python run_phase8_tests.py --mode ui          # Run UI tests only
  python run_phase8_tests.py --mode prompt      # Run prompt system tests
  python run_phase8_tests.py --mode workflow    # Run workflow integration tests
  python run_phase8_tests.py --coverage         # Run with coverage report
  python run_phase8_tests.py --fast             # Run fast tests only
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['ui', 'prompt', 'workflow', 'integration', 'fast', 'performance', 'all'],
        default='all',
        help='Test mode to run (default: all)'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run tests with coverage report'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--maxfail',
        type=int,
        default=5,
        help='Stop after N failures (default: 5)'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run tests in parallel (requires pytest-xdist)'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Build pytest arguments
    pytest_args = []
    
    if args.verbose:
        pytest_args.append('-vvv')
    
    if args.maxfail:
        pytest_args.extend(['--maxfail', str(args.maxfail)])
    
    if args.parallel:
        pytest_args.extend(['-n', 'auto'])
    
    # Record start time
    start_time = time.time()
    
    # Run tests based on mode
    if args.coverage:
        result = run_with_coverage(pytest_args)
    elif args.mode == 'ui':
        result = run_phase8_ui_tests(pytest_args)
    elif args.mode == 'prompt':
        result = run_phase8_prompt_tests(pytest_args)
    elif args.mode == 'workflow':
        result = run_phase8_workflow_tests(pytest_args)
    elif args.mode == 'integration':
        result = run_phase8_integration_tests(pytest_args)
    elif args.mode == 'fast':
        result = run_phase8_fast_tests(pytest_args)
    elif args.mode == 'performance':
        result = run_phase8_performance_tests(pytest_args)
    else:  # all
        result = run_all_phase8_tests(pytest_args)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"⏱️  Test execution completed in {duration:.2f} seconds")
    
    if result.returncode == 0:
        print("✅ All Phase 8 tests passed successfully!")
        print("\n🎉 Phase 8: Advanced Prompt Customization tests are ready for implementation!")
    else:
        print(f"❌ Tests failed with exit code: {result.returncode}")
        print("\n🔧 Review test failures and fix issues before proceeding.")
    
    print("=" * 70)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())