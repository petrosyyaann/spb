from core.db.session import engine
import models


def create_tables():
    models.base.Base.metadata.create_all(engine)
