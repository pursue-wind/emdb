from .routes import MOVIE_ROUTE, COMPANY_ROUTE

ROUTES = sum([
    COMPANY_ROUTE,
    MOVIE_ROUTE
], [])
