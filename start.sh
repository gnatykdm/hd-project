#!/bin/bash

echo "Running Alembic Migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "Migration failed. Check your database connection."
    exit 1
fi

read -p "Do you want to run the database seeder? (y/n): " CHOICE
if [[ "$CHOICE" == "y" || "$CHOICE" == "Y" ]]; then
    echo "Running Faker seed script..."
    python3 -m seed_db
fi

echo "Starting Main Application..."
python3 main.py
