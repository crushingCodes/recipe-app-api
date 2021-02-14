# recipe-app-api

##Running

docker-compose up

## Django commands

docker-compose run app sh -c "python manage.py createsuperuser"

###Testing credentials
test@email.com

password

##Testing

[comment]: <> (--rm removes after running)
docker-compose run --rm app sh -docker-compose run app sh -c "python manage.py test && flake8"