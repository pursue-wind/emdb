from .routes import MOVIE_ROUTE, COMPANY_ROUTE, EMMAI_ROUTE

ROUTES = sum([
    COMPANY_ROUTE,
    MOVIE_ROUTE,
    EMMAI_ROUTE
], [])
