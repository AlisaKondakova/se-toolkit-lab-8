#!/usr/bin/env python3
import json, os, sys, re
from pathlib import Path

def main():
    cfg = Path('/app/nanobot/config.json')
    txt = cfg.read_text()
    def repl(m): 
        return os.environ.get(m.group(1), m.group(0))
    txt = re.sub(r'\$\{([^}]+)\}', repl, txt)
    cfg.write_text(txt)
    print("✓ Config resolved")
    sys.stdout.flush()
    
    os.chdir('/app/nanobot')
    os.environ['PYTHONPATH'] = '/app/nanobot'
    
    # Запускаем main.py напрямую
    os.execvp("python", ["python", "main.py"])

if __name__ == "__main__":
    main()
