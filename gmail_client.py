from datetime import datetime


async def get_unread_count(mcp_client):
    """Get count of unread emails in inbox"""
    try:
        result = await mcp_client.call_tool(
            "mcp__Gmail__search_threads",
            {"query": "is:unread in:inbox", "pageSize": 1}
        )
        # The result includes the total count via estimated count or we count threads
        threads = result.get("threads", [])
        # Search returns approximate count, let's return thread count as proxy
        return len(threads) if threads else 0
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return 0


def get_unread_count_sync(client):
    """Synchronous wrapper for get_unread_count"""
    try:
        result = client.search_threads(query="is:unread in:inbox", pageSize=1)
        threads = result.get("threads", [])
        return len(threads) if threads else 0
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return 0


def get_recent_unread(client, max_results=10):
    """Get recent unread emails using MCP Gmail connector"""
    try:
        result = client.search_threads(
            query="is:unread in:inbox",
            pageSize=max_results
        )

        threads = result.get("threads", [])
        emails = []

        for thread in threads:
            # Get full thread details
            thread_detail = client.get_thread(
                threadId=thread.get("id"),
                messageFormat="MINIMAL"
            )

            messages = thread_detail.get("messages", [])
            if not messages:
                continue

            # Get the first message (usually the original email)
            msg = messages[0]

            emails.append({
                "subject": thread.get("snippet", "(No subject)"),
                "from": msg.get("from", ""),
                "date": None,
                "snippet": msg.get("snippet", ""),
            })

        return emails[:max_results]
    except Exception as e:
        print(f"Error getting recent unread emails: {e}")
        return []
