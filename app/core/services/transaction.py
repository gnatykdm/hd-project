from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_

from app.db.models import Transaction
from app.db.base import get_db


class TransactionService:    
    def __init__(self, db: Session) -> None:
        self.db: Session = db

    def create_transaction(
        self, 
        account_id: int, 
        amount: float, 
        category: str, 
        merchant_name: str
    ) -> Transaction:
        new_tx: Transaction = Transaction(
            account_id=account_id,
            amount=amount,
            category=category,
            merchant_name=merchant_name,
            timestamp=datetime.utcnow()
        )
        self.db.add(new_tx)
        self.db.commit()
        self.db.refresh(new_tx)
        return new_tx

    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_id(self, idx: int) -> Optional[Transaction]:
        stmt = (
            select(Transaction)
            .options(joinedload(Transaction.account))
            .where(Transaction.id == idx)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_account(
        self, 
        account_id: int, 
        pagination: int = 25, 
        offset: int = 0
    ) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_category_breakdown(
        self, 
        account_id: Optional[int] = None, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(
                Transaction.category,
                func.count(Transaction.id).label('count'),
                func.sum(Transaction.amount).label('total'),
                func.avg(Transaction.amount).label('average')
            )
            .group_by(Transaction.category)
        )
        
        if account_id:
            stmt = stmt.where(Transaction.account_id == account_id)
        
        if start_date and end_date:
            stmt = stmt.where(
                and_(
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date
                )
            )
        
        result = self.db.execute(stmt)
        return [
            {
                'category': row[0],
                'count': row[1],
                'total': float(row[2]) if row[2] else 0.0,
                'average': float(row[3]) if row[3] else 0.0
            }
            for row in result.all()
        ]
    
    def get_total_by_account(
        self, 
        account_id: int, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> float:
        stmt = select(func.sum(Transaction.amount)).where(
            Transaction.account_id == account_id
        )
        
        if start_date and end_date:
            stmt = stmt.where(
                and_(
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date
                )
            )
        
        result = self.db.execute(stmt)
        total = result.scalar()
        return float(total) if total else 0.0
    
    def count_all(self) -> int:
        stmt = select(func.count(Transaction.id))
        result = self.db.execute(stmt)
        return result.scalar() or 0
    
    def count_by_account(self, account_id: int) -> int:
        stmt = (
            select(func.count(Transaction.id))
            .where(Transaction.account_id == account_id)
        )
        result = self.db.execute(stmt)
        return result.scalar() or 0


def get_transaction_service(db: Optional[Session] = None) -> TransactionService:
    if db is None:
        db = next(get_db())
    return TransactionService(db)