#!/usr/bin/env python3
"""
Test runner script for Fridge Vision.
Provides convenient test execution with various options.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_tests(args):
    """Run pytest with specified options."""
    cmd = ["pytest"]
    
    # Add test path
    if args.file:
        cmd.append(args.file)
    elif args.marker:
        cmd.extend(["-m", args.marker])
    else:
        cmd.append("tests/")
    
    # Verbosity
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Coverage
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Show print statements
    if args.capture_no:
        cmd.append("-s")
    
    # Fail fast
    if args.failfast:
        cmd.append("-x")
    
    # Show durations
    if args.durations:
        cmd.extend(["--durations", str(args.durations)])
    
    # Keyword expression
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    print(f"Running: {' '.join(cmd)}\n")
    return subprocess.run(cmd)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test runner for Fridge Vision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v -cov            # Run with coverage
  python run_tests.py -m unit            # Run only unit tests
  python run_tests.py -m integration     # Run only integration tests
  python run_tests.py -k model_loader    # Run tests matching 'model_loader'
  python run_tests.py tests/test_api.py  # Run specific test file
        """
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="Specific test file to run"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output (very verbose)"
    )
    
    parser.add_argument(
        "-cov", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "-m", "--marker",
        choices=["unit", "integration", "slow", "api", "mock"],
        help="Run tests with specific marker"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        help="Only run tests matching keyword expression"
    )
    
    parser.add_argument(
        "-s", "--capture-no",
        action="store_true",
        help="Don't capture output (show print statements)"
    )
    
    parser.add_argument(
        "-x", "--failfast",
        action="store_true",
        help="Stop on first failure"
    )
    
    parser.add_argument(
        "-d", "--durations",
        type=int,
        metavar="N",
        help="Show N slowest tests"
    )
    
    args = parser.parse_args()
    
    # Check if tests directory exists
    if not Path("tests").exists():
        print("❌ Error: tests/ directory not found")
        sys.exit(1)
    
    # Run tests
    result = run_tests(args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
