# Twitter

A simple Twitter-like backend project built with **Django**, **Django REST Framework**, and **MySQL**, containerized with **Docker Compose** for local development.

### Docker Compose
```
docker compose build
docker compose up
docker compose exec -it api bash
```

### Default Credentials

| Service | Username | Password | Email |
| ---- | ---- | ---- | ----- |
| Django Admin | admin | admin | admin@email.com |
| MySQL | root | P@sSw0rD |

### Python 
```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
python manage.py test -v2 # show more details of test
```