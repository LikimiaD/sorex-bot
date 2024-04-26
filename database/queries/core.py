import asyncio

from sqlalchemy import select, update

from database.database import async_engine
from database.models import User, Alert
from database.database import async_session_factory


class AsyncORM:
    @staticmethod
    async def create_table():
        async with async_engine.begin() as conn:
            await conn.run_sync(Alert.metadata.create_all, checkfirst=True)
            await conn.run_sync(User.metadata.create_all, checkfirst=True)

    @staticmethod
    async def ensure_user_and_create_alert(telegram_id: int, username: str, cryptocurrency: str, threshold_value: float,
                                           direction: str):
        async with async_session_factory() as session:
            try:
                stmt = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(stmt)
                user = result.scalars().first()

                if not user:
                    user = User(telegram_id=telegram_id, username=username)
                    session.add(user)
                    await session.flush()

                stmt = select(Alert).where(Alert.user_id == user.id, Alert.cryptocurrency == cryptocurrency, Alert.direction == direction)
                result = await session.execute(stmt)
                alert = result.scalars().first()

                if alert:
                    alert.threshold_value = threshold_value
                    alert.direction = direction
                    alert.is_active = True
                else:
                    alert = Alert(user_id=user.id, cryptocurrency=cryptocurrency, threshold_value=threshold_value,
                                  direction=direction, is_active=True)
                    session.add(alert)

                await session.commit()
                return user, alert
            except Exception as e:
                await session.rollback()
                raise e

    @staticmethod
    async def ensure_user(telegram_id: int, username: str):
        async with async_session_factory() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if not user:
                user = User(telegram_id=telegram_id, username=username)
                session.add(user)
                try:
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    raise e
            return user

    @staticmethod
    async def deactivate_old_alerts(telegram_id: int):
        async with async_session_factory() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalars().first()

            update_stmt = update(Alert).where(
                Alert.user_id == user.id,
                Alert.is_active == True
            ).values(is_active=False)
            await session.execute(update_stmt)
            await session.commit()

    @staticmethod
    async def get_alerts():
        async with async_session_factory() as session:
            stmt = select(
                User.telegram_id.label('telegram_id'),
                Alert.cryptocurrency.label('cryptocurrency'),
                Alert.threshold_value.label('threshold_value'),
                Alert.direction.label('direction'),
                Alert.is_active.label('is_active')
            ).join(User, User.id == Alert.user_id).where(Alert.is_active == True)
            result = await session.execute(stmt)
            alerts = [{column: value for column, value in row.items()} for row in result.mappings().all()]
            return alerts


if __name__ == '__main__':
    alerts = asyncio.run(AsyncORM.get_alerts())
    for alert in alerts:
        if isinstance(alert, dict):
            self.queue.put(alert)
        else:
            print(f"Error: Alert expected to be a dict, but got {type(alert)}")
