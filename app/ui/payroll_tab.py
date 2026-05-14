"""
파견료 시트 UI
월별 정산, 근태기록 업로드, 시간외수당 자동계산, 청구내역서 출력
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from app.ui.styles import COLORS, FONTS, create_rounded_button
from app.ui.wage_settings import WageSettingsDialog
from app import database as db
from app.models import MonthlyPayroll, AttendanceRecord
from app import calculator as calc


class PayrollTab(tk.Frame):
    """파견료 탭"""

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['bg_main'])
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # ===== 상단 설정 =====
        top = tk.Frame(self, bg=COLORS['bg_card'], padx=15, pady=10)
        top.pack(fill='x', padx=10, pady=(10, 3))

        row1 = tk.Frame(top, bg=COLORS['bg_card'])
        row1.pack(fill='x', pady=(0, 8))
        tk.Label(row1, text="💰 파견료 정산", font=FONTS['subtitle'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(side='left')
        tk.Label(row1, text="🔒 원 단위 내림 (고정)", font=FONTS['small_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['accent_orange']).pack(side='right')

        # ── 조회 옵션 + 기능 버튼 ──
        row2 = tk.Frame(top, bg=COLORS['bg_card'])
        row2.pack(fill='x', pady=(0, 6))

        tk.Label(row2, text="연도", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.year_var = tk.StringVar(value="2026")
        ttk.Combobox(row2, textvariable=self.year_var,
                     values=[str(y) for y in range(2024, 2031)],
                     width=6, state='readonly', style="Custom.TCombobox").pack(side='left', padx=(5, 12))

        tk.Label(row2, text="월", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.month_var = tk.StringVar(value="3")
        ttk.Combobox(row2, textvariable=self.month_var,
                     values=[str(m) for m in range(1, 13)],
                     width=4, state='readonly', style="Custom.TCombobox").pack(side='left', padx=(5, 12))

        tk.Label(row2, text="직군", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.filter_job_var = tk.StringVar(value="전체")
        ttk.Combobox(row2, textvariable=self.filter_job_var,
                     values=["전체", "촬영보조", "인제스트"], width=8,
                     state='readonly', style="Custom.TCombobox").pack(side='left', padx=(5, 12))

        tk.Label(row2, text="부서", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
        self.filter_dept_var = tk.StringVar(value="전체")
        ttk.Combobox(row2, textvariable=self.filter_dept_var,
                     values=["전체", "취재1부", "취재2부특집", "취재2부스포츠", "편집부"],
                     width=10, state='readonly', style="Custom.TCombobox").pack(side='left', padx=(5, 12))

        btns = tk.Frame(row2, bg=COLORS['bg_card'])
        btns.pack(side='right')
        create_rounded_button(btns, "⚙️ 임금설정", self.open_wage_settings,
                              color=COLORS['accent_purple']).pack(side='left', padx=3)
        create_rounded_button(btns, "📂 근태업로드", self.upload_attendance,
                              color=COLORS['accent_blue']).pack(side='left', padx=3)
        create_rounded_button(btns, "🔄 자동계산", self.auto_calculate,
                              color=COLORS['accent_green']).pack(side='left', padx=3)
        create_rounded_button(btns, "📊 조회", self.load_payroll_data,
                              color=COLORS['accent_cyan']).pack(side='left', padx=3)

        # ── 청구내역서 출력 (상단으로 이동) ──
        tk.Frame(top, bg=COLORS['border'], height=1).pack(fill='x', pady=(4, 6))

        row3 = tk.Frame(top, bg=COLORS['bg_card'])
        row3.pack(fill='x')
        tk.Label(row3, text="📄 청구내역서 출력", font=FONTS['heading'],
                 bg=COLORS['bg_card'], fg=COLORS['text_primary']).pack(side='left')

        tk.Label(row3, text="파견업체", font=FONTS['body_bold'],
                 bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left', padx=(20, 5))
        self.export_company_var = tk.StringVar(value="전체")
        companies = db.get_all_companies()
        names = ["전체"] + [c.name for c in companies]
        ttk.Combobox(row3, textvariable=self.export_company_var,
                     values=names, width=12, state='readonly',
                     style="Custom.TCombobox").pack(side='left', padx=(0, 15))

        create_rounded_button(row3, "📥 엑셀 출력", self.export_excel,
                              color=COLORS['accent_green']).pack(side='right', padx=3)

        # ===== 정산 목록 =====
        list_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=5, pady=5)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(3, 10))

        cols = ('no', 'name', 'dept', 'job', 'days', 'fee', 'absent', 'abs_ded',
                'wk_ot_h', 'wk_ot_a', 'hol_h', 'hol_a', 'hol_ot_h', 'hol_ot_a',
                'night_h', 'night_a', 'ot_total', 'total', 'total_hrs')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='headings',
                                  style="Custom.Treeview", height=20)
        hdrs = {
            'no': ('No', 35), 'name': ('성명', 65), 'dept': ('부서', 75),
            'job': ('직군', 60), 'days': ('근무일', 45), 'fee': ('용역비', 80),
            'absent': ('결근', 35), 'abs_ded': ('결근공제', 70),
            'wk_ot_h': ('평일연장(h)', 65), 'wk_ot_a': ('평일연장(원)', 80),
            'hol_h': ('휴일(h)', 55), 'hol_a': ('휴일(원)', 75),
            'hol_ot_h': ('휴일연장(h)', 65), 'hol_ot_a': ('휴일연장(원)', 80),
            'night_h': ('야간(h)', 50), 'night_a': ('야간(원)', 70),
            'ot_total': ('수당소계', 80), 'total': ('합계', 85),
            'total_hrs': ('총시간', 50)
        }
        for c, (t, w) in hdrs.items():
            self.tree.heading(c, text=t)
            anchor = 'e' if c.endswith(('_a', '_ded', 'fee', 'total')) else 'center'
            self.tree.column(c, width=w, anchor=anchor)

        xscroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        yscroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        yscroll.grid(row=0, column=1, sticky='ns')
        xscroll.grid(row=1, column=0, sticky='ew')
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind('<Double-1>', self.show_worker_detail)


    def open_wage_settings(self):
        WageSettingsDialog(self)

    def upload_attendance(self):
        """근태기록 다중 업로드 (엑셀/CSV/PDF)"""
        filetypes = [
            ("지원 형식", "*.xlsx *.xls *.csv *.pdf"),
            ("Excel", "*.xlsx *.xls"),
            ("CSV", "*.csv"),
            ("PDF", "*.pdf"),
            ("All", "*.*")
        ]
        filepaths = filedialog.askopenfilenames(
            title="근태기록부 파일 선택 (여러 파일 동시 선택 가능)",
            filetypes=filetypes
        )
        if not filepaths:
            return

        total_records = 0
        success_files = []
        fail_files = []

        for filepath in filepaths:
            self._pdf_hint_path = filepath  # 파일명 힌트 저장
            try:
                records = self._parse_attendance_file(filepath)
                if records:
                    db.save_attendance_records(records)
                    total_records += len(records)
                    success_files.append(f"✅ {os.path.basename(filepath)} ({len(records)}건)")
                else:
                    # 사용자가 다이얼로그를 취소한 경우 등
                    fail_files.append(f"⏭️ {os.path.basename(filepath)} (건너뜀)")
            except Exception as e:
                fail_files.append(f"❌ {os.path.basename(filepath)} ({str(e)})")

        # 결과 요약
        result_lines = []
        if success_files:
            result_lines.append(f"총 {total_records}건 업로드 완료\n")
            result_lines.extend(success_files)
        if fail_files:
            if result_lines:
                result_lines.append("")
            result_lines.extend(fail_files)

        if total_records > 0:
            messagebox.showinfo("업로드 결과", "\n".join(result_lines))
            self.load_payroll_data()
        elif fail_files:
            messagebox.showwarning("업로드 결과", "\n".join(result_lines))


    def _parse_attendance_file(self, filepath):
        """근태기록 파일 파싱"""
        records = []
        ext = os.path.splitext(filepath)[1].lower()
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        workers = db.get_all_workers()
        name_to_id = {w.name.strip(): w.id for w in workers}

        if ext == '.csv':
            import csv
            encodings = ['utf-8-sig', 'cp949', 'euc-kr']
            for enc in encodings:
                try:
                    with open(filepath, 'r', encoding=enc) as f:
                        reader = csv.reader(f)
                        header = next(reader, None)
                        for row in reader:
                            if len(row) < 4:
                                continue
                            name = row[0].strip()
                            if name not in name_to_id:
                                continue
                            try:
                                day = int(row[1])
                                start = row[2].strip()
                                end = row[3].strip()
                                is_hol = row[4].strip().upper() in ('Y', '1', 'O', '예') if len(row) > 4 else False
                                wh, wo_wd, wo_hol, wo_hol_ext, wo_night = calc.calc_work_hours(start, end, is_hol)
                                rec = AttendanceRecord(
                                    worker_id=name_to_id[name], worker_name=name,
                                    year=year, month=month, day=day,
                                    start_time=start, end_time=end,
                                    work_hours=wh, overtime_weekday=wo_wd,
                                    overtime_holiday=wo_hol, overtime_holiday_ext=wo_hol_ext,
                                    overtime_night=wo_night, is_holiday=is_hol)
                                records.append(rec)
                            except (ValueError, IndexError):
                                continue
                    break
                except UnicodeDecodeError:
                    continue

        elif ext in ('.xlsx', '.xls'):
            records = self._parse_excel_attendance(filepath, year, month, name_to_id, workers)

        elif ext == '.pdf':
            records = self._parse_pdf_attendance(filepath, year, month, name_to_id, workers)

        return records

    def _parse_excel_attendance(self, filepath, year, month, name_to_id, workers):
        """
        인제스트 근태표 xlsx 파싱
        구조: B열=날짜(YYYY-MM-DD), D열=출근시간(HHMM 숫자), E열=퇴근시간(HHMM 숫자), O열=평/휴일
        openpyxl 스타일 오류 우회를 위해 zipfile+XML 직접 파싱 사용
        """
        import zipfile
        import xml.etree.ElementTree as ET
        from datetime import datetime, timedelta
        import re

        raw_rows = []  # (day, start_str, end_str, is_hol)

        def hhmm_to_str(val):
            """숫자 900 → '09:00', 1800 → '18:00'"""
            try:
                n = int(float(val))
                h, m = divmod(n, 100)
                return f'{h:02d}:{m:02d}'
            except Exception:
                return None

        def xl_serial_to_day(val):
            """Excel 날짜 시리얼 → day(일)"""
            try:
                n = float(val)
                if 40000 < n < 60000:
                    base = datetime(1899, 12, 30)
                    dt = base + timedelta(days=n)
                    return dt.day
            except Exception:
                pass
            # "2026-03-23" 문자열 형식
            m = re.search(r'\d{4}-\d{2}-(\d{2})', str(val))
            if m:
                return int(m.group(1))
            return None

        try:
            with zipfile.ZipFile(filepath) as z:
                # sharedStrings 읽기
                shared = []
                if 'xl/sharedStrings.xml' in z.namelist():
                    with z.open('xl/sharedStrings.xml') as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        ns_uri = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
                        for si in root:
                            text = ''.join(t.text or '' for t in si.iter() if t.text)
                            shared.append(text)

                # sheet1 읽기
                sheet_path = 'xl/worksheets/sheet1.xml'
                if sheet_path not in z.namelist():
                    messagebox.showerror("오류", "xlsx 파일에서 시트를 찾을 수 없습니다.")
                    return []

                with z.open(sheet_path) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns_uri = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''

                    for row_el in root.iter(f'{{{ns_uri}}}row' if ns_uri else 'row'):
                        r_num = int(row_el.get('r', 0))
                        if r_num < 9:  # 헤더 이전 행 스킵
                            continue

                        cells = {}
                        for c in row_el:
                            ref = c.get('r', '')
                            col = ''.join(filter(str.isalpha, ref))
                            t = c.get('t', '')
                            v_el = c.find(f'{{{ns_uri}}}v' if ns_uri else 'v')
                            val = v_el.text if v_el is not None else None
                            if t == 's' and val is not None:
                                idx = int(val)
                                val = shared[idx] if idx < len(shared) else val
                            cells[col] = val

                        # B열=날짜, D열=출근, E열=퇴근, O열=평/휴일
                        b_val = cells.get('B')
                        d_val = cells.get('D')
                        e_val = cells.get('E')
                        o_val = cells.get('O', '')

                        if not b_val or d_val is None or e_val is None:
                            continue

                        # "합 계" 행 등 종료 감지
                        if isinstance(b_val, str) and '합' in b_val:
                            break

                        day = xl_serial_to_day(b_val)
                        if not day:
                            continue

                        start_str = hhmm_to_str(d_val)
                        end_str = hhmm_to_str(e_val)
                        if not start_str or not end_str:
                            continue

                        is_hol = '휴' in str(o_val)
                        raw_rows.append((day, start_str, end_str, is_hol))

        except zipfile.BadZipFile:
            messagebox.showerror("오류", "유효하지 않은 xlsx 파일입니다.")
            return []
        except Exception as e:
            messagebox.showerror("xlsx 오류", f"엑셀 파싱 중 오류:\n{str(e)}")
            return []

        if not raw_rows:
            messagebox.showwarning("파싱 결과 없음",
                "엑셀에서 근태 데이터(날짜+출퇴근시간)를 찾지 못했습니다.\n"
                "파일 형식을 확인해주세요.")
            return []

        # 인력 선택 다이얼로그 (PDF와 동일)
        worker_id, worker_name = self._select_worker_dialog(raw_rows, workers, year, month)
        if not worker_id:
            return []

        records = []
        for (day, start, end, is_hol) in raw_rows:
            try:
                wh, wo_wd, wo_hol, wo_hol_ext, wo_night = calc.calc_work_hours(start, end, is_hol)
                rec = AttendanceRecord(
                    worker_id=worker_id, worker_name=worker_name,
                    year=year, month=month, day=day,
                    start_time=start, end_time=end,
                    work_hours=wh, overtime_weekday=wo_wd,
                    overtime_holiday=wo_hol, overtime_holiday_ext=wo_hol_ext,
                    overtime_night=wo_night, is_holiday=is_hol)
                records.append(rec)
            except Exception:
                continue

        return records

    def _parse_pdf_attendance(self, filepath, year, month, name_to_id, workers):
        """PDF 근태기록 파싱 - 날짜/시간 컬럼 자동 인식"""
        import re
        records = []
        raw_rows = []  # (day, start, end, is_hol) 형태로 수집

        try:
            import pdfplumber
        except ImportError:
            messagebox.showerror("오류", "pdfplumber 패키지가 필요합니다.\npip install pdfplumber")
            return records

        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table:
                                if not row:
                                    continue
                                # 날짜 패턴 탐지: "2026. 3. 23" 또는 "3/23" 또는 숫자
                                date_col = None
                                date_val = None
                                start_col = None
                                end_col = None

                                for ci, cell in enumerate(row):
                                    if cell is None:
                                        continue
                                    cell_s = str(cell).strip()
                                    # 날짜 패턴: "YYYY. M. D" 또는 "M/D"
                                    m = re.search(r'\d{4}\.\s*\d{1,2}\.\s*(\d{1,2})', cell_s)
                                    if m and date_val is None:
                                        date_col = ci
                                        date_val = int(m.group(1))
                                    # 시간 패턴: HH:MM
                                    if re.match(r'^\d{1,2}:\d{2}$', cell_s):
                                        if start_col is None:
                                            start_col = ci
                                        elif end_col is None:
                                            end_col = ci

                                if date_val and start_col is not None and end_col is not None:
                                    start_t = str(row[start_col]).strip()
                                    end_t = str(row[end_col]).strip()
                                    raw_rows.append((date_val, start_t, end_t, False))

        except Exception as e:
            messagebox.showerror("PDF 오류", f"PDF 파싱 중 오류: {str(e)}")
            return records

        if not raw_rows:
            messagebox.showwarning("파싱 결과 없음",
                "PDF에서 근태 데이터(날짜+출퇴근시간)를 찾지 못했습니다.\n"
                "PDF 형식이 지원되지 않거나 데이터가 없습니다.")
            return records

        # 인력 선택 다이얼로그
        worker_id, worker_name = self._select_worker_dialog(raw_rows, workers, year, month)
        if not worker_id:
            return records

        for (day, start, end, is_hol) in raw_rows:
            try:
                wh, wo_wd, wo_hol, wo_hol_ext, wo_night = calc.calc_work_hours(start, end, is_hol)
                rec = AttendanceRecord(
                    worker_id=worker_id, worker_name=worker_name,
                    year=year, month=month, day=day,
                    start_time=start, end_time=end,
                    work_hours=wh, overtime_weekday=wo_wd,
                    overtime_holiday=wo_hol, overtime_holiday_ext=wo_hol_ext,
                    overtime_night=wo_night, is_holiday=is_hol)
                records.append(rec)
            except Exception:
                continue

        return records

    def _select_worker_dialog(self, raw_rows, workers, year, month):
        """파일명 자동 매칭 → 못 찾으면 간단 선택창만 표시 (미리보기 없음)"""
        active = [w for w in workers if w.status in ('재직', '신규')]
        hint_path = getattr(self, '_pdf_hint_path', '')
        fname = os.path.basename(hint_path)

        # 파일명에서 이름 자동 매칭
        matched = next((w for w in active if w.name in fname), None)
        if matched:
            return matched.id, matched.name

        # 자동 매칭 실패 → 간단 선택창
        result = {'worker_id': None, 'worker_name': None}
        dlg = tk.Toplevel(self)
        dlg.title("인력 선택")
        dlg.geometry("420x180")
        dlg.configure(bg=COLORS['bg_main'])
        dlg.grab_set()
        dlg.resizable(False, False)

        tk.Label(dlg, text=f"파일: {fname}",
                 font=FONTS['small'], bg=COLORS['bg_main'],
                 fg=COLORS['text_secondary']).pack(padx=20, pady=(14, 2), anchor='w')
        tk.Label(dlg, text="적용할 인력을 선택하세요.",
                 font=FONTS['body_bold'], bg=COLORS['bg_main'],
                 fg=COLORS['text_primary']).pack(padx=20, anchor='w')

        sel_var = tk.StringVar()
        names = [w.name for w in active]
        cb = ttk.Combobox(dlg, textvariable=sel_var, values=names,
                          font=FONTS['body'], width=22,
                          state='readonly', style="Custom.TCombobox")
        cb.pack(padx=20, pady=10, anchor='w')

        bf = tk.Frame(dlg, bg=COLORS['bg_main'])
        bf.pack(pady=4)

        def on_ok():
            name = sel_var.get().strip()
            if not name:
                messagebox.showwarning("선택 필요", "인력을 선택하세요.", parent=dlg)
                return
            w = next((x for x in active if x.name == name), None)
            if w:
                result['worker_id'] = w.id
                result['worker_name'] = w.name
            dlg.destroy()

        create_rounded_button(bf, "✅ 확인", on_ok,
                              color=COLORS['accent_green']).pack(side='left', padx=6)
        create_rounded_button(bf, "취소", dlg.destroy,
                              color=COLORS['accent_red']).pack(side='left', padx=6)
        dlg.wait_window()
        return result['worker_id'], result['worker_name']


    def auto_calculate(self):
        """시간외수당 자동 계산"""
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        workers = db.get_all_workers()
        active_workers = [w for w in workers if w.status in ('재직', '신규')]
        wage_configs = db.get_all_wage_configs()

        if not wage_configs:
            messagebox.showwarning("임금설정 필요", "먼저 임금설정을 등록해주세요.")
            return

        payrolls = []
        for w in active_workers:
            # 해당 근로자의 임금설정 찾기
            cfg = None
            for wc in wage_configs:
                if wc.job_type == w.job_type and (not wc.grade or wc.grade == w.grade):
                    cfg = wc
                    break
            if not cfg:
                for wc in wage_configs:
                    if wc.job_type == w.job_type:
                        cfg = wc
                        break
            if not cfg:
                continue

            # 근태기록 조회
            records = db.get_attendance_records(worker_id=w.id, year=year, month=month)

            total_hours = sum(r.work_hours for r in records)
            wd_ot = sum(r.overtime_weekday for r in records)
            hol = sum(r.overtime_holiday for r in records)
            hol_ot = sum(r.overtime_holiday_ext for r in records)
            night = sum(r.overtime_night for r in records)

            wd_ot_amt = calc.calc_weekday_overtime(cfg.hourly_wage, wd_ot)
            hol_amt = calc.calc_holiday_work(cfg.hourly_wage, hol)
            hol_ot_amt = calc.calc_holiday_overtime(cfg.hourly_wage, hol_ot)
            night_amt = calc.calc_night_work(cfg.hourly_wage, night)
            ot_subtotal = wd_ot_amt + hol_amt + hol_ot_amt + night_amt

            ot_indirect = calc.calc_overtime_indirect(ot_subtotal, cfg.indirect_ratio)
            retire = calc.calc_retirement_reserve(ot_subtotal, cfg.retirement_ratio)

            try:
                fee = int(w.monthly_fee.replace(',', ''))
            except (ValueError, AttributeError):
                fee = 0

            work_days = len(set(r.day for r in records)) if records else 0

            payroll = MonthlyPayroll(
                worker_id=w.id, worker_name=w.name, year=year, month=month,
                work_days=work_days, base_fee=fee,
                weekday_overtime_hours=round(wd_ot, 2), weekday_overtime_amount=wd_ot_amt,
                holiday_work_hours=round(hol, 2), holiday_work_amount=hol_amt,
                holiday_overtime_hours=round(hol_ot, 2), holiday_overtime_amount=hol_ot_amt,
                night_work_hours=round(night, 2), night_work_amount=night_amt,
                overtime_subtotal=ot_subtotal, overtime_actual=ot_subtotal,
                overtime_indirect=ot_indirect, retirement_reserve=retire,
                fee_subtotal=fee,
                total=fee + ot_subtotal + ot_indirect + retire,
                total_hours=round(total_hours, 2))
            payrolls.append(payroll)

        if payrolls:
            db.save_monthly_payrolls_bulk(payrolls)
            messagebox.showinfo("계산 완료", f"{len(payrolls)}명의 파견료가 계산되었습니다.")
            self.load_payroll_data()
        else:
            messagebox.showinfo("결과 없음", "계산 대상이 없습니다.")

    def load_payroll_data(self):
        """정산 데이터 조회"""
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        payrolls = db.get_monthly_payrolls(year=year, month=month)
        workers = db.get_all_workers()
        w_map = {w.id: w for w in workers}

        job_filter = self.filter_job_var.get()
        dept_filter = self.filter_dept_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, p in enumerate(payrolls, 1):
            w = w_map.get(p.worker_id)
            if not w:
                continue
            if job_filter != "전체" and w.job_type != job_filter:
                continue
            if dept_filter != "전체" and w.department != dept_filter:
                continue

            tag = 'over208' if p.total_hours > 208 else 'normal'
            self.tree.insert('', 'end', iid=str(p.worker_id), values=(
                i, p.worker_name, w.department if w else '', w.job_type if w else '',
                p.work_days, f"{p.base_fee:,}", p.absent_days, f"{p.absent_deduction:,}",
                p.weekday_overtime_hours, f"{p.weekday_overtime_amount:,}",
                p.holiday_work_hours, f"{p.holiday_work_amount:,}",
                p.holiday_overtime_hours, f"{p.holiday_overtime_amount:,}",
                p.night_work_hours, f"{p.night_work_amount:,}",
                f"{p.overtime_subtotal:,}", f"{p.total:,}", p.total_hours
            ), tags=(tag,))

        self.tree.tag_configure('over208', foreground=COLORS['accent_red'])
        self.tree.tag_configure('normal', foreground=COLORS['text_primary'])

    def show_worker_detail(self, event=None, worker_id=None):
        """개인별 상세 정산 화면 (근태 수정/삭제 가능)"""
        if worker_id is None:
            sel = self.tree.selection()
            if not sel:
                return
            worker_id = int(sel[0])

        year  = int(self.year_var.get())
        month = int(self.month_var.get())
        worker = db.get_worker_by_id(worker_id)
        if not worker:
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"📋 {worker.name} — {year}년 {month}월 근태 상세")
        dlg.geometry("980x640")
        dlg.configure(bg=COLORS['bg_main'])
        try:
            dlg.state('zoomed')
        except Exception:
            pass

        # ── 헤더 ──
        hdr = tk.Frame(dlg, bg=COLORS['bg_card'], padx=18, pady=12)
        hdr.pack(fill='x', padx=10, pady=(10, 4))
        tk.Label(hdr, text=f"👤 {worker.name}  ({worker.department} / {worker.job_type})",
                 font=FONTS['subtitle'], bg=COLORS['bg_card'],
                 fg=COLORS['text_primary']).pack(side='left')

        def refresh_header():
            recs = db.get_attendance_records(worker_id=worker_id, year=year, month=month)
            hrs = sum(r.work_hours for r in recs)
            clr = COLORS['accent_red'] if hrs > 208 else COLORS['accent_green']
            total_lbl.config(text=f"총 근무시간: {hrs:.1f}h", fg=clr)
            return recs

        total_lbl = tk.Label(hdr, text="", font=FONTS['heading'],
                             bg=COLORS['bg_card'], fg=COLORS['accent_green'])
        total_lbl.pack(side='right')

        # ── 툴바 (수정/삭제/추가) ──
        toolbar = tk.Frame(dlg, bg=COLORS['bg_card'], padx=12, pady=8)
        toolbar.pack(fill='x', padx=10, pady=2)

        # ── 트리뷰 ──
        rcols = ('rec_id', 'day', 'start', 'end', 'holiday',
                 'hours', 'wd_ot', 'hol', 'hol_ot', 'night')
        rtree = ttk.Treeview(dlg, columns=rcols, show='headings',
                             style="Custom.Treeview")
        rhdrs = [('rec_id','ID',0), ('day','일',55), ('start','출근',80),
                 ('end','퇴근',80), ('holiday','휴일',55), ('hours','근무(h)',80),
                 ('wd_ot','평일연장(h)',100), ('hol','휴일(h)',80),
                 ('hol_ot','휴일연장(h)',100), ('night','야간(h)',80)]
        for c, t, w in rhdrs:
            rtree.heading(c, text=t)
            rtree.column(c, width=w, anchor='center',
                         minwidth=0 if c == 'rec_id' else 40)
        # rec_id 열 숨김
        rtree.column('rec_id', width=0, stretch=False)

        ysb = ttk.Scrollbar(dlg, orient='vertical', command=rtree.yview,
                            style='Custom.Vertical.TScrollbar')
        rtree.configure(yscrollcommand=ysb.set)

        rtree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=4)
        ysb.pack(side='left', fill='y', pady=4)

        def load_tree():
            recs = refresh_header()
            for item in rtree.get_children():
                rtree.delete(item)
            for r in sorted(recs, key=lambda x: x.day):
                rtree.insert('', 'end', iid=str(r.id), values=(
                    r.id, r.day, r.start_time, r.end_time,
                    '●' if r.is_holiday else '',
                    f'{r.work_hours:.2f}', f'{r.overtime_weekday:.2f}',
                    f'{r.overtime_holiday:.2f}', f'{r.overtime_holiday_ext:.2f}',
                    f'{r.overtime_night:.2f}'
                ))

        def open_edit(rec=None):
            """행 추가 또는 수정 다이얼로그"""
            ed = tk.Toplevel(dlg)
            ed.title("근태 수정" if rec else "근태 추가")
            ed.geometry("360x260")
            ed.configure(bg=COLORS['bg_main'])
            ed.grab_set()
            ed.resizable(False, False)

            form = tk.Frame(ed, bg=COLORS['bg_card'], padx=20, pady=16)
            form.pack(fill='both', expand=True, padx=10, pady=10)

            fields = [
                ('일 (1~31)',   'day',     str(rec.day)        if rec else ''),
                ('출근 (HH:MM)', 'start',  rec.start_time      if rec else ''),
                ('퇴근 (HH:MM)', 'end',    rec.end_time        if rec else ''),
            ]
            entries = {}
            for label, key, val in fields:
                row = tk.Frame(form, bg=COLORS['bg_card'], pady=5)
                row.pack(fill='x')
                tk.Label(row, text=label, font=FONTS['body_bold'], width=14, anchor='w',
                         bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
                e = tk.Entry(row, font=FONTS['body'],
                             bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                             relief='flat', insertbackground=COLORS['text_primary'])
                e.insert(0, val)
                e.pack(side='left', fill='x', expand=True, ipady=5)
                entries[key] = e

            # 휴일 체크박스
            hol_var = tk.BooleanVar(value=rec.is_holiday if rec else False)
            hol_row = tk.Frame(form, bg=COLORS['bg_card'], pady=5)
            hol_row.pack(fill='x')
            tk.Label(hol_row, text='휴일 여부', font=FONTS['body_bold'], width=14, anchor='w',
                     bg=COLORS['bg_card'], fg=COLORS['text_secondary']).pack(side='left')
            tk.Checkbutton(hol_row, variable=hol_var,
                           bg=COLORS['bg_card'], activebackground=COLORS['bg_card']).pack(side='left')

            def do_save():
                try:
                    day   = int(entries['day'].get())
                    start = entries['start'].get().strip()
                    end   = entries['end'].get().strip()
                    is_hol = hol_var.get()
                    wh, wo_wd, wo_hol, wo_hol_ext, wo_night = calc.calc_work_hours(start, end, is_hol)
                    if rec:
                        rec.day = day; rec.start_time = start; rec.end_time = end
                        rec.is_holiday = is_hol; rec.work_hours = wh
                        rec.overtime_weekday = wo_wd; rec.overtime_holiday = wo_hol
                        rec.overtime_holiday_ext = wo_hol_ext; rec.overtime_night = wo_night
                        db.save_attendance_records([rec])
                    else:
                        new_rec = AttendanceRecord(
                            worker_id=worker_id, worker_name=worker.name,
                            year=year, month=month, day=day,
                            start_time=start, end_time=end,
                            work_hours=wh, overtime_weekday=wo_wd,
                            overtime_holiday=wo_hol, overtime_holiday_ext=wo_hol_ext,
                            overtime_night=wo_night, is_holiday=is_hol)
                        db.save_attendance_records([new_rec])
                    ed.destroy()
                    load_tree()
                except Exception as ex:
                    messagebox.showerror("오류", f"입력 오류:\n{ex}", parent=ed)

            bf = tk.Frame(ed, bg=COLORS['bg_main'])
            bf.pack(pady=6)
            create_rounded_button(bf, "💾 저장", do_save,
                                  color=COLORS['accent_green']).pack(side='left', padx=6)
            create_rounded_button(bf, "취소", ed.destroy,
                                  color=COLORS['accent_red']).pack(side='left', padx=6)

        def on_edit():
            sel = rtree.selection()
            if not sel:
                messagebox.showwarning("선택", "수정할 행을 선택하세요.", parent=dlg)
                return
            rec_id = int(rtree.item(sel[0])['values'][0])
            recs = db.get_attendance_records(worker_id=worker_id, year=year, month=month)
            rec = next((r for r in recs if r.id == rec_id), None)
            if rec:
                open_edit(rec)

        def on_delete():
            sel = rtree.selection()
            if not sel:
                messagebox.showwarning("선택", "삭제할 행을 선택하세요.", parent=dlg)
                return
            if not messagebox.askyesno("삭제 확인", "선택한 근태 기록을 삭제하시겠습니까?", parent=dlg):
                return
            rec_id = int(rtree.item(sel[0])['values'][0])
            db.delete_attendance_record(rec_id)
            load_tree()

        # 툴바 버튼
        create_rounded_button(toolbar, "➕ 추가", lambda: open_edit(None),
                              color=COLORS['accent_green']).pack(side='left', padx=4)
        create_rounded_button(toolbar, "✏️ 수정", on_edit,
                              color=COLORS['accent_blue']).pack(side='left', padx=4)
        create_rounded_button(toolbar, "🗑️ 삭제", on_delete,
                              color=COLORS['accent_red']).pack(side='left', padx=4)

        # 수당 합계 바
        sm = tk.Frame(dlg, bg=COLORS['bg_card'], padx=15, pady=8)
        sm.pack(fill='x', padx=10, pady=(4, 10), side='bottom')
        sm_lbl = tk.Label(sm, text="", font=FONTS['body_bold'],
                          bg=COLORS['bg_card'], fg=COLORS['accent_cyan'])
        sm_lbl.pack(side='left')

        # 원래 refresh_header가 summary도 업데이트하도록 덮어쓰기
        _orig_refresh = refresh_header
        def refresh_header():
            recs = _orig_refresh()
            wd_ot  = sum(r.overtime_weekday      for r in recs)
            hol_w  = sum(r.overtime_holiday       for r in recs)
            hol_ot = sum(r.overtime_holiday_ext   for r in recs)
            night  = sum(r.overtime_night         for r in recs)
            sm_lbl.config(text=f"평일연장: {wd_ot:.1f}h  |  휴일: {hol_w:.1f}h  |  "
                               f"휴일연장: {hol_ot:.1f}h  |  야간: {night:.1f}h")
            return recs

        load_tree()


    def export_excel(self):
        """청구내역서 엑셀 출력"""
        from app.excel_exporter import export_billing_statement, export_all_companies
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        company = self.export_company_var.get()

        output_dir = filedialog.askdirectory(title="저장 폴더 선택")
        if not output_dir:
            return

        if company == "전체":
            msg = export_all_companies(year, month, output_dir)
        else:
            filename = f"파견료내역서_{company}_{year}년{month}월.xlsx"
            output_path = os.path.join(output_dir, filename)
            msg = export_billing_statement(year, month, company, output_path)

        messagebox.showinfo("출력 결과", msg)
