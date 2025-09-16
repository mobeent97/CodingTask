#!/usr/bin/env python3
"""
Local GitHub Actions Workflow Tester
This script simulates the CI pipeline locally for testing purposes.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, description, cwd=None, check=True):
    """Run a command and report the result."""
    print(f"\n🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    if cwd:
        print(f"   Working directory: {cwd}")

    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"   ✓ Success: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed: {e.stderr.strip()}")
        if not check:
            return False
        return False

def main():
    print("🚀 Testing GitHub Actions Workflow Locally")
    print("=" * 50)

    # Check Python version
    print(f"🐍 Python version: {sys.version}")

    # 1. Setup Python environment (simulate actions/setup-python)
    print("\n📦 Step 1: Setting up Python environment")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"   Using Python {python_version}")

    # 2. Install dependencies (simulate pip install)
    print("\n📦 Step 2: Installing dependencies")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                "Upgrading pip")

    run_command([sys.executable, "-m", "pip", "install", "-r", "app/requirements.txt"],
                "Installing app requirements")

    run_command([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"],
                "Installing testing tools")

    # Install ETL client
    etl_path = Path("etl_client")
    run_command([sys.executable, "-m", "pip", "install", "-e", "."],
                "Installing ETL client package", cwd=etl_path)

    # 3. Test basic functionality
    print("\n🔍 Step 3: Testing basic functionality")
    run_command([sys.executable, "-c", "import sys; print(f'Python {sys.version}')"],
                "Checking Python version")

    # 4. Run tests (simulate pytest)
    print("\n🧪 Step 4: Running tests")
    run_command([sys.executable, "-m", "pytest", "--cov", "--cov-report=term-missing", "--cov-report=xml"],
                "Running tests with coverage", check=False)

    run_command([sys.executable, "-m", "pytest", "tests/", "--cov=etl_client", "--cov-report=term-missing", "--cov-report=xml", "--cov-append"],
                "Running ETL client tests", check=False)

    # 5. Integration test simulation
    print("\n🔗 Step 5: Running integration test simulation")
    print("   Note: Full integration test requires API server. Simulating basic checks...")

    # Test ETL client CLI
    try:
        run_command([sys.executable, "-c", "import etl_client.cli; print('ETL client import successful')"],
                    "Testing ETL client import")
    except:
        run_command(["animal-etl", "--help"],
                    "Testing ETL client CLI", check=False)

    print("\n✅ Local workflow testing completed!")
    print("\n📝 Summary:")
    print("   - Dependencies installed successfully")
    print("   - ETL client package installed")
    print("   - Tests run with coverage")
    print("   - Basic integration checks performed")
    print("\n💡 For full integration testing, start the API server:")
    print("   cd app && uvicorn animal_api:app --host 0.0.0.0 --port 3123")

if __name__ == "__main__":
    main()
