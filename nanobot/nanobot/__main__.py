#!/usr/bin/env python3
import sys, os
from pathlib import Path

def main():
    # Добавляем путь к модулям
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Импортируем и запускаем агент
    from main import run_agent  # или из run.py
    run_agent()

if __name__ == "__main__":
    main()
