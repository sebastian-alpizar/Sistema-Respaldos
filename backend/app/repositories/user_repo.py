from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.database_models import UserModel
from app.models.user import User, UserCreate, UserUpdate
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self) -> List[User]:
        """Obtiene todos los usuarios"""
        try:
            result = await self.db.execute(select(UserModel))
            users = result.scalars().all()
            return [self._model_to_user(user) for user in users]
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {str(e)}")
            return []
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            return self._model_to_user(user) if user else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {str(e)}")
            return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.username == username)
            )
            user = result.scalar_one_or_none()
            return self._model_to_user(user) if user else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario {username}: {str(e)}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
            return self._model_to_user(user) if user else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email {email}: {str(e)}")
            return None
    
    async def create(self, user_data: UserCreate) -> User:
        """Crea un nuevo usuario"""
        try:
            # En producción, hashear la contraseña
            db_user = UserModel(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role.value,
                is_active=user_data.is_active
            )
            
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            
            logger.info(f"Usuario creado: {db_user.username}")
            return self._model_to_user(db_user)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creando usuario: {str(e)}")
            raise
    
    async def update(self, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """Actualiza un usuario"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                return None
            
            # Actualizar campos
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(db_user, field):
                    setattr(db_user, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_user)
            
            logger.info(f"Usuario actualizado: {db_user.username}")
            return self._model_to_user(db_user)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error actualizando usuario {user_id}: {str(e)}")
            return None
    
    async def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                return False
            
            await self.db.delete(db_user)
            await self.db.commit()
            
            logger.info(f"Usuario eliminado: {db_user.username}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error eliminando usuario {user_id}: {str(e)}")
            return False
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica un usuario"""
        try:
            user = await self.get_by_username(username)
            if user and user.is_active:
                # En producción, verificar contraseña hasheada
                # if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                return user
            return None
        except Exception as e:
            logger.error(f"Error autenticando usuario {username}: {str(e)}")
            return None
    
    def _model_to_user(self, db_user: UserModel) -> User:
        """Convierte UserModel a User"""
        from app.models.user import UserRole
        
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            role=UserRole(db_user.role),
            is_active=db_user.is_active,
            created_at=db_user.created_at.isoformat() if db_user.created_at else None
        )