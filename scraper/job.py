import enum

from sqlalchemy import Column, Integer, String, DateTime, func, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



# data.title, data.company, data.company_link, data.date, data.link, data.insights
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String(64))
    company = Column(String(64))
    date = Column(DateTime(timezone=True), server_default=func.now())
    apply_link = Column(String(2048))
    type = Column(String(64))

    def __init__(self, title, date, apply_link, company, type):
        self.title = title
        self.date = date
        self.apply_link = apply_link
        self.company = company
        self.type = type
