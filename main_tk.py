"""Visualize ax+b sequences on a circle with Tkinter (alternate UI to main.py)."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

POINT_RADIUS = 14
HIGHLIGHT_RADIUS = 18
MARGIN = 48


def wrap_value(value: int, n: int) -> int:
    """Map an integer into the range 1..n."""
    return ((value - 1) % n) + 1


def sequence(start: int, a: int, b: int, n: int, max_steps: int | None = None) -> list[int]:
    """Generate x, f(x), f(f(x)), ... with wrapping by n."""
    if max_steps is None:
        max_steps = n
    values = [start]
    current = start
    for _ in range(max_steps):
        current = wrap_value(a * current + b, n)
        values.append(current)
        if current == start:
            break
    return values


class CircleCanvas(tk.Canvas):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, width=520, height=520, background="white", highlightthickness=0)
        self._n = 12
        self._a = 2
        self._b = 1
        self._traverse_active = False
        self._traverse_step = 0
        self._highlight_index: int | None = None

        self.bind("<Configure>", lambda _e: self.redraw())

    def set_params(self, n: int, a: int, b: int) -> None:
        self._n = max(1, n)
        self._a = a
        self._b = b
        self.redraw()

    def current_path(self) -> list[int]:
        return sequence(1, self._a, self._b, self._n)

    def geometry_values(self) -> tuple[float, float, float]:
        width = self.winfo_width() or int(self["width"])
        height = self.winfo_height() or int(self["height"])
        radius = (min(width, height) - 2 * MARGIN) / 2
        return width / 2, height / 2, max(radius, 1.0)

    def point_position(self, index: int) -> tuple[float, float]:
        cx, cy, radius = self.geometry_values()
        angle = 2 * math.pi * (index - 1) / self._n - math.pi / 2
        return cx + radius * math.cos(angle), cy + radius * math.sin(angle)

    def set_traverse(self, active: bool, step: int = 0) -> None:
        self._traverse_active = active
        self._traverse_step = step
        path = self.current_path()
        self._highlight_index = path[min(step, len(path) - 1)] if active and path else None
        self.redraw()

    def advance_traverse(self) -> bool:
        """Advance one step. Returns False when the walk is complete."""
        path = self.current_path()
        if not path or self._traverse_step >= len(path) - 1:
            return False

        self._traverse_step += 1
        self._highlight_index = path[self._traverse_step]
        self.redraw()
        return self._traverse_step < len(path) - 1

    def redraw(self) -> None:
        self.delete("all")
        cx, cy, radius = self.geometry_values()

        self.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius, outline="#555555", width=2
        )

        path = self.current_path()
        line_count = self._traverse_step if self._traverse_active else len(path) - 1
        for i in range(line_count):
            x1, y1 = self.point_position(path[i])
            x2, y2 = self.point_position(path[i + 1])
            self.create_line(x1, y1, x2, y2, fill="blue", width=2)

        for i in range(1, self._n + 1):
            x, y = self.point_position(i)
            is_highlight = self._traverse_active and i == self._highlight_index
            r = HIGHLIGHT_RADIUS if is_highlight else POINT_RADIUS
            self.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill="yellow" if is_highlight else "white",
                outline="#b8860b" if is_highlight else "black",
                width=3 if is_highlight else 1,
            )
            self.create_text(
                x,
                y,
                text=str(i),
                fill="black",
                font=("Segoe UI", 10, "bold") if is_highlight else ("Segoe UI", 9),
            )

        if self._traverse_active and self._highlight_index is not None:
            self._draw_popup(self._highlight_index)

    def _draw_popup(self, value: int) -> None:
        x, y = self.point_position(value)
        y -= HIGHLIGHT_RADIUS + 22
        text_id = self.create_text(
            x, y, text=f"x = {value}", font=("Segoe UI", 10, "bold"), fill="black"
        )
        left, top, right, bottom = self.bbox(text_id)
        box_id = self.create_rectangle(
            left - 12, top - 6, right + 12, bottom + 6, fill="#fff3cd", outline="#ffc107", width=2
        )
        self.tag_raise(text_id, box_id)


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Multiples in Circles - ax + b (Tkinter)")
        self.geometry("720x640")

        self._traverse_active = False

        controls = ttk.Frame(self, padding=(10, 10, 10, 0))
        controls.pack(fill="x")

        ttk.Label(controls, text="Max N:").pack(side="left")
        self.max_n_var = tk.StringVar(value="24")
        max_n_entry = ttk.Entry(controls, textvariable=self.max_n_var, width=6)
        max_n_entry.pack(side="left", padx=(4, 10))
        max_n_entry.bind("<Return>", lambda _e: self._on_params_changed())
        max_n_entry.bind("<FocusOut>", lambda _e: self._on_params_changed())

        ttk.Label(controls, text="Points (N):").pack(side="left")
        self.n_slider = ttk.Scale(controls, from_=1, to=24, orient="horizontal")
        self.n_slider.set(12)
        self.n_slider.pack(side="left", fill="x", expand=True, padx=4)

        self.n_label = ttk.Label(controls, text="12", width=3)
        self.n_label.pack(side="left", padx=(0, 10))

        # Attached after n_label exists so the initial set() cannot fire the callback.
        self.n_slider.configure(command=self._on_slider_changed)

        ttk.Label(controls, text="a:").pack(side="left")
        self.a_var = tk.StringVar(value="2")
        a_entry = ttk.Entry(controls, textvariable=self.a_var, width=6)
        a_entry.pack(side="left", padx=(4, 10))
        a_entry.bind("<Return>", lambda _e: self._on_params_changed())
        a_entry.bind("<FocusOut>", lambda _e: self._on_params_changed())

        ttk.Label(controls, text="b:").pack(side="left")
        self.b_var = tk.StringVar(value="1")
        b_entry = ttk.Entry(controls, textvariable=self.b_var, width=6)
        b_entry.pack(side="left", padx=(4, 10))
        b_entry.bind("<Return>", lambda _e: self._on_params_changed())
        b_entry.bind("<FocusOut>", lambda _e: self._on_params_changed())

        self.traverse_btn = ttk.Button(controls, text="Traverse", command=self._toggle_traverse)
        self.traverse_btn.pack(side="left")

        ttk.Label(
            self,
            text="Traverse mode: press Enter to reveal each segment and move to the next x.",
            foreground="#666666",
        ).pack(fill="x", padx=10, pady=(6, 0))

        self.canvas = CircleCanvas(self)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.bind("<Return>", self._on_enter_pressed)
        self.bind("<KP_Enter>", self._on_enter_pressed)
        self.bind("<Prior>", lambda _e: self._nudge_slider(1))
        self.bind("<Next>", lambda _e: self._nudge_slider(-1))

        self._refresh_canvas()

    def _parse_int(self, var: tk.StringVar, fallback: int) -> int:
        try:
            return int(var.get().strip())
        except ValueError:
            var.set(str(fallback))
            return fallback

    def _slider_value(self) -> int:
        return int(round(float(self.n_slider.get())))

    def _on_max_n_changed(self) -> None:
        max_n = max(1, self._parse_int(self.max_n_var, 24))
        self.max_n_var.set(str(max_n))
        self.n_slider.configure(to=max_n)
        if self._slider_value() > max_n:
            self.n_slider.set(max_n)

    def _on_slider_changed(self, _value: str) -> None:
        self.n_label.configure(text=str(self._slider_value()))
        self._on_params_changed()

    def _on_params_changed(self) -> None:
        self._on_max_n_changed()
        self._refresh_canvas()
        if self._traverse_active:
            self.canvas.set_traverse(True, 0)

    def _refresh_canvas(self) -> None:
        self.canvas.set_params(
            self._slider_value(),
            self._parse_int(self.a_var, 2),
            self._parse_int(self.b_var, 1),
        )

    def _toggle_traverse(self) -> None:
        self._traverse_active = not self._traverse_active
        if self._traverse_active:
            self.traverse_btn.configure(text="Stop Traverse")
            self.canvas.set_traverse(True, 0)
        else:
            self.traverse_btn.configure(text="Traverse")
            self.canvas.set_traverse(False)

    def _on_enter_pressed(self, _event: tk.Event) -> None:
        if not self._traverse_active:
            return
        if not self.canvas.advance_traverse():
            self._toggle_traverse()

    def _nudge_slider(self, delta: int) -> None:
        value = self._slider_value() + delta
        lower = int(float(self.n_slider.cget("from")))
        upper = int(float(self.n_slider.cget("to")))
        if lower <= value <= upper:
            self.n_slider.set(value)


def main() -> None:
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
