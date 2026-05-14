"""
JSON 기반 데이터 저장/로드 모듈
모든 데이터를 data/app_data.json 파일에 저장하고 로드합니다.
"""
import json
import os
from typing import List, Optional
from app.models import Worker, Company, WageConfig, AttendanceRecord, MonthlyPayroll


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DATA_FILE = os.path.join(DATA_DIR, "app_data.json")


def _ensure_data_dir():
    """데이터 디렉토리가 없으면 생성"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_all_data() -> dict:
    """전체 데이터 로드"""
    _ensure_data_dir()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "workers": [],
        "companies": [],
        "wage_configs": [],
        "attendance_records": [],
        "monthly_payrolls": [],
        "next_worker_id": 1,
        "next_company_id": 1,
        "next_wage_config_id": 1,
    }


def _save_all_data(data: dict):
    """전체 데이터 저장"""
    _ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===== Workers =====
def get_all_workers() -> List[Worker]:
    data = _load_all_data()
    return [Worker.from_dict(w) for w in data.get("workers", [])]


def get_worker_by_id(worker_id: int) -> Optional[Worker]:
    workers = get_all_workers()
    for w in workers:
        if w.id == worker_id:
            return w
    return None


def save_worker(worker: Worker) -> Worker:
    data = _load_all_data()
    if worker.id == 0:
        worker.id = data.get("next_worker_id", 1)
        data["next_worker_id"] = worker.id + 1
        data["workers"].append(worker.to_dict())
    else:
        for i, w in enumerate(data["workers"]):
            if w["id"] == worker.id:
                data["workers"][i] = worker.to_dict()
                break
    _save_all_data(data)
    return worker


def delete_worker(worker_id: int):
    data = _load_all_data()
    data["workers"] = [w for w in data["workers"] if w["id"] != worker_id]
    _save_all_data(data)


def save_workers_bulk(workers: List[Worker]):
    """여러 근로자를 한번에 저장 (CSV 임포트용)"""
    data = _load_all_data()
    next_id = data.get("next_worker_id", 1)
    for worker in workers:
        if worker.id == 0:
            worker.id = next_id
            next_id += 1
        # 중복체크 (관리번호)
        exists = False
        for i, w in enumerate(data["workers"]):
            if w.get("management_no") and w["management_no"] == worker.management_no:
                worker.id = w["id"]
                data["workers"][i] = worker.to_dict()
                exists = True
                break
        if not exists:
            data["workers"].append(worker.to_dict())
    data["next_worker_id"] = next_id
    _save_all_data(data)


# ===== Companies =====
def get_all_companies() -> List[Company]:
    data = _load_all_data()
    return [Company.from_dict(c) for c in data.get("companies", [])]


def save_company(company: Company) -> Company:
    data = _load_all_data()
    if company.id == 0:
        company.id = data.get("next_company_id", 1)
        data["next_company_id"] = company.id + 1
        data["companies"].append(company.to_dict())
    else:
        for i, c in enumerate(data["companies"]):
            if c["id"] == company.id:
                data["companies"][i] = company.to_dict()
                break
    _save_all_data(data)
    return company


def delete_company(company_id: int):
    data = _load_all_data()
    data["companies"] = [c for c in data["companies"] if c["id"] != company_id]
    _save_all_data(data)


def save_companies_bulk(companies: List[Company]):
    """여러 업체를 한번에 저장"""
    data = _load_all_data()
    next_id = data.get("next_company_id", 1)
    for company in companies:
        if company.id == 0:
            company.id = next_id
            next_id += 1
        exists = False
        for i, c in enumerate(data["companies"]):
            if c["name"] == company.name:
                company.id = c["id"]
                data["companies"][i] = company.to_dict()
                exists = True
                break
        if not exists:
            data["companies"].append(company.to_dict())
    data["next_company_id"] = next_id
    _save_all_data(data)


# ===== Wage Configs =====
def get_all_wage_configs() -> List[WageConfig]:
    data = _load_all_data()
    return [WageConfig.from_dict(w) for w in data.get("wage_configs", [])]


def save_wage_config(config: WageConfig) -> WageConfig:
    data = _load_all_data()
    if config.id == 0:
        config.id = data.get("next_wage_config_id", 1)
        data["next_wage_config_id"] = config.id + 1
        data["wage_configs"].append(config.to_dict())
    else:
        for i, c in enumerate(data["wage_configs"]):
            if c["id"] == config.id:
                data["wage_configs"][i] = config.to_dict()
                break
    _save_all_data(data)
    return config


def delete_wage_config(config_id: int):
    data = _load_all_data()
    data["wage_configs"] = [c for c in data["wage_configs"] if c["id"] != config_id]
    _save_all_data(data)


# ===== Attendance Records =====
def get_attendance_records(worker_id: int = None, year: int = None, month: int = None) -> List[AttendanceRecord]:
    data = _load_all_data()
    records = [AttendanceRecord.from_dict(r) for r in data.get("attendance_records", [])]
    if worker_id is not None:
        records = [r for r in records if r.worker_id == worker_id]
    if year is not None:
        records = [r for r in records if r.year == year]
    if month is not None:
        records = [r for r in records if r.month == month]
    return records


def save_attendance_records(records: List[AttendanceRecord]):
    """근태기록 저장 (id가 있으면 id로, 없으면 연/월/일로 덮어쓰기)"""
    data = _load_all_data()
    existing = data.get("attendance_records", [])

    # 현재 최대 id 계산
    max_id = max((e.get("id", 0) for e in existing), default=0)

    for record in records:
        rd = record.to_dict()
        found = False

        if rd.get("id", 0) > 0:
            # id가 있으면 id로 식별해 업데이트
            for i, e in enumerate(existing):
                if e.get("id") == rd["id"]:
                    existing[i] = rd
                    found = True
                    break
        else:
            # id 없으면 worker_id+year+month+day 로 덮어쓰기
            for i, e in enumerate(existing):
                if (e["worker_id"] == rd["worker_id"] and
                    e["year"] == rd["year"] and
                    e["month"] == rd["month"] and
                    e["day"] == rd["day"]):
                    rd["id"] = e.get("id", 0)  # 기존 id 유지
                    existing[i] = rd
                    found = True
                    break

        if not found:
            max_id += 1
            rd["id"] = max_id
            existing.append(rd)

    data["attendance_records"] = existing
    _save_all_data(data)


def delete_attendance_record(record_id: int):
    """근태기록 단건 삭제 (id 기준)"""
    data = _load_all_data()
    existing = data.get("attendance_records", [])
    data["attendance_records"] = [e for e in existing if e.get("id") != record_id]
    _save_all_data(data)

# ===== Monthly Payrolls =====
def get_monthly_payrolls(year: int = None, month: int = None, company: str = None) -> List[MonthlyPayroll]:
    data = _load_all_data()
    payrolls = [MonthlyPayroll.from_dict(p) for p in data.get("monthly_payrolls", [])]
    if year is not None:
        payrolls = [p for p in payrolls if p.year == year]
    if month is not None:
        payrolls = [p for p in payrolls if p.month == month]
    return payrolls


def save_monthly_payroll(payroll: MonthlyPayroll):
    data = _load_all_data()
    existing = data.get("monthly_payrolls", [])
    pd = payroll.to_dict()
    found = False
    for i, e in enumerate(existing):
        if (e["worker_id"] == pd["worker_id"] and
            e["year"] == pd["year"] and
            e["month"] == pd["month"]):
            existing[i] = pd
            found = True
            break
    if not found:
        existing.append(pd)
    data["monthly_payrolls"] = existing
    _save_all_data(data)


def save_monthly_payrolls_bulk(payrolls: List[MonthlyPayroll]):
    data = _load_all_data()
    existing = data.get("monthly_payrolls", [])
    for payroll in payrolls:
        pd = payroll.to_dict()
        found = False
        for i, e in enumerate(existing):
            if (e["worker_id"] == pd["worker_id"] and
                e["year"] == pd["year"] and
                e["month"] == pd["month"]):
                existing[i] = pd
                found = True
                break
        if not found:
            existing.append(pd)
    data["monthly_payrolls"] = existing
    _save_all_data(data)
