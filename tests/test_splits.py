"""Tests for split transaction functionality."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PARENT_TRANSACTION = {
    "getTransaction": {
        "id": "txn_parent_123",
        "amount": -50.00,
        "category": {"id": "cat_001", "name": "Groceries", "__typename": "Category"},
        "merchant": {"id": "m_001", "name": "Supermarket", "__typename": "Merchant"},
        "splitTransactions": [
            {
                "id": "split_1",
                "merchant": {"id": "m_002", "name": "Corner Deli", "__typename": "Merchant"},
                "category": {"id": "cat_002", "name": "Dining", "__typename": "Category"},
                "amount": -30.00,
                "notes": "",
                "__typename": "Transaction",
            },
            {
                "id": "split_2",
                "merchant": {"id": "m_003", "name": "Bakery", "__typename": "Merchant"},
                "category": {"id": "cat_001", "name": "Groceries", "__typename": "Category"},
                "amount": -20.00,
                "notes": "bread",
                "__typename": "Transaction",
            },
        ],
        "__typename": "Transaction",
    }
}

PARENT_NO_SPLITS = {
    "getTransaction": {
        "id": "txn_parent_456",
        "amount": -75.00,
        "category": {"id": "cat_003", "name": "Shopping", "__typename": "Category"},
        "merchant": {"id": "m_004", "name": "Department Store", "__typename": "Merchant"},
        "splitTransactions": [],
        "__typename": "Transaction",
    }
}

UPDATE_RESULT = {
    "updateTransactionSplit": {
        "errors": None,
        "transaction": {
            "id": "txn_parent_123",
            "hasSplitTransactions": True,
            "splitTransactions": [
                {
                    "id": "split_new_1",
                    "merchant": {"id": "m_002", "name": "Corner Deli", "__typename": "Merchant"},
                    "category": {"id": "cat_002", "name": "Dining", "__typename": "Category"},
                    "amount": -30.00,
                    "notes": "",
                    "__typename": "Transaction",
                },
                {
                    "id": "split_new_2",
                    "merchant": {"id": "m_003", "name": "Bakery", "__typename": "Merchant"},
                    "category": {"id": "cat_001", "name": "Groceries", "__typename": "Category"},
                    "amount": -20.00,
                    "notes": "bread",
                    "__typename": "Transaction",
                },
            ],
            "__typename": "Transaction",
        },
        "__typename": "UpdateTransactionSplitPayload",
    }
}


class TestGetTransactionSplits:
    """Tests for the get_transaction_splits tool."""

    @pytest.mark.asyncio
    async def test_get_splits_success(self):
        """Test successful retrieval of transaction splits."""
        from server import get_transaction_splits

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(return_value=PARENT_TRANSACTION)

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            result_str = await get_transaction_splits("txn_parent_123")
            result = json.loads(result_str)

            assert result["getTransaction"]["id"] == "txn_parent_123"
            assert result["getTransaction"]["amount"] == -50.00
            assert len(result["getTransaction"]["splitTransactions"]) == 2
            assert result["getTransaction"]["splitTransactions"][0]["amount"] == -30.00
            assert result["getTransaction"]["splitTransactions"][1]["notes"] == "bread"

    @pytest.mark.asyncio
    async def test_get_splits_no_splits(self):
        """Test retrieval of a transaction that has no splits."""
        from server import get_transaction_splits

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(return_value=PARENT_NO_SPLITS)

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            result_str = await get_transaction_splits("txn_parent_456")
            result = json.loads(result_str)

            assert result["getTransaction"]["id"] == "txn_parent_456"
            assert result["getTransaction"]["splitTransactions"] == []

    @pytest.mark.asyncio
    async def test_get_splits_api_error(self):
        """Test error propagation on API failure."""
        from server import get_transaction_splits

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(side_effect=Exception("Transaction not found"))

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            with pytest.raises(Exception, match="Transaction not found"):
                await get_transaction_splits("txn_nonexistent")


class TestSplitTransaction:
    """Tests for the split_transaction tool."""

    @pytest.mark.asyncio
    async def test_split_transaction_success(self):
        """Test successful split of a transaction."""
        from server import split_transaction

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(return_value=PARENT_TRANSACTION)
        mock_client.update_transaction_splits = AsyncMock(return_value=UPDATE_RESULT)

        split_data = json.dumps(
            [
                {"merchantName": "Corner Deli", "amount": -30.00, "categoryId": "cat_002"},
                {"merchantName": "Bakery", "amount": -20.00, "categoryId": "cat_001", "notes": "bread"},
            ]
        )

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            result_str = await split_transaction("txn_parent_123", split_data)
            result = json.loads(result_str)

            assert result["updateTransactionSplit"]["transaction"]["hasSplitTransactions"] is True
            assert len(result["updateTransactionSplit"]["transaction"]["splitTransactions"]) == 2

            # Verify the API was called with correct arguments
            mock_client.update_transaction_splits.assert_called_once()
            call_kwargs = mock_client.update_transaction_splits.call_args[1]
            assert call_kwargs["transaction_id"] == "txn_parent_123"
            assert len(call_kwargs["split_data"]) == 2

    @pytest.mark.asyncio
    async def test_split_transaction_delete_splits(self):
        """Test removing all splits by passing an empty array."""
        from server import split_transaction

        delete_result = {
            "updateTransactionSplit": {
                "errors": None,
                "transaction": {"id": "txn_parent_123", "hasSplitTransactions": False, "splitTransactions": []},
            }
        }

        mock_client = MagicMock()
        mock_client.update_transaction_splits = AsyncMock(return_value=delete_result)

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            result_str = await split_transaction("txn_parent_123", "[]")
            result = json.loads(result_str)

            assert result["updateTransactionSplit"]["transaction"]["hasSplitTransactions"] is False

            # Verify called with empty list
            call_kwargs = mock_client.update_transaction_splits.call_args[1]
            assert call_kwargs["split_data"] == []
            # Should NOT call get_transaction_splits (no validation needed for delete)
            mock_client.get_transaction_splits.assert_not_called()

    @pytest.mark.asyncio
    async def test_split_transaction_invalid_json(self):
        """Test error handling for invalid JSON input."""
        from server import split_transaction

        with patch("server.ensure_authenticated", new_callable=AsyncMock):
            with pytest.raises(ValueError, match="Invalid JSON"):
                await split_transaction("txn_123", "not valid json {")

    @pytest.mark.asyncio
    async def test_split_transaction_not_array(self):
        """Test error handling when split_data is a JSON object instead of array."""
        from server import split_transaction

        with patch("server.ensure_authenticated", new_callable=AsyncMock):
            with pytest.raises(ValueError, match="must be a JSON array"):
                await split_transaction("txn_123", '{"merchantName": "Deli", "amount": -50.00}')

    @pytest.mark.asyncio
    async def test_split_transaction_amount_mismatch(self):
        """Test error when split amounts don't sum to parent transaction amount."""
        from server import split_transaction

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(return_value=PARENT_TRANSACTION)  # parent = -50.00

        split_data = json.dumps(
            [
                {"merchantName": "Corner Deli", "amount": -30.00, "categoryId": "cat_002"},
                {"merchantName": "Bakery", "amount": -15.00, "categoryId": "cat_001"},  # sum = -45.00, not -50.00
            ]
        )

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            with pytest.raises(ValueError, match="Split amounts sum to"):
                await split_transaction("txn_parent_123", split_data)

    @pytest.mark.asyncio
    async def test_split_transaction_amount_rounding_tolerance(self):
        """Test that amounts within 0.01 floating-point tolerance are accepted."""
        from server import split_transaction

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(return_value=PARENT_TRANSACTION)  # parent = -50.00
        mock_client.update_transaction_splits = AsyncMock(return_value=UPDATE_RESULT)

        # Amounts that sum to -49.999 (within 0.01 tolerance of -50.00)
        split_data = json.dumps(
            [
                {"merchantName": "Corner Deli", "amount": -29.999, "categoryId": "cat_002"},
                {"merchantName": "Bakery", "amount": -20.000, "categoryId": "cat_001"},
            ]
        )

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            result_str = await split_transaction("txn_parent_123", split_data)
            result = json.loads(result_str)

            assert result["updateTransactionSplit"]["transaction"]["hasSplitTransactions"] is True

    @pytest.mark.asyncio
    async def test_split_transaction_missing_required_fields(self):
        """Test error when a split is missing required fields."""
        from server import split_transaction

        with patch("server.ensure_authenticated", new_callable=AsyncMock):
            # Missing categoryId
            split_data = json.dumps(
                [
                    {"merchantName": "Corner Deli", "amount": -50.00},
                ]
            )
            with pytest.raises(ValueError, match="missing required fields"):
                await split_transaction("txn_123", split_data)

    @pytest.mark.asyncio
    async def test_split_transaction_with_notes(self):
        """Test that optional notes field passes through correctly."""
        from server import split_transaction

        mock_client = MagicMock()
        mock_client.get_transaction_splits = AsyncMock(return_value=PARENT_TRANSACTION)
        mock_client.update_transaction_splits = AsyncMock(return_value=UPDATE_RESULT)

        split_data = json.dumps(
            [
                {"merchantName": "Corner Deli", "amount": -30.00, "categoryId": "cat_002", "notes": "lunch"},
                {"merchantName": "Bakery", "amount": -20.00, "categoryId": "cat_001"},
            ]
        )

        with patch("server.mm_client", mock_client), patch("server.ensure_authenticated", new_callable=AsyncMock):
            await split_transaction("txn_parent_123", split_data)

            call_kwargs = mock_client.update_transaction_splits.call_args[1]
            assert call_kwargs["split_data"][0]["notes"] == "lunch"
            assert "notes" not in call_kwargs["split_data"][1]  # notes not added when not provided
