"""Public domain model exports."""

from pyjvlink._internal.domain.models.av import AVRecord
from pyjvlink._internal.domain.models.bn import BNPerformanceStatsItem, BNRecord
from pyjvlink._internal.domain.models.br import BRPerformanceStatsItem, BRRecord
from pyjvlink._internal.domain.models.bt import BTRecord
from pyjvlink._internal.domain.models.cc import CCRecord
from pyjvlink._internal.domain.models.ch import CHPerformanceStatsItem, CHRecentGradedWinsItem, CHRecord
from pyjvlink._internal.domain.models.ck import (
    CKBreederPerformanceStatsItem,
    CKJockeyPerformanceStatsItem,
    CKOwnerPerformanceStatsItem,
    CKRecord,
    CKTrainerPerformanceStatsItem,
)
from pyjvlink._internal.domain.models.common import MeetRecordBase
from pyjvlink._internal.domain.models.cs import CSRecord
from pyjvlink._internal.domain.models.dm import DMMiningPredictionsItem, DMRecord
from pyjvlink._internal.domain.models.h1 import (
    H1BracketQuinellaVotesItem,
    H1ExactaVotesItem,
    H1PlaceVotesItem,
    H1QuinellaVotesItem,
    H1Record,
    H1TrioVotesItem,
    H1WideVotesItem,
    H1WinVotesItem,
)
from pyjvlink._internal.domain.models.h6 import H6Record, H6TrifectaVotesItem
from pyjvlink._internal.domain.models.hc import HCRecord
from pyjvlink._internal.domain.models.hn import HNRecord
from pyjvlink._internal.domain.models.hr import (
    HRBracketQuinellaPaybackItem,
    HRExactaPaybackItem,
    HRPlacePaybackItem,
    HRQuinellaPaybackItem,
    HRRecord,
    HRTrifectaPaybackItem,
    HRTrioPaybackItem,
    HRWidePaybackItem,
    HRWinPaybackItem,
)
from pyjvlink._internal.domain.models.hs import HSRecord
from pyjvlink._internal.domain.models.hy import HYRecord
from pyjvlink._internal.domain.models.jc import JCRecord
from pyjvlink._internal.domain.models.jg import JGRecord
from pyjvlink._internal.domain.models.ks import (
    KSFirstRideInfoItem,
    KSFirstWinInfoItem,
    KSPerformanceStatsItem,
    KSRecentGradedWinsItem,
    KSRecord,
)
from pyjvlink._internal.domain.models.o1 import O1BracketQuinellaOddsItem, O1PlaceOddsItem, O1Record, O1WinOddsItem
from pyjvlink._internal.domain.models.o2 import O2QuinellaOddsItem, O2Record
from pyjvlink._internal.domain.models.o3 import O3Record, O3WideOddsItem
from pyjvlink._internal.domain.models.o4 import O4ExactaOddsItem, O4Record
from pyjvlink._internal.domain.models.o5 import O5Record, O5TrioOddsItem
from pyjvlink._internal.domain.models.o6 import O6Record, O6TrifectaOddsItem
from pyjvlink._internal.domain.models.ra import RACornerPassingOrderItem, RARecord
from pyjvlink._internal.domain.models.rc import RCRecord, RCRecordHoldersItem
from pyjvlink._internal.domain.models.se import SEOpponentHorsesItem, SERecord
from pyjvlink._internal.domain.models.sk import SKRecord
from pyjvlink._internal.domain.models.tc import TCRecord
from pyjvlink._internal.domain.models.tk import TKEntryHorsesItem, TKRecord
from pyjvlink._internal.domain.models.tm import TMMiningPredictionsItem, TMRecord
from pyjvlink._internal.domain.models.um import UMPedigree3GenItem, UMRecord
from pyjvlink._internal.domain.models.wc import WCRecord
from pyjvlink._internal.domain.models.we import WERecord
from pyjvlink._internal.domain.models.wf import WFPayoutInfoItem, WFRecord, WFTargetRacesItem
from pyjvlink._internal.domain.models.wh import WHHorseWeightInfosItem, WHRecord
from pyjvlink._internal.domain.models.ys import YSGradedRaceGuideItem, YSRecord
from pyjvlink._internal.protocol.models import UnknownRecord

DomainRecord = (
    AVRecord
    | BNRecord
    | BRRecord
    | BTRecord
    | CCRecord
    | CHRecord
    | CKRecord
    | CSRecord
    | DMRecord
    | H1Record
    | H6Record
    | HCRecord
    | HNRecord
    | HRRecord
    | HSRecord
    | HYRecord
    | JCRecord
    | JGRecord
    | KSRecord
    | O1Record
    | O2Record
    | O3Record
    | O4Record
    | O5Record
    | O6Record
    | RARecord
    | RCRecord
    | SERecord
    | SKRecord
    | TCRecord
    | TKRecord
    | TMRecord
    | UMRecord
    | WCRecord
    | WERecord
    | WFRecord
    | WHRecord
    | YSRecord
    | UnknownRecord
)

__all__ = [
    "AVRecord",
    "MeetRecordBase",
    "BNPerformanceStatsItem",
    "BNRecord",
    "BRPerformanceStatsItem",
    "BRRecord",
    "BTRecord",
    "CCRecord",
    "CHPerformanceStatsItem",
    "CHRecentGradedWinsItem",
    "CHRecord",
    "CKBreederPerformanceStatsItem",
    "CKJockeyPerformanceStatsItem",
    "CKOwnerPerformanceStatsItem",
    "CKRecord",
    "CKTrainerPerformanceStatsItem",
    "CSRecord",
    "DMMiningPredictionsItem",
    "DMRecord",
    "DomainRecord",
    "H1BracketQuinellaVotesItem",
    "H1ExactaVotesItem",
    "H1PlaceVotesItem",
    "H1QuinellaVotesItem",
    "H1Record",
    "H1TrioVotesItem",
    "H1WideVotesItem",
    "H1WinVotesItem",
    "H6Record",
    "H6TrifectaVotesItem",
    "HCRecord",
    "HNRecord",
    "HRBracketQuinellaPaybackItem",
    "HRExactaPaybackItem",
    "HRPlacePaybackItem",
    "HRQuinellaPaybackItem",
    "HRRecord",
    "HRTrifectaPaybackItem",
    "HRTrioPaybackItem",
    "HRWidePaybackItem",
    "HRWinPaybackItem",
    "HSRecord",
    "HYRecord",
    "JCRecord",
    "JGRecord",
    "KSFirstRideInfoItem",
    "KSFirstWinInfoItem",
    "KSPerformanceStatsItem",
    "KSRecentGradedWinsItem",
    "KSRecord",
    "O1BracketQuinellaOddsItem",
    "O1PlaceOddsItem",
    "O1Record",
    "O1WinOddsItem",
    "O2QuinellaOddsItem",
    "O2Record",
    "O3Record",
    "O3WideOddsItem",
    "O4ExactaOddsItem",
    "O4Record",
    "O5Record",
    "O5TrioOddsItem",
    "O6Record",
    "O6TrifectaOddsItem",
    "RACornerPassingOrderItem",
    "RARecord",
    "RCRecord",
    "RCRecordHoldersItem",
    "SEOpponentHorsesItem",
    "SERecord",
    "SKRecord",
    "TCRecord",
    "TKEntryHorsesItem",
    "TKRecord",
    "TMMiningPredictionsItem",
    "TMRecord",
    "UMPedigree3GenItem",
    "UMRecord",
    "UnknownRecord",
    "WCRecord",
    "WERecord",
    "WFPayoutInfoItem",
    "WFRecord",
    "WFTargetRacesItem",
    "WHHorseWeightInfosItem",
    "WHRecord",
    "YSGradedRaceGuideItem",
    "YSRecord",
]
