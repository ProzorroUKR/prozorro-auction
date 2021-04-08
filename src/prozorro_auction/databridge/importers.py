import uuid

from abc import ABC, abstractmethod
from enum import Enum
from fractions import Fraction
from typing import Optional

from barbecue import calculate_coeficient, cooking


class AuctionType(Enum):
    DEFAULT = "default"
    MEAT = "meat"
    LCC = "lcc"


class AuctionAbstractBidImporter(ABC):

    @abstractmethod
    def import_auction_bid_data(self, value_container: Optional[dict] = None) -> dict:
        pass


class AuctionDefaultBidImporter(AuctionAbstractBidImporter):
    """
    Create auction bid data for auction.
    """

    def __init__(self, bid: dict, **kwargs) -> None:
        """
        :param bid: bid data
        """
        self._bid = bid

    def import_auction_bid_data(self, value_container: Optional[dict] = None) -> dict:
        """
        Create bid data for auction.

        :param value_container: lot values item data in case of multilot or bid data otherwise
        :return: auction bid data
        """
        value_container = value_container if value_container else self._bid
        return dict(
            id=self._bid["id"],
            hash=uuid.uuid4().hex,
            name=self._bid["tenderers"][0]["name"] if "tenderers" in self._bid else None,
            date=value_container["date"],
            value=value_container["value"],
        )


class AuctionMEATBidImporter(AuctionDefaultBidImporter):
    """
    Create auction bid data for MEAT auction.
    """

    def __init__(self, bid: dict, **kwargs):
        """
        :param bid: bid data
        :param features: features data list
        """
        super(AuctionMEATBidImporter, self).__init__(bid, **kwargs)
        self._features = kwargs.get("features", None)
        self._parameters = self._get_parameters()

    def import_auction_bid_data(self, value_container: Optional[dict] = None) -> dict:
        """
        Create auction bid data for MEAT auction.

        :param value_container: lot values item data in case of multilot or bid data otherwise
        :return: auction bid data
        """
        value_container = value_container if value_container else self._bid
        bid_data = super(AuctionMEATBidImporter, self).import_auction_bid_data(value_container=value_container)
        bid_data["parameters"] = self._parameters
        bid_data["coeficient"] = self._calculate_coeficient()
        bid_data["amount_features"] = self._calculate_amount_features(value_container)
        return bid_data

    def _get_parameters(self) -> list:
        codes = {feature["code"] for feature in self._features}
        parameters = self._bid.get("parameters", "")
        return [parameter for parameter in parameters if parameter["code"] in codes]

    def _calculate_coeficient(self) -> str:
        return str(calculate_coeficient(self._features, self._parameters))

    def _calculate_amount_features(self, value_container: dict) -> str:
        if self._is_esco(value_container):
            return self._calculate_esco_amount_features(value_container)
        else:
            return self._calculate_default_amount_features(value_container)

    def _is_esco(self, value_container: dict) -> bool:
        return "amountPerformance" in value_container["value"]

    def _calculate_esco_amount_features(self, value_container: dict) -> str:
        amount = str(Fraction(value_container["value"]["amountPerformance"]))
        return self._cook_amount_features(amount, True)

    def _calculate_default_amount_features(self, value_container: dict) -> str:
        amount = value_container["value"]["amount"]
        return self._cook_amount_features(amount, False)

    def _cook_amount_features(self, amount: float, reverse: bool) -> str:
        return str(cooking(amount, self._features, self._parameters, reverse=reverse))


class AuctionLCCBidImporter(AuctionDefaultBidImporter):
    """
    Create auction bid data for LCC auction.
    """

    def import_auction_bid_data(self, value_container: Optional[dict] = None) -> dict:
        """
        Create auction bid data for LCC auction.

        :param value_container: lot values item data in case of multilot or bid data otherwise
        :return: auction bid data
        """
        value_container = value_container if value_container else self._bid
        bid_data = super(AuctionLCCBidImporter, self).import_auction_bid_data(value_container=value_container)
        bid_data["amount_weighted"] = value_container["value"]["amount"]
        return bid_data


class AuctionDefaultBidImporterBuilder(object):

    def __call__(self, bid: dict) -> AuctionDefaultBidImporter:
        return AuctionDefaultBidImporter(bid)


class AuctionMEATBidImporterBuilder(object):

    def __init__(self, auction: dict) -> None:
        self._auction = auction

    def __call__(self, bid: dict) -> AuctionMEATBidImporter:
        importer_kwargs = self._build_meat_kwargs(bid)
        return AuctionMEATBidImporter(bid, **importer_kwargs)

    def _build_meat_kwargs(self, bid: dict) -> dict:
        features = self._auction["features"]
        parameters = bid.get("parameters", None)
        return dict(features=features, parameters=parameters)


class AuctionLCCBidImporterBuilder(object):

    def __call__(self, bid: dict) -> AuctionLCCBidImporter:
        return AuctionLCCBidImporter(bid)


class AuctionBidImporterFactory(object):

    def __init__(self, auction: dict) -> None:
        """
        Init bid importer factory
        
        :param auction: auction data
        """
        self._auction = auction
        self._builders = {
            AuctionType.DEFAULT: AuctionDefaultBidImporterBuilder(),
            AuctionType.MEAT: AuctionMEATBidImporterBuilder(auction),
            AuctionType.LCC: AuctionLCCBidImporterBuilder(),
        }

    def create(self, bid: dict) -> AuctionAbstractBidImporter:
        """
        Create Auction importer by auction type

        :param bid: bid data
        :return: auction factory
        """
        auction_type = self._auction["auction_type"]
        try:
            builder = self._builders[AuctionType(auction_type)]
        except (ValueError, KeyError):
            raise NotImplementedError(f"Auction type {auction_type} not implemented.")
        return builder(bid)
