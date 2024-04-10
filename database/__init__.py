import os
from flask import Flask
from string import Template

from database.models import User, db, Role

def get_connection_url():
    base_url = Template(
        "postgresql${engine_name}://" +
        f"{os.environ.get('POSTGRESQL_USER', 'flask_app')}:" +
        f"{os.environ.get('POSTGRESQL_PASSWORD', 'flask_app')}@" +
        f"{os.environ.get('POSTGRESQL_HOST', '10.10.98.56')}:" +
        f"{os.environ.get('POSTGRESQL_PORT', '5432')}/" +
        f"{os.environ.get('POSTGRESQL_DATABASE', 'flask_app')}")
    return base_url.substitute(
        engine_name="+psycopg2")    # Use psycopg2 driver


def create_all_tables():
    """
    Create all tables in the database.
    """
    db.create_all()


def add_role_table():
    """
    Function to add admin and user roles to the Role table if they do not already exist.
    Returns the admin role after adding it to the table.
    """
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        db.session.add(admin_role)
        db.session.commit()

    user_role = Role.query.filter_by(name="user").first()
    if not user_role:
        user_role = Role(name="user", description="Regular user role")
        db.session.add(user_role)
        db.session.commit()

    return admin_role


def add_admin_user():
    """
    Generate a new admin user if one does not already exist in the database.
    """
    admin_role = add_role_table()
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(username="admin",
                          password="admin123",
                          email="admin@example.com",
                          role_id=admin_role.id)
        db.session.add(admin_user)
        db.session.commit()

def setup_db(app: Flask):
    """
    Set up the database for the Flask app.

    Parameters:
    - app (Flask): The Flask app object.

    Returns:
    None
    """
    if not app.config.get('SQLALCHEMY_DATABASE_URI', None):
        app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_url()
    db.init_app(app)
    with app.app_context():
        create_all_tables()
        add_admin_user()
