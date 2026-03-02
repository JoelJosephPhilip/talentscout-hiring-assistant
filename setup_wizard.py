"""
TalentScout Hiring Assistant - Setup Wizard

Interactive CLI setup wizard for first-time configuration.
Helps users choose between Groq (FREE), OpenAI (Paid), or Ollama (FREE local).

Usage:
    python setup_wizard.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional


class SetupWizard:
    """Interactive setup wizard for TalentScout Hiring Assistant"""
    
    GROQ_CONSOLE_URL = "https://console.groq.com"
    OPENAI_PLATFORM_URL = "https://platform.openai.com"
    OLLAMA_DOWNLOAD_URL = "https://ollama.com/download"
    
    def __init__(self):
        self.env_file = Path(".env")
        self.system = platform.system().lower()
    
    def run(self):
        """Run the setup wizard"""
        self.display_welcome()
        choice = self.get_user_choice()
        
        if choice == "1":
            self.setup_groq()
        elif choice == "2":
            self.setup_openai()
        elif choice == "3":
            self.setup_ollama()
        elif choice == "4":
            self.setup_auto()
        else:
            print("\n❌ Invalid choice. Exiting...")
            sys.exit(1)
        
        self.display_complete()
    
    def display_welcome(self):
        """Display welcome banner"""
        print("\n" + "=" * 60)
        print("   TalentScout Hiring Assistant - Setup Wizard")
        print("=" * 60)
        print("\nWelcome! This wizard will help you configure the application.\n")
        print("How would you like to run the application?\n")
        print("  [1] Groq API (FREE - Fast cloud inference)")
        print("      ↳ Requires API key from console.groq.com")
        print("      ↳ Best for most users - Free tier available\n")
        print("  [2] OpenAI GPT-4o (Cloud - Best quality)")
        print("      ↳ Requires API key (paid)")
        print("      ↳ Premium quality, usage-based pricing\n")
        print("  [3] Ollama (FREE - Runs locally on your machine)")
        print("      ↳ No API key needed")
        print("      ↳ ~4GB download for Llama 3.2 model\n")
        print("  [4] Auto-detect (Try all options)")
        print("      ↳ Will try: Groq → OpenAI → Ollama")
        print("      ↳ Configure multiple providers\n")
    
    def get_user_choice(self) -> str:
        """Get user's choice"""
        while True:
            choice = input("Enter your choice (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    def setup_groq(self):
        """Setup Groq API"""
        print("\n" + "-" * 60)
        print("   Groq API Setup")
        print("-" * 60)
        print(f"\nTo get your FREE Groq API key:\n")
        print(f"  1. Visit: {self.GROQ_CONSOLE_URL}")
        print("  2. Sign up or log in")
        print("  3. Go to API Keys section")
        print("  4. Create a new API key")
        print("  5. Copy and paste it below\n")
        
        api_key = self.prompt_api_key("Groq")
        if api_key:
            print("\n✓ Validating API key...")
            if self.validate_groq_key(api_key):
                print("✓ API key is valid!")
                self.save_env_file(groq_key=api_key)
            else:
                print("⚠ Could not validate API key, saving anyway...")
                self.save_env_file(groq_key=api_key)
    
    def setup_openai(self):
        """Setup OpenAI API"""
        print("\n" + "-" * 60)
        print("   OpenAI API Setup")
        print("-" * 60)
        print(f"\nTo get your OpenAI API key:\n")
        print(f"  1. Visit: {self.OPENAI_PLATFORM_URL}")
        print("  2. Sign up or log in")
        print("  3. Go to API Keys section")
        print("  4. Create a new API key")
        print("  5. Copy and paste it below\n")
        
        api_key = self.prompt_api_key("OpenAI")
        if api_key:
            print("\n✓ Validating API key...")
            if self.validate_openai_key(api_key):
                print("✓ API key is valid!")
                self.save_env_file(openai_key=api_key)
            else:
                print("⚠ Could not validate API key, saving anyway...")
                self.save_env_file(openai_key=api_key)
    
    def setup_ollama(self):
        """Setup Ollama local LLM"""
        print("\n" + "-" * 60)
        print("   Ollama Setup")
        print("-" * 60)
        
        if self.check_ollama_installed():
            print("\n✓ Ollama is already installed!")
        else:
            print("\n✗ Ollama is not installed.")
            print("\nWould you like to install Ollama automatically? (Y/N): ", end="")
            choice = input().strip().upper()
            
            if choice == "Y":
                self.install_ollama()
            else:
                print(f"\nPlease install Ollama manually from: {self.OLLAMA_DOWNLOAD_URL}")
                print("After installation, run this wizard again.")
                sys.exit(0)
        
        print("\n✓ Checking for Llama 3.2 model...")
        if not self.check_model_installed("llama3.2"):
            print("Downloading Llama 3.2 model (~4GB)...")
            self.pull_model("llama3.2")
        else:
            print("✓ Llama 3.2 model is already installed!")
        
        self.save_env_file(ollama=True)
    
    def setup_auto(self):
        """Setup with auto-detect (configure multiple providers)"""
        print("\n" + "-" * 60)
        print("   Auto-Detect Setup")
        print("-" * 60)
        print("\nYou can configure multiple providers. The app will try them in order:")
        print("  1. Groq (if API key set)")
        print("  2. OpenAI (if API key set)")
        print("  3. Ollama (if installed)\n")
        
        groq_key = None
        openai_key = None
        ollama = False
        
        print("Configure Groq? (Y/N): ", end="")
        if input().strip().upper() == "Y":
            print(f"\nGet your FREE API key at: {self.GROQ_CONSOLE_URL}")
            groq_key = self.prompt_api_key("Groq")
        
        print("\nConfigure OpenAI? (Y/N): ", end="")
        if input().strip().upper() == "Y":
            print(f"\nGet your API key at: {self.OPENAI_PLATFORM_URL}")
            openai_key = self.prompt_api_key("OpenAI")
        
        print("\nConfigure Ollama? (Y/N): ", end="")
        if input().strip().upper() == "Y":
            ollama = True
            if not self.check_ollama_installed():
                print("\nInstalling Ollama...")
                self.install_ollama()
            if not self.check_model_installed("llama3.2"):
                print("Downloading Llama 3.2 model...")
                self.pull_model("llama3.2")
        
        self.save_env_file(groq_key=groq_key, openai_key=openai_key, ollama=ollama)
    
    def prompt_api_key(self, provider: str) -> Optional[str]:
        """Prompt user for API key"""
        while True:
            print(f"Enter your {provider} API key: ", end="")
            try:
                api_key = input().strip()
            except EOFError:
                return None
            
            if not api_key:
                print("❌ API key cannot be empty.")
                continue
            
            if len(api_key) < 10:
                print("❌ API key seems too short. Please check and try again.")
                continue
            
            return api_key
    
    def validate_groq_key(self, api_key: str) -> bool:
        """Validate Groq API key"""
        try:
            import requests
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def validate_openai_key(self, api_key: str) -> bool:
        """Validate OpenAI API key"""
        try:
            import requests
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def check_ollama_installed(self) -> bool:
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_model_installed(self, model: str) -> bool:
        """Check if a specific model is installed"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return model in result.stdout
        except Exception:
            return False
    
    def install_ollama(self):
        """Install Ollama using winget (Windows) or Homebrew (macOS)"""
        print(f"\nInstalling Ollama for {self.system}...")
        
        if self.system == "windows":
            print("Using Windows Package Manager (winget)...")
            try:
                result = subprocess.run(
                    ["winget", "install", "Ollama.Ollama", "--accept-source-agreements", "--accept-package-agreements"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    print("✓ Ollama installed successfully!")
                else:
                    print(f"⚠ Installation may have issues: {result.stderr}")
            except FileNotFoundError:
                print("⚠ winget not found. Please install from: https://ollama.com/download/windows")
            except Exception as e:
                print(f"⚠ Installation error: {e}")
        
        elif self.system == "darwin":
            print("Using Homebrew...")
            try:
                subprocess.run(["brew", "install", "ollama"], check=True, timeout=300)
                print("✓ Ollama installed successfully!")
            except FileNotFoundError:
                print("⚠ Homebrew not found. Please install from: https://ollama.com/download/macOS")
            except Exception as e:
                print(f"⚠ Installation error: {e}")
        
        else:
            print(f"Please install Ollama manually from: {self.OLLAMA_DOWNLOAD_URL}")
    
    def pull_model(self, model: str):
        """Pull a model using Ollama"""
        print(f"Pulling {model} model...")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"✓ {model} model installed!")
        except Exception as e:
            print(f"⚠ Error pulling model: {e}")
    
    def save_env_file(self, groq_key: Optional[str] = None, openai_key: Optional[str] = None, ollama: bool = False):
        """Save configuration to .env file"""
        env_content = []
        
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                env_content = f.readlines()
        
        def update_or_add(lines: list, key: str, value: str) -> list:
            """Update existing key or add new one"""
            found = False
            new_lines = []
            for line in lines:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={value}\n")
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f"{key}={value}\n")
            return new_lines
        
        if groq_key:
            env_content = update_or_add(env_content, "GROQ_API_KEY", groq_key)
            env_content = update_or_add(env_content, "GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if openai_key:
            env_content = update_or_add(env_content, "OPENAI_API_KEY", openai_key)
        
        if ollama:
            env_content = update_or_add(env_content, "OLLAMA_BASE_URL", "http://localhost:11434")
            env_content = update_or_add(env_content, "OLLAMA_MODEL", "llama3.2")
        
        env_content = update_or_add(env_content, "LLM_PREFERRED", "auto")
        
        with open(self.env_file, "w") as f:
            f.writelines(env_content)
        
        print(f"\n✓ Configuration saved to {self.env_file}")
    
    def display_complete(self):
        """Display completion message"""
        print("\n" + "=" * 60)
        print("   Setup Complete!")
        print("=" * 60)
        print("\n✓ Configuration saved successfully!")
        print("\nYou can now run the application:")
        print("  - Windows: Double-click run.bat")
        print("  - macOS/Linux: Run ./run.sh")
        print("\nOr start manually:")
        print("  streamlit run src/app.py")
        print("\n" + "=" * 60 + "\n")


def main():
    """Main entry point"""
    wizard = SetupWizard()
    wizard.run()


if __name__ == "__main__":
    main()
