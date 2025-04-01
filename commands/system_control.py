# commands/system_control.py
import os
import sys
import re
import subprocess
import platform

# Import settings and modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.constants import CMD_SYSTEM_CONTROL
from logs.logger import logger

class SystemControl:
    def __init__(self, assistant):
        self.assistant = assistant
        self.system = platform.system()
        logger.info(f"System control handler initialized for {self.system} platform")
    
    def handle(self, command, is_admin=False):
        """
        Handle system control commands (admin only)
        
        Args:
            command (str): The system control command
            is_admin (bool): Whether the user has admin privileges
        
        Returns:
            bool: True if the command was handled successfully, False otherwise
        """
        # Double check admin privileges
        if not is_admin:
            logger.warning("Non-admin user attempted to use system control command")
            self.assistant.respond("Sorry, system control commands require admin mode.")
            return False
        
        try:
            # Process volume control commands
            if "volume" in command.lower():
                return self._handle_volume_control(command)
            
            # Process brightness control commands
            elif "brightness" in command.lower():
                return self._handle_brightness_control(command)
            
            # Process shutdown/restart commands
            elif "shutdown" in command.lower() or "power off" in command.lower():
                return self._handle_shutdown()
            
            elif "restart" in command.lower() or "reboot" in command.lower():
                return self._handle_restart()
            
            # Command not recognized
            else:
                logger.warning(f"Unrecognized system control command: {command}")
                self.assistant.respond("I don't understand that system control command.")
                return False
                
        except Exception as e:
            logger.error(f"Error in system control: {e}")
            self.assistant.respond("I had trouble performing that system operation.")
            return False
    
    def _handle_volume_control(self, command):
        """Handle volume up/down/mute commands"""
        # Extract direction (up, down, mute)
        if "up" in command.lower() or "increase" in command.lower():
            direction = "up"
        elif "down" in command.lower() or "decrease" in command.lower() or "lower" in command.lower():
            direction = "down"
        elif "mute" in command.lower():
            direction = "mute"
        else:
            self.assistant.respond("Please specify if you want to turn the volume up, down, or mute it.")
            return False
        
        # Get volume change level if specified
        level = 10  # Default change percentage
        match = re.search(r'(\d+)(?:\s*percent|\s*%)?', command)
        if match:
            level = int(match.group(1))
            level = max(1, min(100, level))  # Ensure level is between 1 and 100
        
        logger.info(f"Adjusting volume {direction} by {level}%")
        
        # Adjust volume based on operating system
        if self.system == 'Windows':
            return self._adjust_volume_windows(direction, level)
        elif self.system == 'Darwin':  # macOS
            return self._adjust_volume_macos(direction, level)
        elif self.system == 'Linux':
            return self._adjust_volume_linux(direction, level)
        else:
            logger.error(f"Unsupported operating system for volume control: {self.system}")
            self.assistant.respond(f"Volume control is not supported on {self.system}.")
            return False
    
    def _adjust_volume_windows(self, direction, level):
        """Adjust volume on Windows"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            # Get current volume
            current_vol = volume.GetMasterVolumeLevelScalar() * 100
            
            if direction == "up":
                new_vol = min(100, current_vol + level)
                volume.SetMasterVolumeLevelScalar(new_vol / 100, None)
                self.assistant.respond(f"Volume increased to {int(new_vol)}%")
            elif direction == "down":
                new_vol = max(0, current_vol - level)
                volume.SetMasterVolumeLevelScalar(new_vol / 100, None)
                self.assistant.respond(f"Volume decreased to {int(new_vol)}%")
            elif direction == "mute":
                mute_state = volume.GetMute()
                volume.SetMute(not mute_state, None)
                self.assistant.respond("Volume muted" if not mute_state else "Volume unmuted")
            
            return True
        except ImportError:
            # Fallback to nircmd if pycaw is not available
            try:
                if direction == "up":
                    subprocess.call(["nircmd.exe", "changesysvolume", str(655.35 * level)])
                    self.assistant.respond(f"Volume increased by {level}%")
                elif direction == "down":
                    subprocess.call(["nircmd.exe", "changesysvolume", str(-655.35 * level)])
                    self.assistant.respond(f"Volume decreased by {level}%")
                elif direction == "mute":
                    subprocess.call(["nircmd.exe", "mutesysvolume", "2"])
                    self.assistant.respond("Volume toggled mute/unmute")
                return True
            except Exception as e:
                logger.error(f"Error adjusting volume with nircmd: {e}")
                self.assistant.respond("I couldn't adjust the volume. Make sure nircmd is installed.")
                return False
        except Exception as e:
            logger.error(f"Error adjusting Windows volume: {e}")
            self.assistant.respond("I had trouble adjusting the volume.")
            return False
    
    def _adjust_volume_macos(self, direction, level):
        """Adjust volume on macOS"""
        try:
            if direction == "up":
                # Convert percentage to osascript volume (0-100)
                subprocess.call(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) + {level}) --100%"])
                self.assistant.respond(f"Volume increased by {level}%")
            elif direction == "down":
                subprocess.call(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) - {level}) --100%"])
                self.assistant.respond(f"Volume decreased by {level}%")
            elif direction == "mute":
                subprocess.call(["osascript", "-e", "set volume with output muted"])
                self.assistant.respond("Volume muted")
            return True
        except Exception as e:
            logger.error(f"Error adjusting macOS volume: {e}")
            self.assistant.respond("I had trouble adjusting the volume.")
            return False
    
    def _adjust_volume_linux(self, direction, level):
        """Adjust volume on Linux"""
        try:
            if direction == "up":
                subprocess.call(["amixer", "-D", "pulse", "sset", "Master", f"{level}%+"])
                self.assistant.respond(f"Volume increased by {level}%")
            elif direction == "down":
                subprocess.call(["amixer", "-D", "pulse", "sset", "Master", f"{level}%-"])
                self.assistant.respond(f"Volume decreased by {level}%")
            elif direction == "mute":
                subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
                self.assistant.respond("Volume toggled mute/unmute")
            return True
        except Exception as e:
            logger.error(f"Error adjusting Linux volume: {e}")
            self.assistant.respond("I had trouble adjusting the volume. Make sure ALSA tools are installed.")
            return False
    
    def _handle_brightness_control(self, command):
        """Handle screen brightness adjustment"""
        # Extract direction (up or down)
        if "up" in command.lower() or "increase" in command.lower():
            direction = "up"
        elif "down" in command.lower() or "decrease" in command.lower() or "lower" in command.lower():
            direction = "down"
        else:
            self.assistant.respond("Please specify if you want to turn the brightness up or down.")
            return False
        
        # Get brightness change level if specified
        level = 10  # Default change percentage
        match = re.search(r'(\d+)(?:\s*percent|\s*%)?', command)
        if match:
            level = int(match.group(1))
            level = max(1, min(100, level))  # Ensure level is between 1 and 100
        
        logger.info(f"Adjusting brightness {direction} by {level}%")
        
        # Adjust brightness based on operating system
        if self.system == 'Windows':
            return self._adjust_brightness_windows(direction, level)
        elif self.system == 'Darwin':  # macOS
            return self._adjust_brightness_macos(direction, level)
        elif self.system == 'Linux':
            return self._adjust_brightness_linux(direction, level)
        else:
            logger.error(f"Unsupported operating system for brightness control: {self.system}")
            self.assistant.respond(f"Brightness control is not supported on {self.system}.")
            return False
    
    def _adjust_brightness_windows(self, direction, level):
        """Adjust screen brightness on Windows"""
        try:
            import wmi
            
            # Connect to WMI
            wmi_interface = wmi.WMI(namespace='wmi')
            monitors = wmi_interface.WmiMonitorBrightnessMethods()
            
            if not monitors:
                logger.warning("No monitors found for brightness adjustment")
                self.assistant.respond("I couldn't find any monitors to adjust brightness.")
                return False
            
            # Get current brightness
            brightness_info = wmi_interface.WmiMonitorBrightness()[0]
            current_brightness = brightness_info.CurrentBrightness
            
            # Calculate new brightness
            if direction == "up":
                new_brightness = min(100, current_brightness + level)
            else:  # direction == "down"
                new_brightness = max(0, current_brightness - level)
            
            # Set new brightness
            for monitor in monitors:
                monitor.WmiSetBrightness(new_brightness, 0)
            
            self.assistant.respond(f"Brightness {'increased' if direction == 'up' else 'decreased'} to {new_brightness}%")
            return True
        except ImportError:
            logger.error("WMI module not found for Windows brightness control")
            self.assistant.respond("I couldn't adjust the brightness. The WMI module is not installed.")
            return False
        except Exception as e:
            logger.error(f"Error adjusting Windows brightness: {e}")
            self.assistant.respond("I had trouble adjusting the brightness.")
            return False
    
    def _adjust_brightness_macos(self, direction, level):
        """Adjust screen brightness on macOS"""
        try:
            if direction == "up":
                # Use AppleScript to increase brightness
                subprocess.call(["osascript", "-e", "tell application \"System Events\" to key code 144"])
                self.assistant.respond("Brightness increased")
            else:  # direction == "down"
                # Use AppleScript to decrease brightness
                subprocess.call(["osascript", "-e", "tell application \"System Events\" to key code 145"])
                self.assistant.respond("Brightness decreased")
            return True
        except Exception as e:
            logger.error(f"Error adjusting macOS brightness: {e}")
            self.assistant.respond("I had trouble adjusting the brightness.")
            return False
    
    def _adjust_brightness_linux(self, direction, level):
        """Adjust screen brightness on Linux"""
        try:
            # Find the brightness file
            brightness_file = "/sys/class/backlight/intel_backlight/brightness"
            max_brightness_file = "/sys/class/backlight/intel_backlight/max_brightness"
            
            # If intel_backlight doesn't exist, try acpi_video0
            if not os.path.exists(brightness_file):
                brightness_file = "/sys/class/backlight/acpi_video0/brightness"
                max_brightness_file = "/sys/class/backlight/acpi_video0/max_brightness"
            
            # Read current brightness
            with open(brightness_file, 'r') as f:
                current_brightness = int(f.read().strip())
            
            # Read max brightness
            with open(max_brightness_file, 'r') as f:
                max_brightness = int(f.read().strip())
            
            # Calculate current percentage
            current_percent = (current_brightness / max_brightness) * 100
            
            # Calculate new percentage
            if direction == "up":
                new_percent = min(100, current_percent + level)
            else:  # direction == "down"
                new_percent = max(5, current_percent - level)  # Don't go below 5%
            
            # Calculate new brightness value
            new_brightness = int((new_percent / 100) * max_brightness)
            
            # Write new brightness with sudo
            sudo_cmd = ["sudo", "sh", "-c", f"echo {new_brightness} > {brightness_file}"]
            subprocess.call(sudo_cmd)
            
            self.assistant.respond(f"Brightness {'increased' if direction == 'up' else 'decreased'} to {int(new_percent)}%")
            return True
        except Exception as e:
            logger.error(f"Error adjusting Linux brightness: {e}")
            self.assistant.respond("I had trouble adjusting the brightness. Make sure you have proper permissions.")
            return False
    
    def _handle_shutdown(self):
        """Handle system shutdown command"""
        self.assistant.respond("Are you sure you want to shut down the system? Say 'yes' to confirm.")
        
        # Listen for confirmation
        confirmation = self.assistant.speech_recognizer.listen(phrase_time_limit=3)
        
        if confirmation and ('yes' in confirmation.lower() or 'yeah' in confirmation.lower() or 'confirm' in confirmation.lower()):
            self.assistant.respond("Shutting down the system now. Goodbye!")
            logger.info("Executing system shutdown")
            
            # Shutdown based on operating system
            if self.system == 'Windows':
                subprocess.call(["shutdown", "/s", "/t", "10"])
            elif self.system == 'Darwin':  # macOS
                subprocess.call(["osascript", "-e", 'tell app "System Events" to shut down'])
            elif self.system == 'Linux':
                subprocess.call(["sudo", "shutdown", "-h", "now"])
            
            return True
        else:
            self.assistant.respond("Shutdown cancelled.")
            return False
    
    def _handle_restart(self):
        """Handle system restart command"""
        self.assistant.respond("Are you sure you want to restart the system? Say 'yes' to confirm.")
        
        # Listen for confirmation
        confirmation = self.assistant.speech_recognizer.listen(phrase_time_limit=3)
        
        if confirmation and ('yes' in confirmation.lower() or 'yeah' in confirmation.lower() or 'confirm' in confirmation.lower()):
            self.assistant.respond("Restarting the system now. Goodbye!")
            logger.info("Executing system restart")
            
            # Restart based on operating system
            if self.system == 'Windows':
                subprocess.call(["shutdown", "/r", "/t", "10"])
            elif self.system == 'Darwin':  # macOS
                subprocess.call(["osascript", "-e", 'tell app "System Events" to restart'])
            elif self.system == 'Linux':
                subprocess.call(["sudo", "shutdown", "-r", "now"])
            
            return True
        else:
            self.assistant.respond("Restart cancelled.")
            return False