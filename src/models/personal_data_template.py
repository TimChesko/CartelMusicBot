from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import PersonalDataTemplate


class PersonalDataTemplateHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def get_template_by_id(self, template_id: int) -> PersonalDataTemplate:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalDataTemplate).where(PersonalDataTemplate.id == template_id)
                result = await session.execute(query)
                template = result.scalar_one_or_none()
                return template
            except SQLAlchemyError as e:
                self.logger.error(f"Error occurred during query execution: {e}")
                return None

    async def get_all_templates(self) -> list[PersonalDataTemplate]:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalDataTemplate)
                result = await session.execute(query)
                templates = result.scalars().all()
                return templates
            except SQLAlchemyError as e:
                self.logger.error(f"Error occurred during query execution: {e}")
                return None

    async def get_all_args_by_header_data(self, header_data: str) -> list[PersonalDataTemplate]:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(
                    PersonalDataTemplate.name_data,
                    PersonalDataTemplate.text,
                    PersonalDataTemplate.example,
                    PersonalDataTemplate.input_type
                ).where(PersonalDataTemplate.header_data == header_data)\
                    .order_by(PersonalDataTemplate.id)
                result = await session.execute(query)
                return result
            except SQLAlchemyError as e:
                self.logger.error(f"Error occurred during query execution: {e}")
                return None

    async def update_template(self, template_id: int, new_data: dict) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(PersonalDataTemplate).where(PersonalDataTemplate.id == template_id).values(**new_data)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Error occurred during query execution: {e}")
                await session.rollback()
                return False

    async def add_template(self, template: PersonalDataTemplate) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                session.add(template)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового шаблона: %s", e)
                await session.rollback()
                return False
