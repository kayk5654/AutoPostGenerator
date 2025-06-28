#!/usr/bin/env python3
"""
Test runner for Phase 7.1: Universal Python Launcher

This script runs comprehensive tests for the launcher functionality,
including unit tests, integration tests, and cross-platform compatibility tests.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import pytest


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run Phase 7.1 Universal Python Launcher tests"
    )
    parser.add_argument(
        '--mode', 
        choices=['unit', 'integration', 'all', 'fast'],
        default='all',
        help='Test mode to run (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run tests with coverage reporting'
    )
    parser.add_argument(
        '--marker', '-m',
        help='Run tests with specific marker'
    )
    parser.add_argument(
        '--failfast', '-x',
        action='store_true',
        help='Stop on first failure'
    )
    
    args = parser.parse_args()
    
    # Set up test environment
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Base pytest arguments
    pytest_args = []
    
    # Add verbosity
    if args.verbose:
        pytest_args.extend(['-v', '-s'])
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend([
            '--cov=run',  # Will cover run.py when implemented
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    # Add fail fast if requested
    if args.failfast:
        pytest_args.append('-x')
    
    # Select tests based on mode
    if args.mode == 'unit':
        pytest_args.extend([
            '-m', 'launcher and not integration',
            'tests/test_launcher.py',
            'tests/test_launcher_utils.py',
            'tests/test_launcher_config.py'
        ])
    elif args.mode == 'integration':
        pytest_args.extend([
            '-m', 'launcher_integration',
            'tests/test_launcher_integration.py'
        ])
    elif args.mode == 'fast':
        pytest_args.extend([
            '-m', 'launcher and not slow and not integration',
            'tests/test_launcher.py',
            'tests/test_launcher_utils.py',
            'tests/test_launcher_config.py'
        ])
    elif args.mode == 'all':
        pytest_args.extend([
            '-m', 'phase7',
            'tests/test_launcher.py',
            'tests/test_launcher_utils.py',
            'tests/test_launcher_config.py',
            'tests/test_launcher_integration.py'
        ])
    
    # Add custom marker if specified
    if args.marker:
        if '-m' in pytest_args:
            # Combine markers
            marker_index = pytest_args.index('-m') + 1
            pytest_args[marker_index] += f' and {args.marker}'
        else:
            pytest_args.extend(['-m', args.marker])
    
    # Display test configuration
    print("=" * 60)
    print("Phase 7.1 Universal Python Launcher Test Runner")
    print("=" * 60)
    print(f"Test mode: {args.mode}")
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    print(f"Custom marker: {args.marker}")
    print(f"Fail fast: {args.failfast}")
    print("-" * 60)
    
    # Run tests
    try:
        exit_code = pytest.main(pytest_args)
        
        # Display results summary
        print("\n" + "=" * 60)
        if exit_code == 0:
            print("✅ All Phase 7.1 tests passed!")
        else:
            print("❌ Some Phase 7.1 tests failed.")
        print("=" * 60)
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n\n❌ Test run failed with error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())