"""
UI 스타일 정의 — 소프트 로즈·라벤더 프리미엄 테마
KBS 보도영상국 파견인력관리 시스템
"""
import tkinter as tk
from tkinter import ttk


# ===== 색상 팔레트 — 소프트 로즈·라벤더 =====
COLORS = {
    # ── 배경 ──
    'bg_main':     '#F5F3F8',   # 연보라빛 메인 배경
    'bg_sidebar':  '#2C2540',   # 다크 플럼 헤더
    'bg_card':     '#FFFFFF',   # 흰 카드
    'bg_input':    '#FAF8FC',   # 입력 필드 (살짝 보라)
    'bg_hover':    '#F3EFFE',   # 연보라 호버
    'bg_selected': '#EDE6FD',   # 선택
    'bg_header':   '#EDE8F5',   # 테이블 헤더 (연보라)
    'bg_stripe':   '#FAF8FC',   # 줄무늬

    # ── 포인트 — 소프트 로즈·라벤더 ──
    'accent_primary':  '#9B7FD4',   # 소프트 라벤더
    'accent_dark':     '#7457B0',   # 다크 라벤더
    'accent_blue':     '#7B9FE0',   # 소프트 블루
    'accent_purple':   '#B89EE8',   # 연보라
    'accent_green':    '#7DC4A0',   # 소프트 민트그린
    'accent_red':      '#E08080',   # 소프트 로즈레드
    'accent_orange':   '#E8A87C',   # 소프트 피치
    'accent_cyan':     '#7BBFCE',   # 소프트 스카이
    'accent_pink':     '#D4809B',   # 소프트 핑크
    'accent_teal':     '#7ECBC4',   # 소프트 틸

    # ── 텍스트 ──
    'text_primary':   '#1A1A2E',   # 거의 검정
    'text_secondary': '#5C5470',   # 다크 플럼 그레이
    'text_muted':     '#9E96B0',   # 연한 보라 그레이
    'text_white':     '#FFFFFF',
    'text_sidebar':   '#D8D0EE',   # 사이드바 텍스트

    # ── 테두리 ──
    'border':       '#E4DDEF',
    'border_light': '#EDE8F5',
    'divider':      '#D5CCEC',

    # ── 배지 ──
    'badge_green_bg':  '#EEF8F3', 'badge_green_fg':  '#4A9E78',
    'badge_red_bg':    '#FDEEED', 'badge_red_fg':    '#C26060',
    'badge_blue_bg':   '#EEF3FD', 'badge_blue_fg':   '#5B80C4',
    'badge_amber_bg':  '#FDF5EE', 'badge_amber_fg':  '#C48050',
    'badge_purple_bg': '#F0EAFA', 'badge_purple_fg': '#7457B0',
    'badge_cyan_bg':   '#EEF7FA', 'badge_cyan_fg':   '#4A9AAE',
    'badge_pink_bg':   '#FAEEF3', 'badge_pink_fg':   '#B05878',

    # ── 상태 ──
    'status_active': '#4A9E78',
    'status_new':    '#5B80C4',
    'status_left':   '#C26060',
    'status_cancel': '#9E96B0',

    # ── 호환 ──
    'bg_selected_row': '#F0EAFA',
}

# ===== 폰트 =====
FONTS = {
    'title':         ('맑은 고딕', 26, 'bold'),
    'subtitle':      ('맑은 고딕', 22, 'bold'),
    'heading':       ('맑은 고딕', 19, 'bold'),
    'body':          ('맑은 고딕', 18),
    'body_bold':     ('맑은 고딕', 18, 'bold'),
    'small':         ('맑은 고딕', 17),
    'small_bold':    ('맑은 고딕', 17, 'bold'),
    'tiny':          ('맑은 고딕', 15),
    'mono':          ('Consolas', 17),
    'sidebar':       ('맑은 고딕', 18),
    'sidebar_active':('맑은 고딕', 18, 'bold'),
    'button':        ('맑은 고딕', 17, 'bold'),
    'tab':           ('맑은 고딕', 17, 'bold'),
    'tab_active':    ('맑은 고딕', 17, 'bold'),
    'header_title':  ('맑은 고딕', 22, 'bold'),
    'logo':          ('맑은 고딕', 20, 'bold'),
}


def configure_styles(root):
    """ttk 스타일 전체 설정"""
    style = ttk.Style(root)
    style.theme_use('clam')

    # ── Treeview ──
    style.configure('Custom.Treeview',
                    background=COLORS['bg_card'],
                    foreground='#1A1A2E',          # 인력 표시글 검정
                    fieldbackground=COLORS['bg_card'],
                    font=FONTS['body'],
                    rowheight=58,
                    borderwidth=0,
                    relief='flat')
    style.configure('Custom.Treeview.Heading',
                    background=COLORS['bg_header'],
                    foreground=COLORS['text_secondary'],
                    font=FONTS['small_bold'],
                    borderwidth=0,
                    relief='flat',
                    padding=[10, 10])
    style.map('Custom.Treeview',
              background=[('selected', COLORS['badge_purple_bg'])],
              foreground=[('selected', COLORS['accent_dark'])])
    style.map('Custom.Treeview.Heading',
              background=[('active', COLORS['border_light'])])

    # ── Notebook ──
    style.configure('Custom.TNotebook',
                    background=COLORS['bg_main'],
                    borderwidth=0)
    style.configure('Custom.TNotebook.Tab',
                    background=COLORS['bg_card'],
                    foreground=COLORS['text_muted'],
                    font=FONTS['tab'],
                    padding=[20, 10],
                    borderwidth=0)
    style.map('Custom.TNotebook.Tab',
              background=[('selected', COLORS['bg_hover']),
                          ('active',   COLORS['bg_hover'])],
              foreground=[('selected', COLORS['accent_primary']),
                          ('active',   COLORS['accent_primary'])])

    # ── Buttons ──
    for name, bg, fg, hover in [
        ('Accent.TButton',  COLORS['accent_primary'], COLORS['text_white'], COLORS['accent_dark']),
        ('Primary.TButton', '#2C2540',                COLORS['text_white'], '#3D3358'),
        ('Success.TButton', COLORS['badge_green_bg'],  COLORS['badge_green_fg'], '#D8F2E8'),
        ('Danger.TButton',  COLORS['badge_red_bg'],    COLORS['badge_red_fg'],   '#FAD8D8'),
        ('Outline.TButton', COLORS['bg_card'],         COLORS['text_primary'],   COLORS['bg_hover']),
    ]:
        style.configure(name, background=bg, foreground=fg,
                        font=FONTS['button'], padding=[22, 12],
                        borderwidth=0, relief='flat')
        style.map(name, background=[('active', hover), ('pressed', hover)])

    # ── Entry ──
    style.configure('Custom.TEntry',
                    fieldbackground=COLORS['bg_input'],
                    foreground=COLORS['text_primary'],
                    insertcolor=COLORS['accent_primary'],
                    bordercolor=COLORS['border'],
                    borderwidth=1, relief='solid', padding=[11, 9])

    # ── Combobox ──
    style.configure('Custom.TCombobox',
                    fieldbackground=COLORS['bg_input'],
                    foreground=COLORS['text_primary'],
                    background=COLORS['bg_card'],
                    selectbackground=COLORS['badge_purple_bg'],
                    selectforeground=COLORS['accent_dark'],
                    borderwidth=1, relief='solid', padding=[9, 8])
    style.map('Custom.TCombobox',
              fieldbackground=[('readonly', COLORS['bg_input'])],
              background=[('readonly', COLORS['bg_card'])])

    # ── Scrollbar ──
    for name in ('Custom.Vertical.TScrollbar', 'Custom.Horizontal.TScrollbar'):
        style.configure(name,
                        background=COLORS['border'],
                        troughcolor=COLORS['bg_main'],
                        borderwidth=0, arrowsize=14, relief='flat')
        style.map(name, background=[('active', COLORS['accent_primary'])])

    # ── LabelFrame ──
    style.configure('Card.TLabelframe',
                    background=COLORS['bg_card'],
                    foreground=COLORS['text_primary'],
                    font=FONTS['heading'],
                    borderwidth=1, relief='solid',
                    bordercolor=COLORS['border'])
    style.configure('Card.TLabelframe.Label',
                    background=COLORS['bg_card'],
                    foreground=COLORS['accent_primary'],
                    font=FONTS['heading'])

    return style


# ─────────────────────────────────────────
#  버튼 팩토리
# ─────────────────────────────────────────
def create_rounded_button(parent, text, command,
                           color=None, width=None, small=False):
    """소프트 포인트 버튼"""
    bg = color or COLORS['accent_primary']
    pady = 9 if small else 13
    padx = 14 if small else 22
    font = FONTS['small_bold'] if small else FONTS['button']

    def _darken(c, f=0.82):
        c = c.lstrip('#')
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        return f'#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}'

    hover = _darken(bg)
    btn = tk.Button(parent, text=text, command=command,
                    bg=bg, fg=COLORS['text_white'], font=font,
                    relief='flat', cursor='hand2',
                    padx=padx, pady=pady,
                    activebackground=hover, activeforeground=COLORS['text_white'],
                    borderwidth=0, highlightthickness=0)
    if width:
        btn.configure(width=width)
    btn.bind('<Enter>', lambda e: btn.configure(bg=hover))
    btn.bind('<Leave>', lambda e: btn.configure(bg=bg))
    return btn


def create_outline_button(parent, text, command, fg_color=None, width=None):
    """아웃라인 버튼"""
    fg = fg_color or COLORS['text_primary']
    btn = tk.Button(parent, text=text, command=command,
                    bg=COLORS['bg_card'], fg=fg, font=FONTS['button'],
                    relief='solid', cursor='hand2', padx=20, pady=10,
                    activebackground=COLORS['bg_hover'], activeforeground=fg,
                    borderwidth=1, highlightthickness=1,
                    highlightbackground=COLORS['border'])
    if width:
        btn.configure(width=width)
    btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['bg_hover']))
    btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['bg_card']))
    return btn


# ─────────────────────────────────────────
#  배지 / 상태 레이블
# ─────────────────────────────────────────
def create_badge_label(parent, text, style='blue'):
    MAP = {
        'green':  (COLORS['badge_green_bg'],  COLORS['badge_green_fg']),
        'red':    (COLORS['badge_red_bg'],    COLORS['badge_red_fg']),
        'blue':   (COLORS['badge_blue_bg'],   COLORS['badge_blue_fg']),
        'amber':  (COLORS['badge_amber_bg'],  COLORS['badge_amber_fg']),
        'purple': (COLORS['badge_purple_bg'], COLORS['badge_purple_fg']),
        'cyan':   (COLORS['badge_cyan_bg'],   COLORS['badge_cyan_fg']),
        'pink':   (COLORS['badge_pink_bg'],   COLORS['badge_pink_fg']),
        'gray':   ('#F0EEF5',                 COLORS['text_secondary']),
    }
    bg, fg = MAP.get(style, MAP['blue'])
    return tk.Label(parent, text=f'  {text}  ',
                    bg=bg, fg=fg, font=FONTS['small_bold'], padx=3, pady=2)


def create_status_badge(parent, status):
    MAP = {'재직': 'green', '신규': 'blue', '퇴사': 'red', '입사포기': 'gray'}
    return create_badge_label(parent, status, MAP.get(status, 'gray'))


# ─────────────────────────────────────────
#  헬퍼
# ─────────────────────────────────────────
def make_card_frame(parent, padx=0, pady=0):
    return tk.Frame(parent, bg=COLORS['bg_card'],
                    highlightthickness=1,
                    highlightbackground=COLORS['border'])


def make_section_header(parent, title, bg=None):
    bg = bg or COLORS['bg_card']
    return tk.Label(parent, text=title, font=FONTS['subtitle'],
                    bg=bg, fg=COLORS['text_primary'])


def make_label(parent, text, style='body', bg=None):
    bg = bg or COLORS['bg_card']
    FMAP = {
        'title': FONTS['title'], 'subtitle': FONTS['subtitle'],
        'heading': FONTS['heading'], 'body': FONTS['body'],
        'body_bold': FONTS['body_bold'], 'small': FONTS['small'],
        'small_bold': FONTS['small_bold'], 'muted': FONTS['small'],
    }
    fg = COLORS['text_secondary'] if style == 'muted' else COLORS['text_primary']
    return tk.Label(parent, text=text, font=FMAP.get(style, FONTS['body']),
                    bg=bg, fg=fg)
