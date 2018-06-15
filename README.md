# todo-list

To do list with Flask/SQLalchemy

Virtual Environment requirements available in requirements.txt

To use the app, you need to:
  - create the migration repo 
(venv) $ flask db init

  - Migrate and upgrade the db
(venv) $ flask db migrate -m "users table"
(venv) $ flask db upgrade
