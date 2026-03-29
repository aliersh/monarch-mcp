"""Tests for new Monarch Money API tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest

import server


class TestNewMonarchTools:
    """Test newly added Monarch Money API tools."""

    @pytest.mark.asyncio
    async def test_get_account_holdings(self) -> None:
        """Test get_account_holdings functionality."""
        mock_client = AsyncMock()
        mock_holdings = [
            {"symbol": "AAPL", "shares": 100, "value": 15000},
            {"symbol": "GOOGL", "shares": 50, "value": 12500},
        ]
        mock_client.get_account_holdings.return_value = mock_holdings

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.get_account_holdings()

            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result == mock_holdings
            mock_client.get_account_holdings.assert_called_once()

        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_get_account_history(self) -> None:
        """Test get_account_history with date filtering."""
        mock_client = AsyncMock()
        mock_history = [{"date": "2024-01-01", "balance": 1000}, {"date": "2024-01-02", "balance": 1050}]
        mock_client.get_account_history.return_value = mock_history

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.get_account_history(
                account_id="acc123", start_date="2024-01-01", end_date="2024-01-31"
            )

            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result == mock_history

            # Verify call parameters
            mock_client.get_account_history.assert_called_once()
            call_args = mock_client.get_account_history.call_args
            assert call_args.kwargs["account_id"] == "acc123"
            assert "start_date" in call_args.kwargs
            assert "end_date" in call_args.kwargs

        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_get_institutions(self) -> None:
        """Test get_institutions functionality."""
        mock_client = AsyncMock()
        mock_institutions = [{"id": "inst1", "name": "Chase Bank"}, {"id": "inst2", "name": "Wells Fargo"}]
        mock_client.get_institutions.return_value = mock_institutions

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.get_institutions()

            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result == mock_institutions
            mock_client.get_institutions.assert_called_once()

        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_get_recurring_transactions(self) -> None:
        """Test get_recurring_transactions functionality."""
        mock_client = AsyncMock()
        mock_recurring = [
            {"id": "rec1", "amount": -500, "description": "Rent"},
            {"id": "rec2", "amount": 3000, "description": "Salary"},
        ]
        mock_client.get_recurring_transactions.return_value = mock_recurring

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.get_recurring_transactions()

            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result == mock_recurring
            mock_client.get_recurring_transactions.assert_called_once()

        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_set_budget_amount(self) -> None:
        """Test set_budget_amount functionality."""
        mock_client = AsyncMock()
        mock_result = {"category_id": "cat123", "amount": 500, "status": "updated"}
        mock_client.set_budget_amount.return_value = mock_result

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.set_budget_amount(category_id="cat123", amount=500.0)

            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result == mock_result

            # Verify parameters
            mock_client.set_budget_amount.assert_called_once()
            call_args = mock_client.set_budget_amount.call_args
            assert call_args.kwargs["category_id"] == "cat123"
            assert call_args.kwargs["amount"] == 500.0

        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_create_manual_account(self) -> None:
        """Test create_manual_account functionality."""
        mock_client = AsyncMock()
        mock_result = {"id": "acc456", "name": "My Savings", "type": "savings"}
        mock_client.create_manual_account.return_value = mock_result

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.create_manual_account(
                account_name="My Savings", account_type="savings", balance=1000.0
            )

            assert isinstance(result, str)
            parsed_result = json.loads(result)
            assert parsed_result == mock_result

            # Verify parameters
            mock_client.create_manual_account.assert_called_once()
            call_args = mock_client.create_manual_account.call_args
            assert call_args.kwargs["account_name"] == "My Savings"
            assert call_args.kwargs["account_type"] == "savings"
            assert call_args.kwargs["balance"] == 1000.0

        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_error_handling_in_new_tools(self) -> None:
        """Test that new tools properly handle and log errors."""
        mock_client = AsyncMock()
        mock_client.get_account_holdings.side_effect = Exception("API Error")

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            with pytest.raises(Exception, match="API Error"):
                await server.get_account_holdings()

            mock_client.get_account_holdings.assert_called_once()

        finally:
            server.mm_client = original_client


class TestTransactionTags:
    """Test transaction tag tools."""

    @pytest.mark.asyncio
    async def test_get_transaction_tags(self) -> None:
        """Test get_transaction_tags returns all tags."""
        mock_client = AsyncMock()
        mock_result = {
            "householdTransactionTags": [
                {"id": "tag1", "name": "Vacation", "color": "#19D2A5", "order": 0, "transactionCount": 5},
                {"id": "tag2", "name": "Business", "color": "#FF5733", "order": 1, "transactionCount": 12},
            ]
        }
        mock_client.get_transaction_tags.return_value = mock_result

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.get_transaction_tags()
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed == mock_result
            mock_client.get_transaction_tags.assert_called_once()
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_create_transaction_tag(self) -> None:
        """Test create_transaction_tag with valid inputs."""
        mock_client = AsyncMock()
        mock_result = {
            "createTransactionTag": {
                "tag": {
                    "id": "new_tag",
                    "name": "Tax Deductible",
                    "color": "#FF5733",
                    "order": 2,
                    "transactionCount": 0,
                }
            }
        }
        mock_client.create_transaction_tag.return_value = mock_result

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.create_transaction_tag(name="Tax Deductible", color="#FF5733")
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed == mock_result

            call_args = mock_client.create_transaction_tag.call_args
            assert call_args.kwargs["name"] == "Tax Deductible"
            assert call_args.kwargs["color"] == "#FF5733"
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_create_transaction_tag_invalid_color(self) -> None:
        """Test create_transaction_tag rejects invalid color formats."""
        with patch("server.ensure_authenticated", new_callable=AsyncMock):
            with pytest.raises(ValueError, match="Invalid color format"):
                await server.create_transaction_tag(name="Test", color="red")

            with pytest.raises(ValueError, match="Invalid color format"):
                await server.create_transaction_tag(name="Test", color="#GGG")

            with pytest.raises(ValueError, match="Invalid color format"):
                await server.create_transaction_tag(name="Test", color="19D2A5")

    @pytest.mark.asyncio
    async def test_create_transaction_tag_empty_name(self) -> None:
        """Test create_transaction_tag rejects empty name."""
        with patch("server.ensure_authenticated", new_callable=AsyncMock):
            with pytest.raises(ValueError, match="Tag name cannot be empty"):
                await server.create_transaction_tag(name="", color="#FF5733")

    @pytest.mark.asyncio
    async def test_set_transaction_tags(self) -> None:
        """Test set_transaction_tags parses comma-separated IDs."""
        mock_client = AsyncMock()
        mock_result = {
            "setTransactionTags": {"transaction": {"id": "txn123", "tags": [{"id": "tag1"}, {"id": "tag2"}]}}
        }
        mock_client.set_transaction_tags.return_value = mock_result

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.set_transaction_tags(transaction_id="txn123", tag_ids="tag1, tag2")
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed == mock_result

            call_args = mock_client.set_transaction_tags.call_args
            assert call_args.kwargs["transaction_id"] == "txn123"
            assert call_args.kwargs["tag_ids"] == ["tag1", "tag2"]
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_set_transaction_tags_remove_all(self) -> None:
        """Test set_transaction_tags with empty string removes all tags."""
        mock_client = AsyncMock()
        mock_result = {"setTransactionTags": {"transaction": {"id": "txn123", "tags": []}}}
        mock_client.set_transaction_tags.return_value = mock_result

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.set_transaction_tags(transaction_id="txn123", tag_ids="")
            assert isinstance(result, str)

            call_args = mock_client.set_transaction_tags.call_args
            assert call_args.kwargs["tag_ids"] == []
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_create_transaction_with_tags(self) -> None:
        """Test create_transaction applies tags after creation."""
        mock_client = AsyncMock()
        mock_create_result = {"createTransaction": {"transaction": {"id": "new_txn_123"}}}
        mock_client.create_transaction.return_value = mock_create_result
        mock_client.set_transaction_tags.return_value = {"setTransactionTags": {"transaction": {"id": "new_txn_123"}}}

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.create_transaction(
                amount=-25.0,
                merchant_name="Corner Deli",
                account_id="acc123",
                date="2024-07-29",
                category_id="cat123",
                tag_ids="tag1,tag2",
            )

            assert isinstance(result, str)
            mock_client.create_transaction.assert_called_once()
            mock_client.set_transaction_tags.assert_called_once()

            tag_call_args = mock_client.set_transaction_tags.call_args
            assert tag_call_args.kwargs["transaction_id"] == "new_txn_123"
            assert tag_call_args.kwargs["tag_ids"] == ["tag1", "tag2"]
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_create_transaction_with_tags_failure_graceful(self) -> None:
        """Test create_transaction still succeeds if tag application fails."""
        mock_client = AsyncMock()
        mock_create_result = {"createTransaction": {"transaction": {"id": "new_txn_456"}}}
        mock_client.create_transaction.return_value = mock_create_result
        mock_client.set_transaction_tags.side_effect = Exception("Tag API error")

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            # Should NOT raise despite tag failure
            result = await server.create_transaction(
                amount=-10.0,
                merchant_name="Test Shop",
                account_id="acc123",
                date="2024-07-29",
                category_id="cat123",
                tag_ids="tag1",
            )

            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed == mock_create_result
        finally:
            server.mm_client = original_client


class TestUpdateTransactionTags:
    """Test tag support in update_transaction."""

    @pytest.mark.asyncio
    async def test_update_transaction_with_tags(self) -> None:
        """Test update_transaction applies tags after update."""
        mock_client = AsyncMock()
        mock_update_result = {"updateTransaction": {"transaction": {"id": "txn123", "amount": -50.0}}}
        mock_client.update_transaction.return_value = mock_update_result
        mock_client.set_transaction_tags.return_value = {"setTransactionTags": {"transaction": {"id": "txn123"}}}

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.update_transaction(
                transaction_id="txn123",
                amount=-50.0,
                tag_ids="tag1,tag2",
            )

            assert isinstance(result, str)
            mock_client.update_transaction.assert_called_once()
            mock_client.set_transaction_tags.assert_called_once()

            tag_call_args = mock_client.set_transaction_tags.call_args
            assert tag_call_args.kwargs["transaction_id"] == "txn123"
            assert tag_call_args.kwargs["tag_ids"] == ["tag1", "tag2"]
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_update_transaction_with_tags_remove_all(self) -> None:
        """Test update_transaction with empty string removes all tags."""
        mock_client = AsyncMock()
        mock_client.update_transaction.return_value = {"updateTransaction": {"transaction": {"id": "txn123"}}}
        mock_client.set_transaction_tags.return_value = {"setTransactionTags": {"transaction": {"id": "txn123"}}}

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            await server.update_transaction(transaction_id="txn123", tag_ids="")

            tag_call_args = mock_client.set_transaction_tags.call_args
            assert tag_call_args.kwargs["tag_ids"] == []
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_delete_transaction(self) -> None:
        """Test delete_transaction successfully deletes a transaction."""
        mock_client = AsyncMock()
        mock_client.delete_transaction.return_value = True

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.delete_transaction(transaction_id="txn123")

            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed["deleted"] is True
            assert parsed["transaction_id"] == "txn123"
            mock_client.delete_transaction.assert_called_once_with(transaction_id="txn123")
        finally:
            server.mm_client = original_client

    @pytest.mark.asyncio
    async def test_delete_transaction_empty_id(self) -> None:
        """Test delete_transaction raises ValueError for empty ID."""
        with pytest.raises(ValueError, match="transaction_id cannot be empty"):
            await server.delete_transaction(transaction_id="")

    @pytest.mark.asyncio
    async def test_update_transaction_with_tags_failure_graceful(self) -> None:
        """Test update_transaction still succeeds if tag application fails."""
        mock_client = AsyncMock()
        mock_update_result = {"updateTransaction": {"transaction": {"id": "txn123"}}}
        mock_client.update_transaction.return_value = mock_update_result
        mock_client.set_transaction_tags.side_effect = Exception("Tag API error")

        original_client = server.mm_client
        server.mm_client = mock_client

        try:
            result = await server.update_transaction(
                transaction_id="txn123",
                tag_ids="tag1",
            )

            assert isinstance(result, str)
            parsed = json.loads(result)
            assert parsed == mock_update_result
        finally:
            server.mm_client = original_client


class TestToolCounts:
    """Test that we have the expected number of tools."""

    def test_all_tools_available(self) -> None:
        """Test that all expected tools are available."""
        expected_tools = [
            "get_accounts",
            "get_transactions",
            "get_budgets",
            "get_cashflow",
            "get_transaction_categories",
            "get_transaction_tags",
            "create_transaction",
            "create_transaction_tag",
            "update_transaction",
            "delete_transaction",
            "set_transaction_tags",
            "refresh_accounts",
            "get_account_holdings",
            "get_account_history",
            "get_institutions",
            "get_recurring_transactions",
            "set_budget_amount",
            "create_manual_account",
        ]

        for tool_name in expected_tools:
            assert hasattr(server, tool_name), f"Tool {tool_name} not found"

        # Should have 18 tools total now
        assert len(expected_tools) == 18
