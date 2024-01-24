from sqlalchemy import create_engine, Column, Integer, Float, DateTime, func , extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import matplotlib.pyplot as plt

from the_west_inner.marketplace_buy import Marketplace_offer_list

Base = declarative_base()

class MarketplaceOffer(Base):
    __tablename__ = 'marketplace_offers'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    item_price_per_unit = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MarketplaceDataAnalyser:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_offers_to_database(self, offers_list : Marketplace_offer_list):
        with self.Session() as session:
            for offer in offers_list:
                marketplace_offer = MarketplaceOffer(
                    item_id=offer.item_id,
                    item_price_per_unit=offer.item_price_per_unit
                )
                session.add(marketplace_offer)
            session.commit()

    def calculate_average_price(self, item_id):
        with self.Session() as session:
            average_price = session.query(func.avg(MarketplaceOffer.item_price_per_unit)).filter_by(item_id=item_id).scalar()
        return average_price

    def eliminate_outliers(self, item_id, threshold):
        average_price = self.calculate_average_price(item_id)
        upper_limit = average_price * threshold
        with self.Session() as session:
            session.query(MarketplaceOffer).filter(MarketplaceOffer.item_id == item_id, MarketplaceOffer.item_price_per_unit > upper_limit).delete()

    def create_item_tendency_graph(self, item_id):
        with self.Session() as session:
            offers = session.query(MarketplaceOffer.timestamp, MarketplaceOffer.item_price_per_unit).filter_by(item_id=item_id).all()

        timestamps, prices = zip(*offers)

        plt.plot(timestamps, prices, label=f'Item {item_id} Prices')
        plt.xlabel('Timestamp')
        plt.ylabel('Price per Unit')
        plt.title('Item Tendency Graph')
        plt.legend()
        plt.show()

    def limited_time_analysis(self, item_id, start_date, end_date):
        with self.Session() as session:
            offers = session.query(MarketplaceOffer).filter(
                MarketplaceOffer.item_id == item_id,
                MarketplaceOffer.timestamp >= start_date,
                MarketplaceOffer.timestamp <= end_date
            ).all()

        if not offers:
            print("No offers found within the specified time range.")
            return

        # Extract day, month, and year from the timestamp
        days = [offer.timestamp.day for offer in offers]
        months = [offer.timestamp.month for offer in offers]
        years = [offer.timestamp.year for offer in offers]

        # Perform analysis based on your specific requirements
        average_price = sum(offer.item_price_per_unit for offer in offers) / len(offers)

        print(f"Analysis for Item {item_id} within the time range:")
        print(f"Number of offers: {len(offers)}")
        print(f"Average price per unit: {average_price}")
        print(f"Day with the most offers: {max(set(days), key=days.count)}")
        print(f"Month with the most offers: {max(set(months), key=months.count)}")
        print(f"Year with the most offers: {max(set(years), key=years.count)}")
