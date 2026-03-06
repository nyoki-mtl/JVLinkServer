"""
pytest設定ファイル
環境変数によるテストスキップなどの共通設定
"""

import os

import pytest


def pytest_configure(config):
    """pytest設定時のフック"""
    # カスタムマーカーの登録
    config.addinivalue_line("markers", "requires_jvlink: mark test as requiring JVLinkServer connection")


def pytest_collection_modifyitems(config, items):
    """テストコレクション時のフック"""
    if os.getenv("JVLINK_SKIP_TESTS") == "true":
        skip_marker = pytest.mark.skip(reason="Skipping tests that require JVLinkServer (JVLINK_SKIP_TESTS=true)")
        for item in items:
            # すべてのテストをスキップ
            item.add_marker(skip_marker)
