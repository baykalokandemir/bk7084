import sys
import os
print(f"Python Executable: {sys.executable}")
print(f"Sys Path: {sys.path}")
try:
    import imgui
    print(f"Imgui File: {imgui.__file__}")
except ImportError as e:
    print(f"ImportError: {e}")
