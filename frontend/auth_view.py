import tkinter as tk
from database import fetch_all
import services
from .theme import (
    BG_MAIN, CARD_WHITE, PRIMARY_BLUE, BRAND_BLUE, PILL_BLUE, PILL_BLUE_HOVER,
    TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED, SIDEBAR_ACTIVE_BG, BORDER_COLOR,
    FONT_FAMILY, create_rounded_rect
)


class AuthView(tk.Frame):
    """Responsive E Bank Login & Register screen for Desktop, Tablet, and Mobile."""

    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=BG_MAIN)
        self.on_login_success = on_login_success
        self.mode = "login"  # "login" or "register"
        self._build_ui()
        self.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        self.center = tk.Frame(self, bg=BG_MAIN)
        self.center.place(relx=0.5, rely=0.5, anchor="center")

        self.card_w, self.card_h = 430, 500
        self.card_canvas = tk.Canvas(
            self.center, width=self.card_w, height=self.card_h,
            bg=BG_MAIN, highlightthickness=0
        )
        self.card_canvas.pack()

        self.inner = tk.Frame(self.card_canvas, bg=CARD_WHITE)
        self.inner_win = self.card_canvas.create_window(
            self.card_w // 2, self.card_h // 2,
            window=self.inner, width=self.card_w - 64, height=self.card_h - 56
        )

        # Brand Header
        tk.Label(
            self.inner, text="E Bank",
            font=(FONT_FAMILY, 24, "bold"), fg=BRAND_BLUE, bg=CARD_WHITE
        ).pack(anchor="w", pady=(4, 0))

        self.subtitle_lbl = tk.Label(
            self.inner, text="Sign in to your cryptographic e-wallet",
            font=(FONT_FAMILY, 10), fg=TEXT_MUTED, bg=CARD_WHITE
        )
        self.subtitle_lbl.pack(anchor="w", pady=(2, 16))

        # Mode Switcher (Sign In / Create Account)
        tabs_frame = tk.Frame(self.inner, bg="#F1F5F9", padx=4, pady=4)
        tabs_frame.pack(fill="x", pady=(0, 18))
        tabs_frame.columnconfigure(0, weight=1)
        tabs_frame.columnconfigure(1, weight=1)

        self.btn_tab_login = tk.Button(
            tabs_frame, text="Đăng nhập (Login)",
            font=(FONT_FAMILY, 10, "bold"),
            bg=CARD_WHITE, fg=PRIMARY_BLUE,
            activebackground=CARD_WHITE, activeforeground=PRIMARY_BLUE,
            relief="flat", bd=0, pady=6, cursor="hand2",
            command=lambda: self._switch_mode("login")
        )
        self.btn_tab_login.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.btn_tab_register = tk.Button(
            tabs_frame, text="Đăng ký (Register)",
            font=(FONT_FAMILY, 10),
            bg="#F1F5F9", fg=TEXT_MEDIUM,
            activebackground=CARD_WHITE, activeforeground=PRIMARY_BLUE,
            relief="flat", bd=0, pady=6, cursor="hand2",
            command=lambda: self._switch_mode("register")
        )
        self.btn_tab_register.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        # Username field
        tk.Label(
            self.inner, text="Username",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        user_box = tk.Frame(self.inner, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        user_box.pack(fill="x", pady=(0, 14))
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            user_box, textvariable=self.username_var,
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK,
            relief="flat", bd=0, insertbackground=TEXT_DARK
        )
        self.username_entry.pack(fill="x", padx=12, pady=9)

        # Password field
        tk.Label(
            self.inner, text="Password",
            font=(FONT_FAMILY, 10, "bold"), fg=TEXT_DARK, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 4))

        pass_box = tk.Frame(self.inner, bg="#F8FAFC", highlightbackground=BORDER_COLOR, highlightthickness=1)
        pass_box.pack(fill="x", pady=(0, 10))
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            pass_box, textvariable=self.password_var, show="•",
            font=(FONT_FAMILY, 11), bg="#F8FAFC", fg=TEXT_DARK,
            relief="flat", bd=0, insertbackground=TEXT_DARK
        )
        self.password_entry.pack(fill="x", padx=12, pady=9)

        # Status / error message label
        self.msg_lbl = tk.Label(
            self.inner, text="", font=(FONT_FAMILY, 9, "bold"),
            fg="#DC2626", bg=CARD_WHITE, wraplength=340, justify="left"
        )
        self.msg_lbl.pack(anchor="w", pady=(2, 8))

        # Primary Submit Button
        self.submit_btn = tk.Button(
            self.inner, text="Đăng nhập vào E Bank",
            font=(FONT_FAMILY, 11, "bold"),
            bg=PILL_BLUE, fg="#FFFFFF",
            activebackground=PILL_BLUE_HOVER, activeforeground="#FFFFFF",
            relief="flat", bd=0, pady=10, cursor="hand2",
            command=self._on_submit
        )
        self.submit_btn.pack(fill="x", pady=(4, 14))

        # Quick accounts section from DB
        self.quick_frame = tk.Frame(self.inner, bg=CARD_WHITE)
        self.quick_frame.pack(fill="x", pady=(4, 0))
        self._render_quick_users()
        self._redraw_card_bg()

        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self._on_submit())
        self.password_entry.bind("<Return>", lambda e: self._on_submit())
        self.username_entry.focus_set()

    def _on_resize(self, event=None):
        w = self.winfo_width()
        if w <= 10:
            return
        new_w = max(320, min(430, w - 28))
        pad = 36 if new_w < 380 else 64
        if new_w != self.card_w:
            self.card_w = new_w
            self.card_canvas.config(width=self.card_w)
            self.card_canvas.coords(self.inner_win, self.card_w // 2, self.card_h // 2)
            self.card_canvas.itemconfig(self.inner_win, width=self.card_w - pad)
            self.msg_lbl.config(wraplength=self.card_w - pad - 10)
            self._redraw_card_bg()

    def _redraw_card_bg(self):
        self.card_canvas.delete("card_bg")
        create_rounded_rect(
            self.card_canvas, 4, 6, self.card_w - 4, self.card_h - 4,
            r=24, fill="#E2E8F0", outline="", tags=("card_bg",)
        )
        create_rounded_rect(
            self.card_canvas, 2, 2, self.card_w - 6, self.card_h - 8,
            r=24, fill=CARD_WHITE, outline=BORDER_COLOR, width=1, tags=("card_bg",)
        )
        self.card_canvas.tag_lower("card_bg")

    def _render_quick_users(self):
        for w in self.quick_frame.winfo_children():
            w.destroy()
        try:
            users = fetch_all("SELECT username FROM users ORDER BY id ASC LIMIT 5")
        except Exception:
            users = []
        if not users:
            return

        tk.Label(
            self.quick_frame, text="Tài khoản có sẵn trong DB (nhấn để điền nhanh):",
            font=(FONT_FAMILY, 9), fg=TEXT_MUTED, bg=CARD_WHITE
        ).pack(anchor="w", pady=(0, 6))

        chips = tk.Frame(self.quick_frame, bg=CARD_WHITE)
        chips.pack(anchor="w")
        for r in users:
            uname = r["username"]
            btn = tk.Button(
                chips, text=f"👤 {uname}",
                font=(FONT_FAMILY, 9, "bold"),
                bg=SIDEBAR_ACTIVE_BG, fg=PRIMARY_BLUE,
                activebackground=PRIMARY_BLUE, activeforeground="#FFFFFF",
                relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
                command=lambda u=uname: self._fill_quick_user(u)
            )
            btn.pack(side="left", padx=(0, 6))

    def _fill_quick_user(self, username: str):
        self._switch_mode("login")
        self.username_var.set(username)
        row = services.login(username, "test")
        if row:
            self.password_var.set("test")
            self.on_login_success(row["username"])
        else:
            self.password_entry.focus_set()

    def _switch_mode(self, mode: str):
        self.mode = mode
        self.msg_lbl.config(text="")
        if mode == "login":
            self.btn_tab_login.config(bg=CARD_WHITE, fg=PRIMARY_BLUE, font=(FONT_FAMILY, 10, "bold"))
            self.btn_tab_register.config(bg="#F1F5F9", fg=TEXT_MEDIUM, font=(FONT_FAMILY, 10))
            self.subtitle_lbl.config(text="Sign in to your cryptographic e-wallet")
            self.submit_btn.config(text="Đăng nhập vào E Bank")
        else:
            self.btn_tab_register.config(bg=CARD_WHITE, fg=PRIMARY_BLUE, font=(FONT_FAMILY, 10, "bold"))
            self.btn_tab_login.config(bg="#F1F5F9", fg=TEXT_MEDIUM, font=(FONT_FAMILY, 10))
            self.subtitle_lbl.config(text="Create an account & generate RSA-2048 keypair")
            self.submit_btn.config(text="Tạo tài khoản & Sinh khóa RSA")

    def _on_submit(self):
        u = self.username_var.get().strip()
        p = self.password_var.get()
        if self.mode == "login":
            row = services.login(u, p)
            if row:
                self.msg_lbl.config(text="✓ Đăng nhập thành công!", fg="#16A34A")
                self.on_login_success(row["username"])
            else:
                self.msg_lbl.config(text="✗ Sai username hoặc password.", fg="#DC2626")
        else:
            ok, msg = services.register(u, p)
            if ok:
                self.msg_lbl.config(text=f"✓ {msg} Đang đăng nhập...", fg="#16A34A")
                self._render_quick_users()
                self.on_login_success(u)
            else:
                self.msg_lbl.config(text=f"✗ {msg}", fg="#DC2626")
