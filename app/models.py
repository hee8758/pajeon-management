"""
데이터 모델 정의
파견인력, 파견업체, 임금설정, 근태기록 등의 데이터 구조
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import date
import json


@dataclass
class Worker:
    """파견인력 데이터 모델"""
    id: int = 0
    name: str = ""
    management_no: str = ""          # 관리번호
    access_card_no: str = ""         # 출입증번호
    department: str = ""             # 부서 (취재1부, 취재2부특집, 취재2부스포츠, 편집부)
    job_type: str = ""               # 직군 (촬영보조, 인제스트)
    grade: str = ""                  # 등급 (가급, 나급)
    dispatch_company: str = ""       # 파견사
    dispatch_start: str = ""         # 파견일(계약시작일)
    dispatch_end: str = ""           # 퇴사일(계약종료일)
    replaced_by: str = ""            # 교체자
    birth_date: str = ""             # 생년월일/주민번호앞자리
    phone: str = ""                  # 연락처
    address: str = ""                # 주소
    education: str = ""              # 최종학력
    job_description: str = ""        # 직무내용
    monthly_fee: str = ""            # 월간파견료
    status: str = "재직"             # 상태 (재직, 퇴사, 신규, 입사포기)
    note: str = ""                   # 비고

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Company:
    """파견업체 데이터 모델"""
    id: int = 0
    name: str = ""                   # 업체명
    manager_name: str = ""           # 담당자
    phone: str = ""                  # 연락처
    email: str = ""                  # 이메일
    note: str = ""                   # 비고

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WageConfig:
    """임금설정 데이터 모델"""
    id: int = 0
    job_type: str = ""               # 직군
    grade: str = ""                  # 등급
    base_salary: int = 0             # 기본급
    hourly_wage: int = 0             # 시급
    indirect_ratio: float = 0.0      # 간접비율
    retirement_ratio: float = 0.0    # 퇴직충당금율

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AttendanceRecord:
    """근태기록 데이터 모델"""
    id: int = 0                      # 고유 ID (0이면 신규)
    worker_id: int = 0
    worker_name: str = ""
    year: int = 2026
    month: int = 1
    day: int = 1
    start_time: str = ""             # 출근시간 (HH:MM)
    end_time: str = ""               # 퇴근시간 (HH:MM)
    work_hours: float = 0.0          # 총 근무시간
    overtime_weekday: float = 0.0    # 평일연장근로시간
    overtime_holiday: float = 0.0    # 휴일근로시간
    overtime_holiday_ext: float = 0.0  # 휴일연장근로시간
    overtime_night: float = 0.0      # 야간근로시간
    is_holiday: bool = False         # 휴일여부

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class MonthlyPayroll:
    """월별 정산 데이터 모델"""
    worker_id: int = 0
    worker_name: str = ""
    year: int = 2026
    month: int = 1
    work_days: int = 0               # 근무일수
    absent_days: int = 0             # 결근일수
    base_fee: int = 0                # 용역비
    absent_deduction: int = 0        # 결근공제
    leave_deduction_days: int = 0    # 대휴공제일수
    leave_deduction_amount: int = 0  # 대휴공제금액
    fee_subtotal: int = 0            # 용역비 소계

    # 시간외수당
    weekday_overtime_hours: float = 0.0    # 평일연장 시간
    weekday_overtime_amount: int = 0       # 평일연장 금액
    holiday_work_hours: float = 0.0        # 휴일근로 시간
    holiday_work_amount: int = 0           # 휴일근로 금액
    holiday_overtime_hours: float = 0.0    # 휴일연장 시간
    holiday_overtime_amount: int = 0       # 휴일연장 금액
    night_work_hours: float = 0.0          # 야간근로 시간
    night_work_amount: int = 0             # 야간근로 금액
    overtime_subtotal: int = 0             # 시간외수당 소계
    overtime_criteria: int = 0             # 시간외수당 지급기준
    overtime_actual: int = 0               # 시간외수당 실지급액
    overtime_indirect: int = 0             # 시간외수당 간접비
    retirement_reserve: int = 0            # 퇴직급여충당금
    total: int = 0                         # 합계
    total_hours: float = 0.0               # 총 근무시간

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
