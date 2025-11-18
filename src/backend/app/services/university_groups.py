"""
Serviço para gerenciamento de grupos automáticos por universidade (RF052)
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.social import UniversityGroup, UniversityGroupMember
from app.models.profile import Profile
from app.models.user import User

logger = logging.getLogger(__name__)


class UniversityGroupService:
    """Serviço para grupos automáticos por universidade"""

    DEFAULT_DESCRIPTION = (
        "Grupo oficial da comunidade ISMART desta universidade. "
        "Conecte-se com seus colegas, compartilhe experiências e colabore!"
    )

    @staticmethod
    def ensure_group_exists(db: Session, university_name: str) -> UniversityGroup:
        """
        Garante que existe um grupo para a universidade
        Se não existir, cria automaticamente
        """
        if not university_name:
            raise ValueError("Nome da universidade é obrigatório")

        # Verificar se já existe
        group = db.query(UniversityGroup).filter(
            UniversityGroup.university_name == university_name
        ).first()

        if group:
            return group

        # Criar novo grupo
        group = UniversityGroup(
            university_name=university_name,
            name=f"{university_name} - Comunidade ISMART",
            description=UniversityGroupService.DEFAULT_DESCRIPTION
        )

        db.add(group)
        db.commit()
        db.refresh(group)

        logger.info(f"Created university group: {university_name}")

        return group

    @staticmethod
    def add_user_to_group(db: Session, user_id: int, university_name: str) -> bool:
        """
        Adiciona usuário ao grupo da sua universidade
        Retorna True se adicionado, False se já era membro
        """
        if not university_name:
            logger.warning(f"User {user_id} has no university, skipping group assignment")
            return False

        # Garantir que o grupo existe
        group = UniversityGroupService.ensure_group_exists(db, university_name)

        # Verificar se já é membro
        existing = db.query(UniversityGroupMember).filter(
            UniversityGroupMember.group_id == group.id,
            UniversityGroupMember.user_id == user_id
        ).first()

        if existing:
            return False

        # Adicionar como membro
        member = UniversityGroupMember(
            group_id=group.id,
            user_id=user_id
        )

        db.add(member)
        db.commit()

        logger.info(f"Added user {user_id} to group {university_name}")

        return True

    @staticmethod
    def remove_user_from_group(db: Session, user_id: int, university_name: str) -> bool:
        """
        Remove usuário do grupo de uma universidade
        Retorna True se removido, False se não era membro
        """
        group = db.query(UniversityGroup).filter(
            UniversityGroup.university_name == university_name
        ).first()

        if not group:
            return False

        member = db.query(UniversityGroupMember).filter(
            UniversityGroupMember.group_id == group.id,
            UniversityGroupMember.user_id == user_id
        ).first()

        if not member:
            return False

        db.delete(member)
        db.commit()

        logger.info(f"Removed user {user_id} from group {university_name}")

        return True

    @staticmethod
    def handle_university_change(
        db: Session,
        user_id: int,
        old_university: str,
        new_university: str
    ):
        """
        Gerencia mudança de universidade do usuário
        Remove do grupo antigo e adiciona ao novo
        """
        # Remover do grupo antigo
        if old_university:
            UniversityGroupService.remove_user_from_group(db, user_id, old_university)

        # Adicionar ao novo grupo
        if new_university:
            UniversityGroupService.add_user_to_group(db, user_id, new_university)

    @staticmethod
    def sync_all_users(db: Session):
        """
        Sincroniza todos os usuários com seus respectivos grupos
        Útil para popular grupos inicialmente ou após migrações
        """
        # Buscar todos os usuários ativos com universidade
        profiles = db.query(Profile).join(User).filter(
            User.is_active == True,
            Profile.university.isnot(None)
        ).all()

        added_count = 0
        universities_created = set()

        for profile in profiles:
            # Garantir que grupo existe
            group = UniversityGroupService.ensure_group_exists(db, profile.university)
            universities_created.add(profile.university)

            # Adicionar usuário
            if UniversityGroupService.add_user_to_group(db, profile.user_id, profile.university):
                added_count += 1

        logger.info(
            f"Synced university groups: {len(universities_created)} groups, "
            f"{added_count} users added"
        )

        return {
            "groups_created": len(universities_created),
            "users_added": added_count
        }

    @staticmethod
    def get_user_group(db: Session, user_id: int):
        """
        Retorna o grupo da universidade do usuário
        """
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if not profile or not profile.university:
            return None

        group = db.query(UniversityGroup).filter(
            UniversityGroup.university_name == profile.university
        ).first()

        return group

    @staticmethod
    def get_group_members_count(db: Session, group_id: int) -> int:
        """
        Retorna número de membros de um grupo
        """
        return db.query(UniversityGroupMember).filter(
            UniversityGroupMember.group_id == group_id
        ).count()

    @staticmethod
    def get_all_groups_with_stats(db: Session):
        """
        Retorna todos os grupos com estatísticas
        """
        groups = db.query(
            UniversityGroup,
            func.count(UniversityGroupMember.user_id).label('member_count')
        ).outerjoin(UniversityGroupMember).group_by(UniversityGroup.id).all()

        result = []
        for group, member_count in groups:
            result.append({
                "id": group.id,
                "university_name": group.university_name,
                "name": group.name,
                "description": group.description,
                "member_count": member_count,
                "created_at": group.created_at
            })

        return result
