"""Initial schema - servers table

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE server_state AS ENUM ('active', 'offline', 'retired');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create servers table
    op.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id SERIAL PRIMARY KEY,
            hostname VARCHAR(255) NOT NULL UNIQUE,
            ip_address INET,
            state server_state NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS servers;")
    op.execute("DROP TYPE IF EXISTS server_state;")
