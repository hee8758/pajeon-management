"""
메인 윈도우 — 소프트 로즈·라벤더 프리미엄 레이아웃
KBS 보도영상국 파견인력관리 시스템
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.ui.styles import COLORS, FONTS, configure_styles, create_rounded_button
from app.ui.dispatch_tab import DispatchTab
from app.ui.company_tab import CompanyTab
from app.ui.payroll_tab import PayrollTab
from app.ui.statistics_tab import StatisticsTab
from app import database as db
from app.csv_importer import auto_import_all
import os


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("KBS 보도영상국 파견인력 관리 시스템")
        self.root.geometry("1440x900")
        self.root.minsize(1200, 720)
        self.root.configure(bg=COLORS['bg_main'])

        try:
            self.root.state('zoomed')
        except Exception:
            self.root.attributes('-zoomed', True)

        configure_styles(self.root)

        try:
            self.root.iconbitmap(default='')
        except Exception:
            pass

        self._build_ui()
        self._auto_import_data()

    # ──────────────────────────────────────────────
    def _build_ui(self):

        # ══════════════════════════════════════════
        #  앱 헤더 (다크 플럼 배경)
        # ══════════════════════════════════════════
        header = tk.Frame(self.root, bg=COLORS['bg_sidebar'])
        header.pack(fill='x')

        # 상단 소프트 그라디언트 바
        grad = tk.Frame(header, bg=COLORS['bg_sidebar'])
        grad.pack(fill='x')
        for color, h in [
            ('#C9A8E8', 3),   # 연보라
            ('#E8A8C4', 2),   # 연핑크
            ('#A8C4E8', 1),   # 연블루
        ]:
            tk.Frame(grad, bg=color, height=h).pack(fill='x')

        inner = tk.Frame(header, bg=COLORS['bg_sidebar'])
        inner.pack(fill='x', padx=28, pady=14)

        # ── 좌측: 로고 + 타이틀 ──
        left = tk.Frame(inner, bg=COLORS['bg_sidebar'])
        left.pack(side='left')

        # 로고: 소프트 라벤더 박스
        logo_box = tk.Frame(left, bg=COLORS['accent_primary'],
                            width=50, height=50)
        logo_box.pack(side='left', padx=(0, 16))
        logo_box.pack_propagate(False)
        tk.Label(logo_box, text='📋', font=('맑은 고딕', 22),
                 bg=COLORS['accent_primary'], fg='white').place(relx=0.5, rely=0.5, anchor='center')

        # 타이틀
        title_col = tk.Frame(left, bg=COLORS['bg_sidebar'])
        title_col.pack(side='left')

        tk.Label(title_col,
                 text='KBS 보도영상국  파견인력 관리 시스템',
                 font=FONTS['header_title'],
                 bg=COLORS['bg_sidebar'],
                 fg='#EDE8F8').pack(anchor='w')

        sub_row = tk.Frame(title_col, bg=COLORS['bg_sidebar'])
        sub_row.pack(anchor='w', pady=(4, 0))

        for txt, clr in [
            ('파견현황', '#B89EE8'),
            ('  ·  ', '#5C5070'),
            ('파견료 정산', '#E8A8C4'),
            ('  ·  ', '#5C5070'),
            ('업체 관리', '#A8C4E8'),
        ]:
            tk.Label(sub_row, text=txt, font=FONTS['small'],
                     bg=COLORS['bg_sidebar'], fg=clr).pack(side='left')

        # ── 우측: CSV 버튼 + 규칙 배지 ──
        right = tk.Frame(inner, bg=COLORS['bg_sidebar'])
        right.pack(side='right')

        rule_badge = tk.Frame(right, bg='#3A2E4A',
                              highlightthickness=1,
                              highlightbackground='#C9A8E8')
        rule_badge.pack(side='right', padx=(14, 0))
        tk.Label(rule_badge,
                 text='🔒  원 단위 내림  (고정)',
                 font=FONTS['small_bold'],
                 bg='#3A2E4A', fg='#C9A8E8',
                 padx=12, pady=7).pack()

        create_rounded_button(right, '📂  CSV 임포트', self._import_csv,
                              color=COLORS['accent_blue']).pack(side='right', padx=(0, 14))

        # ══════════════════════════════════════════
        #  탭 바 (미디엄 플럼)
        # ══════════════════════════════════════════
        tab_outer = tk.Frame(self.root, bg='#221C35')
        tab_outer.pack(fill='x')

        # 탭바 상단 미세 구분선
        tk.Frame(tab_outer, bg='#C9A8E8', height=1).pack(fill='x')

        tab_inner = tk.Frame(tab_outer, bg='#221C35')
        tab_inner.pack(fill='x', padx=16)

        self._tab_buttons = {}
        self._current_tab = None

        menus = [
            ('📋  파견현황',    'dispatch',   '#B89EE8', '#D0BEFF'),
            ('🏢  파견업체',    'company',    '#E8A8C4', '#FFD0E8'),
            ('💰  파견료 정산', 'payroll',    '#A8C4E8', '#C8DEFF'),
            ('📊  통계',        'statistics', '#A8D8C4', '#C8F0E0'),
        ]

        for text, key, accent, light in menus:
            wrapper = tk.Frame(tab_inner, bg='#221C35')
            wrapper.pack(side='left')

            btn = tk.Button(
                wrapper, text=text,
                font=FONTS['tab'],
                bg='#221C35', fg='#7A6E90',
                relief='flat', cursor='hand2',
                padx=28, pady=14,
                borderwidth=0, highlightthickness=0,
                activebackground='#2E2448',
                activeforeground=light,
                command=lambda k=key, a=accent, w=wrapper: self._show_tab(k, a, w)
            )
            btn.pack()

            indicator = tk.Frame(wrapper, bg='#221C35', height=3)
            indicator.pack(fill='x')

            self._tab_buttons[key] = (btn, accent, wrapper, indicator, light)

            def _enter(e, b=btn, l=light):
                if self._current_tab and self._tab_buttons[self._current_tab][0] is not b:
                    b.configure(bg='#2E2448', fg=l)

            def _leave(e, b=btn, k=key):
                if self._current_tab != k:
                    b.configure(bg='#221C35', fg='#7A6E90')

            btn.bind('<Enter>', _enter)
            btn.bind('<Leave>', _leave)

        # ══════════════════════════════════════════
        #  콘텐츠 영역
        # ══════════════════════════════════════════
        self.content_frame = tk.Frame(self.root, bg=COLORS['bg_main'])
        self.content_frame.pack(fill='both', expand=True)

        self.tabs = {}
        self._show_tab('dispatch', '#B89EE8',
                       self._tab_buttons['dispatch'][2])

    # ──────────────────────────────────────────────
    def _show_tab(self, key, accent=None, wrapper=None):
        if self._current_tab == key:
            return
        accent = accent or COLORS['accent_primary']

        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

        for k, tdata in self._tab_buttons.items():
            btn, ac, wrp, ind, light = tdata
            if k == key:
                btn.configure(bg='#2E2448', fg=light,
                               font=(*FONTS['tab_active'][:2], 'bold'))
                ind.configure(bg=ac)
            else:
                btn.configure(bg='#221C35', fg='#7A6E90',
                               font=FONTS['tab'])
                ind.configure(bg='#221C35')

        if key not in self.tabs:
            if key == 'dispatch':
                self.tabs[key] = DispatchTab(self.content_frame, self)
            elif key == 'company':
                self.tabs[key] = CompanyTab(self.content_frame, self)
            elif key == 'payroll':
                self.tabs[key] = PayrollTab(self.content_frame, self)
            elif key == 'statistics':
                self.tabs[key] = StatisticsTab(self.content_frame, self)

        self.tabs[key].pack(fill='both', expand=True)
        self._current_tab = key

        if hasattr(self.tabs[key], 'load_data'):
            self.tabs[key].load_data()

    # ──────────────────────────────────────────────
    def _auto_import_data(self):
        workers = db.get_all_workers()
        if not workers:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(os.path.join(base_dir, '촬영보조.csv')):
                base_dir = os.path.dirname(base_dir)
            msg = auto_import_all(base_dir)
            if msg:
                messagebox.showinfo('데이터 초기화',
                                    f'CSV 데이터를 자동 임포트했습니다.\n\n{msg}')
                if 'dispatch' in self.tabs:
                    self.tabs['dispatch'].load_data()

    def _import_csv(self):
        folder = filedialog.askdirectory(title='CSV 파일이 있는 폴더를 선택하세요')
        if not folder:
            return
        msg = auto_import_all(folder)
        messagebox.showinfo('임포트 결과', msg)
        for tab in self.tabs.values():
            if hasattr(tab, 'load_data'):
                tab.load_data()
