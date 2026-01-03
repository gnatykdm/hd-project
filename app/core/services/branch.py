from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from app.db.models import Branch, Account
from app.db.base import get_db
from abc import ABC, abstractmethod
from typing import List, Optional

class BranchRepository(ABC):
    
    @abstractmethod
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Branch]:
        pass
    
    @abstractmethod
    def get_by_id(self, idx: int) -> Optional[Branch]:
        pass
    
    @abstractmethod
    def get_by_code(self, branch_code: str) -> Optional[Branch]:
        pass
    
    @abstractmethod
    def get_by_region(self, region: str) -> List[Branch]:
        pass
    
    @abstractmethod
    def create(self, branch: Branch) -> Branch:
        pass
    
    @abstractmethod
    def update(self, branch: Branch) -> Branch:
        pass
    
    @abstractmethod
    def delete(self, idx: int) -> bool:
        pass
    
    @abstractmethod
    def get_branch_with_accounts(self, idx: int) -> Optional[Branch]:
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        pass


class BranchService(BranchRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, pagination: int = 25, offset: int = 0) -> List[Branch]:
        stmt = (
            select(Branch)
            .limit(pagination)
            .offset(offset)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_id(self, idx: int) -> Optional[Branch]:
        stmt = select(Branch).where(Branch.id == idx)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_code(self, branch_code: str) -> Optional[Branch]:
        stmt = select(Branch).where(Branch.branch_code == branch_code)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_region(self, region: str) -> List[Branch]:
        stmt = select(Branch).where(Branch.region == region)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_branch_with_accounts(self, idx: int) -> Optional[Branch]:
        stmt = (
            select(Branch)
            .options(joinedload(Branch.accounts))
            .where(Branch.id == idx)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_branches_by_account_count(self, min_accounts: int = 0) -> List[dict]:
        stmt = (
            select(
                Branch,
                func.count(Account.id).label('account_count')
            )
            .outerjoin(Branch.accounts)
            .group_by(Branch.id)
            .having(func.count(Account.id) >= min_accounts)
        )
        result = self.db.execute(stmt)
        return [
            {
                'branch': row[0],
                'account_count': row[1]
            }
            for row in result.all()
        ]
    
    def create(self, branch: Branch) -> Branch:
        self.db.add(branch)
        self.db.commit()
        self.db.refresh(branch)
        return branch
    
    def update(self, branch: Branch) -> Branch:
        self.db.commit()
        self.db.refresh(branch)
        return branch
    
    def delete(self, idx: int) -> bool:
        branch = self.get_by_id(idx)
        if branch:
            self.db.delete(branch)
            self.db.commit()
            return True
        return False
    
    def count_all(self) -> int:
        stmt = select(func.count(Branch.id))
        result = self.db.execute(stmt)
        return result.scalar()
    
    def count_by_region(self, region: str) -> int:
        stmt = (
            select(func.count(Branch.id))
            .where(Branch.region == region)
        )
        result = self.db.execute(stmt)
        return result.scalar()
    
    def get_all_regions(self) -> List[str]:
        stmt = select(Branch.region).distinct()
        result = self.db.execute(stmt)
        return [r[0] for r in result.all() if r[0] is not None]


def get_branch_service(db: Session = None) -> BranchService:
    if db is None:
        db = next(get_db())
    return BranchService(db)
