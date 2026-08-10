"""Add rainfall and water-level telemetry fields.

Revision ID: 9e4ab67d4a2e
Revises: 30255f4e6992
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9e4ab67d4a2e"
down_revision: Union[str, None] = "30255f4e6992"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("sensor_readings", schema=None) as batch_op:
        batch_op.add_column(sa.Column("rainfall", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("water_level", sa.Float(), nullable=True))
        batch_op.create_check_constraint("chk_rainfall_range", "rainfall >= 0")
        batch_op.create_check_constraint("chk_water_level_range", "water_level BETWEEN 0 AND 100")


def downgrade() -> None:
    with op.batch_alter_table("sensor_readings", schema=None) as batch_op:
        batch_op.drop_constraint("chk_water_level_range", type_="check")
        batch_op.drop_constraint("chk_rainfall_range", type_="check")
        batch_op.drop_column("water_level")
        batch_op.drop_column("rainfall")
