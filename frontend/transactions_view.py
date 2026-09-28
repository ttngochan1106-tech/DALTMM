import tkinter as tk
import services
from .theme import (
    BG_MAIN, CARD_WHITE, PRIMARY_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    SIDEBAR_ACTIVE_BG, BORDER_COLOR, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    TEXT_GREEN, BADGE_FRAUD_BG, BADGE_FRAUD_FG, BADGE_VALID_BG, BADGE_VALID_FG,
    FONT_FAMILY
)


class TransactionsView(tk.Frame):
    """
    Sidebar 'Transactions' View with responsive layouts for Desktop, Tablet, and Mobile:
    - Shows recent transactions of the current user (All transactions / Incomes / Expenses)
    - Live cryptographic verification (SHA-256 + RSA-PSS signature check)
    - Interactive Verify & [DEMO] Tamper Amount inspector
    """

    def __init__(self, parent, current_user: str, on_data_changed, search_var: tk.StringVar = None):
        super().__init__(parent, bg=BG_MAIN)
        self.current_user = current_user
        self.on_data_changed = on_data_changed
        self.search_var = search_var
        self.tx_filter = "all"
        self.selected_tx_id = None
        self.layout_mode = "desktop"
        self._build_ui()

    def _build_ui(self):
        # =====================================================================
        # PANEL 1: RECENT TRANSACTIONS OF CURRENT USER
        # =====================================================================
        self.left_card = tk.Frame(
            self, bg=CARD_WHITE, padx=18, pady=18,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        self.left_card.columnconfigure(0, weight=1)
        self.left_card.rowconfigure(3, weight=1)

        hdr = tk.Frame(self.left_card, bg=CARD_WHITE)
        hdr.grid(row=0, column=0, sticky="ew")
        self.title_lbl = tk.Label(
            hdr, text=f"Recent Transactions ({self.current_user})",
            font=(FONT_FAMILY, 13, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        )
        self.title_lbl.pack(side="left")

        tk.Button(
            hdr, text="↻ Refresh",
            font=(FONT_FAMILY, 9, "bold"),
            bg=SIDEBAR_ACTIVE_BG, fg=PRIMARY_BLUE,
            activebackground=PRIMARY_BLUE, activeforeground="#FFFFFF",
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=self.refresh_data
        ).pack(side="right")

        tabs_bar = tk.Frame(self.left_card, bg=CARD_WHITE)
        tabs_bar.grid(row=1, column=0, sticky="ew", pady=(12, 4))

        self.tab_btns = {}
        for key, label in [("all", "All transactions"), ("incomes", "Incomes"), ("expenses", "Expenses")]:
            btn = tk.Button(
                tabs_bar, text=label,
                font=(FONT_FAMILY, 9, "bold" if key == "all" else "normal"),
                bg=CARD_WHITE,
                fg=PRIMARY_BLUE if key == "all" else TEXT_MEDIUM,
                activebackground=CARD_WHITE, activeforeground=PRIMARY_BLUE,
                relief="flat", bd=0, padx=6, pady=4, cursor="hand2",
                command=lambda k=key: self._set_filter(k)
            )
            btn.pack(side="left", padx=(0, 10))
            self.tab_btns[key] = btn

        tk.Frame(self.left_card, bg="#F1F5F9", height=1).grid(row=2, column=0, sticky="ew", pady=(0, 8))

        list_container = tk.Frame(self.left_card, bg=CARD_WHITE)
        list_container.grid(row=3, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        self.list_canvas = tk.Canvas(list_container, bg=CARD_WHITE, height=280, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.list_canvas.yview)
        self.rows_frame = tk.Frame(self.list_canvas, bg=CARD_WHITE)

        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )
        self.rows_window = self.list_canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.list_canvas.bind(
            "<Configure>",
            lambda e: self.list_canvas.itemconfig(self.rows_window, width=e.width)
        )
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.list_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # =====================================================================
        # PANEL 2: CRYPTO VERIFY & [DEMO] TAMPER AMOUNT
        # =====================================================================
        self.right_card = tk.Frame(
            self, bg=CARD_WHITE, padx=18, pady=18,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )

        tk.Label(
            self.right_card, text="🛡 Verify & Tamper Inspector",
            font=(FONT_FAMILY, 13, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w")
        self.insp_desc_lbl = tk.Label(
            self.right_card, text="Chọn 1 giao dịch hoặc nhập Transaction ID để kiểm tra chữ ký số RSA-PSS hoặc giả lập sửa số tiền (Tamper).",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=320, justify="left"
        )
        self.insp_desc_lbl.pack(anchor="w", pady=(2, 12))

        tk.Label(
            self.right_card, text="Transaction ID",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        txid_box = tk.Frame(self.right_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        txid_box.pack(fill="x", pady=(0, 10))
        self.tx_id_var = tk.StringVar()
        tk.Entry(
            txid_box, textvariable=self.tx_id_var,
            font=("Consolas", 10), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        ).pack(fill="x", padx=10, pady=7)

        tk.Button(
            self.right_card, text="🔍  Verify Giao Dịch (RSA-PSS & SHA-256)",
            font=(FONT_FAMILY, 9, "bold"),
            bg=PILL_BLUE, fg="#FFFFFF",
            activebackground=PILL_BLUE_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self._handle_verify
        ).pack(fill="x", pady=(0, 12))

        self.verify_box = tk.Frame(
            self.right_card, bg="#F8FAFC", padx=12, pady=10,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )
        self.verify_box.pack(fill="x", pady=(0, 14))

        self.verify_badge_lbl = tk.Label(
            self.verify_box, text="Chưa chọn giao dịch",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_MEDIUM, bg="#F8FAFC", wraplength=300, justify="left"
        )
        self.verify_badge_lbl.pack(anchor="w")

        self.verify_detail_lbl = tk.Label(
            self.verify_box,
            text="Nhấn vào một dòng giao dịch để xem chi tiết SHA-256 hash và chữ ký RSA-PSS.",
            font=("Consolas", 8), fg=TEXT_MEDIUM, bg="#F8FAFC",
            justify="left", wraplength=300
        )
        self.verify_detail_lbl.pack(anchor="w", pady=(6, 0))

        tk.Frame(self.right_card, bg=BORDER_COLOR, height=1).pack(fill="x", pady=(2, 12))

        tk.Label(
            self.right_card, text="⚠  [DEMO] Tamper Amount (Sửa DB trái phép)",
            font=(FONT_FAMILY, 10, "bold"), fg=BADGE_FRAUD_BG, bg=CARD_WHITE
        ).pack(anchor="w")
        self.tamp_desc_lbl = tk.Label(
            self.right_card, text="Thay đổi số tiền trực tiếp trong DB mà không có Private Key để thấy Verify phát hiện Possible fraud (INVALID).",
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=320, justify="left"
        )
        self.tamp_desc_lbl.pack(anchor="w", pady=(2, 8))

        tk.Label(
            self.right_card, text="Amount mới (New Tampered Amount)",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        tamp_box = tk.Frame(self.right_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        tamp_box.pack(fill="x", pady=(0, 10))
        self.tamper_amount_var = tk.StringVar()
        tk.Entry(
            tamp_box, textvariable=self.tamper_amount_var,
            font=(FONT_FAMILY, 10), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        ).pack(fill="x", padx=10, pady=7)

        self.tamper_msg_lbl = tk.Label(
            self.right_card, text="", font=(FONT_FAMILY, 8, "bold"),
            fg=BADGE_FRAUD_BG, bg=CARD_WHITE, wraplength=300, justify="left"
        )
        self.tamper_msg_lbl.pack(anchor="w", pady=(0, 6))

        tk.Button(
            self.right_card, text="⚠  Thực hiện Tamper Amount",
            font=(FONT_FAMILY, 9, "bold"),
            bg=BADGE_FRAUD_BG, fg="#FFFFFF",
            activebackground="#991B1B", activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self._handle_tamper
        ).pack(fill="x")

        self._apply_layout_grid()
        self.refresh_data()

    def set_layout_mode(self, mode: str):
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        self._apply_layout_grid()
        self.refresh_data()

    def _apply_layout_grid(self):
        self.left_card.grid_forget()
        self.right_card.grid_forget()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)

        if self.layout_mode == "desktop":
            self.columnconfigure(0, weight=13)
            self.columnconfigure(1, weight=9)
            self.rowconfigure(0, weight=1)
            self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
            self.right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
            wrap_w = 320
        else:
            # Tablet & Mobile: stack vertically
            self.left_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
            self.right_card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
            wrap_w = 285 if self.layout_mode == "mobile" else 520

        self.insp_desc_lbl.config(wraplength=wrap_w)
        self.tamp_desc_lbl.config(wraplength=wrap_w)
        self.verify_badge_lbl.config(wraplength=wrap_w)
        self.verify_detail_lbl.config(wraplength=wrap_w)

    def _set_filter(self, key: str):
        self.tx_filter = key
        for k, btn in self.tab_btns.items():
            if k == key:
                btn.config(fg=PRIMARY_BLUE, font=(FONT_FAMILY, 9, "bold"))
            else:
                btn.config(fg=TEXT_MEDIUM, font=(FONT_FAMILY, 9, "normal"))
        self.refresh_data()

    def refresh_data(self):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        rows = services.list_transactions(self.current_user)
        q = (self.search_var.get().strip().lower() if self.search_var else "")

        filtered = []
        for r in rows:
            is_sender = (r["sender_username"] == self.current_user)
            if self.tx_filter == "incomes" and is_sender:
                continue
            if self.tx_filter == "expenses" and not is_sender:
                continue
            if q:
                haystack = f"{r['id']} {r['sender_username']} {r['receiver_username']} {r['timestamp']}".lower()
                if q not in haystack:
                    continue
            filtered.append(r)

        if not filtered:
            empty = tk.Frame(self.rows_frame, bg=CARD_WHITE, pady=36)
            empty.pack(fill="x")
            tk.Label(
                empty, text="Chưa có giao dịch nào cho bộ lọc này.",
                font=(FONT_FAMILY, 10), fg=TEXT_MUTED, bg=CARD_WHITE
            ).pack()
            return

        for r in filtered:
            self._create_tx_row(r)

        if not self.tx_id_var.get().strip() and filtered:
            self._select_transaction(filtered[0]["id"], filtered[0]["amount"])

    def _create_tx_row(self, r):
        tx_id = r["id"]
        is_sender = (r["sender_username"] == self.current_user)
        counterparty = r["receiver_username"] if is_sender else r["sender_username"]
        direction_txt = f"{r['sender_username']} → {r['receiver_username']}"
        amount = float(r["amount"])
        valid, _, _ = services.verify_transaction(tx_id)
        is_mobile = (self.layout_mode == "mobile")

        row_frame = tk.Frame(self.rows_frame, bg=CARD_WHITE, pady=8, padx=4, cursor="hand2")
        row_frame.pack(fill="x")

        av_canvas = tk.Canvas(row_frame, width=36, height=36, bg=CARD_WHITE, highlightthickness=0)
        av_canvas.pack(side="left", padx=(0, 10))
        av_bg = "#FEE2E2" if not valid else "#DDD6FE"
        av_fg = "#991B1B" if not valid else "#3730A3"
        av_canvas.create_oval(2, 2, 34, 34, fill=av_bg, outline="")
        initials = "".join(p[0].upper() for p in counterparty.split()[:2]) or counterparty[:2].upper()
        av_canvas.create_text(18, 18, text=initials, font=(FONT_FAMILY, 8, "bold"), fill=av_fg)

        mid = tk.Frame(row_frame, bg=CARD_WHITE)
        mid.pack(side="left", fill="x", expand=True)

        top_line = counterparty if is_mobile else f"{counterparty}   ({direction_txt})"
        tk.Label(
            mid, text=top_line,
            font=(FONT_FAMILY, 9 if is_mobile else 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE, anchor="w"
        ).pack(fill="x")

        sub_line = tx_id[-12:] if is_mobile else f"{tx_id}   •   {r['timestamp']}"
        tk.Label(
            mid, text=sub_line,
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_WHITE, anchor="w"
        ).pack(fill="x", pady=(2, 0))

        right = tk.Frame(row_frame, bg=CARD_WHITE)
        right.pack(side="right", padx=(6, 2))

        amt_str = f"-${amount:,.2f}" if is_sender else f"+${amount:,.2f}"
        amt_col = TEXT_DARK if is_sender else TEXT_GREEN
        tk.Label(
            right, text=amt_str,
            font=(FONT_FAMILY, 9 if is_mobile else 10, "bold"), fg=amt_col, bg=CARD_WHITE, anchor="e"
        ).pack(anchor="e")

        if not valid:
            tk.Label(
                right, text=" Possible fraud ",
                font=(FONT_FAMILY, 7 if is_mobile else 8, "bold"),
                bg=BADGE_FRAUD_BG, fg=BADGE_FRAUD_FG, padx=5, pady=1
            ).pack(anchor="e", pady=(2, 0))
        else:
            tk.Label(
                right, text=" ✓ Verified ",
                font=(FONT_FAMILY, 7 if is_mobile else 8, "bold"),
                bg=BADGE_VALID_BG, fg=BADGE_VALID_FG, padx=5, pady=1
            ).pack(anchor="e", pady=(2, 0))

        tk.Frame(self.rows_frame, bg="#F1F5F9", height=1).pack(fill="x")

        def on_click(e, tid=tx_id, amt=amount):
            self._select_transaction(tid, amt)

        for widget in (row_frame, av_canvas, mid, right, *mid.winfo_children(), *right.winfo_children()):
            widget.bind("<Button-1>", on_click)

    def _select_transaction(self, tx_id: str, current_amt: float = None):
        self.selected_tx_id = tx_id
        self.tx_id_var.set(tx_id)
        if current_amt is not None:
            self.tamper_amount_var.set(str(current_amt))
        self.tamper_msg_lbl.config(text="")
        self._handle_verify()

    def _handle_verify(self):
        tx_id = self.tx_id_var.get().strip()
        if not tx_id:
            self.verify_badge_lbl.config(text="✗ Vui lòng nhập Transaction ID", fg=BADGE_FRAUD_BG)
            return

        valid, msg, details = services.verify_transaction(tx_id)
        if details is None:
            self.verify_badge_lbl.config(text=f"✗ {msg}", fg=BADGE_FRAUD_BG)
            self.verify_detail_lbl.config(text="")
            return

        if valid:
            self.verify_badge_lbl.config(text=f"✓ {msg}", fg=TEXT_GREEN)
        else:
            self.verify_badge_lbl.config(text=f"⚠ Possible fraud — {msg}", fg=BADGE_FRAUD_BG)

        info_lines = [
            f"TX ID     : {tx_id}",
            f"Hash      : {'✓ OK' if details['hash_ok'] else '✗ MISMATCH'}",
            f"Signature : {'✓ OK' if details['signature_ok'] else '✗ INVALID'}",
            f"Stored    : {details['stored_hash'][:22]}...",
            f"Recalc    : {details['recalculated_hash'][:22]}...",
        ]
        self.verify_detail_lbl.config(text="\n".join(info_lines))

    def _handle_tamper(self):
        tx_id = self.tx_id_var.get().strip()
        if not tx_id:
            self.tamper_msg_lbl.config(text="✗ Vui lòng chọn hoặc nhập Transaction ID.", fg=BADGE_FRAUD_BG)
            return

        raw_amt = self.tamper_amount_var.get().strip().replace(",", "")
        try:
            new_amount = float(raw_amt)
        except ValueError:
            self.tamper_msg_lbl.config(text="✗ Số tiền mới không hợp lệ.", fg=BADGE_FRAUD_BG)
            return

        changed = services.tamper_transaction(tx_id, new_amount)
        if changed:
            self.tamper_msg_lbl.config(
                text=f"⚠ Đã tamper số tiền giao dịch {tx_id} thành ${new_amount:,.2f}!",
                fg=BADGE_FRAUD_BG
            )
            self._handle_verify()
            self.refresh_data()
            self.on_data_changed()
        else:
            self.tamper_msg_lbl.config(text="✗ Không tìm thấy giao dịch trong DB.", fg=BADGE_FRAUD_BG)
