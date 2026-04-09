"""
JV-Reader の型定義
"""

import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum, IntEnum

from .errors import JVInvalidKeyError, JVInvalidParameterError


class JVDataSpec(str, Enum):
    """JV-Link データ種別"""

    # 蓄積系データ
    TOKU = "TOKU"  # 特別登録馬
    RACE = "RACE"  # レース情報
    DIFF = "DIFF"  # 蓄積系ソフト用蓄積情報
    DIFN = "DIFN"  # 蓄積系ソフト用蓄積情報（新版、サイズ拡張対応）
    BLOD = "BLOD"  # 蓄積系ソフト用血統情報
    BLDN = "BLDN"  # 蓄積系ソフト用血統情報（新版、サイズ拡張対応）
    MING = "MING"  # 蓄積系ソフト用マイニング情報
    SNAP = "SNAP"  # 出走時点情報
    SNPN = "SNPN"  # 出走時点情報（新版、サイズ拡張対応）
    SLOP = "SLOP"  # 坂路調教情報
    YSCH = "YSCH"  # 開催スケジュール
    HOSE = "HOSE"  # 競走馬市場取引価格情報
    HOSN = "HOSN"  # 競走馬市場取引価格情報（新版、サイズ拡張対応）
    HOYU = "HOYU"  # 馬名の意味由来情報
    COMM = "COMM"  # 各種解説情報
    WOOD = "WOOD"  # ウッドチップ調教情報
    TCOV = "TCOV"  # 非蓄積系ソフト用補てん情報（出走馬マスタ）
    TCVN = "TCVN"  # 非蓄積系ソフト用補てん情報（出走馬マスタ、新版・サイズ拡張対応）
    RCOV = "RCOV"  # 非蓄積系ソフト用補てん情報（出走予定馬マスタ）
    RCVN = "RCVN"  # 非蓄積系ソフト用補てん情報（出走予定馬マスタ、新版・サイズ拡張対応）

    # リアルタイム系データ
    BATAI = "0B11"  # 速報馬体重
    SOKHO_RACE_RESULT = "0B12"  # 速報レース情報（成績確定後）
    SOKHO_DATA_MINING = "0B13"  # 速報タイム型データマイニング予想
    SOKHO_KAISAI_BATCH = "0B14"  # 速報開催情報（一括）
    SOKHO_RACE_UMA = "0B15"  # 速報レース情報（出走馬名表～）
    SOKHO_KAISAI_SHITEI = "0B16"  # 速報開催情報（指定）
    SOKHO_DM_TAISEN = "0B17"  # 速報対戦型データマイニング予想
    SOKHO_HYOSU_ALL = "0B20"  # 速報票数（全賭式）
    SOKHO_ODDS_ALL = "0B30"  # 速報オッズ（全賭式）
    SOKHO_ODDS_TANFUKU = "0B31"  # 速報オッズ（単複枠）
    SOKHO_ODDS_UMAREN = "0B32"  # 速報オッズ（馬連）
    SOKHO_ODDS_WIDE = "0B33"  # 速報オッズ（ワイド）
    SOKHO_ODDS_UMATAN = "0B34"  # 速報オッズ（馬単）
    SOKHO_ODDS_SANRENPUKU = "0B35"  # 速報オッズ（3連複）
    SOKHO_ODDS_SANRENTAN = "0B36"  # 速報オッズ（3連単）
    JIKEI_ODDS_TANFUKU = "0B41"  # 時系列オッズ（単複枠）
    JIKEI_ODDS_UMAREN = "0B42"  # 時系列オッズ（馬連）
    SOKHO_WIN5 = "0B51"  # 速報重勝式（WIN5）


class QueryOption(IntEnum):
    """JVOpen option values for stored queries."""

    ACCUMULATED = 1
    WEEKLY = 2
    SETUP = 3
    SETUP_NO_DIALOG = 4


StoredDataspecValue = str | JVDataSpec
StoredDataspecInput = StoredDataspecValue | Sequence[StoredDataspecValue]


@dataclass(frozen=True, slots=True)
class RaceKeyParts:
    """Structured parts for a realtime race key."""

    meet_year: int
    meet_month: int
    meet_day_of_month: int
    racecourse_code: str
    race_number: int
    meet_round: int | None = None
    meet_day: int | None = None


RealtimeKeyInput = str | date | datetime | RaceKeyParts


def _require_key_int(name: str, value: object, *, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise JVInvalidKeyError(f"{name} must be an integer between {minimum} and {maximum}.")
    if not (minimum <= value <= maximum):
        raise JVInvalidKeyError(f"{name} must be between {minimum} and {maximum}, got {value}.")
    return value


def _normalize_racecourse_code(value: object) -> str:
    if not isinstance(value, str):
        raise JVInvalidKeyError("racecourse_code must be a 2-character string.")
    normalized = value.strip().upper()
    if len(normalized) != 2:
        raise JVInvalidKeyError(f"racecourse_code must be 2 characters, got '{value}'.")
    return normalized


def build_race_key_short(parts: RaceKeyParts) -> str:
    """Build a short realtime race key (YYYYMMDDJJRR)."""

    year = _require_key_int("meet_year", parts.meet_year, minimum=1, maximum=9999)
    month = _require_key_int("meet_month", parts.meet_month, minimum=1, maximum=12)
    day_of_month = _require_key_int("meet_day_of_month", parts.meet_day_of_month, minimum=1, maximum=31)
    race_number = _require_key_int("race_number", parts.race_number, minimum=1, maximum=99)
    racecourse_code = _normalize_racecourse_code(parts.racecourse_code)

    try:
        date(year, month, day_of_month)
    except ValueError as e:
        raise JVInvalidKeyError(
            f"Invalid race date: {year:04d}-{month:02d}-{day_of_month:02d}. Expected a real date."
        ) from e

    return f"{year:04d}{month:02d}{day_of_month:02d}{racecourse_code}{race_number:02d}"


def build_race_key(parts: RaceKeyParts) -> str:
    """Build a full realtime race key (YYYYMMDDJJKKHHRR)."""

    if parts.meet_round is None or parts.meet_day is None:
        raise JVInvalidKeyError("meet_round and meet_day are required to build a full race key.")

    short_key = build_race_key_short(parts)
    meet_round = _require_key_int("meet_round", parts.meet_round, minimum=1, maximum=99)
    meet_day = _require_key_int("meet_day", parts.meet_day, minimum=1, maximum=99)
    race_number = _require_key_int("race_number", parts.race_number, minimum=1, maximum=99)
    return f"{short_key[:10]}{meet_round:02d}{meet_day:02d}{race_number:02d}"


DATASPEC_TO_RECORDS: dict[JVDataSpec, tuple[str, ...]] = {
    # 蓄積系 (option=1) および セットアップ (option=3,4)
    JVDataSpec.TOKU: ("TK",),
    JVDataSpec.RACE: ("RA", "SE", "HR", "H1", "H6", "O1", "O2", "O3", "O4", "O5", "O6", "WF", "JG"),
    JVDataSpec.DIFF: ("UM", "KS", "CH", "BR", "BN", "RC", "RA", "SE"),
    JVDataSpec.DIFN: ("UM", "KS", "CH", "BR", "BN", "RC", "RA", "SE"),
    JVDataSpec.BLOD: ("HN", "SK", "BT"),
    JVDataSpec.BLDN: ("HN", "SK", "BT"),
    JVDataSpec.MING: ("DM", "TM"),
    JVDataSpec.SNAP: ("CK",),
    JVDataSpec.SNPN: ("CK",),
    JVDataSpec.SLOP: ("HC",),
    JVDataSpec.YSCH: ("YS",),
    JVDataSpec.HOSE: ("HS",),
    JVDataSpec.HOSN: ("HS",),
    JVDataSpec.HOYU: ("HY",),
    JVDataSpec.COMM: ("CS",),
    JVDataSpec.WOOD: ("WC",),
    # 週次 (option=2)
    JVDataSpec.TCOV: ("UM", "CH", "BR", "BN", "RC", "RA", "SE"),
    JVDataSpec.TCVN: ("UM", "CH", "BR", "BN", "RC", "RA", "SE"),
    JVDataSpec.RCOV: ("UM", "KS", "CH", "BR", "BN", "RC", "RA", "SE"),
    JVDataSpec.RCVN: ("UM", "KS", "CH", "BR", "BN", "RC", "RA", "SE"),
    # 速報系 (option=5, 7)
    JVDataSpec.SOKHO_RACE_RESULT: ("RA", "SE", "HR"),
    JVDataSpec.SOKHO_RACE_UMA: ("RA", "SE", "HR"),
    JVDataSpec.SOKHO_ODDS_ALL: ("O1", "O2", "O3", "O4", "O5", "O6"),
    JVDataSpec.SOKHO_ODDS_TANFUKU: ("O1",),
    JVDataSpec.SOKHO_ODDS_UMAREN: ("O2",),
    JVDataSpec.SOKHO_ODDS_WIDE: ("O3",),
    JVDataSpec.SOKHO_ODDS_UMATAN: ("O4",),
    JVDataSpec.SOKHO_ODDS_SANRENPUKU: ("O5",),
    JVDataSpec.SOKHO_ODDS_SANRENTAN: ("O6",),
    JVDataSpec.SOKHO_HYOSU_ALL: ("H1", "H6"),
    JVDataSpec.BATAI: ("WH",),
    JVDataSpec.SOKHO_KAISAI_BATCH: ("WE", "AV", "JC", "TC", "CC"),
    JVDataSpec.SOKHO_KAISAI_SHITEI: ("WE", "AV", "JC", "TC", "CC"),
    JVDataSpec.SOKHO_DATA_MINING: ("DM",),
    JVDataSpec.SOKHO_DM_TAISEN: ("TM",),
    JVDataSpec.JIKEI_ODDS_TANFUKU: ("O1",),
    JVDataSpec.JIKEI_ODDS_UMAREN: ("O2",),
    JVDataSpec.SOKHO_WIN5: ("WF",),
}
"""
データ種別とそれに含まれるレコード種別の対応。
`spec_datatypes.md` の「（１）蓄積系データ」「（２）速報系データ」などに基づいています。
"""

# リアルタイム系のデータ種別
REALTIME_DATASPECS = {
    JVDataSpec.BATAI,
    JVDataSpec.SOKHO_RACE_RESULT,
    JVDataSpec.SOKHO_DATA_MINING,
    JVDataSpec.SOKHO_KAISAI_BATCH,
    JVDataSpec.SOKHO_RACE_UMA,
    JVDataSpec.SOKHO_KAISAI_SHITEI,
    JVDataSpec.SOKHO_DM_TAISEN,
    JVDataSpec.SOKHO_HYOSU_ALL,
    JVDataSpec.SOKHO_ODDS_ALL,
    JVDataSpec.SOKHO_ODDS_TANFUKU,
    JVDataSpec.SOKHO_ODDS_UMAREN,
    JVDataSpec.SOKHO_ODDS_WIDE,
    JVDataSpec.SOKHO_ODDS_UMATAN,
    JVDataSpec.SOKHO_ODDS_SANRENPUKU,
    JVDataSpec.SOKHO_ODDS_SANRENTAN,
    JVDataSpec.JIKEI_ODDS_TANFUKU,
    JVDataSpec.JIKEI_ODDS_UMAREN,
    JVDataSpec.SOKHO_WIN5,
}


# オプションごとの有効なデータ種別
VALID_DATASPECS_BY_OPTION = {
    # option=1: 蓄積系データ
    1: {
        # 仕様: docs/jvlink/spec_datatypes.md の「JVOpenメソッドで指定可能なoptionとdataspec」
        JVDataSpec.TOKU,
        JVDataSpec.RACE,
        # 旧フォーマットとN拡張の双方を許容
        JVDataSpec.DIFF,
        JVDataSpec.DIFN,
        JVDataSpec.BLOD,
        JVDataSpec.BLDN,
        # 出走時点情報（両系）
        JVDataSpec.SNAP,
        JVDataSpec.SNPN,
        # その他
        JVDataSpec.SLOP,
        JVDataSpec.WOOD,
        JVDataSpec.YSCH,
        JVDataSpec.HOSE,
        JVDataSpec.HOSN,
        JVDataSpec.HOYU,
        JVDataSpec.COMM,
        JVDataSpec.MING,
    },
    # option=2: 今週データ
    2: {
        # 仕様: TCOV/RCOV と TCVN/RCVN の双方を許容。SNAP/SNPN も対象。
        JVDataSpec.TOKU,
        JVDataSpec.RACE,
        JVDataSpec.TCOV,
        JVDataSpec.TCVN,
        JVDataSpec.RCOV,
        JVDataSpec.RCVN,
        JVDataSpec.SNAP,
        JVDataSpec.SNPN,
    },
    # option=3: セットアップデータ
    3: {
        # 仕様: 3,4 は同一セット。旧フォーマットとN拡張の双方を許容。
        JVDataSpec.TOKU,
        JVDataSpec.RACE,
        JVDataSpec.DIFF,
        JVDataSpec.DIFN,
        JVDataSpec.BLOD,
        JVDataSpec.BLDN,
        JVDataSpec.SNAP,
        JVDataSpec.SNPN,
        JVDataSpec.SLOP,
        JVDataSpec.WOOD,
        JVDataSpec.YSCH,
        JVDataSpec.HOSE,
        JVDataSpec.HOSN,
        JVDataSpec.HOYU,
        JVDataSpec.COMM,
        JVDataSpec.MING,
    },
    # option=4: ダイアログ無しセットアップデータ（仕様上 option=3 と同等のセット）
    4: {
        JVDataSpec.TOKU,
        JVDataSpec.RACE,
        JVDataSpec.DIFF,
        JVDataSpec.DIFN,
        JVDataSpec.BLOD,
        JVDataSpec.BLDN,
        JVDataSpec.SNAP,
        JVDataSpec.SNPN,
        JVDataSpec.SLOP,
        JVDataSpec.WOOD,
        JVDataSpec.YSCH,
        JVDataSpec.HOSE,
        JVDataSpec.HOSN,
        JVDataSpec.HOYU,
        JVDataSpec.COMM,
        JVDataSpec.MING,
    },
}


def _get_host_default() -> str:
    """環境変数からホストを取得"""
    value = os.environ.get("JVLINK_SERVER_HOST", "127.0.0.1").strip()
    return value or "127.0.0.1"


def _parse_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as e:
        raise JVInvalidParameterError(f"{name} must be an integer, got '{raw}'.") from e


def _get_port_default() -> int:
    """環境変数からポートを取得"""
    return _parse_int_env("JVLINK_SERVER_PORT", 8765)


def _get_timeout_default() -> int:
    """環境変数からHTTPタイムアウトを取得（秒）"""
    return _parse_int_env("JVLINK_HTTP_TIMEOUT", 60)


def _get_stream_read_timeout_default() -> int:
    """環境変数からストリーミング読み取りタイムアウトを取得（秒）"""
    return _parse_int_env("JVLINK_STREAM_READ_TIMEOUT", 300)  # デフォルト5分


def _get_sid_default() -> str:
    """環境変数からJVInit用のSIDを取得"""
    value = os.environ.get("JVLINK_SID", "UNKNOWN")
    return value


def _require_str(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise JVInvalidParameterError(f"{name} must be a string, got {type(value).__name__}.")
    return value


def _require_int(name: str, value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise JVInvalidParameterError(f"{name} must be an integer, got {type(value).__name__}.")
    return value


def _require_bool(name: str, value: object) -> bool:
    if not isinstance(value, bool):
        raise JVInvalidParameterError(f"{name} must be a boolean, got {type(value).__name__}.")
    return value


@dataclass
class JVServerConfig:
    """JV-Link サーバー設定"""

    host: str = field(default_factory=_get_host_default)
    port: int = field(default_factory=_get_port_default)
    timeout: int = field(default_factory=_get_timeout_default)  # HTTPタイムアウト（秒）
    stream_read_timeout: int = field(
        default_factory=_get_stream_read_timeout_default
    )  # ストリーミング読み取りタイムアウト（秒）
    sid: str = field(default_factory=_get_sid_default)  # JVInit時に使用するSID
    startup_timeout: int = 30  # JV-Link COM初期化
    log_level: str = "warn"  # ログレベル: debug, info, warn, error (デフォルト: warn)
    api_version: str = "v1"  # APIバージョン: v1 (デフォルト)
    # JV-Link破損ファイル自動リトライ設定
    auto_retry: bool = True  # 破損ファイル時の自動リトライ（デフォルト: 有効）
    max_retries: int = 3  # 最大リトライ回数（デフォルト: 3）
    retry_delay_ms: int = 1000  # リトライ間隔（ミリ秒、デフォルト: 1000）
    busy_retry_enabled: bool = False  # busy(-202)時の自動リトライ（デフォルト: 無効）
    busy_max_retries: int = 3  # busy時の最大リトライ回数
    busy_backoff_ms: int = 1000  # busy時の待機時間（ミリ秒）
    respect_retry_after: bool = True  # Retry-Afterヘッダーを優先する

    def __post_init__(self) -> None:
        self.host = _require_str("host", self.host).strip()
        self.port = _require_int("port", self.port)
        self.timeout = _require_int("timeout", self.timeout)
        self.stream_read_timeout = _require_int("stream_read_timeout", self.stream_read_timeout)
        self.sid = _require_str("sid", self.sid)
        self.startup_timeout = _require_int("startup_timeout", self.startup_timeout)
        self.log_level = _require_str("log_level", self.log_level).lower()
        self.api_version = _require_str("api_version", self.api_version).strip()
        self.auto_retry = _require_bool("auto_retry", self.auto_retry)
        self.max_retries = _require_int("max_retries", self.max_retries)
        self.retry_delay_ms = _require_int("retry_delay_ms", self.retry_delay_ms)
        self.busy_retry_enabled = _require_bool("busy_retry_enabled", self.busy_retry_enabled)
        self.busy_max_retries = _require_int("busy_max_retries", self.busy_max_retries)
        self.busy_backoff_ms = _require_int("busy_backoff_ms", self.busy_backoff_ms)
        self.respect_retry_after = _require_bool("respect_retry_after", self.respect_retry_after)

        if not self.host:
            raise JVInvalidParameterError("host must not be empty.")
        if not (1 <= self.port <= 65535):
            raise JVInvalidParameterError(f"port must be between 1 and 65535, got {self.port}.")
        if self.timeout <= 0:
            raise JVInvalidParameterError(f"timeout must be > 0, got {self.timeout}.")
        if self.stream_read_timeout <= 0:
            raise JVInvalidParameterError(f"stream_read_timeout must be > 0, got {self.stream_read_timeout}.")
        if not self.sid:
            raise JVInvalidParameterError("sid must not be empty.")
        if self.sid.startswith(" "):
            raise JVInvalidParameterError("sid must not start with a space.")
        if len(self.sid.encode("utf-8")) > 64:
            raise JVInvalidParameterError("sid must be 64 bytes or less in UTF-8 encoding.")
        if self.startup_timeout <= 0:
            raise JVInvalidParameterError(f"startup_timeout must be > 0, got {self.startup_timeout}.")

        valid_log_levels = {"debug", "info", "warn", "error"}
        if self.log_level not in valid_log_levels:
            raise JVInvalidParameterError(
                f"log_level must be one of {', '.join(sorted(valid_log_levels))}, got '{self.log_level}'."
            )

        if not self.api_version:
            raise JVInvalidParameterError("api_version must not be empty.")
        if self.max_retries < 0:
            raise JVInvalidParameterError(f"max_retries must be >= 0, got {self.max_retries}.")
        if self.retry_delay_ms < 0:
            raise JVInvalidParameterError(f"retry_delay_ms must be >= 0, got {self.retry_delay_ms}.")
        if self.busy_max_retries < 0:
            raise JVInvalidParameterError(f"busy_max_retries must be >= 0, got {self.busy_max_retries}.")
        if self.busy_backoff_ms < 0:
            raise JVInvalidParameterError(f"busy_backoff_ms must be >= 0, got {self.busy_backoff_ms}.")
