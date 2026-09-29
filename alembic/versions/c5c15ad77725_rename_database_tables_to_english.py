"""rename database tables to English

Revision ID: c5c15ad77725
Revises:
Create Date: 2026-09-29 13:56:45.171409
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c5c15ad77725"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Yeni İngilizce tabloları oluştur

    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50)),
        sa.Column("province", sa.String(length=50)),
        sa.Column("installed_power_mw", sa.Numeric(10, 2)),
        sa.Column("commissioning_year", sa.Integer()),
        sa.Column("plant_code", sa.String(length=50)),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "technicians",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("specialization", sa.String(length=100)),
        sa.Column("technician_code", sa.String(length=50)),
        sa.Column("main_plant_code", sa.String(length=50)),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "fault_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_code"),
    )

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_code", sa.String(length=50), nullable=False),
        sa.Column("plant_id", sa.Integer()),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50)),
        sa.Column("criticality", sa.String(length=20)),
        sa.Column("plant_code", sa.String(length=50)),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("equipment_code"),
    )

    op.create_table(
        "faults",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_uuid", postgresql.UUID(as_uuid=True)),
        sa.Column("equipment_id", sa.Integer()),
        sa.Column("category_id", sa.Integer()),
        sa.Column("technician_id", sa.Integer()),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'ACIK'"),
        ),
        sa.Column(
            "priority",
            sa.String(length=20),
            server_default=sa.text("'ORTA'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["fault_categories.id"]),
        sa.ForeignKeyConstraint(["technician_id"], ["technicians.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Eski tablolardaki verileri yeni tablolara aktar

    op.execute("""
        INSERT INTO plants
        (
            id,
            name,
            type,
            province,
            installed_power_mw,
            commissioning_year,
            plant_code
        )
        SELECT
            id,
            ad,
            tip,
            il,
            kurulu_guc_mw,
            devreye_alma_yili,
            santral_kodu
        FROM santraller
    """)

    op.execute("""
        INSERT INTO technicians
        (
            id,
            full_name,
            specialization,
            technician_code,
            main_plant_code
        )
        SELECT
            id,
            ad_soyad,
            uzmanlik,
            tekniker_kodu,
            ana_santral
        FROM teknikerler
    """)

    op.execute("""
        INSERT INTO fault_categories
        (
            id,
            category_code,
            name,
            description
        )
        SELECT
            id,
            kategori_kodu,
            ad,
            aciklama
        FROM ariza_kategorileri
    """)

    op.execute("""
        INSERT INTO equipment
        (
            id,
            equipment_code,
            plant_id,
            name,
            type,
            criticality,
            plant_code
        )
        SELECT
            id,
            ekipman_kodu,
            santral_id,
            ad,
            tip,
            kritiklik,
            santral_kodu
        FROM ekipmanlar
    """)

    op.execute("""
        INSERT INTO faults
        (
            id,
            client_uuid,
            equipment_id,
            category_id,
            technician_id,
            title,
            description,
            status,
            priority,
            created_at,
            updated_at
        )
        SELECT
            id,
            client_uuid,
            ekipman_id,
            kategori_id,
            tekniker_id,
            baslik,
            aciklama,
            durum,
            oncelik,
            olusturma_tarihi,
            guncelleme_tarihi
        FROM arizalar
    """)

    # 3. Eski Türkçe tabloları sil

    op.drop_table("arizalar")
    op.drop_table("ekipmanlar")
    op.drop_table("ariza_kategorileri")
    op.drop_table("teknikerler")
    op.drop_table("santraller")


def downgrade() -> None:
    # Bu migration geri alınmayacak şekilde veri taşıdığı için
    # downgrade işlemi bilinçli olarak uygulanmıyor.
    raise NotImplementedError(
        "This migration moves data from Turkish tables to English tables "
        "and is not automatically reversible."
    )