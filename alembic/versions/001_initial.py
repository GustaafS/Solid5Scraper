"""initial

Revision ID: 001
Revises: 
Create Date: 2024-03-26 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create municipalities table
    op.create_table(
        'municipalities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('vacancy_page_url', sa.String(length=512), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('last_scraped', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_municipalities_id'), 'municipalities', ['id'], unique=False)
    op.create_index(op.f('ix_municipalities_name'), 'municipalities', ['name'], unique=True)

    # Create vacancies table
    op.create_table(
        'vacancies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('municipality', sa.String(length=255), nullable=False),
        sa.Column('salary_scale', sa.String(length=50), nullable=True),
        sa.Column('education_level', postgresql.ENUM('MBO', 'HBO', 'WO', 'OTHER', name='educationlevel'), nullable=True),
        sa.Column('function_category', postgresql.ENUM('IT', 'FINANCE', 'HR', 'DATA', 'MANAGEMENT', 'OTHER', name='functioncategory'), nullable=True),
        sa.Column('publication_date', sa.DateTime(), nullable=True),
        sa.Column('closing_date', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=512), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('municipality_id', sa.Integer(), nullable=True),
        sa.Column('data_tools', sa.String(length=255), nullable=True),
        sa.Column('data_experience_years', sa.Integer(), nullable=True),
        sa.Column('data_certifications', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['municipality_id'], ['municipalities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vacancies_id'), 'vacancies', ['id'], unique=False)
    op.create_index(op.f('ix_vacancies_url'), 'vacancies', ['url'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_vacancies_url'), table_name='vacancies')
    op.drop_index(op.f('ix_vacancies_id'), table_name='vacancies')
    op.drop_table('vacancies')
    
    op.drop_index(op.f('ix_municipalities_name'), table_name='municipalities')
    op.drop_index(op.f('ix_municipalities_id'), table_name='municipalities')
    op.drop_table('municipalities')
    
    # Drop enums
    op.execute('DROP TYPE educationlevel')
    op.execute('DROP TYPE functioncategory') 