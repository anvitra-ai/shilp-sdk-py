"""Shilp Discovery API Client implementation for service discovery and orchestration."""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin

from shilp.models import (
    GenericResponse,
    DiscoveryStats,
    SyncStatus,
    ReplicaType,
    RegisterToDiscoveryRequest,
)


class DiscoveryClient:
    """Client for the Shilp Discovery API."""

    def __init__(self, base_url: str, timeout: int = 30, session: Optional[requests.Session] = None):
        """
        Initialize the Shilp Discovery API client.

        Args:
            base_url: Base URL of the Shilp Discovery server
            timeout: Request timeout in seconds (default: 30)
            session: Optional custom requests.Session instance
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, path)
        
        response = self.session.request(
            method=method,
            url=url,
            json=json_data,
            params=params,
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise requests.HTTPError(
                f"API error: {response.text} (status: {response.status_code})",
                response=response,
            )

        return response.json() if response.content else {}

    def get_shilp_stats(self, account_id: str) -> DiscoveryStats:
        """
        Get statistics for Shilp services.

        Args:
            account_id: Account identifier

        Returns:
            DiscoveryStats with service statistics
        """
        params = {"account_id": account_id}
        data = self._request("GET", "/api/v1/discovery/shilp/stats", params=params)
        
        # Convert the nested structure to DiscoveryStats
        from shilp.models import Status, Replica, ProxyStats
        
        registry_data = data.get("registry", {})
        registry = Status(
            write_replica=Replica(**registry_data.get("write_replica", {})),
            read_replicas=[Replica(**r) for r in registry_data.get("read_replicas", [])],
            available=registry_data.get("available", 0),
            total=registry_data.get("total", 0),
        )
        
        proxy_data = data.get("proxy", {})
        proxy = ProxyStats(
            active_proxies=proxy_data.get("active_proxies", 0),
            targets=proxy_data.get("targets", []),
        )
        
        return DiscoveryStats(registry=registry, proxy=proxy)

    def update_shilp_sync_status(
        self, account_id: str, address: str, status: str
    ) -> GenericResponse:
        """
        Update the sync status of a Shilp service.

        Args:
            account_id: Account identifier
            address: Service address
            status: Sync status (SyncStatus.READY or SyncStatus.SYNCING)

        Returns:
            GenericResponse indicating success or failure
        """
        json_data = {
            "account_id": account_id,
            "address": address,
            "status": status,
        }
        data = self._request("PUT", "/api/v1/discovery/shilp/sync", json_data=json_data)
        return GenericResponse(**data)

    def register_shilp_service(
        self, account_id: str, address: str, service_id: str, replica_type: ReplicaType
    ) -> GenericResponse:
        """
        Register a Shilp service with the discovery system.

        Args:
            account_id: Account identifier
            address: Service address
            service_id: Service identifier
            replica_type: Type of replica (READ_REPLICA, WRITE_REPLICA, or SINGLE_NODE)

        Returns:
            GenericResponse indicating success or failure
        """
        is_read = replica_type == ReplicaType.READ_REPLICA or replica_type == ReplicaType.SINGLE_NODE
        is_write = replica_type == ReplicaType.WRITE_REPLICA or replica_type == ReplicaType.SINGLE_NODE
        
        json_data = {
            "account_id": account_id,
            "address": address,
            "id": service_id,
            "is_read": is_read,
            "is_write": is_write,
        }
        data = self._request("POST", "/api/v1/discovery/shilp/register", json_data=json_data)
        return GenericResponse(**data)

    def unregister_shilp_service(
        self, account_id: str, address: str, service_id: str, replica_type: ReplicaType
    ) -> GenericResponse:
        """
        Unregister a Shilp service from the discovery system.

        Args:
            account_id: Account identifier
            address: Service address
            service_id: Service identifier
            replica_type: Type of replica (READ_REPLICA, WRITE_REPLICA, or SINGLE_NODE)

        Returns:
            GenericResponse indicating success or failure
        """
        is_read = replica_type == ReplicaType.READ_REPLICA or replica_type == ReplicaType.SINGLE_NODE
        is_write = replica_type == ReplicaType.WRITE_REPLICA or replica_type == ReplicaType.SINGLE_NODE
        
        json_data = {
            "account_id": account_id,
            "address": address,
            "id": service_id,
            "is_read": is_read,
            "is_write": is_write,
        }
        data = self._request("DELETE", "/api/v1/discovery/shilp/unregister", json_data=json_data)
        return GenericResponse(**data)

    def register_tei_service(
        self, account_id: str, address: str, service_id: str
    ) -> GenericResponse:
        """
        Register a TEI (Text Embedding Inference) service.

        Args:
            account_id: Account identifier
            address: Service address
            service_id: Service identifier

        Returns:
            GenericResponse indicating success or failure
        """
        json_data = {
            "account_id": account_id,
            "address": address,
            "id": service_id,
        }
        data = self._request("POST", "/api/v1/discovery/tei/register", json_data=json_data)
        return GenericResponse(**data)

    def unregister_tei_service(
        self, account_id: str, address: str, service_id: str
    ) -> GenericResponse:
        """
        Unregister a TEI (Text Embedding Inference) service.

        Args:
            account_id: Account identifier
            address: Service address
            service_id: Service identifier

        Returns:
            GenericResponse indicating success or failure
        """
        json_data = {
            "account_id": account_id,
            "address": address,
            "id": service_id,
        }
        data = self._request("DELETE", "/api/v1/discovery/tei/unregister", json_data=json_data)
        return GenericResponse(**data)
