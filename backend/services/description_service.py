DESCRIPTION_TEMPLATES = [
    "Freshly prepared {item} made with quality ingredients.",
    "{item} - a customer favorite.",
    "Our signature {item} made in-house.",
    "Our best-selling {item}.",
    "Delicious {item} - perfect for any time of day.",
]


def get_item_description(item_name: str, restaurant_id: int | None = None) -> str:
    seed = f"{item_name}_{restaurant_id or 0}"
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(DESCRIPTION_TEMPLATES)
    return DESCRIPTION_TEMPLATES[idx].format(item=item_name)
