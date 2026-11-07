"""Visualize ax+b sequences on equally spaced points around a circle."""

import math
import sys

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QKeySequence, QPainter, QPen, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


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


class PointPopup(QLabel):
    """Floating label shown at the current traverse point."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "QLabel {"
            "background: #fff3cd;"
            "border: 2px solid #ffc107;"
            "border-radius: 10px;"
            "padding: 6px 12px;"
            "font-weight: bold;"
            "font-size: 13px;"
            "}"
        )
        self.hide()

    def show_at(self, pos: QPointF, value: int) -> None:
        self.setText(f"x = {value}")
        self.adjustSize()
        self.move(
            int(pos.x() - self.width() / 2),
            int(pos.y() - self.height() - 22),
        )
        self.show()
        self.raise_()


class CircleCanvas(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(520, 520)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._n = 12
        self._a = 2
        self._b = 1
        self._traverse_active = False
        self._traverse_step = 0
        self._highlight_index: int | None = None

        self.popup = PointPopup(self)

    def set_params(self, n: int, a: int, b: int) -> None:
        self._n = max(1, n)
        self._a = a
        self._b = b
        self.update()

    def current_path(self) -> list[int]:
        return sequence(1, self._a, self._b, self._n)

    def geometry_values(self) -> tuple[QPointF, float]:
        side = min(self.width(), self.height())
        margin = 48
        radius = (side - 2 * margin) / 2
        center = QPointF(self.width() / 2, self.height() / 2)
        return center, radius

    def point_position(self, index: int) -> QPointF:
        center, radius = self.geometry_values()
        angle = 2 * math.pi * (index - 1) / self._n - math.pi / 2
        return QPointF(
            center.x() + radius * math.cos(angle),
            center.y() + radius * math.sin(angle),
        )

    def set_traverse(self, active: bool, step: int = 0) -> None:
        self._traverse_active = active
        self._traverse_step = step
        path = self.current_path()
        if active and path:
            self._highlight_index = path[min(step, len(path) - 1)]
            pos = self.point_position(self._highlight_index)
            self.popup.show_at(pos, self._highlight_index)
        else:
            self._highlight_index = None
            self.popup.hide()
        self.update()

    def advance_traverse(self) -> bool:
        """Advance one step. Returns False when the walk is complete."""
        path = self.current_path()
        if not path:
            return False

        if self._traverse_step >= len(path) - 1:
            return False

        self._traverse_step += 1
        self._highlight_index = path[self._traverse_step]
        pos = self.point_position(self._highlight_index)
        self.popup.show_at(pos, self._highlight_index)
        self.update()
        return self._traverse_step < len(path) - 1

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center, radius = self.geometry_values()

        painter.setPen(QPen(Qt.GlobalColor.darkGray, 2))
        painter.drawEllipse(center, radius, radius)

        for i in range(1, self._n + 1):
            pos = self.point_position(i)
            is_highlight = self._traverse_active and i == self._highlight_index
            if is_highlight:
                painter.setPen(QPen(Qt.GlobalColor.darkYellow, 3))
                painter.setBrush(Qt.GlobalColor.yellow)
                painter.drawEllipse(pos, 18, 18)
            else:
                painter.setPen(QPen(Qt.GlobalColor.black, 1))
                painter.setBrush(Qt.GlobalColor.white)
                painter.drawEllipse(pos, 14, 14)

            painter.setPen(Qt.GlobalColor.black)
            painter.setFont(QFont("Segoe UI", 10 if is_highlight else 9, QFont.Weight.Bold if is_highlight else QFont.Weight.Normal))
            label = str(i)
            text_width = painter.fontMetrics().horizontalAdvance(label)
            text_height = painter.fontMetrics().height()
            painter.drawText(
                QPointF(pos.x() - text_width / 2, pos.y() + text_height / 4),
                label,
            )

        path = self.current_path()
        if self._traverse_active:
            line_count = self._traverse_step
        else:
            line_count = len(path) - 1

        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
        for i in range(line_count):
            p1 = self.point_position(path[i])
            p2 = self.point_position(path[i + 1])
            painter.drawLine(p1, p2)

        painter.end()
        if self._traverse_active and self._highlight_index is not None:
            self.popup.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._traverse_active and self._highlight_index is not None:
            pos = self.point_position(self._highlight_index)
            self.popup.show_at(pos, self._highlight_index)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Multiples in Circles — ax + b")
        self.resize(720, 640)

        self._traverse_active = False

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        controls = QHBoxLayout()

        controls.addWidget(QLabel("Max N:"))
        self.max_n_edit = QLineEdit("24")
        self.max_n_edit.setFixedWidth(60)
        self.max_n_edit.setToolTip("Maximum value for the point-count slider")
        controls.addWidget(self.max_n_edit)

        controls.addWidget(QLabel("Points (N):"))
        self.n_slider = QSlider(Qt.Orientation.Horizontal)
        self.n_slider.setMinimum(1)
        self.n_slider.setMaximum(24)
        self.n_slider.setValue(12)
        self.n_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.n_slider.setTickInterval(1)
        controls.addWidget(self.n_slider, stretch=1)

        self.n_label = QLabel("12")
        self.n_label.setFixedWidth(28)
        controls.addWidget(self.n_label)

        controls.addWidget(QLabel("a:"))
        self.a_edit = QLineEdit("2")
        self.a_edit.setFixedWidth(60)
        controls.addWidget(self.a_edit)

        controls.addWidget(QLabel("b:"))
        self.b_edit = QLineEdit("1")
        self.b_edit.setFixedWidth(60)
        controls.addWidget(self.b_edit)

        self.traverse_btn = QPushButton("Traverse")
        self.traverse_btn.setCheckable(True)
        self.traverse_btn.setToolTip("Step through the path with Enter; click again to stop")
        controls.addWidget(self.traverse_btn)

        layout.addLayout(controls)

        hint = QLabel("Traverse mode: press Enter to reveal each segment and move to the next x.")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint)

        self.canvas = CircleCanvas()
        layout.addWidget(self.canvas, stretch=1)

        self.max_n_edit.editingFinished.connect(self._on_params_changed)
        self.n_slider.valueChanged.connect(self._on_slider_changed)
        self.a_edit.editingFinished.connect(self._on_params_changed)
        self.b_edit.editingFinished.connect(self._on_params_changed)
        self.traverse_btn.toggled.connect(self._on_traverse_toggled)

        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter_shortcut.activated.connect(self._on_enter_pressed)
        enter_shortcut_alt = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        enter_shortcut_alt.activated.connect(self._on_enter_pressed)
        
        page_up_shortcut = QShortcut(QKeySequence(Qt.Key.Key_PageUp), self)
        page_up_shortcut.activated.connect(self._on_page_up_pressed)
        page_down_shortcut = QShortcut(QKeySequence(Qt.Key.Key_PageDown), self)
        page_down_shortcut.activated.connect(self._on_page_down_pressed)

        self._refresh_canvas()

    def _parse_int(self, edit: QLineEdit, fallback: int) -> int:
        try:
            return int(edit.text().strip())
        except ValueError:
            edit.setText(str(fallback))
            return fallback

    def _on_max_n_changed(self) -> None:
        max_n = max(1, self._parse_int(self.max_n_edit, 24))
        self.max_n_edit.setText(str(max_n))
        self.n_slider.setMaximum(max_n)
        if self.n_slider.value() > max_n:
            self.n_slider.setValue(max_n)

    def _on_slider_changed(self, value: int) -> None:
        self.n_label.setText(str(value))
        self._on_params_changed()

    def _on_params_changed(self) -> None:
        self._on_max_n_changed()
        self._refresh_canvas()
        if self._traverse_active:
            self.canvas.set_traverse(True, 0)

    def _refresh_canvas(self) -> None:
        n = self.n_slider.value()
        a = self._parse_int(self.a_edit, 2)
        b = self._parse_int(self.b_edit, 1)
        self.canvas.set_params(n, a, b)

    def _on_traverse_toggled(self, checked: bool) -> None:
        self._traverse_active = checked
        if checked:
            self.traverse_btn.setText("Stop Traverse")
            self.canvas.setFocus()
            self.canvas.set_traverse(True, 0)
        else:
            self.traverse_btn.setText("Traverse")
            self.canvas.set_traverse(False)

    def _on_enter_pressed(self) -> None:
        if not self._traverse_active:
            return
        if not self.canvas.advance_traverse():
            self.traverse_btn.setChecked(False)

    def _on_page_up_pressed(self) -> None:
        current_value = self.n_slider.value()
        max_value = self.n_slider.maximum()
        if current_value < max_value:
            self.n_slider.setValue(current_value + 1)

    def _on_page_down_pressed(self) -> None:
        current_value = self.n_slider.value()
        min_value = self.n_slider.minimum()
        if current_value > min_value:
            self.n_slider.setValue(current_value - 1)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
