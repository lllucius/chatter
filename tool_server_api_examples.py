"""
Tool Server API Examples

This file contains comprehensive examples of using the tool server API endpoints.
These examples demonstrate all the functionality including CRUD operations,
analytics, health monitoring, and bulk operations.
"""


import requests

# Base configuration
API_BASE_URL = "http://localhost:8000/api/v1"
AUTH_HEADERS = {
    "Authorization": "Bearer your_jwt_token_here",
    "Content-Type": "application/json"
}


def create_tool_server_example():
    """Example: Create a new tool server"""

    server_data = {
        "name": "custom_calculator",
        "display_name": "Custom Calculator Server",
        "description": "A specialized calculator with advanced mathematical functions",
        "command": "python",
        "args": ["-m", "advanced_calculator", "--port", "8080"],
        "env": {
            "CALC_MODE": "advanced",
            "LOG_LEVEL": "info"
        },
        "auto_start": True,
        "auto_update": True,
        "max_failures": 3
    }

    response = requests.post(
        f"{API_BASE_URL}/toolservers/servers",
        headers=AUTH_HEADERS,
        json=server_data
    )

    if response.status_code == 201:
        server = response.json()
        print(f"✅ Created server: {server['name']} (ID: {server['id']})")
        return server['id']
    else:
        print(f"❌ Failed to create server: {response.text}")
        return None


def list_tool_servers_example():
    """Example: List all tool servers with filtering"""

    # List all servers
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        servers = response.json()
        print(f"📋 Found {len(servers)} servers:")
        for server in servers:
            print(f"   - {server['name']}: {server['status']} ({server['display_name']})")

    # List only enabled servers
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers?status=enabled",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        servers = response.json()
        print(f"🟢 Found {len(servers)} enabled servers")

    # List excluding built-in servers
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers?include_builtin=false",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        servers = response.json()
        print(f"👤 Found {len(servers)} custom servers")


def get_server_details_example(server_id: str):
    """Example: Get detailed information about a specific server"""

    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers/{server_id}",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        server = response.json()
        print(f"📄 Server Details for {server['name']}:")
        print(f"   - Status: {server['status']}")
        print(f"   - Command: {server['command']} {' '.join(server['args'])}")
        print(f"   - Auto-start: {server['auto_start']}")
        print(f"   - Auto-update: {server['auto_update']}")
        print(f"   - Tools: {len(server.get('tools', []))}")

        if server.get('last_health_check'):
            print(f"   - Last health check: {server['last_health_check']}")
    else:
        print(f"❌ Server not found: {response.text}")


def update_server_example(server_id: str):
    """Example: Update server configuration"""

    update_data = {
        "display_name": "Updated Calculator Server",
        "description": "Updated description with new features",
        "auto_start": False,
        "max_failures": 5
    }

    response = requests.put(
        f"{API_BASE_URL}/toolservers/servers/{server_id}",
        headers=AUTH_HEADERS,
        json=update_data
    )

    if response.status_code == 200:
        server = response.json()
        print(f"✅ Updated server: {server['name']}")
        print(f"   - New display name: {server['display_name']}")
        print(f"   - Auto-start: {server['auto_start']}")
    else:
        print(f"❌ Failed to update server: {response.text}")


def server_control_examples(server_id: str):
    """Example: Server control operations"""

    # Start server
    response = requests.post(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/start",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        result = response.json()
        print(f"🟢 Start server: {result['message']}")

    # Check health
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/health",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        health = response.json()
        print("🏥 Health Check:")
        print(f"   - Running: {health['is_running']}")
        print(f"   - Responsive: {health['is_responsive']}")
        print(f"   - Tools: {health['tools_count']}")

    # Stop server
    response = requests.post(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/stop",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        result = response.json()
        print(f"🔴 Stop server: {result['message']}")

    # Restart server
    response = requests.post(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/restart",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        result = response.json()
        print(f"🔄 Restart server: {result['message']}")

    # Enable server
    response = requests.post(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/enable",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Enable server: {result['message']}")

    # Disable server
    response = requests.post(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/disable",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        result = response.json()
        print(f"❌ Disable server: {result['message']}")


def tool_management_examples(server_id: str):
    """Example: Tool management operations"""

    # Get server tools
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/tools",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        tools = response.json()
        print(f"🔧 Found {len(tools)} tools:")

        for tool in tools:
            print(f"   - {tool['name']}: {tool['status']}")
            print(f"     Description: {tool['description']}")
            print(f"     Calls: {tool['total_calls']}, Errors: {tool['total_errors']}")

            if tool['avg_response_time_ms']:
                print(f"     Avg response time: {tool['avg_response_time_ms']:.1f}ms")

            # Enable/disable individual tools
            if tool['status'] == 'disabled':
                enable_response = requests.post(
                    f"{API_BASE_URL}/toolservers/tools/{tool['id']}/enable",
                    headers=AUTH_HEADERS
                )
                if enable_response.status_code == 200:
                    print(f"     ✅ Enabled tool: {tool['name']}")

            elif tool['status'] == 'enabled' and tool['total_errors'] > 10:
                disable_response = requests.post(
                    f"{API_BASE_URL}/toolservers/tools/{tool['id']}/disable",
                    headers=AUTH_HEADERS
                )
                if disable_response.status_code == 200:
                    print(f"     ❌ Disabled problematic tool: {tool['name']}")


def analytics_examples(server_id: str):
    """Example: Analytics and metrics"""

    # Server-specific metrics
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers/{server_id}/metrics",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        metrics = response.json()
        print(f"📊 Server Metrics for {metrics['server_name']}:")
        print(f"   - Total tools: {metrics['total_tools']}")
        print(f"   - Enabled tools: {metrics['enabled_tools']}")
        print(f"   - Total calls: {metrics['total_calls']}")
        print(f"   - Total errors: {metrics['total_errors']}")
        print(f"   - Success rate: {metrics['success_rate']:.2%}")

        if metrics['avg_response_time_ms']:
            print(f"   - Avg response time: {metrics['avg_response_time_ms']:.1f}ms")

        if metrics['last_activity']:
            print(f"   - Last activity: {metrics['last_activity']}")

    # System-wide analytics
    response = requests.get(
        f"{API_BASE_URL}/analytics/toolservers?period=7d",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        analytics = response.json()
        print("\n📈 System-wide Analytics (Last 7 days):")
        print(f"   - Total servers: {analytics['total_servers']}")
        print(f"   - Active servers: {analytics['active_servers']}")
        print(f"   - Total tools: {analytics['total_tools']}")
        print(f"   - Enabled tools: {analytics['enabled_tools']}")
        print(f"   - Calls this week: {analytics['total_calls_week']}")
        print(f"   - Overall success rate: {analytics['overall_success_rate']:.2%}")
        print(f"   - Avg response time: {analytics['avg_response_time_ms']:.1f}ms")

        # Top tools
        if analytics['top_tools']:
            print("\n🔝 Top Tools:")
            for tool in analytics['top_tools'][:5]:
                print(f"   - {tool['tool_name']} ({tool['server_name']}): {tool['total_calls']} calls")

        # Failing tools
        if analytics['failing_tools']:
            print("\n⚠️  Failing Tools:")
            for tool in analytics['failing_tools']:
                print(f"   - {tool['tool_name']}: {tool['success_rate']:.2%} success rate")


def bulk_operations_example():
    """Example: Bulk operations on multiple servers"""

    # First, get list of servers to work with
    response = requests.get(
        f"{API_BASE_URL}/toolservers/servers",
        headers=AUTH_HEADERS
    )

    if response.status_code == 200:
        servers = response.json()
        server_ids = [s['id'] for s in servers if not s['is_builtin']][:3]  # Max 3 custom servers

        if not server_ids:
            print("ℹ️  No custom servers available for bulk operations")
            return

        # Bulk restart operation
        bulk_operation = {
            "server_ids": server_ids,
            "operation": "restart",
            "parameters": {}
        }

        response = requests.post(
            f"{API_BASE_URL}/toolservers/servers/bulk",
            headers=AUTH_HEADERS,
            json=bulk_operation
        )

        if response.status_code == 200:
            result = response.json()
            print("🔄 Bulk Restart Results:")
            print(f"   - Total requested: {result['total_requested']}")
            print(f"   - Successful: {result['successful']}")
            print(f"   - Failed: {result['failed']}")

            if result['errors']:
                print(f"   - Errors: {result['errors']}")

        # Bulk enable operation
        bulk_operation['operation'] = 'enable'

        response = requests.post(
            f"{API_BASE_URL}/toolservers/servers/bulk",
            headers=AUTH_HEADERS,
            json=bulk_operation
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Bulk Enable Results:")
            print(f"   - Successful: {result['successful']}/{result['total_requested']}")


def time_based_analytics_example():
    """Example: Time-based analytics queries"""

    time_periods = ["1h", "24h", "7d", "30d"]

    for period in time_periods:
        response = requests.get(
            f"{API_BASE_URL}/analytics/toolservers?period={period}",
            headers=AUTH_HEADERS
        )

        if response.status_code == 200:
            analytics = response.json()

            if period == "1h":
                calls_key = "total_calls_today"  # Use today as approximation for 1h
            elif period == "24h":
                calls_key = "total_calls_today"
            elif period == "7d":
                calls_key = "total_calls_week"
            else:  # 30d
                calls_key = "total_calls_month"

            total_calls = analytics.get(calls_key, 0)
            print(f"📅 {period.upper()} Analytics: {total_calls} total calls")


def delete_server_example(server_id: str):
    """Example: Delete a tool server"""

    response = requests.delete(
        f"{API_BASE_URL}/toolservers/servers/{server_id}",
        headers=AUTH_HEADERS
    )

    if response.status_code == 204:
        print("🗑️  Successfully deleted server")
    else:
        print(f"❌ Failed to delete server: {response.text}")


def main():
    """Run all API examples"""

    print("🚀 Tool Server API Examples")
    print("=" * 50)

    # Create a new server
    print("\n1. Creating Tool Server")
    server_id = create_tool_server_example()

    if not server_id:
        print("❌ Cannot continue without a server ID")
        return

    # List servers
    print("\n2. Listing Tool Servers")
    list_tool_servers_example()

    # Get server details
    print("\n3. Server Details")
    get_server_details_example(server_id)

    # Update server
    print("\n4. Updating Server")
    update_server_example(server_id)

    # Server control operations
    print("\n5. Server Control Operations")
    server_control_examples(server_id)

    # Tool management
    print("\n6. Tool Management")
    tool_management_examples(server_id)

    # Analytics
    print("\n7. Analytics and Metrics")
    analytics_examples(server_id)

    # Time-based analytics
    print("\n8. Time-based Analytics")
    time_based_analytics_example()

    # Bulk operations
    print("\n9. Bulk Operations")
    bulk_operations_example()

    # Cleanup - delete the test server
    print("\n10. Cleanup")
    delete_server_example(server_id)

    print("\n✅ All API examples completed!")
    print("\n💡 Key Points:")
    print("   - All endpoints require authentication")
    print("   - Server IDs are UUIDs")
    print("   - Analytics support time-based filtering")
    print("   - Bulk operations provide detailed results")
    print("   - Health checks run automatically in background")


if __name__ == "__main__":
    main()
