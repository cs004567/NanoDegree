#
# Add some sample data to the database.
#
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, CatalogCategory, CatalogItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create a system account for the sample data.
User1 = User(name="System Account", email="sa@localhost")
session.add(User1)
session.commit()

catalogCategory1 = CatalogCategory(name='Basketball')
session.add(catalogCategory1)
session.commit()

catalogItem1 = CatalogItem(name='Basketball',
                           description='NCAA 28.5" Replica Basketball',
                           user_id=1, category=catalogCategory1)
session.add(catalogItem1)
catalogItem2 = CatalogItem(name='Basketball Hoop',
                           description='44 in Portable Polycarbonate \
                               Basketball Hoop', user_id=1,
                           category=catalogCategory1)
session.add(catalogItem2)
session.commit()

catalogCategory2 = CatalogCategory(name='Baseball')
session.add(catalogCategory1)
session.commit()

catalogItem3 = CatalogItem(name='Baseball',
                           description='Recreational Use Baseballs 2-Pack',
                           user_id=1, category=catalogCategory2)
session.add(catalogItem3)
catalogItem4 = CatalogItem(name='Baseball Bat',
                           description='Louisville Slugger Maple Baseball Bat',
                           user_id=1, category=catalogCategory2)
session.add(catalogItem4)
session.commit()

catalogCategory3 = CatalogCategory(name='Soccer')
session.add(catalogCategory1)
session.commit()

catalogItem5 = CatalogItem(name='Soccer Ball',
                           description='Premier League Strike Soccer Ball',
                           user_id=1, category=catalogCategory3)
session.add(catalogItem5)
catalogItem6 = CatalogItem(name='Soccer Goal',
                           description='6.5 ft x 12.5 ft Tournament \
                               Soccer Goal',
                           user_id=1, category=catalogCategory3)
session.add(catalogItem6)
session.commit()

catalogCategory4 = CatalogCategory(name='Golf')
session.add(catalogCategory1)
session.commit()

catalogItem7 = CatalogItem(name='Golf Balls',
                           description='Golf Balls 12-Pack',
                           user_id=1, category=catalogCategory4)
session.add(catalogItem7)
catalogItem8 = CatalogItem(name='Golf Clubs',
                           description='Complete Golf Club Set with Bag',
                           user_id=1, category=catalogCategory4)
session.add(catalogItem8)
session.commit()

catalogCategory5 = CatalogCategory(name='Football')
session.add(catalogCategory1)
session.commit()

catalogItem9 = CatalogItem(name='Football',
                           description='Official Game Ball',
                           user_id=1, category=catalogCategory5)
session.add(catalogItem9)
catalogItem10 = CatalogItem(name='Football Helmet',
                            description='Vengeance Pro Football Helmet',
                            user_id=1, category=catalogCategory5)
session.add(catalogItem10)
session.commit()

catalogCategory6 = CatalogCategory(name='Softball')
session.add(catalogCategory1)
session.commit()

catalogItem11 = CatalogItem(name='Softball Bat',
                            description='Fast-Pitch Softball Bat',
                            user_id=1, category=catalogCategory6)
session.add(catalogItem11)
catalogItem12 = CatalogItem(name='Softball Glove',
                            description='Fast-Pitch Utility Glove',
                            user_id=1, category=catalogCategory6)
session.add(catalogItem12)
session.commit()

catalogCategory7 = CatalogCategory(name='Volleyball')
session.add(catalogCategory1)
session.commit()

catalogItem13 = CatalogItem(name='Volleyball',
                            description='Soft Series Butterfly Volleyball',
                            user_id=1, category=catalogCategory7)
session.add(catalogItem13)
catalogItem14 = CatalogItem(name='Volleyball Equipment',
                            description='Double-Sided Locking Ball Cage',
                            user_id=1, category=catalogCategory7)
session.add(catalogItem14)
session.commit()

catalogCategory8 = CatalogCategory(name='Tennis')
session.add(catalogCategory1)
session.commit()

catalogItem15 = CatalogItem(name='Tennis Racquet',
                            description='Ti S6 Tennis Racquet',
                            user_id=1, category=catalogCategory8)
session.add(catalogItem15)
catalogItem16 = CatalogItem(name='Tennis Ball',
                            description='Hard Court Tennis Balls 3-Pack',
                            user_id=1, category=catalogCategory8)
session.add(catalogItem16)
session.commit()

print "Done adding sample data."
