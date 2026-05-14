"""
파견인력관리 및 파견료 정산 자동화 시스템
메인 엔트리포인트
"""
import tkinter as tk
import sys
import os

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_window import MainWindow


def main():
    root = tk.Tk()

    # DPI 인식 설정 (Windows)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
