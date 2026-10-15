# 验证英文发行版筛选、版本排序及不回退上游下载的边界。
import json
from unittest.mock import patch

import pytest

from src.app.constants import GITHUB_RELEASES_API_URL, GITHUB_RELEASES_URL
from src.features.settings.updates import fetch_update_info, is_newer_version


def release(version="2.3.1-english.1", **overrides):
    tag = f"v{version}"
    result = {
        "tag_name": tag,
        "prerelease": True,
        "draft": False,
        "body": "English build",
        "assets": [{
            "name": f"NTE_Drive_Calc_English_Setup_{version}.exe",
            "state": "uploaded",
            "browser_download_url": f"{GITHUB_RELEASES_URL}/download/{tag}/installer.exe",
        }],
    }
    result.update(overrides)
    return result


def fetch(payload, current="2.3.1-english.1"):
    with patch("src.features.settings.updates.urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
        result = fetch_update_info(GITHUB_RELEASES_API_URL, current)
        request = urlopen.call_args.args[0]
        assert request.full_url == GITHUB_RELEASES_API_URL
        assert "cdk" not in request.full_url
        return result


def test_published_english_prerelease_is_downloadable_without_cdk():
    info = fetch([release()])
    assert info["has_release"]
    assert not info["newer"]
    assert info["latest"] == "2.3.1-english.1"
    assert info["release_url"] == f"{GITHUB_RELEASES_URL}/tag/v2.3.1-english.1"


def test_highest_english_revision_wins_independent_of_api_order():
    info = fetch([release("2.3.1-english.2"), release("2.3.1-english.10"), release()])
    assert info["latest"] == "2.3.1-english.10"
    assert info["newer"]


@pytest.mark.parametrize("payload", [
    [],
    [release(draft=True)],
    [release(assets=[])],
    [release("9.0.0")],
    [None, "not a release", {}],
])
def test_missing_unpublished_or_non_english_installers_do_not_offer_an_update(payload):
    info = fetch(payload)
    assert not info["has_release"]
    assert not info["newer"]
    assert info["url"] == ""


@pytest.mark.parametrize("asset", [
    {"name": "nte-core.exe", "state": "uploaded", "browser_download_url": f"{GITHUB_RELEASES_URL}/download/v2.3.1-english.1/core.exe"},
    {"name": "NTE_Drive_Calc_English_Setup_2.3.1-english.1.exe", "state": "new", "browser_download_url": f"{GITHUB_RELEASES_URL}/download/v2.3.1-english.1/installer.exe"},
    {"name": "NTE_Drive_Calc_English_Setup_2.3.1-english.1.exe", "state": "uploaded", "browser_download_url": "https://github.com/hxwd94666/NTE-Drive-Calculator/releases/download/v2.3.1/installer.exe"},
])
def test_wrong_binary_incomplete_asset_or_upstream_download_is_rejected(asset):
    assert not fetch([release(assets=[asset])])["has_release"]


def test_new_upstream_baseline_takes_priority_over_english_revision():
    assert is_newer_version("2.3.2-english.1", "2.3.1-english.99")
    assert is_newer_version("2.3.1-english.2", "2.3.1-english.1")
    assert not is_newer_version("2.3.1-english.1", "2.3.1-english.2")
