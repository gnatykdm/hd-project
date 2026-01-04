from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.db.models import DateDim
from app.db.base import get_db

class DateDimService:    
    def __init__(self, db: Session) -> None:
        self.db: Session = db
    
    def get_by_date(self, date_key: date) -> Optional[DateDim]:
        stmt = select(DateDim).where(DateDim.date_key == date_key)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
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
    
    def get_current_month_dates(self) -> List[DateDim]:
        today: date = date.today()
        return self.get_by_month(today.year, today.month)
    
    def get_last_n_days(self, n: int) -> List[DateDim]:
        end_date: date = date.today()
        start_date: date = end_date - timedelta(days=n-1)
        return self.get_by_date_range(start_date, end_date)
    
    def populate_date_range(self, start_date: date, end_date: date) -> List[DateDim]:
        date_dims: List[DateDim] = []
        current_date: date = start_date
        
        while current_date <= end_date:
            day_of_week: str = current_date.strftime('%A')
            is_weekend: bool = current_date.weekday() >= 5
            quarter: int = (current_date.month - 1) // 3 + 1
            
            date_dim: DateDim = DateDim(
                date_key=current_date,
                year=current_date.year,
                quarter=quarter,
                month=current_date.month,
                day_of_week=day_of_week,
                is_weekend=is_weekend
            )
            date_dims.append(date_dim)
            current_date += timedelta(days=1)
        
        self.db.add_all(date_dims)
        self.db.commit()
        for dim in date_dims:
            self.db.refresh(dim)
        
        return date_dims
    
    def exists(self, date_key: date) -> bool:
        return self.get_by_date(date_key) is not None
    
    def get_min_date(self) -> Optional[date]:
        stmt = select(DateDim).order_by(DateDim.date_key.asc()).limit(1)
        result = self.db.execute(stmt)
        date_dim: Optional[DateDim] = result.scalar_one_or_none()
        return date_dim.date_key if date_dim else None
    
    def get_max_date(self) -> Optional[date]:
        stmt = select(DateDim).order_by(DateDim.date_key.desc()).limit(1)
        result = self.db.execute(stmt)
        date_dim: Optional[DateDim] = result.scalar_one_or_none()
        return date_dim.date_key if date_dim else None


def get_date_dim_service(db: Optional[Session] = None) -> DateDimService:
    if db is None:
        db = next(get_db())
    return DateDimService(db)