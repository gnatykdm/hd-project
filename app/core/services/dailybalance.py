from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_
from app.db.models import DailyBalance, Account
from app.db.base import get_db
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, timedelta


class DailyBalanceRepository(ABC):
    
    @abstractmethod
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[DailyBalance]:
        pass
    
    @abstractmethod
    def get_by_id(self, idx: int) -> Optional[DailyBalance]:
        pass
    
    @abstractmethod
    def get_by_account(self, account_id: int, pagination: int = 25, offset: int = 0) -> List[DailyBalance]:
        pass
    
    @abstractmethod
    def get_by_account_and_date(self, account_id: int, balance_date: date) -> Optional[DailyBalance]:
        pass
    
    @abstractmethod
    def get_by_date_range(self, account_id: int, start_date: date, end_date: date) -> List[DailyBalance]:
        pass
    
    @abstractmethod
    def create(self, daily_balance: DailyBalance) -> DailyBalance:
        pass
    
    @abstractmethod
    def update(self, daily_balance: DailyBalance) -> DailyBalance:
        pass
    
    @abstractmethod
    def delete(self, idx: int) -> bool:
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        pass


class DailyBalanceService(DailyBalanceRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .order_by(DailyBalance.balance_date.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_id(self, idx: int) -> Optional[DailyBalance]:
        stmt = select(DailyBalance).where(DailyBalance.id == idx)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_account(self, account_id: int, pagination: int = 25, offset: int = 0) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(DailyBalance.account_id == account_id)
            .order_by(DailyBalance.balance_date.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_account_and_date(self, account_id: int, balance_date: date) -> Optional[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date == balance_date
                )
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_date_range(self, account_id: int, start_date: date, end_date: date) -> List[DailyBalance]:
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
    
    def get_balances_by_date(self, balance_date: date) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(DailyBalance.balance_date == balance_date)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_average_balance(self, account_id: int, start_date: date, end_date: date) -> float:
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
    
    def get_min_balance(self, account_id: int, start_date: date, end_date: date) -> float:
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
    
    def get_max_balance(self, account_id: int, start_date: date, end_date: date) -> float:
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
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.get_by_date_range(account_id, start_date, end_date)
    
    def get_accounts_below_threshold(self, threshold: float, balance_date: date) -> List[DailyBalance]:
        stmt = (
            select(DailyBalance)
            .where(
                and_(
                    DailyBalance.balance_date == balance_date,
                    DailyBalance.ending_balance < threshold
                )
            )
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, daily_balance: DailyBalance) -> DailyBalance:
        self.db.add(daily_balance)
        self.db.commit()
        self.db.refresh(daily_balance)
        return daily_balance
    
    def bulk_create(self, daily_balances: List[DailyBalance]) -> List[DailyBalance]:
        self.db.add_all(daily_balances)
        self.db.commit()
        for balance in daily_balances:
            self.db.refresh(balance)
        return daily_balances
    
    def update(self, daily_balance: DailyBalance) -> DailyBalance:
        self.db.commit()
        self.db.refresh(daily_balance)
        return daily_balance
    
    def delete(self, idx: int) -> bool:
        daily_balance = self.get_by_id(idx)
        if daily_balance:
            self.db.delete(daily_balance)
            self.db.commit()
            return True
        return False
    
    def delete_by_account_and_date_range(self, account_id: int, start_date: date, end_date: date) -> int:
        stmt = (
            select(DailyBalance)
            .where(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            )
        )
        result = self.db.execute(stmt)
        balances = list(result.scalars().all())
        count = len(balances)
        for balance in balances:
            self.db.delete(balance)
        self.db.commit()
        return count
    
    def count_all(self) -> int:
        stmt = select(func.count(DailyBalance.id))
        result = self.db.execute(stmt)
        return result.scalar()
    
    def count_by_account(self, account_id: int) -> int:
        stmt = (
            select(func.count(DailyBalance.id))
            .where(DailyBalance.account_id == account_id)
        )
        result = self.db.execute(stmt)
        return result.scalar()


def get_daily_balance_service(db: Session = None) -> DailyBalanceService:
    if db is None:
        db = next(get_db())
    return DailyBalanceService(db)
