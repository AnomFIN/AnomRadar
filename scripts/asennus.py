#!/usr/bin/env python3
"""
AnomRadar v2 Interactive Installer (asennus.py)

Interactive Python installer for Linux, macOS, and Unix systems.
Handles dependencies, configuration, and setup.
"""

import sys
import subprocess
import shutil
from pathlib import Path


def print_header():
    """Print installer header"""
    print("=" * 60)
    print("🔒 AnomRadar v2 Installer")
    print("=" * 60)
    print()


def check_python_version():
    """Check Python version (requires 3.8+)"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("✗ Error: Python 3.8 or higher is required")
        sys.exit(1)


def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✓ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("✗ pip not found")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"✗ requirements.txt not found at {requirements_file}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def create_config_files():
    """Create configuration files from examples"""
    print("\n⚙️  Setting up configuration...")
    
    repo_root = Path(__file__).parent.parent
    
    # Create .env if it doesn't exist
    env_example = repo_root / ".env.example"
    env_file = repo_root / ".env"
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env from .env.example")
    elif env_file.exists():
        print("⚠️  .env already exists, skipping")
    
    # Create anomradar.toml if it doesn't exist
    toml_example = repo_root / "anomradar.toml.example"
    toml_file = repo_root / "anomradar.toml"
    
    if toml_example.exists() and not toml_file.exists():
        shutil.copy(toml_example, toml_file)
        print("✓ Created anomradar.toml from anomradar.toml.example")
    elif toml_file.exists():
        print("⚠️  anomradar.toml already exists, skipping")
    
    # Create directories
    anomradar_dir = Path.home() / ".anomradar"
    anomradar_dir.mkdir(exist_ok=True)
    (anomradar_dir / "cache").mkdir(exist_ok=True)
    (anomradar_dir / "data").mkdir(exist_ok=True)
    (anomradar_dir / "logs").mkdir(exist_ok=True)
    print(f"✓ Created directories in {anomradar_dir}")
    
    return True


def create_cli_entry_point():
    """Create CLI entry point"""
    print("\n🔧 Setting up CLI entry point...")
    
    try:
        # Install package in development mode
        repo_root = Path(__file__).parent.parent
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(repo_root)],
            check=True,
            capture_output=True
        )
        print("✓ CLI entry point created (anomradar command available)")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Could not create CLI entry point")
        print("    You can still run: python -m anomradar.cli")
        return False


def run_self_check():
    """Run self-check to verify installation"""
    print("\n🔍 Running self-check...")
    
    try:
        # Import and run self-check
        from anomradar.cli import self_check
        self_check()
        return True
    except Exception as e:
        print(f"⚠️  Self-check failed: {e}")
        return False


def print_completion_message():
    """Print completion message with next steps"""
    print("\n" + "=" * 60)
    print("✅ Installation completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Customize configuration (optional):")
    print("   - Edit .env for environment variables")
    print("   - Edit anomradar.toml for advanced settings")
    print()
    print("2. Run a test scan:")
    print("   anomradar scan example.com")
    print()
    print("3. Launch the TUI:")
    print("   anomradar tui")
    print()
    print("4. Get help:")
    print("   anomradar --help")
    print()
    print("Happy scanning! 🔒")
    print()


def main():
    """Main installer function"""
    print_header()
    
    # Check requirements
    check_python_version()
    
    if not check_pip():
        print("\n✗ pip is required. Please install pip and try again.")
        sys.exit(1)
    
    # Ask for confirmation
    print("\nThis installer will:")
    print("  • Install Python dependencies")
    print("  • Create configuration files")
    print("  • Set up the anomradar command")
    print("  • Create necessary directories")
    print()
    
    response = input("Continue with installation? [Y/n]: ").strip().lower()
    if response and response not in ('y', 'yes'):
        print("Installation cancelled.")
        sys.exit(0)
    
    # Run installation steps
    success = True
    
    if not install_dependencies():
        success = False
        print("\n⚠️  Dependency installation failed")
    
    if not create_config_files():
        success = False
        print("\n⚠️  Configuration setup failed")
    
    create_cli_entry_point()  # Not critical, continue even if fails
    
    if success:
        run_self_check()
        print_completion_message()
    else:
        print("\n⚠️  Installation completed with warnings")
        print("Please check the errors above and resolve them.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
