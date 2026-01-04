from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.db.models import Account
from app.db.base import get_db
from abc import ABC, abstractmethod
from typing import List, Optional


class AccountRepository(ABC):    
    @abstractmethod
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Account]:
        pass
    
    @abstractmethod
    def get_acc_by_id(self, idx: int) -> Optional[Account]:
        pass
    
    @abstractmethod
    def get_acc_by_number(self, account_number: str) -> Optional[Account]:
        pass
    
    @abstractmethod
    def get_accounts_by_customer(self, customer_id: int) -> List[Account]:
        pass
    
    @abstractmethod 
    def get_accounts_by_branch(self, branch_id: int) -> List[Account]:
        pass
    
    @abstractmethod
    def get_active_accounts(self, pagination: int = 25, offset: int = 0) -> List[Account]:
        pass
    
    @abstractmethod
    def create(self, account: Account) -> Account:
        pass
    
    @abstractmethod
    def update(self, account: Account) -> Account:
        pass
    
    @abstractmethod
    def delete(self, idx: int) -> bool:
        pass


class AccountService(AccountRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Account]:
        stmt = (
            select(Account)
            .options(
                joinedload(Account.customer),
                joinedload(Account.branch)
            )
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_acc_by_id(self, idx: int) -> Optional[Account]:
        stmt = (
            select(Account)
            .options(
                joinedload(Account.customer),
                joinedload(Account.branch)
            )
            .where(Account.id == idx)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_acc_by_number(self, account_number: str) -> Optional[Account]:
        stmt = (
            select(Account)
            .options(
                joinedload(Account.customer),
                joinedload(Account.branch)
            )
            .where(Account.account_number == account_number)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def create_account(self, customer_id: int, branch_id: int, account_number: str, account_type: str = "CHECKING") -> Account:
        """
        Метод-адаптер для UI: принимает простые типы и создает объект модели.
        """
        # Создаем объект модели Account
        new_account = Account(
            customer_id=customer_id,
            branch_id=branch_id,
            account_number=account_number,
            account_type=account_type,
            balance=0.0,      # Начальный баланс
            is_active=True    # По умолчанию активен
        )
        # Вызываем ваш базовый метод create, который делает add и commit
        return self.create(new_account)

    def update_account_status(self, idx: int, status: bool) -> bool:
        account = self.get_acc_by_id(idx)
        if account:
            account.is_active = status
            self.db.commit()
            return True
        return False
    
    def get_accounts_by_customer(self, customer_id: int) -> List[Account]:
        stmt = (
            select(Account)
            .options(joinedload(Account.branch))
            .where(Account.customer_id == customer_id)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_accounts_by_branch(self, branch_id: int) -> List[Account]:
        stmt = (
            select(Account)
            .options(joinedload(Account.customer))
            .where(Account.branch_id == branch_id)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_active_accounts(self, pagination: int = 25, offset: int = 0) -> List[Account]:
        stmt = (
            select(Account)
            .options(
                joinedload(Account.customer),
                joinedload(Account.branch)
            )
            .where(Account.is_active == True)
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_accounts_by_type(self, account_type: str, pagination: int = 25, offset: int = 0) -> List[Account]:
        stmt = (
            select(Account)
            .options(
                joinedload(Account.customer),
                joinedload(Account.branch)
            )
            .where(Account.account_type == account_type)
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, account: Account) -> Account:
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def update(self, account: Account) -> Account:
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def delete(self, idx: int) -> bool:
        account = self.get_acc_by_id(idx)
        if account:
            account.is_active = False
            self.db.commit()
            return True
        return False
    
    def hard_delete(self, idx: int) -> bool:
        account = self.get_acc_by_id(idx)
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False
    
    def count_all(self) -> int:
        stmt = select(Account)
        result = self.db.execute(stmt)
        return len(list(result.scalars().all()))
    
    def count_active(self) -> int:
        stmt = select(Account).where(Account.is_active == True)
        result = self.db.execute(stmt)
        return len(list(result.scalars().all()))


def get_account_repository(db: Session = None) -> AccountService:
    if db is None:
        db = next(get_db())
    return AccountService(db)
