#!/usr/bin/env python3

import os
from datetime import datetime, timedelta, timezone
import argparse

import httpx
from dotenv import load_dotenv


class GoCardlessClient:
    def __init__(self):
        load_dotenv()

        self.base_url = "https://bankaccountdata.gocardless.com/api/v2"
        self.client_id = os.getenv("GOCARDLESS_SECRET_ID")
        self.client_secret = os.getenv("GOCARDLESS_SECRET_KEY")
        self.access_token = None

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Please set GOCARDLESS_CLIENT_ID and GOCARDLESS_CLIENT_SECRET in .env file"
            )

        self._authenticate()

    def _authenticate(self):
        """Authenticate with the API and get an access token."""
        auth_url = f"{self.base_url}/token/new/"
        payload = {
            "secret_id": self.client_id,
            "secret_key": self.client_secret,
        }

        response = httpx.post(auth_url, json=payload)
        response.raise_for_status()
        self.access_token = response.json()["access"]

    def get_agreements(self):
        """Fetch all agreements from the API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }
        response = httpx.get(f"{self.base_url}/agreements/enduser/", headers=headers)
        response.raise_for_status()
        return response.json()["results"]

    def delete_agreement(self, agreement_id: str):
        """Delete an agreement by ID from the API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }
        response = httpx.delete(
            f"{self.base_url}/agreements/enduser/{agreement_id}/", headers=headers
        )
        response.raise_for_status()
        return response.status_code

    @staticmethod
    def calculate_days_until_expiry(created_at):
        """Calculate days until an agreement reaches 90 days old."""
        expiry_date = datetime.fromisoformat(created_at) + timedelta(days=90)
        today = datetime.now(tz=timezone.utc)
        delta = expiry_date - today
        return delta.days


def cleanup_expired_agreements(client):
    """
    Remove agreements that expired more than a week ago.
    We'll consider an agreement expired if its expiry date was over 7 days ago.
    """
    agreements = client.get_agreements()
    if not agreements:
        print("No agreements found for cleanup.")
        return

    deleted_count = 0
    for agreement in agreements:
        created_at = agreement.get("created")
        if not created_at:
            continue

        days_left = client.calculate_days_until_expiry(created_at)

        # If it's expired for more than 7 days, days_left would be < -7
        if days_left < -7:
            agreement_id = agreement["id"]
            try:
                client.delete_agreement(agreement_id)
                print(
                    f"Deleted agreement {agreement_id} (expired {abs(days_left)} days ago)."
                )
                deleted_count += 1
            except httpx.HTTPError as err:
                print(f"Failed to delete agreement {agreement_id}: {err}")

    print(f"Cleanup complete. Total agreements deleted: {deleted_count}")


def list_agreements_status(client):
    """List agreements and their expiration status."""
    agreements = client.get_agreements()
    if not agreements:
        print("No agreements found.")
        return

    print("\nAgreement Expiration Status:")
    print("-" * 40)

    for agreement in agreements:
        agreement_id = agreement["id"]
        institution_id = agreement["institution_id"]
        created_at = agreement.get("created", datetime.now().isoformat())

        if created_at:
            days_left = client.calculate_days_until_expiry(created_at)
            if days_left >= 0:
                print(f"Agreement {agreement_id} ({institution_id}):")
                print(f"  Expires in: {days_left} days ({created_at})")
            else:
                print(f"Agreement {agreement_id} ({institution_id}):")
                print(f"  Expired: {-days_left} days ago ({created_at})")
        else:
            print(f"Agreement {agreement_id}:")
            print("  No expiry date set")
        print("-" * 40)


def main():
    parser = argparse.ArgumentParser(description="Manage GoCardless agreements.")
    parser.add_argument(
        "-c",
        "--cleanup-expired",
        action="store_true",
        help="Cleanup agreements expired more than a week ago.",
    )
    args = parser.parse_args()

    try:
        client = GoCardlessClient()

        if args.cleanup_expired:
            cleanup_expired_agreements(client)
        else:
            list_agreements_status(client)

    except httpx.HTTPError as e:
        print(f"Error connecting to GoCardless API: {e}")


if __name__ == "__main__":
    main()
