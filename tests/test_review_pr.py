import pytest

from cert_review.pr_comment import _sanitize_warning


def test_sanitize_warning_strips_temp_prefix():
    w = ("clang-tidy: partial: /private/tmp/cert-review-work-abc/src/rgw/foo.cc")
    assert "`src/rgw/foo.cc`" in _sanitize_warning(w)


def test_review_pr_requires_git_repo(tmp_path):
    from cert_review import api
    (tmp_path / "src").mkdir()
    with pytest.raises(Exception):
        api.review_pr(str(tmp_path), "HEAD", "HEAD", profile="default")