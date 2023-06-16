echo $(ls)
alembic -c alembic.ini upgrade head
hypercorn src/main:app --bind 0.0.0.0:8002 --reload
