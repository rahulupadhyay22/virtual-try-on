def build_upload_folder(user_id: int, folder: str) -> str:
    return f"fabricvision/{folder}/{user_id}/"


def build_shop_upload_folder(shop_id: int) -> str:
    return f"fabricvision/cloth_images/shop/{shop_id}/"
