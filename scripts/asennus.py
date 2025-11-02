#!/usr/bin/env python3
"""
AnomRadar v2 Interactive Installation Wizard (asennus.py)

This installer will:
1. Check Python version
2. Create virtual environment
3. Install requirements
4. Create configuration files (.env and anomradar.toml)
5. Set up directory structure
6. Create command alias (Unix only)
7. Run self-check to verify installation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def print_step(step: int, message: str):
    """Print a step message."""
    print(f"{Colors.CYAN}[Step {step}] {message}{Colors.END}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False
    return True


def run_command(cmd: list, cwd: Optional[str] = None, capture: bool = False) -> tuple:
    """
    Run a shell command.
    
    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        capture: Capture output
    
    Returns:
        Tuple of (success, output)
    """
    try:
        if capture:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        else:
            subprocess.run(cmd, cwd=cwd, check=True)
            return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)
    except FileNotFoundError:
        return False, "Command not found"


def main():
    """Main installer function."""
    print_header("AnomRadar v2 Installation Wizard")
    
    print(f"{Colors.BLUE}Welcome to AnomRadar v2 setup!{Colors.END}")
    print("This wizard will guide you through the installation process.\n")
    
    # Get installation directory
    install_dir = Path.cwd()
    print(f"Installation directory: {install_dir}\n")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    if check_python_version():
        print_success(f"Python {sys.version.split()[0]} (OK)")
    else:
        print_error(f"Python {sys.version.split()[0]} is too old")
        print("AnomRadar v2 requires Python 3.8 or higher")
        sys.exit(1)
    
    # Step 2: Create virtual environment
    print_step(2, "Creating virtual environment")
    venv_dir = install_dir / ".venv"
    
    if venv_dir.exists():
        print_warning(f"Virtual environment already exists at {venv_dir}")
        response = input("Recreate it? (y/N): ").strip().lower()
        if response == 'y':
            import shutil
            shutil.rmtree(venv_dir)
        else:
            print("Using existing virtual environment")
    
    if not venv_dir.exists():
        success, output = run_command([sys.executable, "-m", "venv", ".venv"])
        if success:
            print_success("Virtual environment created")
        else:
            print_error(f"Failed to create virtual environment: {output}")
            sys.exit(1)
    
    # Determine pip path
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    # Step 3: Upgrade pip
    print_step(3, "Upgrading pip")
    success, _ = run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    if success:
        print_success("Pip upgraded")
    else:
        print_warning("Failed to upgrade pip (continuing anyway)")
    
    # Step 4: Install requirements
    print_step(4, "Installing requirements")
    requirements_file = install_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print_error(f"requirements.txt not found at {requirements_file}")
        sys.exit(1)
    
    print("Installing packages (this may take a few minutes)...")
    success, output = run_command([str(pip_path), "install", "-r", "requirements.txt"])
    if success:
        print_success("All requirements installed")
    else:
        print_error(f"Failed to install requirements: {output}")
        sys.exit(1)
    
    # Step 5: Create directory structure
    print_step(5, "Creating directory structure")
    home_dir = Path.home()
    anomradar_home = home_dir / ".anomradar"
    
    dirs_to_create = [
        anomradar_home,
        anomradar_home / "cache",
        anomradar_home / "logs",
        anomradar_home / "reports",
    ]
    
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)
    
    print_success(f"Directory structure created at {anomradar_home}")
    
    # Step 6: Create configuration files
    print_step(6, "Creating configuration files")
    
    # Copy .env.example to .env if it doesn't exist
    env_example = install_dir / ".env.example"
    env_file = install_dir / ".env"
    
    if env_example.exists() and not env_file.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print_success(".env file created")
    elif env_file.exists():
        print_warning(".env file already exists (not overwriting)")
    else:
        print_warning(".env.example not found (skipping .env creation)")
    
    # Copy anomradar.toml.example to ~/.anomradar/anomradar.toml if it doesn't exist
    toml_example = install_dir / "anomradar.toml.example"
    toml_file = anomradar_home / "anomradar.toml"
    
    if toml_example.exists() and not toml_file.exists():
        import shutil
        shutil.copy(toml_example, toml_file)
        print_success(f"Configuration file created at {toml_file}")
    elif toml_file.exists():
        print_warning(f"Configuration file already exists at {toml_file} (not overwriting)")
    else:
        print_warning("anomradar.toml.example not found (skipping)")
    
    # Step 7: Create command alias (Unix only)
    if platform.system() != "Windows":
        print_step(7, "Creating command alias")
        
        shell_rc = None
        shell = os.environ.get("SHELL", "")
        
        if "bash" in shell:
            shell_rc = home_dir / ".bashrc"
        elif "zsh" in shell:
            shell_rc = home_dir / ".zshrc"
        
        if shell_rc and shell_rc.exists():
            alias_line = f'alias anomradar="{python_path} -m anomradar.cli"'
            
            # Check if alias already exists
            with open(shell_rc, "r") as f:
                content = f.read()
            
            if "alias anomradar=" not in content:
                with open(shell_rc, "a") as f:
                    f.write(f"\n# AnomRadar v2 alias\n{alias_line}\n")
                print_success(f"Alias added to {shell_rc}")
                print(f"  Run: source {shell_rc}")
                print(f"  Or restart your terminal")
            else:
                print_warning("Alias already exists")
        else:
            print_warning("Could not detect shell config file")
            print(f"  To use AnomRadar, run: {python_path} -m anomradar.cli")
    else:
        print_step(7, "Windows setup")
        print(f"To use AnomRadar on Windows:")
        print(f"  1. Activate virtual environment: .venv\\Scripts\\activate")
        print(f"  2. Run: python -m anomradar.cli")
    
    # Step 8: Run self-check
    print_step(8, "Running self-check")
    print()
    success, _ = run_command([str(python_path), "-m", "anomradar.cli", "self-check"])
    
    if success:
        print()
        print_success("Installation completed successfully!")
    else:
        print()
        print_warning("Installation completed with warnings")
        print("Run 'anomradar self-check' for diagnostics")
    
    # Final instructions
    print_header("Next Steps")
    
    if platform.system() == "Windows":
        print(f"{Colors.BLUE}1. Activate virtual environment:{Colors.END}")
        print(f"   .venv\\Scripts\\activate")
        print(f"\n{Colors.BLUE}2. Run your first scan:{Colors.END}")
        print(f"   python -m anomradar.cli scan example.com")
    else:
        print(f"{Colors.BLUE}1. Reload shell configuration:{Colors.END}")
        if shell_rc:
            print(f"   source {shell_rc}")
        print(f"\n{Colors.BLUE}2. Run your first scan:{Colors.END}")
        print(f"   anomradar scan example.com")
    
    print(f"\n{Colors.BLUE}3. Explore other commands:{Colors.END}")
    print(f"   anomradar --help")
    print(f"   anomradar tui")
    print(f"   anomradar doctor")
    
    print(f"\n{Colors.GREEN}Happy scanning! 🔒{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Installation cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Installation failed: {e}{Colors.END}")
        sys.exit(1)
