# create_message_table.py
from app import app, db  # import your Flask app and db

class Projects(db.Model):
    __tablename__ = "projects"   # give it its own table name
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255))  # path/URL to project image
    title = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(255))
    source_code = db.Column(db.String(255))  # GitHub or repo link

# Use application context to safely create the table
with app.app_context():
    db.create_all()  # only creates missing tables
    print("Projects table created successfully!")
