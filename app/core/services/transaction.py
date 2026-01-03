from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_, or_, desc
from app.db.models import Transaction, Account
from app.db.base import get_db
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta


class TransactionRepository(ABC):
    
    @abstractmethod
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_by_id(self, idx: int) -> Optional[Transaction]:
        pass
    
    @abstractmethod
    def get_by_account(self, account_id: int, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_by_category(self, category: str, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: datetime, end_date: datetime, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        pass
    
    @abstractmethod
    def get_by_amount_range(self, min_amount: float, max_amount: float, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        pass
    
    @abstractmethod
    def create(self, transaction: Transaction) -> Transaction:
        pass
    
    @abstractmethod
    def update(self, transaction: Transaction) -> Transaction:
        pass
    
    @abstractmethod
    def delete(self, idx: int) -> bool:
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        pass


class TransactionService(TransactionRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
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
    
    def get_by_account(self, account_id: int, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_category(self, category: str, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.category == category)
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                and_(
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date
                )
            )
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_amount_range(self, min_amount: float, max_amount: float, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                and_(
                    Transaction.amount >= min_amount,
                    Transaction.amount <= max_amount
                )
            )
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_account_and_date_range(self, account_id: int, start_date: datetime, end_date: datetime) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                and_(
                    Transaction.account_id == account_id,
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date
                )
            )
            .order_by(Transaction.timestamp.desc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_merchant(self, merchant_name: str, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.merchant_name == merchant_name)
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def search_transactions(self, query: str, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        search_pattern = f"%{query}%"
        stmt = (
            select(Transaction)
            .where(
                or_(
                    Transaction.category.ilike(search_pattern),
                    Transaction.merchant_name.ilike(search_pattern)
                )
            )
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_largest_transactions(self, limit: int = 10, start_date: datetime = None, end_date: datetime = None) -> List[Transaction]:
        stmt = select(Transaction)
        
        if start_date and end_date:
            stmt = stmt.where(
                and_(
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date
                )
            )
        
        stmt = stmt.order_by(Transaction.amount.desc()).limit(limit)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_recent_transactions(self, days: int = 7, pagination: int = 25, offset: int = 0) -> List[Transaction]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(Transaction)
            .where(Transaction.timestamp >= cutoff_date)
            .order_by(Transaction.timestamp.desc())
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_total_by_account(self, account_id: int, start_date: datetime = None, end_date: datetime = None) -> float:
        stmt = select(func.sum(Transaction.amount)).where(Transaction.account_id == account_id)
        
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
    
    def get_total_by_category(self, category: str, start_date: datetime = None, end_date: datetime = None) -> float:
        stmt = select(func.sum(Transaction.amount)).where(Transaction.category == category)
        
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
    
    def get_category_breakdown(self, account_id: int = None, start_date: datetime = None, end_date: datetime = None) -> List[dict]:
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
    
    def get_merchant_breakdown(self, account_id: int = None, start_date: datetime = None, end_date: datetime = None, limit: int = 10) -> List[dict]:
        stmt = (
            select(
                Transaction.merchant_name,
                func.count(Transaction.id).label('count'),
                func.sum(Transaction.amount).label('total')
            )
            .where(Transaction.merchant_name.isnot(None))
            .group_by(Transaction.merchant_name)
            .order_by(desc('total'))
            .limit(limit)
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
                'merchant_name': row[0],
                'count': row[1],
                'total': float(row[2]) if row[2] else 0.0
            }
            for row in result.all()
        ]
    
    def get_average_transaction_amount(self, account_id: int = None, start_date: datetime = None, end_date: datetime = None) -> float:
        stmt = select(func.avg(Transaction.amount))
        
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
        avg = result.scalar()
        return float(avg) if avg else 0.0
    
    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def bulk_create(self, transactions: List[Transaction]) -> List[Transaction]:
        self.db.add_all(transactions)
        self.db.commit()
        for transaction in transactions:
            self.db.refresh(transaction)
        return transactions
    
    def update(self, transaction: Transaction) -> Transaction:
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def delete(self, idx: int) -> bool:
        transaction = self.get_by_id(idx)
        if transaction:
            self.db.delete(transaction)
            self.db.commit()
            return True
        return False
    
    def delete_by_account(self, account_id: int) -> int:
        stmt = select(Transaction).where(Transaction.account_id == account_id)
        result = self.db.execute(stmt)
        transactions = list(result.scalars().all())
        count = len(transactions)
        for transaction in transactions:
            self.db.delete(transaction)
        self.db.commit()
        return count
    
    def count_all(self) -> int:
        stmt = select(func.count(Transaction.id))
        result = self.db.execute(stmt)
        return result.scalar()
    
    def count_by_account(self, account_id: int) -> int:
        stmt = (
            select(func.count(Transaction.id))
            .where(Transaction.account_id == account_id)
        )
        result = self.db.execute(stmt)
        return result.scalar()
    
    def count_by_category(self, category: str) -> int:
        stmt = (
            select(func.count(Transaction.id))
            .where(Transaction.category == category)
        )
        result = self.db.execute(stmt)
        return result.scalar()


def get_transaction_service(db: Session = None) -> TransactionService:
    if db is None:
        db = next(get_db())
    return TransactionService(db)
