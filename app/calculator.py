"""
시간외수당 계산 엔진
decimal 모듈을 사용하여 부동소수점 오차 방지
원 단위 내림(고정) 규칙 적용
"""
from decimal import Decimal, ROUND_DOWN, getcontext

# decimal 정밀도 설정
getcontext().prec = 28


def floor_to_won(amount: Decimal) -> int:
    """원 단위 내림 (고정) - AI가 임의 변경 불가"""
    return int(amount.quantize(Decimal('1'), rounding=ROUND_DOWN))


def calc_weekday_overtime(hourly_wage: int, hours: float) -> int:
    """
    평일연장근로수당: 시급 × 1.5 × 1.1
    """
    if hours <= 0:
        return 0
    wage = Decimal(str(hourly_wage))
    h = Decimal(str(hours))
    amount = wage * Decimal('1.5') * Decimal('1.1') * h
    return floor_to_won(amount)


def calc_holiday_work(hourly_wage: int, hours: float) -> int:
    """
    휴일근로수당: 시급 × 1.5 × 1.1
    """
    if hours <= 0:
        return 0
    wage = Decimal(str(hourly_wage))
    h = Decimal(str(hours))
    amount = wage * Decimal('1.5') * Decimal('1.1') * h
    return floor_to_won(amount)


def calc_holiday_overtime(hourly_wage: int, hours: float) -> int:
    """
    휴일연장근로수당: 시급 × 2.0 × 1.1
    """
    if hours <= 0:
        return 0
    wage = Decimal(str(hourly_wage))
    h = Decimal(str(hours))
    amount = wage * Decimal('2.0') * Decimal('1.1') * h
    return floor_to_won(amount)


def calc_night_work(hourly_wage: int, hours: float) -> int:
    """
    야간근로수당: 시급 × 0.5 × 1.1
    22:00~06:00 근무시 무조건 적용
    """
    if hours <= 0:
        return 0
    wage = Decimal(str(hourly_wage))
    h = Decimal(str(hours))
    amount = wage * Decimal('0.5') * Decimal('1.1') * h
    return floor_to_won(amount)


def calc_work_hours(start_time: str, end_time: str, is_holiday: bool = False):
    """
    근무시간 계산
    - 4시간 근무 후 무조건 30분 휴게시간 적용
    - 예: 09:00~18:00 근무 → 9시간 - 1시간(점심+휴게) = 8시간 실근무
    - 기본 근무시간: 8시간 (09:00~18:00 기준, 점심1시간 포함 총9시간)
    
    반환: (총근무시간, 평일연장시간, 휴일근로시간, 휴일연장시간, 야간근로시간)
    """
    if not start_time or not end_time:
        return (0.0, 0.0, 0.0, 0.0, 0.0)

    try:
        sh, sm = map(int, start_time.split(':'))
        eh, em = map(int, end_time.split(':'))
    except (ValueError, AttributeError):
        return (0.0, 0.0, 0.0, 0.0, 0.0)

    start_min = sh * 60 + sm
    end_min = eh * 60 + em

    # 자정 넘어가는 경우
    if end_min <= start_min:
        end_min += 24 * 60

    total_min = end_min - start_min

    # 휴게시간 적용: 4시간 이상 근무시 30분 휴게
    # 일반적으로 8시간 이상 근무시 1시간 휴게 (점심)
    break_min = 0
    if total_min >= 8 * 60:  # 8시간 이상
        break_min = 60  # 1시간 휴게 (점심 포함)
    elif total_min >= 4 * 60:  # 4시간 이상
        break_min = 30  # 30분 휴게

    actual_work_min = total_min - break_min
    actual_work_hours = actual_work_min / 60.0

    # 기본 근무시간 (8시간)
    standard_hours = 8.0

    weekday_overtime = 0.0
    holiday_work = 0.0
    holiday_overtime = 0.0
    night_work = 0.0

    if is_holiday:
        # 휴일: 8시간까지 → 휴일근로, 8시간 초과 → 휴일연장근로
        if actual_work_hours <= standard_hours:
            holiday_work = actual_work_hours
        else:
            holiday_work = standard_hours
            holiday_overtime = actual_work_hours - standard_hours
    else:
        # 평일: 8시간 초과분 → 평일연장근로
        if actual_work_hours > standard_hours:
            weekday_overtime = actual_work_hours - standard_hours

    # 야간근로: 22:00~06:00 근무시간 계산
    night_start = 22 * 60  # 22:00
    night_end = 30 * 60    # 06:00 (다음날)

    # 실제 근무 구간에서 야간 시간 계산
    work_start = start_min
    work_end = end_min  # 이미 자정 넘어가는 경우 처리됨

    # 22:00~30:00 (=06:00) 구간과 겹치는 시간
    night_overlap_start = max(work_start, night_start)
    night_overlap_end = min(work_end, night_end)
    if night_overlap_end > night_overlap_start:
        night_min = night_overlap_end - night_overlap_start
        night_work = night_min / 60.0

    # 00:00~06:00 구간도 체크 (시작시간이 자정 전인 경우)
    if work_start < night_start and work_end > 24 * 60:
        early_night_start = 24 * 60  # 자정
        early_night_end = min(work_end, night_end)
        if early_night_end > early_night_start:
            # 이미 위에서 계산됨 (night_start~night_end가 22:00~30:00이므로)
            pass

    return (
        round(actual_work_hours, 2),
        round(weekday_overtime, 2),
        round(holiday_work, 2),
        round(holiday_overtime, 2),
        round(night_work, 2)
    )


def calc_overtime_indirect(overtime_amount: int, indirect_ratio: float) -> int:
    """시간외수당 간접비 계산"""
    amount = Decimal(str(overtime_amount)) * Decimal(str(indirect_ratio))
    return floor_to_won(amount)


def calc_retirement_reserve(overtime_amount: int, retirement_ratio: float) -> int:
    """퇴직급여 충당금 계산"""
    amount = Decimal(str(overtime_amount)) * Decimal(str(retirement_ratio))
    return floor_to_won(amount)


def calc_absent_deduction(monthly_fee: int, work_days_in_month: int, absent_days: int) -> int:
    """결근공제 계산"""
    if work_days_in_month <= 0 or absent_days <= 0:
        return 0
    daily = Decimal(str(monthly_fee)) / Decimal(str(work_days_in_month))
    amount = daily * Decimal(str(absent_days))
    return floor_to_won(amount)
