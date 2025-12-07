"""
Configuration manager
"""
import json
import os


class ConfigManager:
    """Manage application configuration"""
    
    DEFAULT_CONFIG = {
        "ocr_backend": "windows",
        "target_language": "en",       # Language to translate to
        "translation_backend": "ollama",
        "google_api_key": "",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3",
        "window_opacity": 0.9,
        "result_font_size": 14
    }
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def get_defaults(self):
        """Return a copy of default configuration"""
        return self.DEFAULT_CONFIG.copy()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except:
                pass
        
        # Return default configuration
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates):
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save_config()
