"""
CSV 데이터 임포트 모듈
촬영보조.csv, 인제스트.csv, 파견업체.csv 파일을 읽어 데이터를 로드합니다.
"""
import csv
import os
import re
from typing import List, Tuple
from app.models import Worker, Company


def _detect_encoding(filepath: str) -> str:
    """파일 인코딩 자동 감지"""
    encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                f.read(1000)
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return 'cp949'


def _clean_text(text: str) -> str:
    """텍스트 정리"""
    if text is None:
        return ""
    return text.strip()


def _parse_fee(fee_str: str) -> str:
    """파견료 문자열 정리 (콤마 포함 숫자)"""
    cleaned = _clean_text(fee_str)
    if not cleaned:
        return "0"
    return cleaned


def import_shooting_assistant_csv(filepath: str) -> Tuple[List[Worker], str]:
    """
    촬영보조.csv 임포트
    구조: 순번, 성명, 관리번호, 출입증번호, 파견사, 파견일, 퇴사일, 교체자/상태,
          주민번호, 연락처, 주소, 최종학력, 직무내용, 월간파견료, 비고
    부서 구분: 취재1부, 취재2부특집, 취재2부스포츠
    """
    encoding = _detect_encoding(filepath)
    workers = []
    current_department = ""
    errors = []

    try:
        with open(filepath, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                if not row or all(not cell.strip() for cell in row):
                    continue

                # 부서 헤더 감지
                first_col = _clean_text(row[0]) if row else ""

                if '취재1부' in first_col or (len(row) > 2 and '취재1부' in _clean_text(row[2])):
                    current_department = "취재1부"
                    continue
                elif '특집' in first_col:
                    current_department = "취재2부특집"
                    continue
                elif '스포츠' in first_col:
                    current_department = "취재2부스포츠"
                    continue

                # 헤더행 또는 총계행 건너뛰기
                if first_col in ('순번', '') or '총' in first_col:
                    continue

                # 숫자로 시작하는 행 = 데이터행
                try:
                    int(first_col)
                except ValueError:
                    continue

                if len(row) < 14:
                    continue

                # 상태 판단
                replaced_or_status = _clean_text(row[7]) if len(row) > 7 else ""
                status = "재직"
                replaced_by = ""
                if replaced_or_status in ('신규',):
                    status = "신규"
                elif replaced_or_status in ('입사포기',):
                    status = "입사포기"
                elif replaced_or_status:
                    replaced_by = replaced_or_status
                    status = "재직"

                worker = Worker(
                    name=_clean_text(row[1]),
                    management_no=_clean_text(row[2]),
                    access_card_no=_clean_text(row[3]),
                    dispatch_company=_clean_text(row[4]),
                    dispatch_start=_clean_text(row[5]),
                    dispatch_end=_clean_text(row[6]),
                    replaced_by=replaced_by,
                    birth_date=_clean_text(row[8]) if len(row) > 8 else "",
                    phone=_clean_text(row[9]) if len(row) > 9 else "",
                    address=_clean_text(row[10]) if len(row) > 10 else "",
                    education=_clean_text(row[11]) if len(row) > 11 else "",
                    job_description=_clean_text(row[12]) if len(row) > 12 else "촬영보조",
                    monthly_fee=_parse_fee(row[13]) if len(row) > 13 else "0",
                    department=current_department if current_department else "취재1부",
                    job_type="촬영보조",
                    grade="",
                    status=status,
                    note=_clean_text(row[14]) if len(row) > 14 else "",
                )
                if worker.name:
                    workers.append(worker)

    except Exception as e:
        errors.append(f"촬영보조 CSV 읽기 오류: {str(e)}")

    msg = f"촬영보조 {len(workers)}명 임포트 완료"
    if errors:
        msg += f" (오류: {'; '.join(errors)})"
    return workers, msg


def import_ingest_csv(filepath: str) -> Tuple[List[Worker], str]:
    """
    인제스트.csv 임포트
    구조: 순번, 성명, 등급, 출입증번호, 관리번호, 파견사, 입사일, 퇴사일,
          파견료, 직무내용, 교체자, 연락처, 생년월일, 주소, 최종학력
    """
    encoding = _detect_encoding(filepath)
    workers = []
    errors = []

    try:
        with open(filepath, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                if not row or all(not cell.strip() for cell in row):
                    continue

                first_col = _clean_text(row[0]) if row else ""

                # 헤더행 건너뛰기
                if first_col in ('순번', '편집부', '') or '총' in first_col:
                    continue

                # 숫자로 시작하는 행 = 데이터행
                try:
                    int(first_col)
                except ValueError:
                    continue

                if len(row) < 10:
                    continue

                # 퇴사여부로 상태 판단
                end_date = _clean_text(row[7])
                status = "재직"
                if end_date == "입사포기":
                    status = "입사포기"

                worker = Worker(
                    name=_clean_text(row[1]),
                    grade=_clean_text(row[2]),
                    access_card_no=_clean_text(row[3]),
                    management_no=_clean_text(row[4]),
                    dispatch_company=_clean_text(row[5]),
                    dispatch_start=_clean_text(row[6]),
                    dispatch_end=end_date,
                    monthly_fee=_parse_fee(row[8]) if len(row) > 8 else "0",
                    job_description=_clean_text(row[9]) if len(row) > 9 else "인제스트",
                    replaced_by=_clean_text(row[10]) if len(row) > 10 else "",
                    phone=_clean_text(row[11]) if len(row) > 11 else "",
                    birth_date=_clean_text(row[12]) if len(row) > 12 else "",
                    address=_clean_text(row[13]) if len(row) > 13 else "",
                    education=_clean_text(row[14]) if len(row) > 14 else "",
                    department="편집부",
                    job_type="인제스트",
                    status=status,
                )
                if worker.name:
                    workers.append(worker)

    except Exception as e:
        errors.append(f"인제스트 CSV 읽기 오류: {str(e)}")

    msg = f"인제스트 {len(workers)}명 임포트 완료"
    if errors:
        msg += f" (오류: {'; '.join(errors)})"
    return workers, msg


def import_company_csv(filepath: str) -> Tuple[List[Company], str]:
    """
    파견업체.csv 임포트
    구조: 구분, 업체, 담당자, 연락처, 메일주소, 비고
    """
    encoding = _detect_encoding(filepath)
    companies = []
    errors = []

    try:
        with open(filepath, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                if not row or all(not cell.strip() for cell in row):
                    continue

                first_col = _clean_text(row[0]) if row else ""

                # 헤더/메모행 건너뛰기
                if first_col in ('구분', '', '현재 없음') or '파견업체' in first_col or '*' in first_col:
                    continue

                try:
                    int(first_col)
                except ValueError:
                    continue

                if len(row) < 5:
                    continue

                company = Company(
                    name=_clean_text(row[1]),
                    manager_name=_clean_text(row[2]),
                    phone=_clean_text(row[3]),
                    email=_clean_text(row[4]).replace('\t', ''),
                    note=_clean_text(row[5]) if len(row) > 5 else "",
                )
                if company.name:
                    companies.append(company)

    except Exception as e:
        errors.append(f"파견업체 CSV 읽기 오류: {str(e)}")

    msg = f"파견업체 {len(companies)}개 임포트 완료"
    if errors:
        msg += f" (오류: {'; '.join(errors)})"
    return companies, msg


def auto_import_all(base_dir: str) -> str:
    """프로젝트 디렉토리에서 모든 CSV 자동 임포트"""
    from app import database as db

    messages = []

    # 촬영보조
    shooting_csv = os.path.join(base_dir, "촬영보조.csv")
    if os.path.exists(shooting_csv):
        workers, msg = import_shooting_assistant_csv(shooting_csv)
        if workers:
            db.save_workers_bulk(workers)
        messages.append(msg)

    # 인제스트
    ingest_csv = os.path.join(base_dir, "인제스트.csv")
    if os.path.exists(ingest_csv):
        workers, msg = import_ingest_csv(ingest_csv)
        if workers:
            db.save_workers_bulk(workers)
        messages.append(msg)

    # 파견업체
    company_csv = os.path.join(base_dir, "파견업체.csv")
    if os.path.exists(company_csv):
        companies, msg = import_company_csv(company_csv)
        if companies:
            db.save_companies_bulk(companies)
        messages.append(msg)

    return "\n".join(messages)
