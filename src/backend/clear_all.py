from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
db.query(User).delete()
db.commit()
db.close()
