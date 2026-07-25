"""
测试: MockRepository — Mock 文件读取、字段校验、引用完整性
"""
import pytest
from repository import MockRepository, reset_repository, MOCK_DIR


@pytest.fixture(autouse=True)
def reset():
    reset_repository()
    yield
    reset_repository()


def test_can_load_products():
    repo = MockRepository()
    products = repo.get_all_products()
    assert len(products) == 6
    assert all("id" in p for p in products)
    assert all("name" in p for p in products)


def test_can_find_product_by_id():
    repo = MockRepository()
    p = repo.get_product_by_id("prod_001")
    assert p is not None
    assert p["name"] == "戴森V15 Detect无绳吸尘器"


def test_product_not_found():
    repo = MockRepository()
    p = repo.get_product_by_id("nonexistent")
    assert p is None


def test_can_load_evidences():
    repo = MockRepository()
    evidences = repo.get_all_evidences()
    assert len(evidences) == 20


def test_evidences_by_product():
    repo = MockRepository()
    evds = repo.get_evidences_by_product("prod_001")
    assert len(evds) == 5


def test_evidence_by_id():
    repo = MockRepository()
    e = repo.get_evidence_by_id("evd_001")
    assert e is not None
    assert e["title"].startswith("6款高端吸尘器")


def test_evidence_not_found():
    repo = MockRepository()
    e = repo.get_evidence_by_id("nonexistent")
    assert e is None


def test_can_load_channels():
    repo = MockRepository()
    channels = repo.get_all_channels()
    assert len(channels) == 14


def test_channels_by_product():
    repo = MockRepository()
    chs = repo.get_channels_by_product("prod_001")
    assert len(chs) == 3


def test_can_load_comments():
    repo = MockRepository()
    comments = repo.get_all_comments()
    assert len(comments) == 5


def test_filter_by_category():
    repo = MockRepository()
    home_appliances = repo.get_products_by_category("家电")
    assert len(home_appliances) == 4
    digital = repo.get_products_by_category("数码")
    assert len(digital) == 2


def test_categories():
    repo = MockRepository()
    cats = repo.get_categories()
    assert len(cats) == 2
    names = {c["category_name"] for c in cats}
    assert names == {"家电", "数码"}


def test_category_profile_exists():
    repo = MockRepository()
    profile = repo.get_category_profile("家电")
    assert profile is not None
    assert profile["category_name"] == "家电"
    assert len(profile["dynamic_fields"]) > 0


def test_category_profile_not_found():
    repo = MockRepository()
    profile = repo.get_category_profile("nonexistent")
    assert profile is None


def test_validation_no_errors_on_good_data():
    repo = MockRepository()
    assert len(repo.errors) == 0
    assert repo.is_valid


def test_stats():
    repo = MockRepository()
    stats = repo.stats()
    assert stats["products"] == 6
    assert stats["evidences"] == 20
    assert stats["channels"] == 14
    assert stats["comments"] == 5
    assert stats["categories"] == 2
