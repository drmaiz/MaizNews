#!/usr/bin/env python3
"""MCP Client wrapper for Gmail and Google Calendar connectors."""

import json
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional


class MCPClient:
    """Base MCP client for calling MCP tools via subprocess."""

    @staticmethod
    def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via subprocess and return the result.
        This is a placeholder that would use the actual MCP client.
        """
        try:
            # This would call the MCP tool via subprocess in a real environment
            # For now, return sample data
            return {"result": None, "error": "MCP not configured"}
        except Exception as e:
            print(f"Error calling MCP tool {tool_name}: {e}")
            return {"result": None, "error": str(e)}


class MCPGmailClient:
    """Gmail client using MCP connectors."""

    def __init__(self):
        self.mcp = MCPClient()

    def search_threads(
        self,
        query: str = "is:unread in:inbox",
        pageSize: int = 10,
        pageToken: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search email threads using MCP Gmail connector.

        Args:
            query: Gmail search query (e.g., "is:unread in:inbox")
            pageSize: Maximum number of threads to return
            pageToken: Page token for pagination

        Returns:
            Dictionary containing threads list
        """
        arguments = {
            "query": query,
            "pageSize": pageSize,
        }
        if pageToken:
            arguments["pageToken"] = pageToken

        result = self.mcp.call_tool("mcp__Gmail__search_threads", arguments)
        return result.get("result", {"threads": []})

    def get_thread(
        self,
        threadId: str,
        messageFormat: str = "MINIMAL"
    ) -> Dict[str, Any]:
        """
        Get a specific email thread using MCP Gmail connector.

        Args:
            threadId: The thread ID
            messageFormat: Message format (MINIMAL, FULL_CONTENT, METADATA_ONLY)

        Returns:
            Dictionary containing thread details
        """
        arguments = {
            "threadId": threadId,
            "messageFormat": messageFormat,
        }

        result = self.mcp.call_tool("mcp__Gmail__get_thread", arguments)
        return result.get("result", {"messages": []})

    def get_unread_count(self) -> int:
        """Get count of unread emails."""
        try:
            result = self.search_threads(query="is:unread in:inbox", pageSize=50)
            threads = result.get("threads", [])
            # Count unread messages across all threads
            unread = 0
            for thread in threads:
                # Each thread can have multiple unread messages
                unread += len([m for m in thread.get("messages", []) if m.get("internalDate")])
            return len(threads) if threads else 0
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0

    def get_recent_unread(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent unread emails."""
        try:
            result = self.search_threads(
                query="is:unread in:inbox",
                pageSize=max_results
            )

            threads = result.get("threads", [])
            emails = []

            for thread in threads:
                thread_detail = self.get_thread(
                    threadId=thread.get("id"),
                    messageFormat="MINIMAL"
                )

                messages = thread_detail.get("messages", [])
                if not messages:
                    continue

                msg = messages[0]
                headers = msg.get("headers", {})

                emails.append({
                    "subject": headers.get("subject", "(No subject)"),
                    "from": headers.get("from", ""),
                    "date": None,
                    "snippet": msg.get("snippet", ""),
                })

            return emails[:max_results]
        except Exception as e:
            print(f"Error getting recent unread emails: {e}")
            return []


class MCPCalendarClient:
    """Google Calendar client using MCP connectors."""

    def __init__(self):
        self.mcp = MCPClient()

    def list_events(
        self,
        calendarId: str = "primary",
        startTime: Optional[str] = None,
        endTime: Optional[str] = None,
        pageSize: int = 50,
        orderBy: str = "startTime",
        pageToken: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List calendar events using MCP Google Calendar connector.

        Args:
            calendarId: Calendar ID (default: primary)
            startTime: Start time in ISO 8601 format
            endTime: End time in ISO 8601 format
            pageSize: Maximum number of events to return
            orderBy: Sort order (startTime, lastModified, etc.)
            pageToken: Page token for pagination

        Returns:
            Dictionary containing events list
        """
        if not startTime:
            startTime = datetime.now(timezone.utc).isoformat()
        if not endTime:
            endTime = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        arguments = {
            "calendarId": calendarId,
            "startTime": startTime,
            "endTime": endTime,
            "pageSize": pageSize,
            "orderBy": orderBy,
        }
        if pageToken:
            arguments["pageToken"] = pageToken

        result = self.mcp.call_tool("mcp__Google-Calendar__list_events", arguments)
        return result.get("result", {"events": []})

    def get_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get calendar events for the specified number of days.

        Args:
            days: Number of days to retrieve events for

        Returns:
            List of events
        """
        try:
            now = datetime.now(timezone.utc)
            end = now + timedelta(days=days)

            result = self.list_events(
                startTime=now.isoformat(),
                endTime=end.isoformat(),
                pageSize=50
            )

            events = []
            for item in result.get("events", []):
                start_raw = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date")
                end_raw = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")

                if not start_raw:
                    continue

                all_day = "dateTime" not in item.get("start", {})
                try:
                    start_dt = datetime.fromisoformat(start_raw.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_raw.replace('Z', '+00:00'))
                except:
                    start_dt = datetime.fromisoformat(start_raw)
                    end_dt = datetime.fromisoformat(end_raw)

                events.append({
                    "summary": item.get("summary", "(No title)"),
                    "start": start_dt,
                    "end": end_dt,
                    "all_day": all_day,
                    "location": item.get("location", ""),
                })

            return events
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return []
