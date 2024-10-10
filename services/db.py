from sqlalchemy import create_engine, text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


from config import Config as cfg


def test_request():
    base = automap_base()
    engine = create_engine(
        f"mysql+pymysql://{cfg.DATABASE_USER}"
        f":{cfg.DATABASE_PASSWORD}@{cfg.DATABASE_HOST}/{cfg.DATABASE_NAME}?charset=utf8mb4"
    )
    base.prepare(autoload_with=engine)
    contacts = base.classes.contacts
    session = Session(engine)
    print(session)
    data = session.query(contacts).all()

    for d in data:
        print(d.id)

    session.close()


class Duplicates:
    # TODO: нужно создать алгоритм, чтобы определять похожие номера телефонов.
    def __init__(self) -> None:
        base = automap_base()
        self.engine = create_engine(
            f"mysql+pymysql://{cfg.DATABASE_USER}"
            f":{cfg.DATABASE_PASSWORD}@{cfg.DATABASE_HOST}/{cfg.DATABASE_NAME}?charset=utf8mb4"
        )
        base.prepare(autoload_with=self.engine)
        self.companies = base.classes.companies
        self.leads = base.classes.leads
        self.pipelines = base.classes.pipelines

    def company_exists(self, phone_number):
        session = Session(self.engine)
        company = (
            session.query(self.companies)
            .filter(self.companies.Telefon.contains([phone_number]))
            .first()
        )
        session.close()
        if company:
            return True
        else:
            return False

    def is_actual(self, phone_number):
        """
            Проверяем компанию по номеру телефона,
            воронке "телемаркетинг"(id 3644770),
            статусу "закрыто и не реализовано" (id 143).
            Предполагается, что, если такая организация находится, то
            парсер не игнорирует ее при проверке.
        """
        session = Session(self.engine)
        query = (
            session.query(self.companies)
            .join(self.leads, (self.leads.company_id == self.companies.id))
            .filter(self.companies.Telefon.contains([phone_number]))
            .filter(self.leads.pipeline_id == 3644770)
            .filter(self.leads.status_id == 143)
        )
        result = query.first()
        if result:
            return True
        else:
            return False
