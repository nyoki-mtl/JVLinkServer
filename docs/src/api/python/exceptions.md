# 例外クラス

## 階層

```
JVLinkError
├── JVServerError
│   └── JVOpenError
├── JVConnectionError
├── JVTimeoutError
└── JVDataError
    ├── JVValidationError
    │   ├── JVInvalidDataSpecError
    │   ├── JVInvalidOptionError
    │   ├── JVInvalidFromTimeError
    │   ├── JVInvalidKeyError
    │   └── JVInvalidParameterError
    └── JVNoDataError
```

## 主な使い分け

- `JVConnectionError`: 接続不可、サーバー未起動
- `JVTimeoutError`: HTTP/ストリームの待機超過
- `JVOpenError`: JV-Link `JVOpen` 起因のエラー（`error_code` 参照）
- `JVValidationError` 系: DataSpec/日時/key/option 等の入力不正
- `JVDataError`: データ処理全般のエラー
- `JVNoDataError`: 互換用の no-data 例外。現在の `query_stored*` / `query_realtime*` は no-data を例外化せず、空の結果を返します

## 例

```python
from pyjvlink import Client
from pyjvlink.errors import (
    JVConnectionError,
    JVValidationError,
    JVOpenError,
    JVDataError,
)

try:
    async with Client() as client:
        await client.query_stored("RACE", "20240101", 1)
except JVConnectionError:
    ...
except JVValidationError:
    ...
except JVOpenError as err:
    print(err.error_code)
except JVDataError:
    ...
```
