from prozorro_auction.settings import MASK_OBJECT_DATA_SINGLE


MASK_FIELDS = (
    "items",
    "features",
    "value",
    "minimalStep",
    "procuringEntity",
    "stages",
    "initial_bids",
    "results",
)

IGNORE_KEYS = {
    "id",
    "bidder_id",
    "start",
    "type",
    "currency",
    "kind",
}

def mask_simple_data(v):
    if isinstance(v, str):
        v = "0" * len(v)
    elif isinstance(v, bool):
        pass
    elif isinstance(v, int) or isinstance(v, float):
        v = 0
    return v


def ignore_mask(key):
    if key in IGNORE_KEYS:
        return True
    elif key.startswith("time") or key.endswith("time"):
        return True


def mask_process_compound(data):
    if isinstance(data, list):
        data = [mask_process_compound(e) for e in data]
    elif isinstance(data, dict):
        for i, j in data.items():
            if not ignore_mask(i):
                j = mask_process_compound(j)
                if i == "identifier":  # identifier.id
                    j["id"] = mask_simple_data(j["id"])
            data[i] = j
    else:
        data = mask_simple_data(data)
    return data


def mask_data(obj):
    is_masked = obj.pop("is_masked", False)
    if (
        MASK_OBJECT_DATA_SINGLE and is_masked
        and "timer" not in obj  # finished
    ):
        obj["title"] = "Тимчасово замасковано, щоб русня не підглядала"
        obj["title_en"] = "It is temporarily disguised so that the rusnya does not spy"
        obj.pop("title_ru", "")

        for k in MASK_FIELDS:
            if k in obj:
                obj[k] = mask_process_compound(obj[k])
