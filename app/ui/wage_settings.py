"""
임금설정 다이얼로그
직군별 기본급, 시급, 간접비율, 퇴직충당금율 설정
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.styles import COLORS, FONTS, create_rounded_button
from app import database as db
from app.models import WageConfig


class WageSettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("💰 임금설정")
        self.geometry("700x500")
        self.configure(bg=COLORS['bg_main'])
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 350
        y = (self.winfo_screenheight() // 2) - 250
        self.geometry(f'+{x}+{y}')
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=10)
        header.pack(fill='x', padx=10, pady=(10, 5))
        tk.Label(header, text="직군별 임금 설정", font=FONTS['subtitle'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(side='left')
        tk.Label(header, text="🔒 반올림: 원 단위 내림 (고정)", font=FONTS['small_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['accent_orange']).pack(side='right')

        btn_frame = tk.Frame(header, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', pady=(8, 0))
        create_rounded_button(btn_frame, "➕ 추가", self.add_config,
                              color=COLORS['accent_green']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "✏️ 수정", self.edit_config,
                              color=COLORS['accent_blue']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "🗑️ 삭제", self.delete_config,
                              color=COLORS['accent_red']).pack(side='left', padx=3)

        list_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=10, pady=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        cols = ('no', 'job_type', 'grade', 'base_salary', 'hourly_wage', 'indirect', 'retirement')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings',
                                  style="Custom.Treeview", height=12)
        hdrs = {'no': ('No', 40), 'job_type': ('직군', 80), 'grade': ('등급', 60),
                'base_salary': ('기본급', 110), 'hourly_wage': ('시급', 90),
                'indirect': ('간접비율', 80), 'retirement': ('퇴직충당금율', 100)}
        for c, (t, w) in hdrs.items():
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor='center')
        self.tree.pack(fill='both', expand=True)

        info = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=8)
        info.pack(fill='x', padx=10, pady=(0, 10))
        tk.Label(info, text="※ 시간외수당 계산식: 평일연장[시급×1.5×1.1] | 휴일[시급×1.5×1.1] | 휴일연장[시급×2.0×1.1] | 야간[시급×0.5×1.1]",
                 font=FONTS['small'], bg=COLORS['bg_card'], fg=COLORS['accent_cyan']).pack(anchor='w')

    def load_data(self):
        configs = db.get_all_wage_configs()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, c in enumerate(configs, 1):
            self.tree.insert('', 'end', iid=str(c.id),
                             values=(i, c.job_type, c.grade, f"{c.base_salary:,}",
                                     f"{c.hourly_wage:,}",
                                     f"{c.indirect_ratio:.6f}",
                                     f"{c.retirement_ratio:.6f}"))

    def add_config(self):
        self._open_dialog(None)

    def edit_config(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("선택", "수정할 항목을 선택하세요.")
            return
        cid = int(sel[0])
        configs = db.get_all_wage_configs()
        cfg = next((c for c in configs if c.id == cid), None)
        if cfg:
            self._open_dialog(cfg)

    def delete_config(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("삭제", "삭제하시겠습니까?"):
            db.delete_wage_config(int(sel[0]))
            self.load_data()

    def _open_dialog(self, config):
        dlg = tk.Toplevel(self)
        dlg.title("임금설정" if config else "임금설정 추가")
        dlg.geometry("520x380")
        dlg.configure(bg=COLORS['bg_main'])
        dlg.transient(self)
        dlg.grab_set()
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() // 2) - 200
        y = (dlg.winfo_screenheight() // 2) - 175
        dlg.geometry(f'+{x}+{y}')

        form = tk.Frame(dlg, bg=COLORS['bg_card'], padx=20, pady=15)
        form.pack(fill='both', expand=True, padx=10, pady=10)

        if config is None:
            config = WageConfig()

        entries = {}
        # 간접비율·퇴직충당금율은 소수점 4자리까지 그대로 표시
        indirect_str = f"{config.indirect_ratio:.6f}" if config.indirect_ratio else "0.000000"
        retire_str   = f"{config.retirement_ratio:.6f}" if config.retirement_ratio else "0.000000"
        fields = [('job_type', '직군', config.job_type), ('grade', '등급', config.grade),
                  ('base_salary', '기본급', str(config.base_salary)),
                  ('hourly_wage', '시급', str(config.hourly_wage)),
                  ('indirect_ratio', '간접비율 (소수, 예:0.123456)', indirect_str),
                  ('retirement_ratio', '퇴직충당금율 (소수, 예:0.083333)', retire_str)]

        for key, name, val in fields:
            row = tk.Frame(form, bg=COLORS['bg_card'], pady=4)
            row.pack(fill='x')
            lbl_width = 22 if key in ('indirect_ratio', 'retirement_ratio') else 10
            tk.Label(row, text=name, font=FONTS['body_bold'], width=lbl_width, anchor='w',
                     bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
            if key == 'job_type':
                v = tk.StringVar(value=val)
                ttk.Combobox(row, textvariable=v, values=["촬영보조", "인제스트"],
                             state='readonly', style="Custom.TCombobox").pack(side='left', fill='x', expand=True)
                entries[key] = v
            elif key == 'grade':
                v = tk.StringVar(value=val)
                ttk.Combobox(row, textvariable=v, values=["가급", "나급"],
                             state='readonly', style="Custom.TCombobox").pack(side='left', fill='x', expand=True)
                entries[key] = v
            else:
                e = tk.Entry(row, bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                             insertbackground=COLORS['text_primary'], font=FONTS['body'], relief='flat')
                e.insert(0, val)
                e.pack(side='left', fill='x', expand=True, ipady=4)
                entries[key] = e

        bf = tk.Frame(form, bg=COLORS['bg_card'], pady=10)
        bf.pack(fill='x')

        def save():
            try:
                config.job_type = entries['job_type'].get()
                config.grade = entries['grade'].get()
                config.base_salary = int(entries['base_salary'].get().replace(',', ''))
                config.hourly_wage = int(entries['hourly_wage'].get().replace(',', ''))
                # 간접비율·퇴직충당금율: 반올림 없이 소수점 4자리 정밀도 유지
                from decimal import Decimal, ROUND_DOWN
                indirect_raw = entries['indirect_ratio'].get().strip()
                retire_raw   = entries['retirement_ratio'].get().strip()
                config.indirect_ratio   = float(Decimal(indirect_raw).quantize(Decimal('0.000001'), rounding=ROUND_DOWN))
                config.retirement_ratio = float(Decimal(retire_raw).quantize(Decimal('0.000001'), rounding=ROUND_DOWN))
                db.save_wage_config(config)
                dlg.destroy()
                self.load_data()
            except Exception as ex:
                messagebox.showerror("오류", f"입력값 오류:\n{ex}\n\n간접비율 예시: 0.123456")

        create_rounded_button(bf, "💾 저장", save, color=COLORS['accent_green']).pack(side='right', padx=5)
        create_rounded_button(bf, "취소", dlg.destroy, color=COLORS['bg_input']).pack(side='right', padx=5)
