from enum import Enum


class AuctionType(Enum):
    DEFAULT = "default"
    MEAT = "meat"
    LCC = "lcc"
    MIXED = "mixed"


class ProcurementMethodType(Enum):
    CLOSE_FRAMEWORK_AGREEMENT_UA = "closeFrameworkAgreementUA"
    CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA = "closeFrameworkAgreementSelectionUA"
    BELOW_THRESHOLD = "belowThreshold"
    ABOVE_THRESHOLD = "aboveThreshold"
    ABOVE_THRESHOLD_EU = "aboveThresholdEU"
    ABOVE_THRESHOLD_UA = "aboveThresholdUA"
    ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"
    COMPETITIVE_DIALOGUE_EU_STAGE_2 = "competitiveDialogueEU.stage2"
    COMPETITIVE_DIALOGUE_UA_STAGE_2 = "competitiveDialogueUA.stage2"
    ESCO = "esco"
    SIMPLE_DEFENSE = "simple.defense"


class CriterionClassificationID(Enum):
    CRITERION_OTHER_LIFE_CYCLE_COST_COST_OF_USE = "CRITERION.OTHER.LIFE_CYCLE_COST.COST_OF_USE"
    CRITERION_OTHER_LIFE_CYCLE_COST_MAINTENANCE_COST = "CRITERION.OTHER.LIFE_CYCLE_COST.MAINTENANCE_COST"
    CRITERION_OTHER_LIFE_CYCLE_COST_END_OF_LIFE_COST = "CRITERION.OTHER.LIFE_CYCLE_COST.END_OF_LIFE_COST"
    CRITERION_OTHER_LIFE_CYCLE_COST_ECOLOGICAL_COST = "CRITERION.OTHER.LIFE_CYCLE_COST.ECOLOGICAL_COST"

CRITERIA_LCC = [
    CriterionClassificationID.CRITERION_OTHER_LIFE_CYCLE_COST_COST_OF_USE.value,
    CriterionClassificationID.CRITERION_OTHER_LIFE_CYCLE_COST_MAINTENANCE_COST.value,
    CriterionClassificationID.CRITERION_OTHER_LIFE_CYCLE_COST_END_OF_LIFE_COST.value,
    CriterionClassificationID.CRITERION_OTHER_LIFE_CYCLE_COST_ECOLOGICAL_COST.value,
]

PROCUREMENT_METHOD_TYPES_DEFAULT = [
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA.value,
    ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA.value,
    ProcurementMethodType.BELOW_THRESHOLD.value,
    ProcurementMethodType.ABOVE_THRESHOLD.value,
    ProcurementMethodType.ABOVE_THRESHOLD_EU.value,
    ProcurementMethodType.ABOVE_THRESHOLD_UA.value,
    ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE.value,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE_2.value,
    ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE_2.value,
    ProcurementMethodType.ESCO.value,
    ProcurementMethodType.SIMPLE_DEFENSE.value,
]
