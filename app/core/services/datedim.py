from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.db.models import DateDim
from app.db.base import get_db
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, timedelta


class DateDimRepository(ABC):
    
    @abstractmethod
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[DateDim]:
        pass
    
    @abstractmethod
    def get_by_date(self, date_key: date) -> Optional[DateDim]:
        pass
    
    @abstractmethod
    def get_by_year(self, year: int) -> List[DateDim]:
        pass
    
    @abstractmethod
    def get_by_quarter(self, year: int, quarter: int) -> List[DateDim]:
        pass
    
    @abstractmethod
    def get_by_month(self, year: int, month: int) -> List[DateDim]:
        pass
    
    @abstractmethod
    def get_weekends(self, start_date: date, end_date: date) -> List[DateDim]:
        pass
    
    @abstractmethod
    def get_weekdays(self, start_date: date, end_date: date) -> List[DateDim]:
        pass
    
    @abstractmethod
    def create(self, date_dim: DateDim) -> DateDim:
        pass
    
    @abstractmethod
    def update(self, date_dim: DateDim) -> DateDim:
        pass
    
    @abstractmethod
    def delete(self, date_key: date) -> bool:
        pass


class DateDimService(DateDimRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .order_by(DateDim.date_key.asc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_date(self, date_key: date) -> Optional[DateDim]:
        stmt = select(DateDim).where(DateDim.date_key == date_key)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_year(self, year: int) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(DateDim.year == year)
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_quarter(self, year: int, quarter: int) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(
                and_(
                    DateDim.year == year,
                    DateDim.quarter == quarter
                )
            )
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_month(self, year: int, month: int) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(
                and_(
                    DateDim.year == year,
                    DateDim.month == month
                )
            )
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(
                and_(
                    DateDim.date_key >= start_date,
                    DateDim.date_key <= end_date
                )
            )
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_weekends(self, start_date: date, end_date: date) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(
                and_(
                    DateDim.date_key >= start_date,
                    DateDim.date_key <= end_date,
                    DateDim.is_weekend == True
                )
            )
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_weekdays(self, start_date: date, end_date: date) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(
                and_(
                    DateDim.date_key >= start_date,
                    DateDim.date_key <= end_date,
                    DateDim.is_weekend == False
                )
            )
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_day_of_week(self, day_of_week: str, start_date: date, end_date: date) -> List[DateDim]:
        stmt = (
            select(DateDim)
            .where(
                and_(
                    DateDim.date_key >= start_date,
                    DateDim.date_key <= end_date,
                    DateDim.day_of_week == day_of_week
                )
            )
            .order_by(DateDim.date_key.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_current_quarter_dates(self) -> List[DateDim]:
        today = date.today()
        current_quarter = (today.month - 1) // 3 + 1
        return self.get_by_quarter(today.year, current_quarter)
    
    def get_current_month_dates(self) -> List[DateDim]:
        today = date.today()
        return self.get_by_month(today.year, today.month)
    
    def get_current_year_dates(self) -> List[DateDim]:
        today = date.today()
        return self.get_by_year(today.year)
    
    def get_last_n_days(self, n: int) -> List[DateDim]:
        end_date = date.today()
        start_date = end_date - timedelta(days=n-1)
        return self.get_by_date_range(start_date, end_date)
    
    def create(self, date_dim: DateDim) -> DateDim:
        self.db.add(date_dim)
        self.db.commit()
        self.db.refresh(date_dim)
        return date_dim
    
    def bulk_create(self, date_dims: List[DateDim]) -> List[DateDim]:
        self.db.add_all(date_dims)
        self.db.commit()
        for dim in date_dims:
            self.db.refresh(dim)
        return date_dims
    
    def populate_date_range(self, start_date: date, end_date: date) -> List[DateDim]:
        date_dims = []
        current_date = start_date
        
        while current_date <= end_date:
            day_of_week = current_date.strftime('%A')
            is_weekend = current_date.weekday() >= 5
            quarter = (current_date.month - 1) // 3 + 1
            
            date_dim = DateDim(
                date_key=current_date,
                year=current_date.year,
                quarter=quarter,
                month=current_date.month,
                day_of_week=day_of_week,
                is_weekend=is_weekend
            )
            date_dims.append(date_dim)
            current_date += timedelta(days=1)
        
        return self.bulk_create(date_dims)
    
    def update(self, date_dim: DateDim) -> DateDim:
        self.db.commit()
        self.db.refresh(date_dim)
        return date_dim
    
    def delete(self, date_key: date) -> bool:
        date_dim = self.get_by_date(date_key)
        if date_dim:
            self.db.delete(date_dim)
            self.db.commit()
            return True
        return False
    
    def exists(self, date_key: date) -> bool:
        return self.get_by_date(date_key) is not None
    
    def get_min_date(self) -> Optional[date]:
        stmt = select(DateDim).order_by(DateDim.date_key.asc()).limit(1)
        result = self.db.execute(stmt)
        date_dim = result.scalar_one_or_none()
        return date_dim.date_key if date_dim else None
    
    def get_max_date(self) -> Optional[date]:
        stmt = select(DateDim).order_by(DateDim.date_key.desc()).limit(1)
        result = self.db.execute(stmt)
        date_dim = result.scalar_one_or_none()
        return date_dim.date_key if date_dim else None


def get_date_dim_service(db: Session = None) -> DateDimService:
    if db is None:
        db = next(get_db())
    return DateDimService(db)
