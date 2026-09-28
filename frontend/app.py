import ctypes
import tkinter as tk
from .theme import (
    BG_MAIN, BG_SIDEBAR, SIDEBAR_ACTIVE_BG, BORDER_COLOR, CARD_WHITE,
    PRIMARY_BLUE, BRAND_BLUE, SEARCH_BG, TEXT_DARK, TEXT_MEDIUM, TEXT_MUTED,
    FONT_FAMILY, create_rounded_rect, get_device_mode
)
from .auth_view import AuthView
from .home_view import HomeView
from .transfer_view import TransferView
from .transactions_view import TransactionsView


class EBankApp(tk.Tk):
    """
    Main Window Application for E Bank Crypto E-Wallet.
    Supports responsive breakpoints:
    - Desktop (>= 1024px): Full 230px Left Sidebar + multi-column dashboard
    - Tablet (680px - 1023px): Compact 76px Icon Rail Sidebar + 2-col / stacked layout
    - Mobile (< 680px): Compact Mobile Header + Scrollable 1-col stack + Bottom Navigation Bar
    """

    def __init__(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        super().__init__()
        self.title("E Bank — Cryptographic E-Wallet")
        self.geometry("1280x820")
        self.minsize(360, 580)
        self.configure(bg=BG_MAIN)

        self.current_user = None
        self.active_tab = "home"
        self.device_mode = "desktop"
        self._resize_after_id = None

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search_changed())

        self.root_container = tk.Frame(self, bg=BG_MAIN)
        self.root_container.pack(fill="both", expand=True)

        self.bind("<Configure>", self._on_window_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self.show_auth()

    def set_viewport_preset(self, preset: str):
        """Quick helper to resize the window to Desktop, Tablet, or Mobile dimensions."""
        if preset == "desktop":
            self.geometry("1280x820")
        elif preset == "tablet":
            self.geometry("820x780")
        elif preset == "mobile":
            self.geometry("415x760")

    def show_auth(self):
        self.current_user = None
        for w in self.root_container.winfo_children():
            w.destroy()

        auth = AuthView(self.root_container, on_login_success=self.show_dashboard)
        auth.pack(fill="both", expand=True)

    def show_dashboard(self, username: str):
        self.current_user = username
        self.active_tab = "home"
        self.device_mode = None  # Force initial responsive layout apply

        for w in self.root_container.winfo_children():
            w.destroy()

        self.root_container.columnconfigure(0, weight=0)
        self.root_container.columnconfigure(1, weight=1)
        self.root_container.rowconfigure(0, weight=1)
        self.root_container.rowconfigure(1, weight=0)

        # =====================================================================
        # 1. LEFT SIDEBAR (Full 230px on Desktop, 76px Icon Rail on Tablet, Hidden on Mobile)
        # =====================================================================
        self.sidebar = tk.Frame(self.root_container, bg=BG_SIDEBAR, width=230)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        tk.Frame(self.sidebar, bg=BORDER_COLOR, width=1).pack(side="right", fill="y")

        self.sidebar_inner = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        self.sidebar_inner.pack(side="left", fill="both", expand=True)

        self.logo_frame = tk.Frame(self.sidebar_inner, bg=BG_SIDEBAR, padx=26, pady=22)
        self.logo_frame.pack(fill="x")
        self.logo_lbl = tk.Label(
            self.logo_frame, text="E Bank",
            font=(FONT_FAMILY, 20, "bold"), fg=BRAND_BLUE, bg=BG_SIDEBAR, anchor="w"
        )
        self.logo_lbl.pack(fill="x")

        self.nav_canvas = tk.Canvas(
            self.sidebar_inner, width=215, height=220,
            bg=BG_SIDEBAR, highlightthickness=0
        )
        self.nav_canvas.pack(fill="x", pady=(6, 0))

        self.sidebar_divider = tk.Frame(self.sidebar_inner, bg=BORDER_COLOR, height=1)
        self.sidebar_divider.pack(fill="x", padx=20, pady=14)

        self.logout_frame = tk.Frame(self.sidebar_inner, bg=BG_SIDEBAR, padx=16, pady=18)
        self.logout_frame.pack(side="bottom", fill="x")
        self.logout_btn = tk.Button(
            self.logout_frame, text="⎋  Đăng xuất (Switch User)",
            font=(FONT_FAMILY, 9, "bold"),
            bg="#E2E8F0", fg=TEXT_DARK,
            activebackground="#CBD5E1", activeforeground=TEXT_DARK,
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self.show_auth
        )
        self.logout_btn.pack(fill="x")

        # =====================================================================
        # 2. RIGHT MAIN AREA (Header + Scrollable Viewport)
        # =====================================================================
        self.main_area = tk.Frame(self.root_container, bg=BG_MAIN, padx=24, pady=14)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)

        # --- TOP HEADER BAR ---
        self.header = tk.Frame(self.main_area, bg=BG_MAIN)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.header.columnconfigure(0, weight=1)

        # Header Top Row (Title on left + Viewport presets + Bell & Avatar on right)
        self.header_top = tk.Frame(self.header, bg=BG_MAIN)
        self.header_top.grid(row=0, column=0, sticky="ew")

        welcome_name = "Eda" if self.current_user.lower() == "eda" else self.current_user
        self.welcome_lbl = tk.Label(
            self.header_top, text=f"Welcome, {welcome_name}",
            font=(FONT_FAMILY, 20), fg=TEXT_DARK, bg=BG_MAIN
        )
        self.welcome_lbl.pack(side="left")

        self.header_right = tk.Frame(self.header_top, bg=BG_MAIN)
        self.header_right.pack(side="right")

        # Responsive Viewport Preset Switcher (Desktop / Tablet / Mobile)
        self.vp_bar = tk.Frame(self.header_right, bg="#E2E8F0", padx=2, pady=2)
        self.vp_bar.pack(side="left", padx=(0, 10))
        self.vp_btns = {}
        for vp_key, vp_txt in [("desktop", "🖥"), ("tablet", "📱"), ("mobile", "📲")]:
            b = tk.Button(
                self.vp_bar, text=vp_txt,
                font=(FONT_FAMILY, 8, "bold"),
                bg=CARD_WHITE if vp_key == "desktop" else "#E2E8F0",
                fg=PRIMARY_BLUE if vp_key == "desktop" else TEXT_MEDIUM,
                relief="flat", bd=0, padx=6, pady=2, cursor="hand2",
                command=lambda k=vp_key: self.set_viewport_preset(k)
            )
            b.pack(side="left", padx=1)
            self.vp_btns[vp_key] = b

        # Desktop/Tablet inline Search Bar container
        self.search_holder_inline = tk.Frame(self.header_right, bg=BG_MAIN)
        self.search_holder_inline.pack(side="left", padx=(0, 10))

        # Mobile second-row Search Bar container
        self.search_holder_mobile = tk.Frame(self.header, bg=BG_MAIN)

        self.search_canvas = tk.Canvas(
            self.search_holder_inline, width=230, height=38,
            bg=BG_MAIN, highlightthickness=0
        )
        self.search_canvas.pack(fill="x", expand=True)
        self.search_entry = tk.Entry(
            self.search_canvas, textvariable=self.search_var,
            font=(FONT_FAMILY, 10), bg=SEARCH_BG, fg=TEXT_DARK,
            relief="flat", bd=0, insertbackground=TEXT_DARK
        )
        self._search_win = self.search_canvas.create_window(125, 19, window=self.search_entry, width=170, height=22)
        self.search_canvas.bind("<Configure>", self._redraw_search_pill)

        self._search_placeholder = True
        self.search_entry.insert(0, "Search")
        self.search_entry.config(fg=TEXT_MUTED)

        def on_search_focus_in(e):
            if self._search_placeholder:
                self._search_placeholder = False
                self.search_entry.delete(0, "end")
                self.search_entry.config(fg=TEXT_DARK)

        def on_search_focus_out(e):
            if not self.search_entry.get().strip():
                self._search_placeholder = True
                self.search_entry.delete(0, "end")
                self.search_entry.insert(0, "Search")
                self.search_entry.config(fg=TEXT_MUTED)

        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)

        # Notification Bell Circle
        bell_canvas = tk.Canvas(self.header_right, width=38, height=38, bg=BG_MAIN, highlightthickness=0, cursor="hand2")
        bell_canvas.pack(side="left", padx=(0, 10))
        bell_canvas.create_oval(2, 2, 36, 36, fill=SEARCH_BG, outline="")
        bell_canvas.create_text(19, 19, text="🔔", font=(FONT_FAMILY, 10), fill=TEXT_DARK)
        bell_canvas.bind("<Button-1>", lambda e: self.navigate("transactions"))

        # User Profile Avatar + Full Name
        self.user_chip = tk.Frame(self.header_right, bg=BG_MAIN, cursor="hand2")
        self.user_chip.pack(side="left")

        av_c = tk.Canvas(self.user_chip, width=36, height=36, bg=BG_MAIN, highlightthickness=0)
        av_c.pack(side="left", padx=(0, 6))
        av_c.create_oval(2, 2, 34, 34, fill="#CBD5E1", outline="#94A3B8", width=1)
        initials = self.current_user[:1].upper()
        av_c.create_oval(12, 8, 24, 20, fill="#334155", outline="")
        av_c.create_arc(6, 20, 30, 38, start=0, extent=180, fill="#475569", outline="")
        av_c.create_text(18, 14, text=initials, font=(FONT_FAMILY, 7, "bold"), fill="#FFFFFF")

        full_display = "Eda Tunca" if self.current_user.lower() == "eda" else self.current_user
        self.user_name_lbl = tk.Label(
            self.user_chip, text=full_display,
            font=(FONT_FAMILY, 9, "bold"), fg=TEXT_DARK, bg=BG_MAIN
        )
        self.user_name_lbl.pack(side="left")

        # --- SCROLLABLE MAIN CONTENT VIEWPORT ---
        viewport_wrap = tk.Frame(self.main_area, bg=BG_MAIN)
        viewport_wrap.grid(row=1, column=0, sticky="nsew")
        viewport_wrap.columnconfigure(0, weight=1)
        viewport_wrap.rowconfigure(0, weight=1)

        self.page_canvas = tk.Canvas(viewport_wrap, bg=BG_MAIN, highlightthickness=0)
        self.page_scrollbar = tk.Scrollbar(viewport_wrap, orient="vertical", command=self.page_canvas.yview)
        self.content_frame = tk.Frame(self.page_canvas, bg=BG_MAIN)

        self.content_frame.bind(
            "<Configure>",
            lambda e: self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))
        )
        self.content_win = self.page_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.page_canvas.bind("<Configure>", self._on_page_canvas_configure)
        self.page_canvas.configure(yscrollcommand=self.page_scrollbar.set)

        self.page_canvas.grid(row=0, column=0, sticky="nsew")
        self.page_scrollbar.grid(row=0, column=1, sticky="ns")

        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # =====================================================================
        # 3. MOBILE BOTTOM NAVIGATION BAR (Shown only in Mobile mode <680px)
        # =====================================================================
        self.bottom_nav = tk.Canvas(
            self.root_container, height=58, bg=CARD_WHITE,
            highlightthickness=1, highlightbackground=BORDER_COLOR
        )
        self.bottom_nav.bind("<Configure>", lambda e: self._draw_bottom_mobile_nav())

        # Instantiate the 3 views: Home, Transfer, Transactions
        clean_search = self._get_clean_search_var()
        self.views = {
            "home": HomeView(
                self.content_frame,
                current_user=self.current_user,
                on_navigate=self.navigate,
                search_var=clean_search
            ),
            "transfer": TransferView(
                self.content_frame,
                current_user=self.current_user,
                on_data_changed=self._refresh_all_views,
                on_navigate=self.navigate
            ),
            "transactions": TransactionsView(
                self.content_frame,
                current_user=self.current_user,
                on_data_changed=self._refresh_all_views,
                search_var=clean_search
            ),
        }

        self._apply_responsive_mode(get_device_mode(self.winfo_width()))
        self.navigate("home")

    def _on_page_canvas_configure(self, event):
        self.page_canvas.itemconfig(self.content_win, width=event.width)

    def _on_mousewheel(self, event):
        if not hasattr(self, "page_canvas") or not self.page_canvas.winfo_exists():
            return
        # Scroll page_canvas when in tablet/mobile or when content overflows
        bbox = self.page_canvas.bbox("all")
        if bbox and (bbox[3] - bbox[1]) > self.page_canvas.winfo_height():
            self.page_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _redraw_search_pill(self, event=None):
        c = self.search_canvas
        c.delete("pill_bg")
        w = max(c.winfo_width(), 140)
        h = max(c.winfo_height(), 36)
        create_rounded_rect(c, 2, 2, w - 2, h - 2, r=18, fill=SEARCH_BG, outline="", tags=("pill_bg",))
        c.create_oval(14, 12, 24, 22, outline=TEXT_DARK, width=1.5, tags=("pill_bg",))
        c.create_line(23, 21, 28, 26, fill=TEXT_DARK, width=1.5, tags=("pill_bg",))
        c.tag_lower("pill_bg")
        c.coords(self._search_win, 34 + (w - 46) / 2, h / 2)
        c.itemconfig(self._search_win, width=max(80, w - 48))

    def _on_window_configure(self, event=None):
        if event is not None and event.widget is not self:
            return
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(40, self._check_breakpoint)

    def _check_breakpoint(self):
        self._resize_after_id = None
        if not self.current_user or not hasattr(self, "views"):
            return
        w = self.winfo_width()
        if w <= 10:
            return
        mode = get_device_mode(w)
        if mode != self.device_mode:
            self._apply_responsive_mode(mode)

    def _apply_responsive_mode(self, mode: str):
        self.device_mode = mode

        # Highlight active viewport preset button
        if hasattr(self, "vp_btns"):
            for k, btn in self.vp_btns.items():
                btn.config(
                    bg=CARD_WHITE if k == mode else "#E2E8F0",
                    fg=PRIMARY_BLUE if k == mode else TEXT_MEDIUM
                )

        welcome_name = "Eda" if self.current_user.lower() == "eda" else self.current_user

        if mode == "desktop":
            # Show full 230px left sidebar, hide mobile bottom nav
            self.bottom_nav.grid_remove()
            self.sidebar.grid(row=0, column=0, sticky="nsew")
            self.sidebar.config(width=230)
            self.root_container.columnconfigure(0, minsize=230)
            self.logo_frame.config(padx=26, pady=22)
            self.logo_lbl.config(text="E Bank", font=(FONT_FAMILY, 20, "bold"), anchor="w")
            self.nav_canvas.config(width=215)
            self.logout_btn.config(text="⎋  Đăng xuất (Switch User)")

            # Header layout
            self.main_area.config(padx=24, pady=14)
            self.welcome_lbl.config(text=f"Welcome, {welcome_name}", font=(FONT_FAMILY, 20))
            self.user_name_lbl.pack(side="left")
            self.search_holder_mobile.grid_forget()
            self.search_canvas.pack_forget()
            self.search_canvas = self._reparent_search(self.search_holder_inline, width=230)
            self.search_holder_inline.pack(side="left", padx=(0, 10))
            self.page_scrollbar.grid_remove()

        elif mode == "tablet":
            # Show compact 76px icon-rail sidebar, hide mobile bottom nav
            self.bottom_nav.grid_remove()
            self.sidebar.grid(row=0, column=0, sticky="nsew")
            self.sidebar.config(width=76)
            self.root_container.columnconfigure(0, minsize=76)
            self.logo_frame.config(padx=8, pady=20)
            self.logo_lbl.config(text="E", font=(FONT_FAMILY, 20, "bold"), anchor="center")
            self.nav_canvas.config(width=72)
            self.logout_btn.config(text="⎋")

            # Header layout
            self.main_area.config(padx=18, pady=12)
            self.welcome_lbl.config(text=f"Welcome, {welcome_name}", font=(FONT_FAMILY, 17))
            self.user_name_lbl.pack_forget()
            self.search_holder_mobile.grid_forget()
            self.search_canvas = self._reparent_search(self.search_holder_inline, width=175)
            self.search_holder_inline.pack(side="left", padx=(0, 8))
            self.page_scrollbar.grid(row=0, column=1, sticky="ns")

        else:
            # Mobile (<680px): Hide left sidebar, show Bottom Navigation Bar
            self.sidebar.grid_remove()
            self.root_container.columnconfigure(0, minsize=0)
            self.bottom_nav.grid(row=1, column=0, columnspan=2, sticky="ew")

            # Compact 2-row Mobile Header
            self.main_area.config(padx=12, pady=10)
            self.welcome_lbl.config(text=f"E Bank • {welcome_name}", font=(FONT_FAMILY, 14, "bold"))
            self.user_name_lbl.pack_forget()
            self.search_holder_inline.pack_forget()
            self.search_holder_mobile.grid(row=1, column=0, sticky="ew", pady=(8, 0))
            self.search_canvas = self._reparent_search(self.search_holder_mobile, width=320)
            self.page_scrollbar.grid(row=0, column=1, sticky="ns")

        self._draw_sidebar_nav()
        self._draw_bottom_mobile_nav()

        for v in self.views.values():
            if hasattr(v, "set_layout_mode"):
                v.set_layout_mode(mode)

    def _reparent_search(self, parent_holder: tk.Frame, width: int) -> tk.Canvas:
        """Move the search canvas cleanly between inline header (desktop/tablet) and row-2 (mobile)."""
        current_val = self.search_var.get()
        is_ph = getattr(self, "_search_placeholder", False)

        for w in self.search_holder_inline.winfo_children():
            w.destroy()
        for w in self.search_holder_mobile.winfo_children():
            w.destroy()

        c = tk.Canvas(parent_holder, width=width, height=36, bg=BG_MAIN, highlightthickness=0)
        c.pack(fill="x", expand=True)

        self.search_entry = tk.Entry(
            c, textvariable=self.search_var,
            font=(FONT_FAMILY, 10), bg=SEARCH_BG, fg=TEXT_MUTED if is_ph else TEXT_DARK,
            relief="flat", bd=0, insertbackground=TEXT_DARK
        )
        self._search_win = c.create_window(width // 2, 18, window=self.search_entry, width=width - 48, height=20)
        c.bind("<Configure>", self._redraw_search_pill)

        def on_search_focus_in(e):
            if self._search_placeholder:
                self._search_placeholder = False
                self.search_entry.delete(0, "end")
                self.search_entry.config(fg=TEXT_DARK)

        def on_search_focus_out(e):
            if not self.search_entry.get().strip():
                self._search_placeholder = True
                self.search_entry.delete(0, "end")
                self.search_entry.insert(0, "Search")
                self.search_entry.config(fg=TEXT_MUTED)

        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)
        return c

    def _get_clean_search_var(self):
        proxy = tk.StringVar(value="")
        self._clean_search_proxy = proxy
        return proxy

    def _on_search_changed(self):
        if not hasattr(self, "_clean_search_proxy"):
            return
        val = self.search_var.get()
        if getattr(self, "_search_placeholder", False) or val == "Search":
            self._clean_search_proxy.set("")
        else:
            self._clean_search_proxy.set(val)

        if hasattr(self, "views"):
            self.views["home"]._draw_transactions_card()
            self.views["transactions"].refresh_data()

    def _draw_sidebar_nav(self):
        if not hasattr(self, "nav_canvas") or not self.nav_canvas.winfo_exists():
            return
        c = self.nav_canvas
        c.delete("all")
        is_rail = (self.device_mode == "tablet")

        nav_items = [
            ("home", "Home"),
            ("transfer", "Transfer"),
            ("transactions", "Transactions"),
        ]

        y_start = 10
        item_h = 46
        gap = 8

        for idx, (key, label) in enumerate(nav_items):
            y1 = y_start + idx * (item_h + gap)
            y2 = y1 + item_h
            is_active = (self.active_tab == key)
            tag = f"nav_{key}"

            pill_right = 64 if is_rail else 202
            if is_active:
                create_rounded_rect(
                    c, -14 if not is_rail else 8, y1, pill_right, y2, r=20,
                    fill=SIDEBAR_ACTIVE_BG, outline="", tags=(tag,)
                )
                fg_color = PRIMARY_BLUE
                font_weight = "bold"
            else:
                create_rounded_rect(
                    c, -14 if not is_rail else 8, y1, pill_right, y2, r=20,
                    fill=BG_SIDEBAR, outline="", tags=(tag,)
                )
                fg_color = TEXT_DARK
                font_weight = "normal"

            ix = 36 if is_rail else 32
            iy = (y1 + y2) / 2
            self._draw_nav_icon(c, key, ix, iy, fg_color, tag)

            if not is_rail:
                c.create_text(
                    54, iy,
                    text=label,
                    font=(FONT_FAMILY, 10, font_weight),
                    fill=fg_color, anchor="w", tags=(tag,)
                )

            c.tag_bind(tag, "<Button-1>", lambda e, k=key: self.navigate(k))
            c.tag_bind(tag, "<Enter>", lambda e: c.config(cursor="hand2"))
            c.tag_bind(tag, "<Leave>", lambda e: c.config(cursor=""))

    def _draw_bottom_mobile_nav(self):
        if not hasattr(self, "bottom_nav") or not self.bottom_nav.winfo_exists():
            return
        c = self.bottom_nav
        c.delete("all")
        w = max(c.winfo_width(), 360)
        h = max(c.winfo_height(), 58)

        items = [
            ("home", "Home"),
            ("transfer", "Transfer"),
            ("transactions", "Transactions"),
            ("logout", "Logout"),
        ]
        col_w = w / len(items)

        for idx, (key, label) in enumerate(items):
            cx = col_w * (idx + 0.5)
            is_active = (self.active_tab == key)
            fg_color = PRIMARY_BLUE if is_active else TEXT_MEDIUM
            tag = f"mnav_{key}"

            if is_active:
                create_rounded_rect(
                    c, cx - 34, 6, cx + 34, h - 6, r=14,
                    fill=SIDEBAR_ACTIVE_BG, outline="", tags=(tag,)
                )

            self._draw_nav_icon(c, key, cx, 20, fg_color, tag)
            c.create_text(
                cx, 42, text=label,
                font=(FONT_FAMILY, 8, "bold" if is_active else "normal"),
                fill=fg_color, tags=(tag,)
            )

            if key == "logout":
                c.tag_bind(tag, "<Button-1>", lambda e: self.show_auth())
            else:
                c.tag_bind(tag, "<Button-1>", lambda e, k=key: self.navigate(k))

    def _draw_nav_icon(self, c: tk.Canvas, key: str, ix: float, iy: float, fg_color: str, tag: str):
        if key == "home":
            c.create_polygon(
                ix, iy - 7, ix - 8, iy, ix - 5, iy, ix - 5, iy + 7,
                ix - 1, iy + 7, ix - 1, iy + 2, ix + 1, iy + 2, ix + 1, iy + 7,
                ix + 5, iy + 7, ix + 5, iy, ix + 8, iy,
                fill=fg_color, outline=fg_color, width=1, tags=(tag,)
            )
        elif key == "transfer":
            c.create_line(ix - 7, iy - 3, ix + 6, iy - 3, fill=fg_color, width=1.8, tags=(tag,))
            c.create_polygon(ix + 3, iy - 6, ix + 8, iy - 3, ix + 3, iy, fill=fg_color, outline="", tags=(tag,))
            c.create_line(ix - 6, iy + 3, ix + 7, iy + 3, fill=fg_color, width=1.8, tags=(tag,))
            c.create_polygon(ix - 3, iy, ix - 8, iy + 3, ix - 3, iy + 6, fill=fg_color, outline="", tags=(tag,))
        elif key == "transactions":
            c.create_line(ix - 7, iy - 4, ix + 6, iy - 4, fill=fg_color, width=1.8, tags=(tag,))
            c.create_polygon(ix + 3, iy - 7, ix + 8, iy - 4, ix + 3, iy - 1, fill=fg_color, outline="", tags=(tag,))
            c.create_line(ix - 6, iy + 4, ix + 7, iy + 4, fill=fg_color, width=1.8, tags=(tag,))
            c.create_polygon(ix - 3, iy + 1, ix - 8, iy + 4, ix - 3, iy + 7, fill=fg_color, outline="", tags=(tag,))
        elif key == "logout":
            c.create_rectangle(ix - 6, iy - 6, ix + 2, iy + 6, outline=fg_color, width=1.5, tags=(tag,))
            c.create_line(ix - 1, iy, ix + 7, iy, fill=fg_color, width=1.8, tags=(tag,))
            c.create_polygon(ix + 4, iy - 3, ix + 8, iy, ix + 4, iy + 3, fill=fg_color, outline="", tags=(tag,))

    def navigate(self, target: str):
        focus_dep = False
        if target == "deposit":
            target = "transfer"
            focus_dep = True

        self.active_tab = target
        self._draw_sidebar_nav()
        self._draw_bottom_mobile_nav()

        for k, v in self.views.items():
            if k == target:
                v.refresh_data()
                v.grid(row=0, column=0, sticky="nsew")
                v.tkraise()
            else:
                v.grid_remove()

        self.page_canvas.yview_moveto(0)
        if focus_dep and hasattr(self.views["transfer"], "focus_deposit"):
            self.views["transfer"].focus_deposit()

    def _refresh_all_views(self):
        for v in self.views.values():
            v.refresh_data()


def run_app():
    app = EBankApp()
    app.mainloop()
