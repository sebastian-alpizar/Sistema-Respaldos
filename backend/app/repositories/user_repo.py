from typing import List, Optional
import logging
from app.models.user import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self):
        # En una implementación real, esto usaría una base de datos
        self._users = []
        self._next_id = 1
    
    async def get_all(self) -> List[User]:
        """Obtiene todos los usuarios"""
        return self._users.copy()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID"""
        for user in self._users:
            if user.id == user_id:
                return user
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario"""
        for user in self._users:
            if user.username == username:
                return user
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        for user in self._users:
            if user.email == email:
                return user
        return None
    
    async def create(self, user_data: UserCreate) -> User:
        """Crea un nuevo usuario"""
        user = User(
            id=self._next_id,
            **user_data.dict(exclude={'password'}),  # En producción, hash la contraseña
            created_at="2025-01-01T00:00:00"  # Timestamp real en producción
        )
        
        self._users.append(user)
        self._next_id += 1
        
        logger.info(f"Usuario creado: {user.username}")
        return user
    
    async def update(self, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """Actualiza un usuario"""
        for i, user in enumerate(self._users):
            if user.id == user_id:
                update_dict = update_data.dict(exclude_unset=True)
                updated_user = user.copy(update=update_dict)
                self._users[i] = updated_user
                
                logger.info(f"Usuario actualizado: {updated_user.username}")
                return updated_user
        
        return None
    
    async def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        for i, user in enumerate(self._users):
            if user.id == user_id:
                deleted_user = self._users.pop(i)
                logger.info(f"Usuario eliminado: {deleted_user.username}")
                return True
        
        return False
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica un usuario"""
        # En producción, esto debería verificar contraseñas hasheadas
        user = await self.get_by_username(username)
        if user and user.is_active:
            # Simulación de verificación de contraseña
            # En producción, usar: bcrypt.checkpw(password.encode(), user.password_hash.encode())
            return user
        return None