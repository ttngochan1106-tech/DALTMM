import tkinter as tk
import services
from .theme import (
    BG_MAIN, CARD_WHITE, CARD_SOFT_BLUE, PRIMARY_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    CHART_LIGHT_BLUE, CHART_DARK_BLUE, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    TEXT_GREEN, BADGE_FRAUD_BG, BADGE_FRAUD_FG, FONT_FAMILY,
    create_rounded_rect, draw_cards_artwork
)


class HomeView(tk.Frame):
    """
    Main Home Dashboard matching the E Bank screenshot, with responsive layouts
    for Desktop (>=1024px), Tablet (680-1023px), and Mobile (<680px).
    """

    def __init__(self, parent, current_user: str, on_navigate, search_var: tk.StringVar = None):
        super().__init__(parent, bg=BG_MAIN)
        self.current_user = current_user
        self.on_navigate = on_navigate
        self.search_var = search_var
        self.tx_filter = "all"  # "all", "incomes", "expenses"
        self.layout_mode = "desktop"
        self.incomes_text = "$20,000"
        self.expenses_text = "$10,000"
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # =====================================================================
        # ROW 0: TOP SUMMARY ROW (Total balance | Incomes card | Expenses card)
        # =====================================================================
        self.top_row = tk.Frame(self, bg=BG_MAIN)
        self.top_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # 1. Total Balance section
        self.bal_frame = tk.Frame(self.top_row, bg=BG_MAIN)
        bal_header = tk.Frame(self.bal_frame, bg=BG_MAIN)
        bal_header.pack(fill="x", pady=(2, 4))
        tk.Label(
            bal_header, text="Total balance",
            font=(FONT_FAMILY, 13), fg=TEXT_DARK, bg=BG_MAIN
        ).pack(side="left")

        tk.Label(
            bal_header, text="USD  ▾",
            font=(FONT_FAMILY, 9, "bold"), fg=PRIMARY_BLUE, bg=BG_MAIN, cursor="hand2"
        ).pack(side="right", padx=(0, 16))

        self.balance_lbl = tk.Label(
            self.bal_frame, text="$120,000",
            font=(FONT_FAMILY, 30), fg="#232946", bg=BG_MAIN, anchor="w"
        )
        self.balance_lbl.pack(fill="x")

        # 2. Incomes Card
        self.inc_canvas = tk.Canvas(self.top_row, height=92, bg=BG_MAIN, highlightthickness=0)
        self.inc_canvas.bind("<Configure>", lambda e: self._draw_stat_card(
            self.inc_canvas, "Incomes", "February", self.incomes_text, "+11.01%"
        ))

        # 3. Expenses Card
        self.exp_canvas = tk.Canvas(self.top_row, height=92, bg=BG_MAIN, highlightthickness=0)
        self.exp_canvas.bind("<Configure>", lambda e: self._draw_stat_card(
            self.exp_canvas, "Expenses", "February", self.expenses_text, "-1.01%"
        ))

        # =====================================================================
        # ROW 1: QUICK ACTION PILLS BAR
        # =====================================================================
        self.actions_canvas = tk.Canvas(self, height=56, bg=BG_MAIN, highlightthickness=0)
        self.actions_canvas.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.actions_canvas.bind("<Configure>", self._draw_quick_actions_bar)

        # =====================================================================
        # ROW 2: MIDDLE SECTION (My cards | Financial Overview)
        # =====================================================================
        self.mid_row = tk.Frame(self, bg=BG_MAIN)
        self.mid_row.grid(row=2, column=0, sticky="ew", pady=(0, 14))

        # --- My cards ---
        self.cards_col = tk.Frame(self.mid_row, bg=BG_MAIN)

        cards_hdr = tk.Frame(self.cards_col, bg=BG_MAIN)
        cards_hdr.pack(fill="x", pady=(2, 4))
        tk.Label(
            cards_hdr, text="My cards",
            font=(FONT_FAMILY, 13), fg=TEXT_DARK, bg=BG_MAIN
        ).pack(side="left")

        see_details_lbl = tk.Label(
            cards_hdr, text="See details  ▸",
            font=(FONT_FAMILY, 9, "bold"), fg=PRIMARY_BLUE, bg=BG_MAIN, cursor="hand2"
        )
        see_details_lbl.pack(side="right", padx=(0, 8))
        see_details_lbl.bind("<Button-1>", lambda e: self.on_navigate("transfer"))

        # Overlapping 3 credit cards canvas (responsive width)
        self.cards_canvas = tk.Canvas(self.cards_col, width=430, height=182, bg=BG_MAIN, highlightthickness=0)
        self.cards_canvas.pack(fill="x", anchor="w")
        self.cards_canvas.bind("<Configure>", self._on_cards_canvas_configure)

        # Card balances below cards
        card_footer = tk.Frame(self.cards_col, bg=BG_MAIN)
        card_footer.pack(fill="x", pady=(2, 0))

        c_left = tk.Frame(card_footer, bg=BG_MAIN)
        c_left.pack(side="left", padx=(4, 28))
        tk.Label(
            c_left, text="Total Card Balance",
            font=(FONT_FAMILY, 9), fg=TEXT_MEDIUM, bg=BG_MAIN
        ).pack(anchor="w")
        self.card_total_lbl = tk.Label(
            c_left, text="$100,000",
            font=(FONT_FAMILY, 15), fg="#232946", bg=BG_MAIN
        )
        self.card_total_lbl.pack(anchor="w", pady=(2, 0))

        c_right = tk.Frame(card_footer, bg=BG_MAIN)
        c_right.pack(side="left")
        tk.Label(
            c_right, text="Available Card Balance",
            font=(FONT_FAMILY, 9), fg=TEXT_MEDIUM, bg=BG_MAIN
        ).pack(anchor="w")
        self.card_avail_lbl = tk.Label(
            c_right, text="$70,600",
            font=(FONT_FAMILY, 15), fg="#232946", bg=BG_MAIN
        )
        self.card_avail_lbl.pack(anchor="w", pady=(2, 0))

        # --- Financial Overview chart card ---
        self.chart_canvas = tk.Canvas(self.mid_row, height=250, bg=BG_MAIN, highlightthickness=0)
        self.chart_canvas.bind("<Configure>", self._draw_financial_overview)

        # =====================================================================
        # ROW 3: BOTTOM TRANSACTIONS CARD
        # =====================================================================
        self.tx_card_canvas = tk.Canvas(self, height=225, bg=BG_MAIN, highlightthickness=0)
        self.tx_card_canvas.grid(row=3, column=0, sticky="nsew", pady=(0, 4))
        self.rowconfigure(3, weight=1)
        self.tx_card_canvas.bind("<Configure>", self._draw_transactions_card)

        self._apply_layout_grid()
        self.refresh_data()

    def _on_cards_canvas_configure(self, event=None):
        cw = self.cards_canvas.winfo_width()
        if cw > 10:
            s = min(1.0, max(0.68, (cw - 8) / 425.0))
            new_h = int(182 * s)
            if abs(self.cards_canvas.winfo_height() - new_h) > 3:
                self.cards_canvas.config(height=new_h)
        draw_cards_artwork(self.cards_canvas, username=self._get_card_holder_name())

    def set_layout_mode(self, mode: str):
        """Switch between 'desktop', 'tablet', and 'mobile' grid arrangements."""
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        self._apply_layout_grid()
        self._draw_quick_actions_bar()
        self._draw_financial_overview()
        self._draw_transactions_card()

    def _apply_layout_grid(self):
        # Clear grid placements inside top_row and mid_row
        for w in (self.bal_frame, self.inc_canvas, self.exp_canvas):
            w.grid_forget()
        for w in (self.cards_col, self.chart_canvas):
            w.grid_forget()

        for c in range(3):
            self.top_row.columnconfigure(c, weight=0, uniform="")
        for c in range(2):
            self.mid_row.columnconfigure(c, weight=0, uniform="")

        if self.layout_mode == "desktop":
            # Desktop: 3 columns in top_row, 2 columns in mid_row, 1-row quick actions
            self.balance_lbl.config(font=(FONT_FAMILY, 30))
            self.top_row.columnconfigure(0, weight=11, uniform="top_d")
            self.top_row.columnconfigure(1, weight=10, uniform="top_d")
            self.top_row.columnconfigure(2, weight=10, uniform="top_d")

            self.bal_frame.grid(row=0, column=0, sticky="nsew", padx=(4, 18), pady=4)
            self.inc_canvas.grid(row=0, column=1, sticky="nsew", padx=8)
            self.exp_canvas.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

            self.actions_canvas.config(height=56)

            self.mid_row.columnconfigure(0, weight=10, uniform="mid_d")
            self.mid_row.columnconfigure(1, weight=11, uniform="mid_d")
            self.cards_col.grid(row=0, column=0, sticky="nsew", padx=(2, 14))
            self.chart_canvas.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        elif self.layout_mode == "tablet":
            # Tablet: Total balance on row 0, Incomes + Expenses side-by-side on row 1
            # Quick actions in 2 rows; My cards and Chart stacked full-width
            self.balance_lbl.config(font=(FONT_FAMILY, 28))
            self.top_row.columnconfigure(0, weight=1, uniform="top_t")
            self.top_row.columnconfigure(1, weight=1, uniform="top_t")

            self.bal_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 10))
            self.inc_canvas.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
            self.exp_canvas.grid(row=1, column=1, sticky="nsew", padx=(6, 0))

            self.actions_canvas.config(height=94)

            self.mid_row.columnconfigure(0, weight=1)
            self.cards_col.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 14))
            self.chart_canvas.grid(row=1, column=0, sticky="ew", padx=2)

        else:
            # Mobile (<680px): 1-column vertical stack for all cards & 3-row quick actions
            self.balance_lbl.config(font=(FONT_FAMILY, 25))
            self.top_row.columnconfigure(0, weight=1)

            self.bal_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 8))
            self.inc_canvas.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 8))
            self.exp_canvas.grid(row=2, column=0, sticky="ew", padx=0)

            self.actions_canvas.config(height=130)

            self.mid_row.columnconfigure(0, weight=1)
            self.cards_col.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 12))
            self.chart_canvas.grid(row=1, column=0, sticky="ew", padx=0)

    def _get_card_holder_name(self):
        if self.current_user.lower() == "eda":
            return "Eda Tunca"
        return self.current_user

    def refresh_data(self):
        """Fetch latest balance & transactions for current_user from services.py."""
        bal = services.get_balance(self.current_user)
        if bal is None:
            bal = 120000.0
        if abs(bal - round(bal)) < 0.005:
            self.balance_lbl.config(text=f"${bal:,.0f}")
        else:
            self.balance_lbl.config(text=f"${bal:,.2f}")

        self.incomes_text = "$20,000"
        self.expenses_text = "$10,000"

        self._draw_stat_card(self.inc_canvas, "Incomes", "February", self.incomes_text, "+11.01%")
        self._draw_stat_card(self.exp_canvas, "Expenses", "February", self.expenses_text, "-1.01%")
        draw_cards_artwork(self.cards_canvas, username=self._get_card_holder_name())
        self._draw_transactions_card()

    def _draw_stat_card(self, canvas: tk.Canvas, title: str, month: str, amount: str, pct: str):
        canvas.delete("all")
        w = max(canvas.winfo_width(), 200)
        h = max(canvas.winfo_height(), 88)
        create_rounded_rect(canvas, 2, 2, w - 2, h - 2, r=16, fill=CARD_SOFT_BLUE, outline="")

        canvas.create_text(
            20, 25, text=title,
            font=(FONT_FAMILY, 10, "bold"), fill=TEXT_DARK, anchor="w"
        )
        canvas.create_text(
            w - 20, 25, text=month,
            font=(FONT_FAMILY, 9), fill=TEXT_MEDIUM, anchor="e"
        )
        canvas.create_text(
            20, 60, text=amount,
            font=(FONT_FAMILY, 17), fill=TEXT_DARK, anchor="w"
        )
        canvas.create_text(
            w - 20, 61, text=f"{pct}  ↗",
            font=(FONT_FAMILY, 9, "bold"), fill=TEXT_DARK, anchor="e"
        )

    def _draw_quick_actions_bar(self, event=None):
        c = self.actions_canvas
        c.delete("all")
        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 56)

        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=14, fill=CARD_WHITE, outline="")

        all_pills = [
            ("⇄  Transfer money", "transfer"),
            ("▣  Pay bills", "deposit"),
            ("📈  Investments", "transactions"),
            ("◔  Insights", "transactions"),
            ("⑂  Split a bill", "transfer"),
            ("📅  Schedule payments", "transactions"),
            ("↻  Exchange currency", "transfer"),
        ]

        # Split pills into 1 row (desktop), 2 rows (tablet), or 3 rows (mobile)
        if self.layout_mode == "desktop" and w >= 760:
            rows_spec = [all_pills]
        elif self.layout_mode == "tablet" or (460 <= w < 760):
            rows_spec = [all_pills[:4], all_pills[4:]]
        else:
            rows_spec = [all_pills[:3], all_pills[3:5], all_pills[5:]]

        pad_x = 12
        pad_y = 10
        gap_x = 8
        gap_y = 8
        num_rows = len(rows_spec)
        row_h = max(28, (h - 2 * pad_y - gap_y * (num_rows - 1)) / num_rows)

        for r_idx, row_pills in enumerate(rows_spec):
            y1 = pad_y + r_idx * (row_h + gap_y)
            y2 = y1 + row_h
            avail_w = w - 2 * pad_x - gap_x * (len(row_pills) - 1)
            weights = [len(lbl) + 4 for lbl, _ in row_pills]
            total_wt = sum(weights)
            cur_x = pad_x

            for (label, target), wt in zip(row_pills, weights):
                pw = avail_w * (wt / total_wt)
                x1, x2 = cur_x, cur_x + pw
                tag = f"pill_{r_idx}_{label}"
                rect_id = create_rounded_rect(
                    c, x1, y1, x2, y2, r=14,
                    fill=PILL_BLUE, outline="", tags=(tag,)
                )
                c.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=label, font=(FONT_FAMILY, 8, "bold"),
                    fill="#FFFFFF", tags=(tag,)
                )

                def on_enter(e, rid=rect_id):
                    c.itemconfig(rid, fill=PILL_BLUE_HOVER)
                    c.config(cursor="hand2")

                def on_leave(e, rid=rect_id):
                    c.itemconfig(rid, fill=PILL_BLUE)
                    c.config(cursor="")

                c.tag_bind(tag, "<Enter>", on_enter)
                c.tag_bind(tag, "<Leave>", on_leave)
                c.tag_bind(tag, "<Button-1>", lambda e, t=target: self.on_navigate(t))
                cur_x = x2 + gap_x

    def _draw_financial_overview(self, event=None):
        c = self.chart_canvas
        c.delete("all")
        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 245)

        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=16, fill=CARD_WHITE, outline="")

        # Header
        c.create_text(
            20, 24, text="Financial Overview",
            font=(FONT_FAMILY, 10, "bold"), fill=TEXT_DARK, anchor="w"
        )
        c.create_text(
            w - 18, 24, text="Last 6 months ▾",
            font=(FONT_FAMILY, 9, "bold"), fill=PRIMARY_BLUE, anchor="e"
        )

        # Legend: Incomes & Expenses pills
        create_rounded_rect(c, 20, 46, 40, 57, r=5, fill=CHART_LIGHT_BLUE, outline="")
        c.create_text(46, 51, text="Incomes", font=(FONT_FAMILY, 8), fill=TEXT_MEDIUM, anchor="w")

        create_rounded_rect(c, 96, 46, 116, 57, r=5, fill=CHART_DARK_BLUE, outline="")
        c.create_text(122, 51, text="Expenses", font=(FONT_FAMILY, 8), fill=TEXT_MEDIUM, anchor="w")

        # Y-axis labels
        y_labels = [
            ("20,000", 88),
            ("10,000", 122),
            ("5,000", 156),
            ("1,000", 190),
        ]
        for txt, y_pos in y_labels:
            c.create_text(18, y_pos, text=txt, font=(FONT_FAMILY, 8), fill=TEXT_MUTED, anchor="w")

        # Bar Chart Data matching the screenshot (Jul, Aug, Sep, Nov, Dec, Jan, Feb)
        months_data = [
            ("Jul", 0.62, 0.59),
            ("Aug", 0.58, 0.36),
            ("Sep", 0.37, 0.38),
            ("Nov", 0.85, 0.61),
            ("Dec", 0.45, 0.46),
            ("Jan", 0.65, 0.65),
            ("Feb", 0.55, 0.49),
        ]

        chart_left = 64 if w < 380 else 76
        chart_right = w - 14
        base_y = 205
        max_bar_h = 112
        col_w = max(28, (chart_right - chart_left) / len(months_data))
        bar_w = 8 if w < 390 else 11

        for idx, (m_name, inc_ratio, exp_ratio) in enumerate(months_data):
            cx = chart_left + col_w * (idx + 0.5)

            inc_h = max(14, max_bar_h * inc_ratio)
            ix1, iy1, ix2, iy2 = cx - bar_w - 1.5, base_y - inc_h, cx - 1.5, base_y
            create_rounded_rect(c, ix1, iy1, ix2, iy2, r=5, fill=CHART_LIGHT_BLUE, outline="")

            exp_h = max(14, max_bar_h * exp_ratio)
            ex1, ey1, ex2, ey2 = cx + 1.5, base_y - exp_h, cx + bar_w + 1.5, base_y
            create_rounded_rect(c, ex1, ey1, ex2, ey2, r=5, fill=CHART_DARK_BLUE, outline="")

            c.create_text(cx, base_y + 18, text=m_name, font=(FONT_FAMILY, 8), fill=TEXT_MUTED)

    def _set_tx_filter(self, flt: str):
        self.tx_filter = flt
        self._draw_transactions_card()

    def _get_display_transactions(self):
        db_rows = services.list_transactions(self.current_user)
        items = []

        for r in db_rows:
            is_sender = (r["sender_username"] == self.current_user)
            counterparty = r["receiver_username"] if is_sender else r["sender_username"]
            valid, _, _ = services.verify_transaction(r["id"])
            initials = "".join(part[0].upper() for part in counterparty.split()[:2]) or counterparty[:2].upper()
            items.append({
                "id": r["id"],
                "initials": initials,
                "name": counterparty,
                "full_name": f"{counterparty}  ({r['id']})",
                "amount": float(r["amount"]),
                "is_income": not is_sender,
                "fraud": not valid,
                "avatar_bg": "#DCD7FE" if not valid else "#D8E2FF",
                "avatar_fg": "#4338CA",
            })

        demo_items = [
            {
                "id": "DEMO-MARIA",
                "initials": "M",
                "name": "Maria",
                "full_name": "Maria",
                "amount": 40.00,
                "is_income": False,
                "fraud": True,
                "avatar_bg": "#DDD6FE",
                "avatar_fg": "#3730A3",
            },
            {
                "id": "DEMO-ALEXA",
                "initials": "AC",
                "name": "Alexa Capton",
                "full_name": "Alexa Capton",
                "amount": 100.00,
                "is_income": True,
                "fraud": False,
                "avatar_bg": "#DDD6FE",
                "avatar_fg": "#3730A3",
            },
        ]
        items.extend(demo_items)

        q = (self.search_var.get().strip().lower() if self.search_var else "")
        if q:
            items = [it for it in items if q in it["full_name"].lower() or q in it["id"].lower()]

        if self.tx_filter == "incomes":
            items = [it for it in items if it["is_income"]]
        elif self.tx_filter == "expenses":
            items = [it for it in items if not it["is_income"]]

        return items[:3]

    def _draw_transactions_card(self, event=None):
        c = self.tx_card_canvas
        c.delete("all")
        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 215)
        is_compact = (w < 500)

        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=16, fill=CARD_WHITE, outline="")

        # Title
        c.create_text(
            20, 26, text="Transactions",
            font=(FONT_FAMILY, 13), fill=TEXT_DARK, anchor="w"
        )

        # Filter funnel icon & 3-dots menu on top right
        fx = w - 52
        c.create_polygon(
            fx - 6, 20, fx + 6, 20, fx + 1.5, 26, fx + 1.5, 31, fx - 1.5, 31, fx - 1.5, 26,
            fill="", outline=TEXT_DARK, width=1.4
        )
        mx = w - 24
        for dy in (-5, 0, 5):
            c.create_oval(mx - 1.5, 25 + dy - 1.5, mx + 1.5, 25 + dy + 1.5, fill=TEXT_DARK, outline="")

        # Sub-tabs: All transactions | Incomes | Expenses ...... See all ▸
        if is_compact:
            tabs = [
                ("All", "all", 20),
                ("Incomes", "incomes", 68),
                ("Expenses", "expenses", 142),
            ]
        else:
            tabs = [
                ("All transactions", "all", 22),
                ("Incomes", "incomes", 142),
                ("Expenses", "expenses", 222),
            ]

        for label, key, tx_x in tabs:
            is_active = (self.tx_filter == key)
            color = PRIMARY_BLUE if is_active else TEXT_MEDIUM
            weight = "bold" if is_active else "normal"
            t_tag = f"tx_tab_{key}"
            tid = c.create_text(
                tx_x, 58, text=label,
                font=(FONT_FAMILY, 9, weight), fill=color, anchor="w", tags=(t_tag,)
            )
            if is_active:
                bbox = c.bbox(tid)
                if bbox:
                    c.create_line(bbox[0], 71, bbox[2], 71, fill=PRIMARY_BLUE, width=2.5)
            c.tag_bind(t_tag, "<Button-1>", lambda e, k=key: self._set_tx_filter(k))
            c.tag_bind(t_tag, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(t_tag, "<Leave>", lambda e: c.config(cursor=""))

        c.create_line(20, 72, w - 20, 72, fill="#F1F5F9", width=1)

        c.create_text(
            w - 20, 58, text="See all  ▸",
            font=(FONT_FAMILY, 9, "bold"), fill=PRIMARY_BLUE, anchor="e", tags=("see_all_tx",)
        )
        c.tag_bind("see_all_tx", "<Button-1>", lambda e: self.on_navigate("transactions"))
        c.tag_bind("see_all_tx", "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind("see_all_tx", "<Leave>", lambda e: c.config(cursor=""))

        rows = self._get_display_transactions()
        row_y = 98
        row_step = 48

        for idx, item in enumerate(rows):
            cy = row_y + idx * row_step
            if cy + 16 > h:
                break

            row_tag = f"home_tx_row_{idx}"
            av_x = 38
            c.create_oval(
                av_x - 17, cy - 17, av_x + 17, cy + 17,
                fill=item["avatar_bg"], outline="", tags=(row_tag,)
            )
            c.create_text(
                av_x, cy, text=item["initials"],
                font=(FONT_FAMILY, 9, "bold"), fill=item["avatar_fg"], tags=(row_tag,)
            )

            disp_name = item["name"] if is_compact else item["full_name"]
            c.create_text(
                68, cy, text=disp_name,
                font=(FONT_FAMILY, 10), fill=TEXT_DARK, anchor="w", tags=(row_tag,)
            )

            amt_str = f"+${item['amount']:,.2f}" if item["is_income"] else f"-${item['amount']:,.2f}"
            amt_color = TEXT_GREEN if item["is_income"] else TEXT_DARK

            if item["fraud"]:
                c.create_text(
                    w - 20, cy - 9, text=amt_str,
                    font=(FONT_FAMILY, 10, "bold"), fill=amt_color, anchor="e", tags=(row_tag,)
                )
                bx1, by1, bx2, by2 = w - 112, cy + 3, w - 20, cy + 22
                create_rounded_rect(
                    c, bx1, by1, bx2, by2, r=5,
                    fill=BADGE_FRAUD_BG, outline="", tags=(row_tag,)
                )
                c.create_text(
                    (bx1 + bx2) / 2, (by1 + by2) / 2,
                    text="Possible fraud",
                    font=(FONT_FAMILY, 8, "bold"), fill=BADGE_FRAUD_FG, tags=(row_tag,)
                )
            else:
                c.create_text(
                    w - 20, cy, text=amt_str,
                    font=(FONT_FAMILY, 10, "bold"), fill=amt_color, anchor="e", tags=(row_tag,)
                )

            c.tag_bind(row_tag, "<Button-1>", lambda e: self.on_navigate("transactions"))
            c.tag_bind(row_tag, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(row_tag, "<Leave>", lambda e: c.config(cursor=""))
