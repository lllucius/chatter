"""Middleware to handle undefined query parameters."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse


class UndefinedQueryParamMiddleware(BaseHTTPMiddleware):
    """
    Middleware that converts 'undefined' string values in query parameters to empty strings,
    which allows FastAPI to use default values instead of failing validation.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and convert 'undefined' query parameters."""
        
        # Parse the URL
        parsed_url = urlparse(str(request.url))
        
        if parsed_url.query:
            # Parse query parameters
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            
            # Convert 'undefined' values to empty strings (which will be treated as None)
            modified = False
            cleaned_params = {}
            
            for key, values in query_params.items():
                cleaned_values = []
                for value in values:
                    if value == "undefined":
                        # Remove the parameter entirely by not adding it
                        modified = True
                    else:
                        cleaned_values.append(value)
                
                # Only add the parameter if it has values after filtering
                if cleaned_values:
                    cleaned_params[key] = cleaned_values
            
            # If we modified the query params, update the request URL
            if modified:
                # Build new query string
                new_query = urlencode(cleaned_params, doseq=True)
                
                # Create new URL
                new_parsed = parsed_url._replace(query=new_query)
                new_url = urlunparse(new_parsed)
                
                # Update the request URL
                request._url = new_url
                # Also update the raw query string for FastAPI
                request.scope["query_string"] = new_query.encode()
        
        # Continue with the request
        response = await call_next(request)
        return response