from prozorro_auction.settings import MASK_OBJECT_DATA
from hashlib import sha224
import standards

MASK_IDENTIFIER_IDS = set(standards.load("organizations/mask_identifiers.json"))


def mask_simple_data(v):
    if isinstance(v, str):
        v = "0" * len(v)
    elif isinstance(v, bool):
        pass
    elif isinstance(v, int) or isinstance(v, float):
        v = 0
    return v


def ignore_mask(key):
    ignore_keys = {
        "id",
        "bidder_id",
        "start",
        "type",
        "currency",
        "kind",
    }
    if key in ignore_keys:
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
    identifier_id = obj.get("procuringEntity", {}).get("identifier", {}).get("id")
    if (
        MASK_OBJECT_DATA
        and identifier_id
        and sha224(identifier_id.encode()).hexdigest() in MASK_IDENTIFIER_IDS
        and "timer" not in obj  # finished
    ):
        obj["title"] = "Тимчасово замасковано, щоб русня не підглядала"
        obj["title_en"] = "It is temporarily disguised so that the rusnya does not spy"
        obj.pop("title_ru", "")

        for k in (
            "items", "features",
            "value", "minimalStep",
            "procuringEntity",
            "stages", "initial_bids", "results",
        ):
            if k in obj:
                obj[k] = mask_process_compound(obj[k])
