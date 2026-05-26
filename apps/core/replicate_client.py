import os


def get_replicate_client():
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise ValueError("REPLICATE_API_TOKEN is not set")

    import replicate

    return replicate.Client(api_token=token)
