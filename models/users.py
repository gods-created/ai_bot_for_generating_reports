from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), nullable=True, default='')
    report_resource: Mapped[str] = mapped_column(String(100), nullable=True, default='')
    created_at: Mapped[str] = mapped_column(String(50), nullable=True, default=lambda: datetime.now().strftime('%d.%m.%Y %H:%M:%S'))

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'report_resource': self.report_resource,
            'created_at': self.created_at
        }