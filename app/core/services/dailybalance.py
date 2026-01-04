from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.db.models import DailyBalance
from app.db.base import get_db


class DailyBalanceService:    
    def __init__(self, db: Session) -> None:
        self.db: Session = db
    
    def get_by_account(
        self, 
        account_id: int, 
        pagination: int = 25, 
        offset: int = 0
    ) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(DailyBalance.account_id == account_id)
            .order_by(DailyBalance.balance_date.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_date_range(
        self, 
        account_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            )
            .order_by(DailyBalance.balance_date.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_latest_balance(self, account_id: int) -> Optional[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(DailyBalance.account_id == account_id)
            .order_by(DailyBalance.balance_date.desc())
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_average_balance(
        self, 
        account_id: int, 
        start_date: date, 
        end_date: date
    ) -> float:
        stmt = (
            select(func.avg(DailyBalance.ending_balance))
            .where(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            )
        )
        result = self.db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg else 0.0
    
    def get_min_balance(
        self, 
        account_id: int, 
        start_date: date, 
        end_date: date
    ) -> float:
        stmt = (
            select(func.min(DailyBalance.ending_balance))
            .where(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            )
        )
        result = self.db.execute(stmt)
        min_val = result.scalar()
        return float(min_val) if min_val else 0.0
    
    def get_max_balance(
        self, 
        account_id: int, 
        start_date: date, 
        end_date: date
    ) -> float:
        stmt = (
            select(func.max(DailyBalance.ending_balance))
            .where(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            )
        )
        result = self.db.execute(stmt)
        max_val = result.scalar()
        return float(max_val) if max_val else 0.0
    
    def get_balance_trend(self, account_id: int, days: int = 30) -> List[DailyBalance]:
        end_date: date = date.today()
        start_date: date = end_date - timedelta(days=days)
        return self.get_by_date_range(account_id, start_date, end_date)
    
    def get_balances_by_date(self, balance_date: date) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(DailyBalance.balance_date == balance_date)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def count_all(self) -> int:
        stmt = select(func.count(DailyBalance.id))
        result = self.db.execute(stmt)
        return result.scalar() or 0


def get_daily_balance_service(db: Optional[Session] = None) -> DailyBalanceService:
    if db is None:
        db = next(get_db())
    return DailyBalanceService(db)