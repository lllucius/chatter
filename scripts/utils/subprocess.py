"""Common subprocess utilities for SDK generation."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class ProcessError(Exception):
    """Exception raised when a subprocess fails."""
    
    def __init__(self, command: List[str], returncode: int, stdout: str, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"Command failed with exit code {returncode}: {' '.join(command)}")


def run_command(
    cmd: List[str], 
    description: str,
    cwd: Optional[Path] = None,
    capture_output: bool = True,
    check: bool = True,
    timeout: Optional[int] = None
) -> Tuple[bool, str, str]:
    """
    Run a command and return success status with output.
    
    Args:
        cmd: Command to run as a list of strings
        description: Human-readable description for logging
        cwd: Working directory to run command in
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise exception on non-zero exit
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success, stdout, stderr)
        
    Raises:
        ProcessError: If check=True and command fails
    """
    print(f"🔧 {description}...")
    print(f"   Command: {' '.join(cmd)}")
    if cwd:
        print(f"   Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            cwd=str(cwd) if cwd else None,
            timeout=timeout
        )
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            if capture_output:
                if result.stdout:
                    print(f"   stdout: {result.stdout}")
                if result.stderr:
                    print(f"   stderr: {result.stderr}")
                    
        if check and not success:
            raise ProcessError(cmd, result.returncode, result.stdout, result.stderr)
            
        return success, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired as e:
        print(f"❌ {description} timed out after {timeout} seconds")
        if check:
            raise ProcessError(cmd, -1, "", f"Timeout after {timeout} seconds")
        return False, "", f"Timeout after {timeout} seconds"
    
    except FileNotFoundError:
        print(f"❌ {description} failed: Command not found: {cmd[0]}")
        if check:
            raise ProcessError(cmd, -1, "", f"Command not found: {cmd[0]}")
        return False, "", f"Command not found: {cmd[0]}"


def check_command_available(command: str) -> bool:
    """Check if a command is available in the system PATH."""
    try:
        subprocess.run(
            ["which", command] if sys.platform != "win32" else ["where", command],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def ensure_command_available(command: str, install_hint: Optional[str] = None) -> None:
    """Ensure a command is available, raising an error with install hint if not."""
    if not check_command_available(command):
        error_msg = f"Required command '{command}' not found in PATH"
        if install_hint:
            error_msg += f". Install with: {install_hint}"
        raise ProcessError([command], -1, "", error_msg)