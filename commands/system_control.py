# system_control.py - Handles system control functions

import os
import platform
import subprocess
import re
from logs.logger import log_action, log_error
from config.constants import SYSTEM_CONTROL_KEYWORDS, UNAUTHORIZED_MESSAGE

def control_system(command, is_admin):
    """
    Control system functions based on the command.
    
    Args:
        command (str): The system control command
        is_admin (bool): Whether the user is authenticated as admin
        
    Returns:
        str: Response message
    """
    try:
        # Convert command to lowercase for easier matching
        cmd_lower = command.lower()
        
        # Check for volume control
        if "volume" in cmd_lower:
            return control_volume(cmd_lower)
            
        # Check for shutdown/restart (admin only)
        elif any(word in cmd_lower for word in ["shutdown", "restart", "reboot"]):
            if not is_admin:
                log_action("Unauthorized shutdown/restart attempt")
                return UNAUTHORIZED_MESSAGE
            else:
                return power_control(cmd_lower)
                
        # Check for system updates (admin only)
        elif "update" in cmd_lower and "system" in cmd_lower:
            if not is_admin:
                log_action("Unauthorized system update attempt")
                return UNAUTHORIZED_MESSAGE
            else:
                return check_for_updates()
                
        # Unknown system command
        else:
            return "I'm not sure how to perform that system operation."
            
    except Exception as e:
        log_error("Error in system control", e)
        return "I encountered an error trying to control the system."

def control_volume(command):
    """
    Control system volume.
    
    Args:
        command (str): The volume control command
        
    Returns:
        str: Response message
    """
    try:
        current_os = platform.system().lower()
        
        # Extract volume level if specified
        volume_level = None
        level_match = re.search(r'(\d+)(?:\s*%)?', command)
        if level_match:
            volume_level = int(level_match.group(1))
            
        # Check for volume up/down/mute
        if "up" in command or "increase" in command:
            if current_os == "windows":
                # Windows volume up
                for _ in range(5):  # Press volume up key multiple times
                    subprocess.run("powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]175)", shell=True)
            elif current_os == "darwin":  # macOS
                subprocess.run("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'", shell=True)
            elif current_os == "linux":
                subprocess.run("amixer -D pulse sset Master 10%+", shell=True)
                
            return "I've increased the volume."
            
        elif "down" in command or "decrease" in command or "lower" in command:
            if current_os == "windows":
                # Windows volume down
                for _ in range(5):  # Press volume down key multiple times
                    subprocess.run("powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]174)", shell=True)
            elif current_os == "darwin":  # macOS
                subprocess.run("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'", shell=True)
            elif current_os == "linux":
                subprocess.run("amixer -D pulse sset Master 10%-", shell=True)
                
            return "I've decreased the volume."
            
        elif "mute" in command or "unmute" in command:
            if current_os == "windows":
                # Windows mute toggle
                subprocess.run("powershell -c (New-Object -ComObject WScript.Shell).SendKeys([char]173)", shell=True)
            elif current_os == "darwin":  # macOS
                subprocess.run("osascript -e 'set volume output muted not (output muted of (get volume settings))'", shell=True)
            elif current_os == "linux":
                subprocess.run("amixer -D pulse set Master 1+ toggle", shell=True)
                
            return "I've toggled mute."
            
        elif volume_level is not None:
            # Set to specific volume level
            if volume_level < 0 or volume_level > 100:
                return "Volume level must be between 0 and 100 percent."
                
            if current_os == "windows":
                # Windows set volume (approximate)
                level = int((65535 * volume_level) / 100)
                subprocess.run(f"powershell -c \"[Audio]::Volume = {volume_level / 100}\"", shell=True)
            elif current_os == "darwin":  # macOS
                subprocess.run(f"osascript -e 'set volume output volume {volume_level}'", shell=True)
            elif current_os == "linux":
                subprocess.run(f"amixer -D pulse sset Master {volume_level}%", shell=True)
                
            return f"I've set the volume to {volume_level} percent."
            
        else:
            return "Please specify how you want to adjust the volume (up, down, mute, or a specific percentage)."
            
    except Exception as e:
        log_error("Error controlling volume", e)
        return "I encountered an error trying to control the volume."

def power_control(command):
    """
    Control system power (shutdown/restart).
    
    Args:
        command (str): The power control command
        
    Returns:
        str: Response message
    """
    try:
        current_os = platform.system().lower()
        
        # Check for shutdown
        if "shutdown" in command:
            log_action("Executing shutdown command")
            
            if current_os == "windows":
                subprocess.run("shutdown /s /t 60", shell=True)
                return "I'll shut down your computer in 60 seconds. To cancel, say 'cancel shutdown'."
            elif current_os in ["darwin", "linux"]:  # macOS or Linux
                subprocess.run("sudo shutdown -h +1", shell=True)
                return "I'll shut down your computer in 1 minute. To cancel, use 'sudo shutdown -c'."
            else:
                return "I don't know how to shut down this operating system."
                
        # Check for restart
        elif any(word in command for word in ["restart", "reboot"]):
            log_action("Executing restart command")
            
            if current_os == "windows":
                subprocess.run("shutdown /r /t 60", shell=True)
                return "I'll restart your computer in 60 seconds. To cancel, say 'cancel restart'."
            elif current_os in ["darwin", "linux"]:  # macOS or Linux
                subprocess.run("sudo shutdown -r +1", shell=True)
                return "I'll restart your computer in 1 minute. To cancel, use 'sudo shutdown -c'."
            else:
                return "I don't know how to restart this operating system."
                
        # Check for cancel
        elif "cancel" in command:
            log_action("Cancelling power command")
            
            if current_os == "windows":
                subprocess.run("shutdown /a", shell=True)
                return "I've cancelled the shutdown or restart."
            elif current_os in ["darwin", "linux"]:  # macOS or Linux
                subprocess.run("sudo shutdown -c", shell=True)
                return "I've cancelled the shutdown or restart."
            else:
                return "I don't know how to cancel power commands on this operating system."
                
        else:
            return "Please specify whether you want to shut down or restart the computer."
            
    except Exception as e:
        log_error("Error in power control", e)
        return "I encountered an error trying to control system power."

def check_for_updates():
    """
    Check for system updates.
    
    Returns:
        str: Response message
    """
    try:
        current_os = platform.system().lower()
        
        log_action("Checking for system updates")
        
        if current_os == "windows":
            # Windows update check
            subprocess.Popen("start ms-settings:windowsupdate", shell=True)
            return "I've opened Windows Update for you to check for updates."
            
        elif current_os == "darwin":  # macOS
            # macOS update check
            subprocess.Popen("open macappstore://showUpdatesPage", shell=True)
            return "I've opened the App Store updates page for you to check for updates."
            
        elif current_os == "linux":
            # Linux update check (for apt-based systems)
            try:
                # Try to use apt update
                update_process = subprocess.Popen(
                    "sudo apt update",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = update_process.communicate()
                
                if update_process.returncode == 0:
                    return "System update check completed. Please use the terminal to see available updates."
                else:
                    return "I couldn't check for updates. Your system might not use apt, or there might be an issue with permissions."
            except:
                return "I couldn't check for updates on your Linux system."
                
        else:
            return "I don't know how to check for updates on this operating system."
            
    except Exception as e:
        log_error("Error checking for updates", e)
        return "I encountered an error trying to check for system updates."