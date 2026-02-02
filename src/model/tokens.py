from pydantic import BaseModel, ConfigDict


class RuleSchema(BaseModel):
    """Модель одной роли/права."""
    name: str

    model_config = ConfigDict(from_attributes=True)


class RulesSchema(BaseModel):
    """Модель списка ролей пользователя."""
    rules: list[RuleSchema]

    model_config = ConfigDict(from_attributes=True)
