"""seed_statuses

Revision ID: a1b2c3d4e5f6
Revises: d7227b385958
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '01466aad413a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STATUSES = ('Новая', 'В работе', 'На проверке', 'Завершена')


def upgrade() -> None:
    """Seed reference statuses."""
    op.execute(
        "INSERT INTO status (name) VALUES "
        + ", ".join(f"('{s}')" for s in STATUSES)
        + " ON CONFLICT (name) DO NOTHING"
    )


def downgrade() -> None:
    """Remove seeded statuses."""
    names = ", ".join(f"'{s}'" for s in STATUSES)
    op.execute(f"DELETE FROM status WHERE name IN ({names})")
