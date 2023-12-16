from sqlmodel import Session

from database import SQLMessage, create_db_and_tables, engine

create_db_and_tables()


message1 = SQLMessage(
    session_id=7709, session_idx=2, session_message="hi", message_type="Human"
)


with Session(engine) as session:
    session.add(message1)
    session.commit()
