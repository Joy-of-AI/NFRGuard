import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def check_balance(account_id: str) -> dict:
    """Check the balance for a specific account.

    Args:
        account_id (str): The account ID to check balance for.

    Returns:
        dict: status and balance information or error message.
    """
    # Simulate balance check - in real implementation, this would call Bank of Anthos services
    if account_id.startswith("acc_"):
        return {
            "status": "success",
            "account_id": account_id,
            "balance": "1,250.50",
            "currency": "USD",
            "last_updated": "2025-01-14T21:46:00Z"
        }
    else:
        return {
            "status": "error",
            "error_message": f"Account '{account_id}' not found.",
        }


def get_transaction_history(account_id: str, limit: int = 10) -> dict:
    """Get transaction history for an account.

    Args:
        account_id (str): The account ID to get transactions for.
        limit (int): Maximum number of transactions to return.

    Returns:
        dict: status and transaction list or error message.
    """
    # Simulate transaction history - in real implementation, this would call Bank of Anthos services
    if account_id.startswith("acc_"):
        transactions = [
            {
                "transaction_id": "txn_001",
                "amount": "100.00",
                "type": "debit",
                "description": "Purchase at Store ABC",
                "timestamp": "2025-01-14T10:30:00Z"
            },
            {
                "transaction_id": "txn_002", 
                "amount": "500.00",
                "type": "credit",
                "description": "Salary deposit",
                "timestamp": "2025-01-13T09:00:00Z"
            }
        ]
        return {
            "status": "success",
            "account_id": account_id,
            "transactions": transactions[:limit],
            "total_count": len(transactions)
        }
    else:
        return {
            "status": "error",
            "error_message": f"Account '{account_id}' not found.",
        }


def process_transaction(from_account: str, to_account: str, amount: float, description: str) -> dict:
    """Process a new transaction between accounts.

    Args:
        from_account (str): Source account ID.
        to_account (str): Destination account ID.
        amount (float): Transaction amount.
        description (str): Transaction description.

    Returns:
        dict: status and transaction result or error message.
    """
    # Simulate transaction processing - in real implementation, this would call Bank of Anthos services
    if from_account.startswith("acc_") and to_account.startswith("acc_"):
        return {
            "status": "success",
            "transaction_id": "txn_new_001",
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "description": description,
            "timestamp": "2025-01-14T21:46:00Z",
            "status": "completed"
        }
    else:
        return {
            "status": "error",
            "error_message": "Invalid account IDs provided.",
        }


root_agent = Agent(
    name="banking_assistant",
    model="gemini-2.5-flash",
    description=(
        "Banking Assistant Agent for Bank of Anthos. Helps with balance checking, "
        "transaction history, and transaction processing."
    ),
    instruction=(
        "You are a helpful banking assistant for Bank of Anthos. You can help users "
        "check their account balances, view transaction history, and process transactions. "
        "Always be professional and helpful when assisting with banking operations."
    ),
    tools=[check_balance, get_transaction_history, process_transaction],
)