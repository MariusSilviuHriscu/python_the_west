from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from the_west_inner.quest_requirements import Quest_requirement,Quest_requirement_travel

Base = declarative_base()

class Quest(Base):
    __tablename__ = 'quests'

    quest_id = Column(Integer, primary_key=True)
    quest_group = Column(String)
    quest_name = Column(String)
    requirements = relationship('Requirement', back_populates='quest')

class Requirement(Base):
    __tablename__ = 'requirements'

    requirement_id = Column(Integer, primary_key=True)
    quest_id = Column(Integer, ForeignKey('quests.quest_id'))
    type = Column(String)
    solved = Column(Boolean)

    quest = relationship('Quest', back_populates='requirements')

# Database connection setup
engine = create_engine('sqlite:///quest_database.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def insert_quest_requirement(quest_group: str, quest_id: int, requirement_instance: Quest_requirement):
    quest = session.query(Quest).filter_by(quest_id=quest_id, quest_group=quest_group).first()

    if not quest:
        quest = Quest(quest_id=quest_id, quest_group=quest_group)
        session.add(quest)

    requirement_data = Requirement(type=type(requirement_instance).__name__,
                                   solved=requirement_instance.solved,
                                   quest=quest)

    session.add(requirement_data)
    session.commit()

def retrieve_requirements(quest_group: str, quest_id: int, quest_requirement_classes):
    quest = session.query(Quest).filter_by(quest_id=quest_id, quest_group=quest_group).first()

    if quest:
        requirements = []
        for requirement_data in quest.requirements:
            requirement_class = next((cls for cls in quest_requirement_classes if cls.__name__ == requirement_data.type), None)
            if requirement_class:
                requirement_instance = requirement_class(**requirement_data.__dict__)
                requirements.append(requirement_instance)

        return requirements

    return None

if __name__ == '__main__':
    # Example usage:
    quest_requirement_instance = Quest_requirement_travel(x=10, y=20, employer_key="merchant", quest_id=1, solved=False)
    insert_quest_requirement(quest_group='adventure', quest_id=1, requirement_instance=quest_requirement_instance)
    
    # Retrieve requirements and print their attributes
    retrieved_requirements = retrieve_requirements(quest_group='adventure', quest_id=1, quest_requirement_classes=[Quest_requirement_travel])
    if retrieved_requirements:
        for requirement in retrieved_requirements:
            print(f"Requirement Type: {type(requirement).__name__}, Solved: {requirement.solved}, X: {requirement.x}, Y: {requirement.y}, Employer Key: {requirement.employer_key}")
