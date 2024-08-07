from kivy.core.window import Window

from dataclasses import dataclass


@dataclass
class MouseCaller:
    width: int = 0
    height: int = 0

    @property
    def center(self) -> (int, int):
        return Window.mouse_pos

    @staticmethod
    def to_window(*args):
        return args
