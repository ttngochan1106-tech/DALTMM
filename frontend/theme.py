import math
import tkinter as tk

# Responsive Breakpoints (in pixels)
BP_MOBILE = 680    # < 680px -> Mobile layout
BP_TABLET = 1024   # 680px..1023px -> Tablet layout, >= 1024px -> Desktop layout

# Color Palette matching the E Bank UI screenshot
BG_MAIN = "#F2F4FA"          # Soft lavender-gray main background
BG_SIDEBAR = "#F0F3FA"       # Sidebar background
SIDEBAR_ACTIVE_BG = "#DCE4FF" # Active pill background in sidebar
SIDEBAR_HOVER_BG = "#E6ECFF"
BORDER_COLOR = "#E2E7F4"

CARD_WHITE = "#FFFFFF"       # White card background
CARD_SOFT_BLUE = "#EAEFF9"   # Incomes / Expenses card background
SEARCH_BG = "#E6EAF5"        # Search bar and top icon circle background

PRIMARY_BLUE = "#2563EB"     # Primary E Bank blue
BRAND_BLUE = "#1E4DB7"       # "E Bank" logo color
PILL_BLUE = "#2F66E9"        # Quick action pill button color
PILL_BLUE_HOVER = "#1D4ED8"
CHART_LIGHT_BLUE = "#DCE5FB" # Incomes bar in chart
CHART_DARK_BLUE = "#2F66E9"  # Expenses bar in chart

TEXT_DARK = "#1E2640"        # Main dark navy/slate text
TEXT_MEDIUM = "#475569"      # Secondary text
TEXT_MUTED = "#64748B"       # Muted labels (e.g. February, chart axes)
TEXT_GREEN = "#16A34A"       # +$100.00 income green
BADGE_FRAUD_BG = "#C83E3B"   # "Possible fraud" red badge background
BADGE_FRAUD_FG = "#FFFFFF"
BADGE_VALID_BG = "#DCFCE7"
BADGE_VALID_FG = "#15803D"

FONT_FAMILY = "Segoe UI"


def get_device_mode(width: int) -> str:
    """Return 'mobile', 'tablet', or 'desktop' based on window width."""
    if width < BP_MOBILE:
        return "mobile"
    if width < BP_TABLET:
        return "tablet"
    return "desktop"


def create_rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r=16, **kwargs):
    """Draw a smooth rounded rectangle on a Tkinter Canvas."""
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1 + r, y1,
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def create_right_pill(canvas: tk.Canvas, x1, y1, x2, y2, r=22, **kwargs):
    """Draw a sidebar pill rounded on the right side."""
    return create_rounded_rect(canvas, x1, y1, x2, y2, r=r, **kwargs)


def draw_contactless_icon(canvas: tk.Canvas, x, y, color="#D1D5DB", scale=1.0):
    """Draw the contactless payment wave icon on credit cards."""
    for radius in (4, 8, 12):
        r = max(2, radius * scale)
        canvas.create_arc(
            x - r, y - r, x + r, y + r,
            start=-45, extent=90, style=tk.ARC,
            outline=color, width=max(1, int(1.6 * scale))
        )


def draw_mastercard_circles(canvas: tk.Canvas, x, y, r=10, c1="#9CA3AF", c2="#D1D5DB"):
    """Draw the two overlapping circles at the bottom right of a card."""
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=c1, outline="")
    canvas.create_oval(x, y - r, x + 2 * r, y + r, fill=c2, outline="")


def draw_cards_artwork(canvas: tk.Canvas, username: str = "Eda Tunca"):
    """
    Render the 3 overlapping credit/debit cards from the E Bank design onto `canvas`.
    Scales proportionally to fit mobile, tablet, or desktop canvas widths.
    """
    canvas.delete("all")
    cw = canvas.winfo_width()
    if cw <= 10:
        cw = int(canvas.cget("width") or 430)
    # Reference design width is 425px; scale down smoothly on narrow mobile screens
    s = min(1.0, max(0.68, (cw - 8) / 425.0))

    def sx(val):
        return val * s

    def sy(val):
        return val * s

    # --- CARD 3 (Back Right - Dark Navy/Indigo Card) ---
    c3_x1, c3_y1, c3_x2, c3_y2 = sx(205), sy(16), sx(415), sy(168)
    create_rounded_rect(canvas, c3_x1 + 2, c3_y1 + 4, c3_x2 + 2, c3_y2 + 4, r=sx(16), fill="#CBD5E1", outline="")
    create_rounded_rect(canvas, c3_x1, c3_y1, c3_x2, c3_y2, r=sx(16), fill="#1E1B4B", outline="#312E81", width=1)
    canvas.create_arc(sx(280), sy(-10), sx(440), sy(130), start=160, extent=130, style=tk.CHORD, fill="#4338CA", outline="")
    canvas.create_arc(sx(310), sy(60), sx(440), sy(200), start=90, extent=150, style=tk.CHORD, fill="#3730A3", outline="")
    draw_contactless_icon(canvas, sx(386), sy(40), color="#E0E7FF", scale=0.95 * s)
    canvas.create_text(
        sx(355), sy(108), text="00 0000",
        font=(FONT_FAMILY, max(8, int(12 * s)), "normal"), fill="#E0E7FF", anchor="e"
    )
    draw_mastercard_circles(canvas, sx(375), sy(145), r=max(6, sx(9)), c1="#818CF8", c2="#C7D2FE")

    # --- CARD 2 (Middle - Purple/Blue Marble Swirl Card) ---
    c2_x1, c2_y1, c2_x2, c2_y2 = sx(115), sy(14), sx(345), sy(170)
    create_rounded_rect(canvas, c2_x1 + 2, c2_y1 + 4, c2_x2 + 2, c2_y2 + 4, r=sx(16), fill="#94A3B8", outline="")
    create_rounded_rect(canvas, c2_x1, c2_y1, c2_x2, c2_y2, r=sx(16), fill="#8B7CB8", outline="#A78BFA", width=1)
    marble_blobs = [
        (180, 18, 330, 115, "#60A5FA"),
        (210, 40, 342, 160, "#A78BFA"),
        (240, 20, 340, 95, "#C4B5FD"),
        (225, 85, 335, 165, "#6366F1"),
        (260, 55, 342, 135, "#93C5FD"),
    ]
    for bx1, by1, bx2, by2, bcol in marble_blobs:
        create_rounded_rect(canvas, sx(bx1), sy(by1), sx(bx2), sy(by2), r=sx(28), fill=bcol, outline="")
    canvas.create_line(sx(245), sy(22), sx(275), sy(65), sx(250), sy(110), sx(295), sy(155), smooth=True, fill="#E0E7FF", width=max(1, int(2 * s)))
    canvas.create_line(sx(285), sy(20), sx(315), sy(75), sx(280), sy(125), sx(325), sy(162), smooth=True, fill="#DDD6FE", width=max(1, int(1.5 * s)))
    draw_contactless_icon(canvas, sx(316), sy(40), color="#1E1B4B", scale=0.95 * s)
    draw_mastercard_circles(canvas, sx(305), sy(146), r=max(6, sx(9)), c1="#4B5563", c2="#9CA3AF")

    # --- CARD 1 (Front Left - Matte Black Debit Card with 3D Torus Ring) ---
    c1_x1, c1_y1, c1_x2, c1_y2 = sx(6), sy(10), sx(256), sy(176)
    create_rounded_rect(canvas, c1_x1 + 3, c1_y1 + 5, c1_x2 + 3, c1_y2 + 5, r=sx(18), fill="#94A3B8", outline="")
    create_rounded_rect(canvas, c1_x1, c1_y1, c1_x2, c1_y2, r=sx(18), fill="#0D1017", outline="#262B38", width=1)

    # Glowing torus / spiral artwork in center-right of Card 1
    cx, cy = sx(142), sy(92)
    ring_r = sx(34)
    for i in range(18):
        angle = i * (math.pi / 9)
        ox = math.cos(angle) * sx(10)
        oy = math.sin(angle) * sy(10)
        if i % 3 == 0:
            ring_color = "#22D3EE"
        elif i % 3 == 1:
            ring_color = "#6366F1"
        else:
            ring_color = "#A855F7"
        canvas.create_oval(
            cx - ring_r + ox, cy - ring_r + oy,
            cx + ring_r + ox, cy + ring_r + oy,
            outline=ring_color, width=1
        )
    hole_r = sx(16)
    canvas.create_oval(cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r, fill="#0D1017", outline="#1E293B")

    # Silver EMV Chip on left
    chip_x1, chip_y1, chip_x2, chip_y2 = sx(32), sy(68), sx(66), sy(94)
    create_rounded_rect(canvas, chip_x1, chip_y1, chip_x2, chip_y2, r=sx(5), fill="#9CA3AF", outline="#D1D5DB", width=1)
    canvas.create_line(chip_x1, (chip_y1 + chip_y2) / 2, chip_x2, (chip_y1 + chip_y2) / 2, fill="#4B5563", width=1)
    canvas.create_line((chip_x1 + chip_x2) / 2, chip_y1, (chip_x1 + chip_x2) / 2, chip_y2, fill="#4B5563", width=1)

    draw_contactless_icon(canvas, sx(224), sy(36), color="#9CA3AF", scale=0.95 * s)

    canvas.create_text(
        sx(32), sy(118), text="DEBIT CARD",
        font=(FONT_FAMILY, max(6, int(8 * s)), "bold"), fill="#9CA3AF", anchor="w"
    )
    display_name = username if len(username) <= 14 else username[:14]
    canvas.create_text(
        sx(32), sy(140), text=f"{display_name}    12/24",
        font=(FONT_FAMILY, max(6, int(7 * s)), "normal"), fill="#D1D5DB", anchor="w"
    )

    draw_mastercard_circles(canvas, sx(214), sy(150), r=max(6, sx(10)), c1="#6B7280", c2="#D1D5DB")
