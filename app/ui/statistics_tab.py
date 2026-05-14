"""
통계 시트 UI - 시간외근무 순위별 나열
"""
import tkinter as tk
from tkinter import ttk
from app.ui.styles import COLORS, FONTS, create_rounded_button
from app import database as db


class StatisticsTab(tk.Frame):
    """통계 탭"""

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=10)
        top.pack(fill='x', padx=10, pady=(10, 5))
        tk.Label(top, text="📊 시간외근무 통계", font=FONTS['subtitle'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(side='left')

        row2 = tk.Frame(top, bg=COLORS['bg_card'])
        row2.pack(fill='x', pady=(8, 0))

        tk.Label(row2, text="연도", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.year_var = tk.StringVar(value="2026")
        ttk.Combobox(row2, textvariable=self.year_var,
                     values=[str(y) for y in range(2024, 2031)], width=6,
                     state='readonly', style="Custom.TCombobox").pack(side='left', padx=(5, 15))

        tk.Label(row2, text="월", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.month_var = tk.StringVar(value="3")
        ttk.Combobox(row2, textvariable=self.month_var,
                     values=[str(m) for m in range(1, 13)], width=4,
                     state='readonly', style="Custom.TCombobox").pack(side='left', padx=(5, 15))

        create_rounded_button(row2, "📊 조회", self.load_stats,
                              color=COLORS['accent_cyan']).pack(side='left', padx=10)

        self.summary_label = tk.Label(row2, text="", font=FONTS['body_bold'],
                                       bg=COLORS['bg_card'], fg=COLORS['text_primary'])
        self.summary_label.pack(side='right')

        # 순위 목록
        list_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=10, pady=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        cols = ('rank', 'name', 'dept', 'job', 'company', 'total_hrs',
                'wd_ot', 'hol', 'hol_ot', 'night', 'ot_total_amt')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings',
                                  style="Custom.Treeview", height=22)
        hdrs = {
            'rank': ('순위', 45), 'name': ('성명', 80), 'dept': ('부서', 85),
            'job': ('직군', 70), 'company': ('파견업체', 90),
            'total_hrs': ('총시간', 60), 'wd_ot': ('평일연장(h)', 75),
            'hol': ('휴일(h)', 60), 'hol_ot': ('휴일연장(h)', 75),
            'night': ('야간(h)', 55), 'ot_total_amt': ('수당합계', 95),
        }
        for c, (t, w) in hdrs.items():
            self.tree.heading(c, text=t)
            anch = 'e' if c == 'ot_total_amt' else 'center'
            self.tree.column(c, width=w, anchor=anch)

        scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        # 부서별 요약
        summary_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=10)
        summary_frame.pack(fill='x', padx=10, pady=(5, 10))
        tk.Label(summary_frame, text="부서별 시간외근무 요약", font=FONTS['heading'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(anchor='w', pady=(0, 5))

        dcols = ('dept', 'count', 'avg_hrs', 'max_hrs', 'total_amt')
        self.dept_tree = ttk.Treeview(summary_frame, columns=dcols, show='headings',
                                       style="Custom.Treeview", height=5)
        dhdrs = {'dept': ('부서', 120), 'count': ('인원', 60), 'avg_hrs': ('평균시간', 80),
                 'max_hrs': ('최대시간', 80), 'total_amt': ('수당합계', 120)}
        for c, (t, w) in dhdrs.items():
            self.dept_tree.heading(c, text=t)
            self.dept_tree.column(c, width=w, anchor='center' if c != 'total_amt' else 'e')
        self.dept_tree.pack(fill='x')

    def load_stats(self):
        """통계 데이터 로드 - 시간외근무 순위"""
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        payrolls = db.get_monthly_payrolls(year=year, month=month)
        workers = db.get_all_workers()
        w_map = {w.id: w for w in workers}

        # 시간외근무 시간 합계로 정렬
        payrolls_with_ot = []
        for p in payrolls:
            ot_total = p.weekday_overtime_hours + p.holiday_work_hours + p.holiday_overtime_hours + p.night_work_hours
            payrolls_with_ot.append((p, ot_total))
        payrolls_with_ot.sort(key=lambda x: x[1], reverse=True)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for rank, (p, ot_hrs) in enumerate(payrolls_with_ot, 1):
            w = w_map.get(p.worker_id)
            tag = 'over208' if p.total_hours > 208 else ('high_ot' if ot_hrs > 20 else 'normal')
            self.tree.insert('', 'end', values=(
                rank, p.worker_name,
                w.department if w else '', w.job_type if w else '',
                w.dispatch_company if w else '',
                f"{p.total_hours:.1f}", f"{p.weekday_overtime_hours:.1f}",
                f"{p.holiday_work_hours:.1f}", f"{p.holiday_overtime_hours:.1f}",
                f"{p.night_work_hours:.1f}", f"{p.overtime_subtotal:,}"
            ), tags=(tag,))

        self.tree.tag_configure('over208', foreground=COLORS['accent_red'])
        self.tree.tag_configure('high_ot', foreground=COLORS['accent_orange'])
        self.tree.tag_configure('normal', foreground=COLORS['text_primary'])

        # 부서별 요약
        dept_stats = {}
        for p, ot in payrolls_with_ot:
            w = w_map.get(p.worker_id)
            dept = w.department if w else '미분류'
            if dept not in dept_stats:
                dept_stats[dept] = {'count': 0, 'hours': [], 'total_amt': 0}
            dept_stats[dept]['count'] += 1
            dept_stats[dept]['hours'].append(p.total_hours)
            dept_stats[dept]['total_amt'] += p.overtime_subtotal

        for item in self.dept_tree.get_children():
            self.dept_tree.delete(item)

        for dept, s in dept_stats.items():
            avg = sum(s['hours']) / len(s['hours']) if s['hours'] else 0
            mx = max(s['hours']) if s['hours'] else 0
            self.dept_tree.insert('', 'end', values=(
                dept, s['count'], f"{avg:.1f}", f"{mx:.1f}", f"{s['total_amt']:,}"))

        total_workers = len(payrolls_with_ot)
        over208 = len([p for p, _ in payrolls_with_ot if p.total_hours > 208])
        self.summary_label.config(
            text=f"총 {total_workers}명 | 208h 초과: {over208}명",
            fg=COLORS['accent_red'] if over208 > 0 else COLORS['accent_green'])
