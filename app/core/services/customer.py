from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from app.db.models import Customer, Account
from app.db.base import get_db
from abc import ABC, abstractmethod
from typing import List, Optional


class CustomerRepository(ABC):
    
    @abstractmethod
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Customer]:
        pass
    
    @abstractmethod
    def get_by_id(self, idx: int) -> Optional[Customer]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Customer]:
        pass
    
    @abstractmethod
    def get_by_segment(self, segment: str) -> List[Customer]:
        pass
    
    @abstractmethod
    def get_by_credit_score_range(self, min_score: int, max_score: int) -> List[Customer]:
        pass
    
    @abstractmethod
    def create(self, customer: Customer) -> Customer:
        pass
    
    @abstractmethod
    def update(self, customer: Customer) -> Customer:
        pass
    
    @abstractmethod
    def delete(self, idx: int) -> bool:
        pass
    
    @abstractmethod
    def get_customer_with_accounts(self, idx: int) -> Optional[Customer]:
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        pass


class CustomerService(CustomerRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Customer]:
        stmt = (
            select(Customer)
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_id(self, idx: int) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.id == idx)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.email == email)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_segment(self, segment: str) -> List[Customer]:
        stmt = select(Customer).where(Customer.customer_segment == segment)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_credit_score_range(self, min_score: int, max_score: int) -> List[Customer]:
        stmt = (
            select(Customer)
            .where(
                Customer.credit_score >= min_score,
                Customer.credit_score <= max_score
            )
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_customer_with_accounts(self, idx: int) -> Optional[Customer]:
        stmt = (
            select(Customer)
            .options(joinedload(Customer.accounts))
            .where(Customer.id == idx)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def search_customers(self, query: str) -> List[Customer]:
        search_pattern = f"%{query}%"
        stmt = (
            select(Customer)
            .where(
                or_(
                    Customer.full_name.ilike(search_pattern),
                    Customer.email.ilike(search_pattern)
                )
            )
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_customers_by_account_count(self, min_accounts: int = 1) -> List[dict]:
        stmt = (
            select(
                Customer,
                func.count(Account.id).label('account_count')
            )
            .outerjoin(Customer.accounts)
            .group_by(Customer.id)
            .having(func.count(Account.id) >= min_accounts)
        )
        result = self.db.execute(stmt)
        return [
            {
                'customer': row[0],
                'account_count': row[1]
            }
            for row in result.all()
        ]
    
    def get_high_value_customers(self, min_credit_score: int = 700) -> List[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.credit_score >= min_credit_score)
            .order_by(Customer.credit_score.desc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def update(self, customer: Customer) -> Customer:
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def delete(self, idx: int) -> bool:
        customer = self.get_by_id(idx)
        if customer:
            self.db.delete(customer)
            self.db.commit()
            return True
        return False
    
    def count_all(self) -> int:
        stmt = select(func.count(Customer.id))
        result = self.db.execute(stmt)
        return result.scalar()
    
    def count_by_segment(self, segment: str) -> int:
        stmt = (
            select(func.count(Customer.id))
            .where(Customer.customer_segment == segment)
        )
        result = self.db.execute(stmt)
        return result.scalar()
    
    def get_all_segments(self) -> List[str]:
        stmt = select(Customer.customer_segment).distinct()
        result = self.db.execute(stmt)
        return [r[0] for r in result.all() if r[0] is not None]
    
    def get_average_credit_score(self) -> float:
        stmt = select(func.avg(Customer.credit_score))
        result = self.db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg else 0.0


def get_customer_service(db: Session = None) -> CustomerService:
    if db is None:
        db = next(get_db())
    return CustomerService(db)
