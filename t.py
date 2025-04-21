import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton, 
                              QVBoxLayout, QLabel, QComboBox)
from PySide6.QtCore import Qt, QRectF, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QPalette, QPainterPath, QBrush, QFont


class ContinuousRectangleBorder:
    """A reusable border class that can be applied to any widget"""
    
    def __init__(self, border_radius=None, border_color=None, border_width=2, background_color=None):
        self.border_radius = border_radius
        self.border_color = border_color if border_color is not None else QColor("#8A2BE2")  # Default purple
        self.border_width = border_width
        self.background_color = background_color  # Can be None for transparent background
    
    def apply_to(self, widget):
        """Apply this border to the given widget"""
        # Store the border in the widget
        widget._continuous_border = self
        
        # Store the original paint event
        if not hasattr(widget, '_original_paintEvent'):
            widget._original_paintEvent = widget.paintEvent
        
        # Override the paint event
        def new_paintEvent(event):
            painter = QPainter(widget)
            painter.setRenderHint(QPainter.Antialiasing, True)
            
            # Get the rect of the widget
            rect = widget.rect()
            
            # Create the path for the background and border
            adjusted_rect = QRectF(
                rect.x() + self.border_width/2,
                rect.y() + self.border_width/2,
                rect.width() - self.border_width,
                rect.height() - self.border_width
            )
            
            path = self._get_continuous_rect_path(adjusted_rect, widget)
            
            # Fill background if color is provided
            if self.background_color is not None:
                painter.fillPath(path, QBrush(self.background_color))
            
            # Draw the border
            pen = QPen(self.border_color)
            pen.setWidth(self.border_width)
            painter.setPen(pen)
            painter.drawPath(path)
            
            # Call the original paint event to draw the widget's content
            painter.save()
            widget._original_paintEvent(event)
            painter.restore()
        
        # Replace the widget's paint event with our custom one
        widget.paintEvent = new_paintEvent
        
        # Make background transparent if we're handling the background
        if self.background_color is not None:
            widget.setStyleSheet(widget.styleSheet() + "background-color: transparent;")
    
    def _get_continuous_rect_path(self, rect, widget):
        """
        Create a path with continuous rounded corners as implemented in Flutter's
        ContinuousRectangleBorder class.
        """
        path = QPainterPath()
        
        # Parameters
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()
        
        # Calculate radius - either use custom radius or calculate based on widget size
        if self.border_radius is not None:
            # Use the custom radius, but ensure it doesn't exceed half the shortest side
            shortest_side = min(rect.width(), rect.height())
            radius = min(self.border_radius, shortest_side / 2)
        else:
            # Default calculation: 20% of the shortest side
            radius = min(rect.width(), rect.height()) * 0.2
        
        # This mimics Flutter's ContinuousRectangleBorder implementation
        # using cubic Bezier curves at each corner
        
        # Start at top-left corner
        path.moveTo(left, top + radius)
        
        # Top-left corner - cubic Bezier that creates a continuous curve
        path.cubicTo(left, top, left, top, left + radius, top)
        
        # Top edge
        path.lineTo(right - radius, top)
        
        # Top-right corner
        path.cubicTo(right, top, right, top, right, top + radius)
        
        # Right edge
        path.lineTo(right, bottom - radius)
        
        # Bottom-right corner
        path.cubicTo(right, bottom, right, bottom, right - radius, bottom)
        
        # Bottom edge
        path.lineTo(left + radius, bottom)
        
        # Bottom-left corner
        path.cubicTo(left, bottom, left, bottom, left, bottom - radius)
        
        # Close the path
        path.closeSubpath()
        
        return path

class LineEdit(QLineEdit):
    def __init__(self, placeholder_text="", border_radius=None, parent=None):
        super().__init__(parent)
        
        # Set placeholder text
        self.setPlaceholderText(placeholder_text)
        self.custom_border_radius = border_radius
        
        # Set styling for the line edit
        # self.setMinimumHeight(60)  # Taller text box
        self.size = QSize(250, 60)
        self.setStyleSheet("""
            QLineEdit {
                color: #ffffff;
                border: none;
                padding: 12px 20px;
                font-size: 22px;
                font-family: Arial;
                background-color: transparent;
            }
        """)

        border = ContinuousRectangleBorder(
            border_radius=28, 
            border_color=QColor("#8A2BE2"),
            background_color=QColor("#2D2D2D")
        )
        border.apply_to(self)


class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        # Set styling for the button
        self.size = QSize(250, 60)
        font = QFont("Arial", 18)
        font.setWeight(QFont.Light)
        self.setFont(font)
        
        self.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                padding: 20px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                color: #f0f0f0;
            }
            
            QPushButton:pressed {
                color: #e0e0e0;
            }
        """)
        
        # Apply the continuous rectangle border
        border = ContinuousRectangleBorder(
            border_radius=28,  # Large radius for pill shape
            border_color=None,  # No border, just background
            border_width=0,
            background_color=QColor("#9932CC")  # Bright purple color
        )
        border.apply_to(self)
    


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Log In")
        self.setMinimumSize(600, 200)
        
        # Set dark background for the window
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        self.setPalette(palette)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Create our custom text box with a specific border radius (28 pixels)
        text_box = LineEdit("Enter Access Key", border_radius=28)
        button = PrimaryButton("Log In")
        layout.addWidget(text_box)
        layout.addSpacing(20)
        layout.addWidget(button)
        
        # Set layout
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())