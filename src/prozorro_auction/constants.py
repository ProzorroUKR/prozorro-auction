from enum import Enum


class AuctionType(Enum):
    DEFAULT = "default"
    MEAT = "meat"
    LCC = "lcc"


class ProcurementMethodType(Enum):
    CLOSE_FRAMEWORK_AGREEMENT_UA = "closeFrameworkAgreementUA"
    CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA = "closeFrameworkAgreementSelectionUA"
    BELOW_THRESHOLD = "belowThreshold"
    ABOVE_THRESHOLD_EU = "aboveThresholdEU"
    ABOVE_THRESHOLD_UA = "aboveThresholdUA"
    ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"
    COMPETITIVE_DIALOGUE_EU_STAGE_2 = "competitiveDialogueEU.stage2"
    COMPETITIVE_DIALOGUE_UA_STAGE_2 = "competitiveDialogueUA.stage2"
    ESCO = "esco"
    SIMPLE_DEFENSE = "simple.defense"


class CriterionClassificationScheme(Enum):
    LCC = "LCC"


PROCUREMENT_METHOD_TYPES_DEFAULT = [
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA.value,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA.value,
    ProcurementMethodType.BELOW_THRESHOLD.value,
    ProcurementMethodType.ABOVE_THRESHOLD_EU.value,
    ProcurementMethodType.ABOVE_THRESHOLD_UA.value,
    ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE.value,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE_2.value,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE_2.value,
    ProcurementMethodType.ESCO.value,
    ProcurementMethodType.SIMPLE_DEFENSE.value,
]
