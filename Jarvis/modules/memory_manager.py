import os
import json
import config

class MemoryManager:
    """Manages short-term context and long-term memory for Jarvis."""
    
    def __init__(self):
        self.memory_file = os.path.join(config.MEMORY_DIR, "chat_memory.json")
        self.context_history = []
        self._load_memory()
        
    def _load_memory(self):
        os.makedirs(config.MEMORY_DIR, exist_ok=True)
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Load last 10 messages for short-term context
                    self.context_history = data.get("history", [])[-10:]
            except Exception as e:
                print(f"[Memory Error] {e}")
                self.context_history = []
                
    def _save_memory(self):
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({"history": self.context_history}, f, indent=2)
        except Exception as e:
            print(f"[Memory Error] {e}")

    def add_message(self, role, content):
        """Add a message to the context history."""
        self.context_history.append({"role": role, "content": content})
        if len(self.context_history) > 20: # Keep last 20 messages in memory
            self.context_history = self.context_history[-20:]
        self._save_memory()
        
    def get_context(self):
        """Return the current context history."""
        return self.context_history
        
    def clear_context(self):
        """Clear the current context."""
        self.context_history = []
        self._save_memory()

# Global memory instance
memory = MemoryManager()
