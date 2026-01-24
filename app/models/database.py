"""
Supabase database client.
"""

from supabase import create_client, Client
from functools import lru_cache
from app.config import get_settings
import structlog

logger = structlog.get_logger()


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    settings = get_settings()

    try:
        # Try the Supabase library first
        client = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase client created successfully")
        return client
    except Exception as e:
        logger.warning(f"Supabase library failed, using REST client: {e}")
        # Use REST-based client that works with any Supabase version
        return _create_rest_client()


def _create_rest_client():
    """Create a REST-based Supabase client that works without library compatibility issues."""
    logger.info("Creating REST-based Supabase client")

    import requests
    from app.config import get_settings

    settings = get_settings()

    class RestSupabaseResponse:
        def __init__(self, data=None, error=None):
            self.data = data or []
            self.error = error
            self.count = len(self.data) if self.data else 0

    class RestSupabaseQuery:
        def __init__(self, table_name, base_url, headers):
            self.table_name = table_name
            self.base_url = base_url
            self.headers = headers
            self._filters = []
            self._select_fields = "*"
            self._limit_count = None
            self._order_field = None
            self._order_desc = False
            self._count_mode = None

        def select(self, *args, count=None):
            # Handle both select("col1", "col2") and select("col1,col2") formats
            if len(args) == 0:
                self._select_fields = "*"
            elif len(args) == 1:
                self._select_fields = args[0]
            else:
                # Multiple arguments - join them with commas
                self._select_fields = ",".join(args)
            self._count_mode = count  # "exact", "planned", or "estimated"
            return self

        def eq(self, column, value):
            self._filters.append(f"{column}=eq.{value}")
            return self

        def neq(self, column, value):
            self._filters.append(f"{column}=neq.{value}")
            return self

        def gt(self, column, value):
            self._filters.append(f"{column}=gt.{value}")
            return self

        def gte(self, column, value):
            self._filters.append(f"{column}=gte.{value}")
            return self

        def lt(self, column, value):
            self._filters.append(f"{column}=lt.{value}")
            return self

        def lte(self, column, value):
            self._filters.append(f"{column}=lte.{value}")
            return self

        def is_(self, column, value):
            # Convert Python None to PostgREST 'null'
            if value is None:
                value = "null"
            elif value is True:
                value = "true"
            elif value is False:
                value = "false"
            self._filters.append(f"{column}=is.{value}")
            return self

        def in_(self, column, values):
            """Filter where column value is in a list of values."""
            if not values:
                # Empty list - return no results by using impossible filter
                self._filters.append(f"{column}=eq.__empty__")
                return self
            # PostgREST format: column=in.(val1,val2,val3)
            values_str = ",".join(str(v) for v in values)
            self._filters.append(f"{column}=in.({values_str})")
            return self

        def limit(self, count):
            self._limit_count = count
            return self

        def order(self, field, desc=False):
            self._order_field = field
            self._order_desc = desc
            return self

        def execute(self):
            """Execute the query via REST API."""
            try:
                # Handle insert operations
                if hasattr(self, '_is_insert') and self._is_insert:
                    url = f"{self.base_url}/rest/v1/{self.table_name}"
                    headers = {**self.headers, "Prefer": "return=representation"}

                    response = requests.post(url, json=self._insert_data, headers=headers, timeout=30)

                    if response.status_code in [200, 201]:
                        try:
                            if response.text.strip():
                                result_data = response.json()
                                if isinstance(result_data, list):
                                    return RestSupabaseResponse(data=result_data)
                                else:
                                    return RestSupabaseResponse(data=[result_data])
                            else:
                                # Empty response, return inserted data with mock ID
                                mock_data = {**self._insert_data, "id": f"rest-{hash(str(self._insert_data)) % 10000}"}
                                return RestSupabaseResponse(data=[mock_data])
                        except Exception as parse_error:
                            logger.warning(f"JSON parse error, returning mock data: {parse_error}")
                            mock_data = {**self._insert_data, "id": f"rest-{hash(str(self._insert_data)) % 10000}"}
                            return RestSupabaseResponse(data=[mock_data])
                    else:
                        logger.error(f"REST insert failed: {response.status_code} - {response.text}")
                        return RestSupabaseResponse(error=f"HTTP {response.status_code}: {response.text}")

                # Handle update operations
                elif hasattr(self, '_is_update') and self._is_update:
                    url = f"{self.base_url}/rest/v1/{self.table_name}"
                    headers = {**self.headers, "Prefer": "return=representation"}

                    # Add filters to URL params for WHERE clause (PostgREST format)
                    params = {}
                    if self._filters:
                        for filter_expr in self._filters:
                            if "=" in filter_expr:
                                # Split on first = to get column=eq.value
                                column, operator_value = filter_expr.split("=", 1)
                                params[column] = operator_value

                    response = requests.patch(url, json=self._update_data, headers=headers, params=params, timeout=30)

                    if response.status_code in [200, 204]:
                        try:
                            if response.text.strip():
                                result_data = response.json()
                                if isinstance(result_data, list):
                                    return RestSupabaseResponse(data=result_data)
                                else:
                                    return RestSupabaseResponse(data=[result_data])
                            else:
                                # No response data, return success
                                return RestSupabaseResponse(data=[])
                        except Exception:
                            return RestSupabaseResponse(data=[])
                    else:
                        logger.error(f"REST update failed: {response.status_code} - {response.text}")
                        return RestSupabaseResponse(error=f"HTTP {response.status_code}: {response.text}")

                # Handle select operations
                else:
                    # Build query parameters
                    params = {"select": self._select_fields}

                    # Add filters as query parameters (PostgREST format)
                    if self._filters:
                        for filter_expr in self._filters:
                            if "=" in filter_expr:
                                # Split on first = to get column=eq.value
                                column, operator_value = filter_expr.split("=", 1)
                                params[column] = operator_value

                    if self._limit_count:
                        params["limit"] = self._limit_count

                    if self._order_field:
                        order_val = f"{self._order_field}.desc" if self._order_desc else self._order_field
                        params["order"] = order_val

                    # Handle count mode - add Prefer header
                    request_headers = self.headers.copy()
                    if self._count_mode:
                        request_headers["Prefer"] = f"count={self._count_mode}"

                    # Make request
                    url = f"{self.base_url}/rest/v1/{self.table_name}"
                    response = requests.get(url, headers=request_headers, params=params, timeout=30)

                    if response.status_code in [200, 206]:
                        data = response.json()

                        # Parse count from Content-Range header if present
                        # Format: "0-9/100" where 100 is total count
                        count = len(data) if data else 0
                        content_range = response.headers.get("Content-Range", "")
                        if "/" in content_range:
                            try:
                                count = int(content_range.split("/")[-1])
                            except (ValueError, IndexError):
                                pass

                        result = RestSupabaseResponse(data=data)
                        result.count = count
                        return result
                    else:
                        logger.error(f"REST query failed: {response.status_code} - {response.text}")
                        return RestSupabaseResponse(error=f"HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"REST operation exception: {str(e)}")
                return RestSupabaseResponse(error=str(e))

        def single(self):
            """Execute query expecting single result."""
            result = self.execute()
            if result.data and len(result.data) > 0:
                return RestSupabaseResponse(data=result.data[0])
            return RestSupabaseResponse(data={})

    class RestSupabaseTable:
        def __init__(self, name, base_url, headers):
            self.name = name
            self.base_url = base_url
            self.headers = headers

        def select(self, *args):
            return RestSupabaseQuery(self.name, self.base_url, self.headers).select(*args)

        def insert(self, data):
            """Insert data via REST API."""
            query = RestSupabaseQuery(self.name, self.base_url, self.headers)
            query._insert_data = data
            query._is_insert = True
            return query

        def update(self, data):
            query = RestSupabaseQuery(self.name, self.base_url, self.headers)
            query._update_data = data
            query._is_update = True
            return query

        def delete(self):
            query = RestSupabaseQuery(self.name, self.base_url, self.headers)
            query._is_delete = True
            return query

    class RestSupabaseClient:
        def __init__(self):
            self.base_url = settings.supabase_url
            self.headers = {
                'apikey': settings.supabase_key,
                'Authorization': f'Bearer {settings.supabase_key}',
                'Content-Type': 'application/json'
            }

        def table(self, name):
            return RestSupabaseTable(name, self.base_url, self.headers)

        def rpc(self, function_name, params=None):
            """Call stored procedure via REST."""
            try:
                url = f"{self.base_url}/rest/v1/rpc/{function_name}"
                response = requests.post(url, json=params or {}, headers=self.headers, timeout=30)

                if response.status_code == 200:
                    return RestSupabaseResponse(data=response.json())
                else:
                    return RestSupabaseResponse(error=f"HTTP {response.status_code}")

            except Exception as e:
                return RestSupabaseResponse(error=str(e))

    return RestSupabaseClient()


def _create_mock_client():
    """Create a mock Supabase client for testing."""
    logger.info("Creating mock Supabase client for testing")

    class MockSupabaseResponse:
        def __init__(self, data=None, error=None):
            self.data = data or []
            self.error = error
            self.count = len(self.data) if self.data else 0

    class MockSupabaseTable:
        def __init__(self, name):
            self.name = name

        def insert(self, data):
            logger.info(f"Mock insert into {self.name}: {data}")
            # Return a query object that will return the data when executed
            mock_data = {**data, "id": f"mock-{hash(str(data)) % 10000}"}
            query = MockSupabaseQuery(self.name)
            query._insert_data = [mock_data]
            return query

        def select(self, columns="*"):
            return MockSupabaseQuery(self.name)

        def eq(self, column, value):
            return MockSupabaseQuery(self.name)

        def update(self, data):
            logger.info(f"Mock update on {self.name}: {data}")
            return MockSupabaseQuery(self.name)

        def delete(self):
            logger.info(f"Mock delete on {self.name}")
            return MockSupabaseQuery(self.name)

    class MockSupabaseQuery:
        def __init__(self, table_name):
            self.table_name = table_name
            self._insert_data = None

        def eq(self, column, value):
            return self

        def execute(self):
            logger.info(f"Mock query executed on {self.table_name}")
            # Return insert data if available, otherwise empty result
            data = self._insert_data if self._insert_data is not None else []
            return MockSupabaseResponse(data=data)

        def single(self):
            logger.info(f"Mock single query executed on {self.table_name}")
            return MockSupabaseResponse(data={})

        def limit(self, count):
            return self

        def order(self, column, desc=False):
            return self

    class MockSupabaseClient:
        def table(self, name):
            return MockSupabaseTable(name)

        def rpc(self, function_name, params=None):
            logger.info(f"Mock RPC call: {function_name} with params: {params}")
            return MockSupabaseResponse(data={"success": True})

    return MockSupabaseClient()


def get_db() -> Client:
    """Get Supabase database client."""
    return get_supabase_client()
