from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse


def get_invite_url(request, sender_id, team_id, receipient):
    """
    Generate invite url for a given team and email
    """
    # Encode the team and email information using URL-safe base64 encoding
    team_id = team_id
    sender_id = sender_id
    receipient_email = receipient

    encoded_team_id = urlsafe_base64_encode(str(team_id).encode())
    encoded_email = urlsafe_base64_encode(str(receipient_email).encode())
    encoded_sender_id = urlsafe_base64_encode(str(sender_id).encode())
    current_site = get_current_site(request).domain
    relativeLink = reverse("teams-invite", kwargs={"pk": team_id})
    absurl = (
        "http://"
        + current_site
        + relativeLink
        + f"?team={encoded_team_id}&from={encoded_sender_id}&to={encoded_email}"
    )

    return absurl


def decode_absurl(team, sender, receipient):
    """
    Get receipt email, sender id and team id from request parameters
    """
    team_id = urlsafe_base64_decode(team).decode()
    sender_id = urlsafe_base64_decode(sender).decode()
    email_id = urlsafe_base64_decode(receipient).decode()

    return {
        "team_id": team_id,
        "sender_id": sender_id,
        "email_id": email_id,
    }
