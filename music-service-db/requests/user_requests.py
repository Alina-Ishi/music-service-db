from datetime import date
from typing import Optional, List
from sqlmodel import Session, select
from models import User, Subscription, Payment, Tariff

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)

def get_active_subscription(session: Session, user_id: int) -> Optional[Subscription]:
    today = date.today()
    stmt = (
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.status == "active")
        .where(Subscription.start_date <= today)
        .where(Subscription.end_date >= today)
        .order_by(Subscription.end_date.desc())
    )
    return session.exec(stmt).first()

def get_user_payments(session: Session, user_id: int, limit: int = 20) -> List[Payment]:
    stmt = (
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.paid_at.desc())
        .limit(limit)
    )
    return list(session.exec(stmt))

def get_all_tariffs(session: Session) -> List[Tariff]:
    return list(session.exec(select(Tariff).order_by(Tariff.price)))

def create_user(session: Session, email: str, name: str, password_hash: str,
                country: Optional[str] = None) -> User:
    user = User(email=email, name=name, password_hash=password_hash, country=country)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user