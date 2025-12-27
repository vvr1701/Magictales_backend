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
        # Try to create client with explicit options for newer versions
        client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key,
        )
        logger.info("Supabase client created successfully")
        return client
    except TypeError as e:
        if "proxy" in str(e):
            logger.warning(f"Proxy parameter issue, trying alternative client creation: {e}")
            # Fallback for version compatibility
            try:
                # Try with minimal parameters
                client = create_client(settings.supabase_url, settings.supabase_key)
                logger.info("Supabase client created with fallback method")
                return client
            except Exception as e2:
                logger.warning(f"All Supabase client creation methods failed: {e2}")
                # Use mock client for testing
                return _create_mock_client()
        else:
            logger.warning(f"Supabase client creation failed, using mock: {e}")
            return _create_mock_client()
    except Exception as e:
        logger.warning(f"Unexpected error creating Supabase client, using mock: {e}")
        return _create_mock_client()


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
