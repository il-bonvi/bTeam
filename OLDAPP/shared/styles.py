# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# ===============================================================================

"""Style sheets for bTeam GUI themes"""

THEMES = {
    "Forest Green": {
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2d2d2d",
        "accent": "#4CAF50",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "border": "#3d3d3d",
    },
    "Dark Blue": {
        "bg_primary": "#0f1419",
        "bg_secondary": "#1a2332",
        "accent": "#2196F3",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "border": "#2a3548",
    },
    "Ocean": {
        "bg_primary": "#0a0e27",
        "bg_secondary": "#1a2847",
        "accent": "#00BCD4",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "border": "#2a3d5c",
    },
    "Sunset": {
        "bg_primary": "#1a0f0f",
        "bg_secondary": "#2d1a1a",
        "accent": "#FF6B35",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "border": "#3d2a2a",
    },
    "Midnight": {
        "bg_primary": "#0d0d0d",
        "bg_secondary": "#1a1a1a",
        "accent": "#9C27B0",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "border": "#2d2d2d",
    },
}


def get_style(theme_name: str = "Forest Green") -> str:
    """Generate stylesheet for the given theme"""
    
    theme = THEMES.get(theme_name, THEMES["Forest Green"])
    
    stylesheet = f"""
    QMainWindow {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
    }}
    
    QWidget {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
    }}
    
    QLabel {{
        color: {theme['text_primary']};
    }}
    
    QPushButton {{
        background-color: {theme['accent']};
        color: {theme['text_primary']};
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }}
    
    QPushButton:hover {{
        background-color: {adjust_brightness(theme['accent'], 1.2)};
    }}
    
    QPushButton:pressed {{
        background-color: {adjust_brightness(theme['accent'], 0.8)};
    }}
    
    QLineEdit, QTextEdit {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid {theme['accent']};
    }}
    
    QComboBox {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 4px;
    }}
    
    QComboBox::drop-down {{
        border: none;
        background-color: {theme['accent']};
    }}
    
    QTableWidget {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        gridline-color: {theme['border']};
    }}
    
    QTableWidget::item {{
        padding: 4px;
    }}
    
    QTableWidget::item:selected {{
        background-color: {theme['accent']};
    }}
    
    QHeaderView::section {{
        background-color: {theme['accent']};
        color: {theme['text_primary']};
        padding: 4px;
        border: none;
    }}
    
    QListWidget {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
    }}
    
    QListWidget::item:selected {{
        background-color: {theme['accent']};
    }}
    
    QDialog {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
    }}
    
    QGroupBox {{
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }}
    
    QScrollBar:vertical {{
        background-color: {theme['bg_secondary']};
        width: 12px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {theme['accent']};
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {adjust_brightness(theme['accent'], 1.2)};
    }}
    """
    
    return stylesheet


def adjust_brightness(hex_color: str, factor: float) -> str:
    """Adjust brightness of a hex color"""
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Adjust brightness
    r = int(min(255, max(0, r * factor)))
    g = int(min(255, max(0, g * factor)))
    b = int(min(255, max(0, b * factor)))
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"
