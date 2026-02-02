from src.model.!!!users import UserBaseWithPasswordAndEmail
from src.repository.update.!!!users import UserRepository

class UserService:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user_by_login(self, username: str) -> UserBaseWithPasswordAndEmail:
        user = await self.user_repo.get_user_by_login(username)
        result = UserBaseWithPasswordAndEmail.model_validate(status)

        return UserBaseWithEmail(id=result.id, username=result.username, email=result.email)

get_available_rules_for_user

get_user_by_login

get_user_by_user_id

create_user_with_rules