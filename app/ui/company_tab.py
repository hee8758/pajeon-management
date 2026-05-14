"""
파견업체 시트 UI
업체 등록/수정/삭제, 업체별 담당자 관리
"""
import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.styles import COLORS, FONTS, create_rounded_button
from app import database as db
from app.models import Company


class CompanyTab(tk.Frame):
    """파견업체 탭"""

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # ===== 상단 헤더 =====
        header_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=12)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))

        title_row = tk.Frame(header_frame, bg=COLORS['bg_card'])
        title_row.pack(fill='x')

        tk.Label(title_row, text="🏢 파견업체 관리", font=FONTS['subtitle'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(side='left')

        self.company_count_label = tk.Label(title_row, text="", font=FONTS['small'],
                                             bg=COLORS['bg_card'], fg=COLORS['text_secondary'])
        self.company_count_label.pack(side='left', padx=15)

        tk.Label(title_row, text="⚠️ 담당자의 교체가 빈번하니 업데이트 필수",
                 font=FONTS['small'], bg=COLORS['bg_card'],
                 fg=COLORS['accent_orange']).pack(side='right', padx=10)

        btn_frame = tk.Frame(header_frame, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', pady=(10, 0))

        create_rounded_button(btn_frame, "➕ 업체 등록", self.add_company,
                              color=COLORS['accent_green']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "✏️ 수정", self.edit_company,
                              color=COLORS['accent_blue']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "🗑️ 삭제", self.delete_company,
                              color=COLORS['accent_red']).pack(side='left', padx=3)

        # ===== 업체 목록 =====
        list_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=10, pady=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('no', 'name', 'manager', 'phone', 'email', 'note')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                  style="Custom.Treeview", height=15)

        headings = {
            'no': ('No', 50), 'name': ('업체명', 120), 'manager': ('담당자', 100),
            'phone': ('연락처', 130), 'email': ('이메일', 220), 'note': ('비고', 200),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor='center' if col == 'no' else 'w')

        scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        self.tree.bind('<Double-1>', lambda e: self.edit_company())

        # ===== 하단: 업체별 파견인력 =====
        detail_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=10, pady=10)
        detail_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        tk.Label(detail_frame, text="📋 소속 파견인력", font=FONTS['heading'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(anchor='w', pady=(0, 5))

        worker_columns = ('no', 'name', 'department', 'job_type', 'status', 'fee')
        self.worker_tree = ttk.Treeview(detail_frame, columns=worker_columns,
                                         show='headings', style="Custom.Treeview", height=8)

        worker_headings = {
            'no': ('No', 50), 'name': ('성명', 100), 'department': ('부서', 100),
            'job_type': ('직군', 80), 'status': ('상태', 70), 'fee': ('파견료', 100),
        }
        for col, (text, width) in worker_headings.items():
            self.worker_tree.heading(col, text=text)
            self.worker_tree.column(col, width=width, anchor='center' if col in ('no', 'status') else 'w')

        self.worker_tree.pack(fill='both', expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_company_select)

    def load_data(self):
        """데이터 로드"""
        self.companies = db.get_all_companies()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, c in enumerate(self.companies, 1):
            self.tree.insert('', 'end', iid=str(c.id),
                             values=(idx, c.name, c.manager_name, c.phone, c.email, c.note))

        self.company_count_label.config(text=f"총 {len(self.companies)}개 업체")

    def on_company_select(self, event):
        """업체 선택 시 소속 인력 표시"""
        selection = self.tree.selection()
        if not selection:
            return

        company_id = int(selection[0])
        company = None
        for c in self.companies:
            if c.id == company_id:
                company = c
                break

        if not company:
            return

        # 해당 업체 소속 인력
        all_workers = db.get_all_workers()
        company_workers = [w for w in all_workers if w.dispatch_company == company.name]

        for item in self.worker_tree.get_children():
            self.worker_tree.delete(item)

        for idx, w in enumerate(company_workers, 1):
            self.worker_tree.insert('', 'end',
                                     values=(idx, w.name, w.department, w.job_type, w.status, w.monthly_fee))

    def add_company(self):
        """업체 등록"""
        self._open_company_dialog(None)

    def edit_company(self):
        """업체 수정"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "수정할 업체를 선택해주세요.")
            return
        company_id = int(selection[0])
        company = None
        for c in self.companies:
            if c.id == company_id:
                company = c
                break
        if company:
            self._open_company_dialog(company)

    def delete_company(self):
        """업체 삭제"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "삭제할 업체를 선택해주세요.")
            return
        company_id = int(selection[0])
        company = None
        for c in self.companies:
            if c.id == company_id:
                company = c
                break
        if company and messagebox.askyesno("삭제 확인",
                                            f"'{company.name}' 업체를 삭제하시겠습니까?"):
            db.delete_company(company_id)
            self.load_data()

    def _open_company_dialog(self, company):
        """업체 등록/수정 다이얼로그"""
        is_new = company is None
        dialog = tk.Toplevel(self)
        dialog.title("업체 등록" if is_new else "업체 수정")
        dialog.geometry("450x350")
        dialog.configure(bg=COLORS['bg_main'])
        dialog.transient(self)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 225
        y = (dialog.winfo_screenheight() // 2) - 175
        dialog.geometry(f'+{x}+{y}')

        form = tk.Frame(dialog, bg=COLORS['bg_card'], padx=25, pady=20)
        form.pack(fill='both', expand=True, padx=10, pady=10)

        if company is None:
            company = Company()

        entries = {}
        fields = [
            ('name', '업체명', company.name),
            ('manager_name', '담당자', company.manager_name),
            ('phone', '연락처', company.phone),
            ('email', '이메일', company.email),
            ('note', '비고', company.note),
        ]

        for field_key, field_name, default_val in fields:
            row = tk.Frame(form, bg=COLORS['bg_card'], pady=5)
            row.pack(fill='x')
            tk.Label(row, text=field_name, font=FONTS['body_bold'], width=8, anchor='w',
                     bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
            entry = tk.Entry(row, bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                             insertbackground=COLORS['text_primary'],
                             font=FONTS['body'], relief='flat')
            entry.insert(0, default_val or '')
            entry.pack(side='left', fill='x', expand=True, ipady=4)
            entries[field_key] = entry

        btn_frame = tk.Frame(form, bg=COLORS['bg_card'], pady=15)
        btn_frame.pack(fill='x')

        def save():
            for field_key, _, _ in fields:
                setattr(company, field_key, entries[field_key].get())
            db.save_company(company)
            dialog.destroy()
            self.load_data()
            messagebox.showinfo("저장 완료", f"'{company.name}' 업체 정보가 저장되었습니다.")

        create_rounded_button(btn_frame, "💾 저장", save,
                              color=COLORS['accent_green']).pack(side='right', padx=5)
        create_rounded_button(btn_frame, "취소", dialog.destroy,
                              color=COLORS['bg_input']).pack(side='right', padx=5)
