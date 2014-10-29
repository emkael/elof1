from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.types import Boolean, Date, Float, Integer, String

Base = declarative_base()


class Driver(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True)
    driver = Column(String(1024))
    country = Column(String(255))

    rankings = relationship(
        'Ranking',
        order_by='Ranking.rank_date',
        back_populates='driver',
        cascade="all",
        passive_deletes=True)

    def __repr__(self):
        return (u"<%s (#%d)>" % (self.driver, self.id)).encode('utf8')

    def get_ranking(self, rank_date=None):
        ranks = self.rankings
        if rank_date is not None:
            ranks = [r for r in ranks if r.rank_date <= rank_date]
        if len(ranks):
            return ranks[-1]
        return None

    @staticmethod
    def fetch(name, country, session):
        driver = session.query(Driver).filter(Driver.driver == name).first()
        if not driver:
            driver = Driver()
            driver.driver = name
            driver.country = country
            session.add(driver)
        return driver

driver_entry = Table('driver_entries', Base.metadata,
                     Column(
                     '_driver',
                     Integer,
                     ForeignKey(
                         'drivers.id',
                         onupdate="CASCADE",
                         ondelete="CASCADE")),
                     Column(
                     '_entry',
                     Integer,
                     ForeignKey(
                         'entries.id',
                         onupdate="CASCADE",
                         ondelete="CASCADE")),
                     Column('id', Integer, primary_key=True))


class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    result = Column(String(255))
    car_no = Column(String(255))
    result_group = Column(Integer)

    _race = Column(
        Integer,
        ForeignKey(
            'races.id',
            onupdate="CASCADE",
            ondelete="CASCADE"))
    race = relationship(
        'Race',
        back_populates='entries',
        order_by=result_group)

    drivers = relationship(
        'Driver',
        secondary=driver_entry,
        cascade="all",
        passive_deletes=True)

    def __repr__(self):
        return ('#%s (%s) %s[%d]' % (self.car_no, ', '.join([driver.__repr__().decode('utf8') for driver in self.drivers]), self.result, self.result_group)).encode('utf8')


class Race(Base):
    __tablename__ = 'races'

    id = Column(Integer, primary_key=True)
    race = Column(String(1024))
    date = Column(Date)
    ranked = Column(Boolean, nullable=False, server_default='0', default=False)

    _type = Column(
        Integer,
        ForeignKey(
            'race_types.id',
            onupdate="CASCADE",
            ondelete="CASCADE"))
    type = relationship(
        'RaceType',
        back_populates='races',
        order_by='Race.date')

    entries = relationship(
        'Entry',
        back_populates='race',
        order_by='Entry.result_group',
        cascade="all",
        passive_deletes=True)

    def __repr__(self):
        return ('%s (%s)' % (self.race, self.date)).encode('utf8')


class RaceType(Base):
    __tablename__ = 'race_types'

    id = Column(Integer, primary_key=True)
    code = Column(String(255))
    description = Column(String(1024))

    races = relationship(
        'Race',
        back_populates='type',
        cascade="all",
        passive_deletes=True)

    def __repr__(self):
        return ('%s (%s)' % (self.description, self.code)).encode('utf8')


class Ranking(Base):
    __tablename__ = 'rankings'

    id = Column(Integer, primary_key=True)
    rank_date = Column(Date)
    ranking = Column(Float)

    _driver = Column(
        Integer,
        ForeignKey(
            'drivers.id',
            onupdate="CASCADE",
            ondelete="CASCADE"))
    driver = relationship(
        'Driver',
        back_populates='rankings',
     order_by=rank_date)

    def __repr__(self):
        return ("%s: %0.2f (%s)" % (self.driver.__repr__().decode('utf8'), self.ranking, self. rank_date)).encode('utf8')


__all__ = ['Driver', 'Entry', 'Ranking', 'Race', 'RaceType']
