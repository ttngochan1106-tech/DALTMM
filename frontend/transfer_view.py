import tkinter as tk
from database import fetch_all
import services
from .theme import (
    BG_MAIN, CARD_WHITE, CARD_SOFT_BLUE, PRIMARY_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    SIDEBAR_ACTIVE_BG, BORDER_COLOR, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    TEXT_GREEN, FONT_FAMILY
)


class TransferView(tk.Frame):
    """
    Sidebar 'Transfer' View with responsive layouts for Desktop, Tablet, and Mobile:
    - Transfer money to another user (RSA-PSS digital signature via services.transfer)
    - Deposit money into current user's wallet (via services.deposit)
    """

    def __init__(self, parent, current_user: str, on_data_changed, on_navigate):
        super().__init__(parent, bg=BG_MAIN)
        self.current_user = current_user
        self.on_data_changed = on_data_changed
        self.on_navigate = on_navigate
        self.layout_mode = "desktop"
        self._build_ui()

    def _build_ui(self):
        # =====================================================================
        # TOP BALANCE & CRYPTO KEY BANNER
        # =====================================================================
        self.banner = tk.Frame(self, bg=CARD_SOFT_BLUE, padx=20, pady=14)

        self.left_b = tk.Frame(self.banner, bg=CARD_SOFT_BLUE)
        tk.Label(
            self.left_b, text="Available Balance",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_MEDIUM, bg=CARD_SOFT_BLUE
        ).pack(anchor="w")
        self.bal_lbl = tk.Label(
            self.left_b, text="$0.00",
            font=(FONT_FAMILY, 24, "bold"), fg=TEXT_DARK, bg=CARD_SOFT_BLUE
        )
        self.bal_lbl.pack(anchor="w", pady=(2, 0))

        self.right_b = tk.Frame(self.banner, bg=CARD_SOFT_BLUE)
        self.engine_lbl = tk.Label(
            self.right_b, text="🔐 Digital Signature Engine: SHA-256 + RSA-PSS (2048-bit)",
            font=(FONT_FAMILY, 9, "bold"), fg=PRIMARY_BLUE, bg=CARD_SOFT_BLUE
        )
        self.engine_lbl.pack(anchor="w")
        self.key_lbl = tk.Label(
            self.right_b, text="",
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_SOFT_BLUE, wraplength=420, justify="left"
        )
        self.key_lbl.pack(anchor="w", pady=(4, 0))

        # =====================================================================
        # CARD 1: TRANSFER MONEY (CHUYỂN TIỀN)
        # =====================================================================
        self.tx_card = tk.Frame(
            self, bg=CARD_WHITE, padx=20, pady=18,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )

        tk.Label(
            self.tx_card, text="⇄  Transfer Money (Chuyển tiền)",
            font=(FONT_FAMILY, 13, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w")
        self.tx_desc_lbl = tk.Label(
            self.tx_card, text="Mỗi giao dịch chuyển tiền được băm SHA-256 và ký số bằng RSA Private Key của bạn.",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=380, justify="left"
        )
        self.tx_desc_lbl.pack(anchor="w", pady=(2, 14))

        tk.Label(
            self.tx_card, text="Người nhận (Receiver Username)",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        rec_box = tk.Frame(self.tx_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        rec_box.pack(fill="x", pady=(0, 8))
        self.receiver_var = tk.StringVar()
        self.receiver_entry = tk.Entry(
            rec_box, textvariable=self.receiver_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        )
        self.receiver_entry.pack(fill="x", padx=12, pady=8)

        self.recipients_frame = tk.Frame(self.tx_card, bg=CARD_WHITE)
        self.recipients_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            self.tx_card, text="Số tiền chuyển (Amount)",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        amt_box = tk.Frame(self.tx_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        amt_box.pack(fill="x", pady=(0, 8))
        self.tx_amount_var = tk.StringVar()
        self.tx_amount_entry = tk.Entry(
            amt_box, textvariable=self.tx_amount_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        )
        self.tx_amount_entry.pack(fill="x", padx=12, pady=8)

        q_amt = tk.Frame(self.tx_card, bg=CARD_WHITE)
        q_amt.pack(fill="x", pady=(0, 12))
        for val in (10, 50, 100, 500, 1000):
            tk.Button(
                q_amt, text=f"${val:,}",
                font=(FONT_FAMILY, 8, "bold"),
                bg="#F1F5F9", fg=TEXT_MEDIUM,
                activebackground=SIDEBAR_ACTIVE_BG, activeforeground=PRIMARY_BLUE,
                relief="flat", bd=0, padx=7, pady=3, cursor="hand2",
                command=lambda v=val: self.tx_amount_var.set(str(v))
            ).pack(side="left", padx=(0, 5))

        self.tx_status_lbl = tk.Label(
            self.tx_card, text="", font=(FONT_FAMILY, 9, "bold"),
            fg=TEXT_GREEN, bg=CARD_WHITE, wraplength=340, justify="left"
        )
        self.tx_status_lbl.pack(anchor="w", pady=(0, 8))

        tk.Button(
            self.tx_card, text="⇄  Xác nhận Ký số & Chuyển tiền",
            font=(FONT_FAMILY, 10, "bold"),
            bg=PILL_BLUE, fg="#FFFFFF",
            activebackground=PILL_BLUE_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=10, cursor="hand2",
            command=self._handle_transfer
        ).pack(fill="x")

        # =====================================================================
        # CARD 2: DEPOSIT MONEY (NẠP TIỀN) & CRYPTO FLOW INFO
        # =====================================================================
        self.dep_card = tk.Frame(
            self, bg=CARD_WHITE, padx=20, pady=18,
            highlightbackground=BORDER_COLOR, highlightthickness=1
        )

        tk.Label(
            self.dep_card, text="＋  Deposit Money (Nạp tiền vào ví)",
            font=(FONT_FAMILY, 13, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w")
        self.dep_desc_lbl = tk.Label(
            self.dep_card, text="Nạp thêm số dư vào tài khoản hiện tại để thực hiện giao dịch.",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE, wraplength=380, justify="left"
        )
        self.dep_desc_lbl.pack(anchor="w", pady=(2, 14))

        tk.Label(
            self.dep_card, text="Số tiền nạp (Deposit Amount)",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        dep_box = tk.Frame(self.dep_card, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        dep_box.pack(fill="x", pady=(0, 8))
        self.dep_amount_var = tk.StringVar()
        self.dep_amount_entry = tk.Entry(
            dep_box, textvariable=self.dep_amount_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK, relief="flat", bd=0
        )
        self.dep_amount_entry.pack(fill="x", padx=12, pady=8)

        q_dep = tk.Frame(self.dep_card, bg=CARD_WHITE)
        q_dep.pack(fill="x", pady=(0, 12))
        for val in (100, 1000, 5000, 10000):
            tk.Button(
                q_dep, text=f"+${val:,}",
                font=(FONT_FAMILY, 8, "bold"),
                bg="#F1F5F9", fg=TEXT_MEDIUM,
                activebackground=SIDEBAR_ACTIVE_BG, activeforeground=PRIMARY_BLUE,
                relief="flat", bd=0, padx=7, pady=3, cursor="hand2",
                command=lambda v=val: self.dep_amount_var.set(str(v))
            ).pack(side="left", padx=(0, 5))

        self.dep_status_lbl = tk.Label(
            self.dep_card, text="", font=(FONT_FAMILY, 9, "bold"),
            fg=TEXT_GREEN, bg=CARD_WHITE, wraplength=340, justify="left"
        )
        self.dep_status_lbl.pack(anchor="w", pady=(0, 8))

        tk.Button(
            self.dep_card, text="＋  Nạp tiền ngay (Deposit)",
            font=(FONT_FAMILY, 10, "bold"),
            bg="#0F172A", fg="#FFFFFF",
            activebackground="#1E293B", activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=10, cursor="hand2",
            command=self._handle_deposit
        ).pack(fill="x", pady=(0, 16))

        info_box = tk.Frame(self.dep_card, bg="#F8FAFC", padx=12, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        info_box.pack(fill="x")
        tk.Label(
            info_box, text="Luồng Mật Mã Giao Dịch (Cryptographic Flow):",
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg="#F8FAFC"
        ).pack(anchor="w")
        self.crypto_log_lbl = tk.Label(
            info_box,
            text="1. Canonical: sender|receiver|amount|timestamp|tx_id\n"
                 "2. Hash: SHA-256 digest (64 hex chars)\n"
                 "3. Sign: RSA-PSS (MGF1-SHA256) với Private Key\n"
                 "4. Verify: Kiểm tra bằng Public Key ở tab Transactions",
            font=("Consolas", 8), fg=TEXT_MEDIUM, bg="#F8FAFC", justify="left", wraplength=330
        )
        self.crypto_log_lbl.pack(anchor="w", pady=(4, 0))

        self._apply_layout_grid()
        self.refresh_data()

    def set_layout_mode(self, mode: str):
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        self._apply_layout_grid()

    def _apply_layout_grid(self):
        self.banner.grid_forget()
        self.tx_card.grid_forget()
        self.dep_card.grid_forget()
        self.left_b.pack_forget()
        self.right_b.pack_forget()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        if self.layout_mode == "desktop":
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.left_b.pack(side="left")
            self.right_b.pack(side="right")
            self.banner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
            self.tx_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
            self.dep_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
            wrap_w = 380
        else:
            # Tablet & Mobile: 1-column stack
            self.left_b.pack(anchor="w", fill="x")
            self.right_b.pack(anchor="w", fill="x", pady=(8, 0))
            self.banner.grid(row=0, column=0, sticky="ew", pady=(0, 12))
            self.tx_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
            self.dep_card.grid(row=2, column=0, sticky="ew", pady=(0, 8))
            wrap_w = 290 if self.layout_mode == "mobile" else 520

        self.tx_desc_lbl.config(wraplength=wrap_w)
        self.dep_desc_lbl.config(wraplength=wrap_w)
        self.crypto_log_lbl.config(wraplength=wrap_w)
        self.key_lbl.config(wraplength=wrap_w)

    def focus_deposit(self):
        self.dep_amount_entry.focus_set()

    def refresh_data(self):
        bal = services.get_balance(self.current_user)
        if bal is None:
            bal = 0.0
        self.bal_lbl.config(text=f"${bal:,.2f}")

        u = services.get_user(self.current_user)
        if u:
            self.key_lbl.config(text=f"Key: {u['public_key_path']}")

        for w in self.recipients_frame.winfo_children():
            w.destroy()
        try:
            others = fetch_all(
                "SELECT username FROM users WHERE username != ? ORDER BY id ASC LIMIT 6",
                (self.current_user,)
            )
        except Exception:
            others = []

        if others:
            tk.Label(
                self.recipients_frame, text="Chọn nhanh:",
                font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=CARD_WHITE
            ).pack(side="left", padx=(0, 6))
            for r in others:
                uname = r["username"]
                tk.Button(
                    self.recipients_frame, text=f"@{uname}",
                    font=(FONT_FAMILY, 8, "bold"),
                    bg=SIDEBAR_ACTIVE_BG, fg=PRIMARY_BLUE,
                    activebackground=PRIMARY_BLUE, activeforeground="#FFFFFF",
                    relief="flat", bd=0, padx=8, pady=2, cursor="hand2",
                    command=lambda name=uname: self.receiver_var.set(name)
                ).pack(side="left", padx=(0, 4))

    def _handle_transfer(self):
        receiver = self.receiver_var.get().strip()
        raw_amt = self.tx_amount_var.get().strip().replace(",", "")
        try:
            amount = float(raw_amt)
        except ValueError:
            self.tx_status_lbl.config(text="✗ Số tiền không hợp lệ.", fg="#DC2626")
            return

        ok, msg, tx_id = services.transfer(self.current_user, receiver, amount)
        if ok:
            self.tx_status_lbl.config(text=f"✓ {msg}\nMã giao dịch: {tx_id}", fg=TEXT_GREEN)
            self.tx_amount_var.set("")
            self.crypto_log_lbl.config(
                text=f"✓ Đã ký số thành công giao dịch {tx_id}\n"
                     f"• {self.current_user} -> {receiver} (${amount:,.2f})\n"
                     f"• Trạng thái: SIGNED (RSA-PSS + SHA-256)"
            )
            self.refresh_data()
            self.on_data_changed()
        else:
            self.tx_status_lbl.config(text=f"✗ {msg}", fg="#DC2626")

    def _handle_deposit(self):
        raw_amt = self.dep_amount_var.get().strip().replace(",", "")
        try:
            amount = float(raw_amt)
        except ValueError:
            self.dep_status_lbl.config(text="✗ Số tiền nạp không hợp lệ.", fg="#DC2626")
            return

        ok, msg = services.deposit(self.current_user, amount)
        if ok:
            self.dep_status_lbl.config(text=f"✓ {msg}", fg=TEXT_GREEN)
            self.dep_amount_var.set("")
            self.refresh_data()
            self.on_data_changed()
        else:
            self.dep_status_lbl.config(text=f"✗ {msg}", fg="#DC2626")
