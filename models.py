from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.String, primary_key=True)
    fin = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    pass_type = db.Column(db.String, nullable=False)
    doa = db.Column(db.String, nullable=False)
    company_uen = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    doe = db.Column(db.String, nullable=False)

class Amendment(db.Model):
    __tablename__ = 'amendments'
    amendment_id = db.Column(db.String, primary_key=True)
    application_id = db.Column(db.String, db.ForeignKey('applications.id'), nullable=False)
    amendment_date = db.Column(db.String, nullable=False)
    original_value = db.Column(db.String, nullable=False)
    amended_value = db.Column(db.String, nullable=False)

class STVP(db.Model):
    __tablename__ = 'stvps'
    id = db.Column(db.String, primary_key=True)
    application_id = db.Column(db.String, db.ForeignKey('applications.id'), nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)