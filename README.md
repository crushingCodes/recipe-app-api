# Recipe App API
Followed the tutorial [Build a Backend REST API with Python & Django - Advanced](https://www.udemy.com/share/101XNgA0UfeVpUQHQ=/)

This is a simple API for managing food recipes. It handles ingredients, tags, and recipe images.


***Technologies:***

Python, Django, Django Rest Framework, Docker, Travis CI

## To run it

`docker-compose up
`

## Development

### Building

`docker-compose build
`

### Testing

`docker-compose run --rm app sh -c "python manage.py test && flake8"`

Note: '--rm' causes docker to remove it after running
