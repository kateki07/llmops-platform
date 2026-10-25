"""给 app 表补上 id / created_at / updated_at 的默认值

第1周的初始化迁移把 app 表建成了「三列都没有默认值」的样子（当时课程还在
Python 侧写死 app_id，也没有新建应用的入口，所以一直没暴露）。后面的迁移把
id 的类型改成了 uuid，但没补默认值 —— 结果从第10周前端能新建应用开始，
POST /apps 必然炸：

    null value in column "id" of relation "app" violates not-null constraint
    null value in column "updated_at" of relation "app" violates not-null constraint

库里其他 21 张表都有默认值（id → uuid_generate_v4()，两个时间戳 →
CURRENT_TIMESTAMP(0)），只有 app 这一张漏了，这里补齐，和模型定义对上。

Revision ID: b1f3c0a7e2d4
Revises: a5086d2a507c
"""
from alembic import op

revision = "b1f3c0a7e2d4"
down_revision = "a5086d2a507c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE app ALTER COLUMN id SET DEFAULT uuid_generate_v4()")
    op.execute("ALTER TABLE app ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP(0)")
    op.execute("ALTER TABLE app ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP(0)")


def downgrade():
    op.execute("ALTER TABLE app ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE app ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE app ALTER COLUMN id DROP DEFAULT")
