"""
파견현황 시트 UI
이름검색, 부서/직군/등급/상태 필터, 개인별 상세정보 표시
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from app.ui.styles import COLORS, FONTS, create_rounded_button, create_status_badge
from app import database as db
from app.models import Worker


class DispatchTab(tk.Frame):
    """파견현황 탭"""

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # ===== 상단 필터 영역 =====
        filter_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=12)
        filter_frame.pack(fill='x', padx=10, pady=(10, 5))

        # 타이틀 행
        title_row = tk.Frame(filter_frame, bg=COLORS['bg_card'])
        title_row.pack(fill='x', pady=(0, 10))

        tk.Label(title_row, text="📋 파견현황", font=FONTS['subtitle'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(side='left')

        # 반올림 규칙 표시 (잠금 상태)
        rule_frame = tk.Frame(title_row, bg=COLORS['accent_orange'], padx=8, pady=3)
        rule_frame.pack(side='right')
        tk.Label(rule_frame, text="🔒 반올림 규칙: 원 단위 내림 (고정)",
                 font=FONTS['small_bold'], bg=COLORS['accent_orange'],
                 fg=COLORS['text_white']).pack()

        # 인원 통계
        self.stats_label = tk.Label(title_row, text="", font=FONTS['small'],
                                     bg=COLORS['bg_card'], fg=COLORS['text_secondary'])
        self.stats_label.pack(side='right', padx=15)

        # 필터 행
        filter_row = tk.Frame(filter_frame, bg=COLORS['bg_card'])
        filter_row.pack(fill='x')

        # 검색
        tk.Label(filter_row, text="🔍", font=FONTS['body'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *_: self.filter_data())
        search_entry = tk.Entry(filter_row, textvariable=self.search_var,
                                bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                                insertbackground=COLORS['text_primary'],
                                font=FONTS['body'], relief='flat', width=15)
        search_entry.pack(side='left', padx=(5, 15), ipady=4)
        search_entry.insert(0, '')

        # 부서 필터
        tk.Label(filter_row, text="부서", font=FONTS['small_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, 5))
        self.dept_var = tk.StringVar(value="전체")
        dept_combo = ttk.Combobox(filter_row, textvariable=self.dept_var,
                                   values=["전체", "취재1부", "취재2부특집", "취재2부스포츠", "편집부"],
                                   width=12, state='readonly', style="Custom.TCombobox")
        dept_combo.pack(side='left', padx=(0, 15))
        dept_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_data())

        # 직군 필터
        tk.Label(filter_row, text="직군", font=FONTS['small_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, 5))
        self.job_var = tk.StringVar(value="전체")
        job_combo = ttk.Combobox(filter_row, textvariable=self.job_var,
                                  values=["전체", "촬영보조", "인제스트"],
                                  width=10, state='readonly', style="Custom.TCombobox")
        job_combo.pack(side='left', padx=(0, 15))
        job_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_data())

        # 등급 필터
        tk.Label(filter_row, text="등급", font=FONTS['small_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, 5))
        self.grade_var = tk.StringVar(value="전체")
        grade_combo = ttk.Combobox(filter_row, textvariable=self.grade_var,
                                    values=["전체", "가급", "나급", ""],
                                    width=8, state='readonly', style="Custom.TCombobox")
        grade_combo.pack(side='left', padx=(0, 15))
        grade_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_data())

        # 상태 필터
        tk.Label(filter_row, text="상태", font=FONTS['small_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, 5))
        self.status_var = tk.StringVar(value="전체")
        status_combo = ttk.Combobox(filter_row, textvariable=self.status_var,
                                     values=["전체", "재직", "신규", "퇴사", "입사포기"],
                                     width=8, state='readonly', style="Custom.TCombobox")
        status_combo.pack(side='left', padx=(0, 15))
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_data())

        # 버튼 그룹
        btn_frame = tk.Frame(filter_row, bg=COLORS['bg_card'])
        btn_frame.pack(side='right')

        create_rounded_button(btn_frame, "➕ 신규등록", self.add_worker,
                              color=COLORS['accent_green']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "✏️ 수정", self.edit_worker,
                              color=COLORS['accent_blue']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "🔄 교체", self.replace_worker,
                              color=COLORS['accent_orange']).pack(side='left', padx=3)
        create_rounded_button(btn_frame, "🗑️ 삭제", self.delete_worker,
                              color=COLORS['accent_red']).pack(side='left', padx=3)

        # ===== 메인 컨텐츠 영역 =====
        content_frame = tk.Frame(self, bg=COLORS['bg_main'])
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # 좌측: 목록 Treeview
        left_frame = tk.Frame(content_frame, bg=COLORS['bg_card'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        columns = ('no', 'name', 'department', 'job_type', 'grade', 'company',
                    'start_date', 'end_date', 'remaining', 'status', 'fee')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings',
                                  style="Custom.Treeview", height=25)

        headings = {
            'no': ('No', 40), 'name': ('성명', 70), 'department': ('부서', 90),
            'job_type': ('직군', 70), 'grade': ('등급', 50), 'company': ('파견업체', 90),
            'start_date': ('계약시작일', 90), 'end_date': ('계약종료일', 90),
            'remaining': ('잔여일', 55), 'status': ('상태', 60), 'fee': ('파견료', 90),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            anchor = 'center' if col in ('no', 'grade', 'status', 'remaining') else 'w'
            self.tree.column(col, width=width, anchor=anchor)

        tree_scroll = ttk.Scrollbar(left_frame, orient='vertical', command=self.tree.yview,
                                     style="Custom.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', lambda e: self.edit_worker())

        # 우측: 개인별 상세 정보 패널
        right_frame = tk.Frame(content_frame, bg=COLORS['bg_card'], width=320)
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        right_frame.pack_propagate(False)

        self._build_detail_panel(right_frame)

    def _build_detail_panel(self, parent):
        """개인별 상세정보 패널 구성"""
        # 타이틀
        header = tk.Frame(parent, bg=COLORS['bg_header'], padx=15, pady=10)
        header.pack(fill='x')
        tk.Label(header, text="👤 인력 상세정보", font=FONTS['heading'],
                 bg=COLORS['bg_header'], fg=COLORS['text_primary']).pack(anchor='w')

        # 스크롤 가능한 상세 영역
        canvas = tk.Canvas(parent, bg=COLORS['bg_card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        self.detail_frame = tk.Frame(canvas, bg=COLORS['bg_card'])

        self.detail_frame.bind('<Configure>',
                               lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.detail_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 상세 필드 라벨
        self.detail_labels = {}
        fields = [
            ('name', '성명'), ('management_no', '관리번호'), ('access_card_no', '출입증번호'),
            ('department', '부서'), ('job_type', '직군'), ('grade', '등급'),
            ('dispatch_company', '파견업체'), ('phone', '연락처'),
            ('dispatch_start', '계약시작일'), ('dispatch_end', '계약종료일'),
            ('status', '상태'), ('monthly_fee', '파견료'),
            ('replaced_by', '교체자'), ('birth_date', '생년월일'),
            ('address', '주소'), ('education', '최종학력'),
            ('note', '비고'),
        ]

        for field_key, field_name in fields:
            row = tk.Frame(self.detail_frame, bg=COLORS['bg_card'], padx=15, pady=4)
            row.pack(fill='x')
            tk.Label(row, text=field_name, font=FONTS['small_bold'], width=10, anchor='w',
                     bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
            value_label = tk.Label(row, text="-", font=FONTS['body'], anchor='w',
                                   bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                                   wraplength=180)
            value_label.pack(side='left', fill='x', expand=True)
            self.detail_labels[field_key] = value_label

    def load_data(self):
        """데이터 로드 및 표시"""
        self.workers = db.get_all_workers()
        self.filter_data()

    def filter_data(self, *args):
        """필터 적용하여 데이터 표시"""
        search = self.search_var.get().strip()
        dept = self.dept_var.get()
        job = self.job_var.get()
        grade = self.grade_var.get()
        status = self.status_var.get()

        filtered = self.workers
        if search:
            filtered = [w for w in filtered if search.lower() in w.name.lower()]
        if dept != "전체":
            filtered = [w for w in filtered if w.department == dept]
        if job != "전체":
            filtered = [w for w in filtered if w.job_type == job]
        if grade != "전체":
            filtered = [w for w in filtered if w.grade == grade]
        if status != "전체":
            filtered = [w for w in filtered if w.status == status]

        # 트리뷰 갱신
        for item in self.tree.get_children():
            self.tree.delete(item)

        from datetime import date, datetime
        today = date.today()

        for idx, w in enumerate(filtered, 1):
            # 잔여일 계산
            remaining = "-"
            try:
                end = w.dispatch_end.replace('.', '-')
                if end and end != "입사포기":
                    end_date = datetime.strptime(end, "%Y-%m-%d").date()
                    diff = (end_date - today).days
                    remaining = str(diff)
            except (ValueError, AttributeError):
                pass

            # 파견료 포맷
            fee = w.monthly_fee
            try:
                fee_num = int(fee.replace(',', ''))
                fee = f"{fee_num:,}"
            except (ValueError, AttributeError):
                pass

            values = (idx, w.name, w.department, w.job_type, w.grade,
                      w.dispatch_company, w.dispatch_start, w.dispatch_end,
                      remaining, w.status, fee)
            tag = f'status_{w.status}'
            self.tree.insert('', 'end', iid=str(w.id), values=values, tags=(tag,))

        # 상태별 색상
        self.tree.tag_configure('status_재직', foreground=COLORS['status_active'])
        self.tree.tag_configure('status_신규', foreground=COLORS['status_new'])
        self.tree.tag_configure('status_퇴사', foreground=COLORS['status_left'])
        self.tree.tag_configure('status_입사포기', foreground=COLORS['status_cancel'])

        # 통계 업데이트
        total = len(self.workers)
        active = len([w for w in self.workers if w.status == '재직'])
        new = len([w for w in self.workers if w.status == '신규'])
        showing = len(filtered)
        self.stats_label.config(text=f"전체 {total}명 | 재직 {active}명 | 신규 {new}명 | 표시 {showing}명")

    def on_select(self, event):
        """트리뷰 항목 선택 시 상세정보 표시"""
        selection = self.tree.selection()
        if not selection:
            return

        worker_id = int(selection[0])
        worker = db.get_worker_by_id(worker_id)
        if not worker:
            return

        # 상세 패널 업데이트
        field_map = {
            'name': worker.name,
            'management_no': worker.management_no,
            'access_card_no': worker.access_card_no,
            'department': worker.department,
            'job_type': worker.job_type,
            'grade': worker.grade or '-',
            'dispatch_company': worker.dispatch_company,
            'phone': worker.phone,
            'dispatch_start': worker.dispatch_start,
            'dispatch_end': worker.dispatch_end,
            'status': worker.status,
            'monthly_fee': worker.monthly_fee,
            'replaced_by': worker.replaced_by or '-',
            'birth_date': worker.birth_date,
            'address': worker.address,
            'education': worker.education,
            'note': worker.note or '-',
        }

        for key, value in field_map.items():
            if key in self.detail_labels:
                self.detail_labels[key].config(text=str(value) if value else "-")
                # 상태 색상
                if key == 'status':
                    color_map = {
                        '재직': COLORS['status_active'],
                        '신규': COLORS['status_new'],
                        '퇴사': COLORS['status_left'],
                        '입사포기': COLORS['status_cancel'],
                    }
                    self.detail_labels[key].config(fg=color_map.get(value, COLORS['text_primary']))

    def add_worker(self):
        """신규 인력 등록"""
        self._open_worker_dialog(None)

    def edit_worker(self):
        """인력 정보 수정"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "수정할 인력을 선택해주세요.")
            return
        worker_id = int(selection[0])
        worker = db.get_worker_by_id(worker_id)
        if worker:
            self._open_worker_dialog(worker)

    def replace_worker(self):
        """인력 교체"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "교체할 인력을 선택해주세요.")
            return
        worker_id = int(selection[0])
        worker = db.get_worker_by_id(worker_id)
        if not worker:
            return

        # 교체자 이름 입력
        new_name = simpledialog.askstring("인력 교체",
                                           f"'{worker.name}' 의 교체자 이름을 입력하세요:")
        if new_name:
            # 기존 인력 퇴사 처리
            worker.status = "퇴사"
            worker.replaced_by = new_name
            db.save_worker(worker)

            # 신규 인력 등록 다이얼로그
            new_worker = Worker(
                name=new_name,
                department=worker.department,
                job_type=worker.job_type,
                grade=worker.grade,
                dispatch_company=worker.dispatch_company,
                job_description=worker.job_description,
                status="신규",
            )
            self._open_worker_dialog(new_worker, is_replacement=True)

    def delete_worker(self):
        """인력 삭제"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("선택 필요", "삭제할 인력을 선택해주세요.")
            return
        worker_id = int(selection[0])
        worker = db.get_worker_by_id(worker_id)
        if worker and messagebox.askyesno("삭제 확인",
                                           f"'{worker.name}' 를 삭제하시겠습니까?"):
            db.delete_worker(worker_id)
            self.load_data()

    def _open_worker_dialog(self, worker, is_replacement=False):
        """인력 등록/수정 다이얼로그"""
        is_new = worker is None or worker.id == 0
        dialog = tk.Toplevel(self)
        dialog.title("신규 인력 등록" if is_new else "인력 정보 수정")
        dialog.geometry("550x700")
        dialog.configure(bg=COLORS['bg_main'])
        dialog.transient(self)
        dialog.grab_set()

        # 다이얼로그 가운데 정렬
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f'+{x}+{y}')

        # 스크롤 영역
        canvas = tk.Canvas(dialog, bg=COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient='vertical', command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=COLORS['bg_card'], padx=20, pady=15)
        form_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=form_frame, anchor='nw', width=530)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        if worker is None:
            worker = Worker()

        entries = {}
        fields = [
            ('name', '성명', worker.name),
            ('management_no', '관리번호', worker.management_no),
            ('access_card_no', '출입증번호', worker.access_card_no),
            ('department', '부서', worker.department),
            ('job_type', '직군', worker.job_type),
            ('grade', '등급', worker.grade),
            ('dispatch_company', '파견업체', worker.dispatch_company),
            ('phone', '연락처', worker.phone),
            ('dispatch_start', '계약시작일', worker.dispatch_start),
            ('dispatch_end', '계약종료일', worker.dispatch_end),
            ('birth_date', '생년월일', worker.birth_date),
            ('address', '주소', worker.address),
            ('education', '최종학력', worker.education),
            ('monthly_fee', '월간파견료', worker.monthly_fee),
            ('status', '상태', worker.status),
            ('note', '비고', worker.note),
        ]

        for field_key, field_name, default_val in fields:
            row = tk.Frame(form_frame, bg=COLORS['bg_card'], pady=3)
            row.pack(fill='x')
            tk.Label(row, text=field_name, font=FONTS['body_bold'], width=10, anchor='w',
                     bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')

            if field_key == 'department':
                var = tk.StringVar(value=default_val)
                combo = ttk.Combobox(row, textvariable=var,
                                     values=["취재1부", "취재2부특집", "취재2부스포츠", "편집부"],
                                     state='readonly', style="Custom.TCombobox")
                combo.pack(side='left', fill='x', expand=True, ipady=3)
                entries[field_key] = var
            elif field_key == 'job_type':
                var = tk.StringVar(value=default_val)
                combo = ttk.Combobox(row, textvariable=var,
                                     values=["촬영보조", "인제스트"],
                                     state='readonly', style="Custom.TCombobox")
                combo.pack(side='left', fill='x', expand=True, ipady=3)
                entries[field_key] = var
            elif field_key == 'grade':
                var = tk.StringVar(value=default_val)
                combo = ttk.Combobox(row, textvariable=var,
                                     values=["가급", "나급", ""],
                                     state='readonly', style="Custom.TCombobox")
                combo.pack(side='left', fill='x', expand=True, ipady=3)
                entries[field_key] = var
            elif field_key == 'status':
                var = tk.StringVar(value=default_val)
                combo = ttk.Combobox(row, textvariable=var,
                                     values=["재직", "신규", "퇴사", "입사포기"],
                                     state='readonly', style="Custom.TCombobox")
                combo.pack(side='left', fill='x', expand=True, ipady=3)
                entries[field_key] = var
            elif field_key == 'dispatch_company':
                var = tk.StringVar(value=default_val)
                companies = db.get_all_companies()
                company_names = [c.name for c in companies]
                combo = ttk.Combobox(row, textvariable=var,
                                     values=company_names,
                                     style="Custom.TCombobox")
                combo.pack(side='left', fill='x', expand=True, ipady=3)
                entries[field_key] = var
            else:
                entry = tk.Entry(row, bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                                 insertbackground=COLORS['text_primary'],
                                 font=FONTS['body'], relief='flat')
                entry.insert(0, default_val or '')
                entry.pack(side='left', fill='x', expand=True, ipady=4)
                entries[field_key] = entry

        # 저장 버튼
        btn_frame = tk.Frame(form_frame, bg=COLORS['bg_card'], pady=15)
        btn_frame.pack(fill='x')

        def save():
            for field_key, _, _ in fields:
                val = entries[field_key]
                if isinstance(val, tk.StringVar):
                    setattr(worker, field_key, val.get())
                else:
                    setattr(worker, field_key, val.get())
            db.save_worker(worker)
            dialog.destroy()
            self.load_data()
            messagebox.showinfo("저장 완료", f"'{worker.name}' 정보가 저장되었습니다.")

        create_rounded_button(btn_frame, "💾 저장", save,
                              color=COLORS['accent_green']).pack(side='right', padx=5)
        create_rounded_button(btn_frame, "취소", dialog.destroy,
                              color=COLORS['bg_input']).pack(side='right', padx=5)
