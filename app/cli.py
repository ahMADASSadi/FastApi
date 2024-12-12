from typing import Optional
import subprocess

from datetime import datetime

from sqlmodel import Session, select

from pathlib import Path

from app.models.user_model import User
from app.config.setting import get_engine


def run_subprocess(command: list[str]) -> None:
    try:
        result = subprocess.run(command, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command: {e.stderr.decode()}")
        raise


"""
    Function to create a superuser by prompting for the phone number.
    
    Based on yout preferences you can change and update both this view and the user model,
it will works just fine.
"""
def create_super_user(session: Session):
    """
    Function to create a superuser by prompting for the phone number.
    """
    phone_number = input("Enter Phone number: ")
    role = "admin"

    # Check if a superuser already exists
    existing_user = session.exec(
        select(User).where(User.phone_number == phone_number)
    ).first()
    if existing_user:
        print(f"Superuser with phone number {phone_number} already exists.")
        print("Changing the role to admin")
        existing_user.role = 'admin'
        return

    new_superuser = User(phone_number=phone_number, role=role)
    session.add(new_superuser)
    session.commit()
    session.refresh(new_superuser)
    print(f"Superuser created with phone number: {new_superuser.phone_number}")


# Function to handle Alembic migrations
def migrations(option: Optional[str] = None) -> None:
    from app.config.setting import DATABASE_URL

    alembic_dir = Path("app/config/migrations")
    config_dir = Path("app/config")
    alembic_ini_path = config_dir / "alembic.ini"
    env_py_path = alembic_dir / "env.py"

    # Step 1: Initialize Alembic if migrations folder doesn't exist
    if not alembic_dir.exists():
        print("Initializing Alembic...")
        run_subprocess(["alembic", "init", str(alembic_dir)])

        # Move alembic.ini to app/config
        default_alembic_ini = Path("alembic.ini")
        if default_alembic_ini.exists():
            default_alembic_ini.rename(alembic_ini_path)
            print(f"Moved alembic.ini to {alembic_ini_path}")
        else:
            print("Error: alembic.ini file not found after initialization.")
            return

        print("Alembic initialized.")

    # Step 2: Update alembic.ini with the correct DATABASE_URL
    if alembic_ini_path.exists():
        alembic_ini_content = alembic_ini_path.read_text()
        alembic_ini_content = alembic_ini_content.replace(
            "script_location = app/config/migrations", "script_location = app/config/migrations"
        )
        alembic_ini_content = alembic_ini_content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname", f"sqlalchemy.url = {
                DATABASE_URL}"
        )
        alembic_ini_path.write_text(alembic_ini_content)
        print(f"Updated {alembic_ini_path} with the correct values.")

    # Step 3: Ensure __init__.py files exist
    for directory in [config_dir, alembic_dir]:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"Created {init_file}")

    # Step 4: Update env.py to use SQLModel
    if env_py_path.exists():
        with open(env_py_path, "r") as f:
            env_py_content = f.read()
        if "target_metadata" not in env_py_content or "SQLModel" not in env_py_content:
            updated_env_py = env_py_content.replace(
                "from alembic import context",
                "from alembic import context\nfrom sqlmodel import SQLModel",
            )
            updated_env_py = updated_env_py.replace(
                "target_metadata = None",
                "target_metadata = SQLModel.metadata",
            )
            with open(env_py_path, "w") as f:
                f.write(updated_env_py)
            print(f"Updated {env_py_path} to use SQLModel.")

    # Step 5: Handle migration or makemigrations based on the option
    if option == "makemigrations":
        run_subprocess(["alembic", "-c", str(alembic_ini_path),
                       "revision", "--autogenerate", "-m", f'"{datetime.now().strftime('%Y-%m-%d:%H:%M')}"'])
        print("Finished making migrations!")
    elif option == "migrate":
        run_subprocess(
            ['alembic', "-c", str(alembic_ini_path), 'upgrade', 'head'])
        print("All migrations are done!")


def commands(command: Optional[str]) -> None:
    if command is None:
        return "No command provided."

    commands_dict = {
        "makemigrations": lambda: migrations("makemigrations"),
        "migrate": lambda: migrations("migrate"),
        "createsuperuser": lambda: create_super_user(Session(get_engine())),
    }

    if command in commands_dict:
        commands_dict[command]()  # Call the mapped function
    else:
        print(f"Invalid command: {command}")
