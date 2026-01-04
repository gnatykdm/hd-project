from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_

from app.db.models import Customer
from app.db.base import get_db


class CustomerService:
    def __init__(self, db: Session) -> None:
        self.db: Session = db
    
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Customer]:
        stmt = (
            select(Customer)
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_all_customers(self) -> List[Customer]:
        stmt = select(Customer)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_by_id(self, idx: int) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.id == idx)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_customer_with_accounts(self, idx: int) -> Optional[Customer]:
        stmt = (
            select(Customer)
            .options(joinedload(Customer.accounts))
            .where(Customer.id == idx)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def search_customers(self, query: str) -> List[Customer]:
        search_pattern: str = f"%{query}%"
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
    
    def create_customer(self, full_name: str, email: str, credit_score: int) -> Customer:
        new_customer: Customer = Customer(
            full_name=full_name,
            email=email,
            credit_score=credit_score,
            customer_segment="Standard"
        )
        self.db.add(new_customer)
        self.db.commit()
        self.db.refresh(new_customer)
        return new_customer
    
    def delete_customer(self, idx: int) -> bool:
        customer: Optional[Customer] = self.get_by_id(idx)
        if customer:
            self.db.delete(customer)
            self.db.commit()
            return True
        return False
    
    def count_all(self) -> int:
        stmt = select(func.count(Customer.id))
        result = self.db.execute(stmt)
        return result.scalar() or 0
    
    def count_by_segment(self, segment: str) -> int:
        stmt = (
            select(func.count(Customer.id))
            .where(Customer.customer_segment == segment)
        )
        result = self.db.execute(stmt)
        return result.scalar() or 0
    
    def get_all_segments(self) -> List[str]:
        stmt = select(Customer.customer_segment).distinct()
        result = self.db.execute(stmt)
        return [r for r in result.scalars().all() if r is not None]
    
    def get_average_credit_score(self) -> float:
        stmt = select(func.avg(Customer.credit_score))
        result = self.db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg else 0.0


def get_customer_service(db: Optional[Session] = None) -> CustomerService:
    if db is None:
        db = next(get_db())
    return CustomerService(db)