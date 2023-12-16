from sqlmodel import Session, SQLModel, create_engine

from dataformats import SQLMessage

message1 = SQLMessage(
    session_id=777, session_idx=1, session_message="hi", message_type="Human"
)

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(message1)
    session.commit()
