from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = Column(Integer, primary_key=True)
    telegram_id: Mapped[int] = Column(Integer, nullable=False, unique=True)
    username: Mapped[str] = Column(String(256), nullable=False)
    alerts: Mapped[list['Alert']] = relationship('Alert', back_populates='user')


class Alert(Base):
    __tablename__ = 'alerts'

    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey('users.id'))
    cryptocurrency: Mapped[str] = Column(String(50), nullable=False)
    threshold_value: Mapped[float] = Column(Float, nullable=False)
    direction: Mapped[str] = Column(String(20), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship('User', back_populates='alerts')
    