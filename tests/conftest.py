import shutil
import pytest

need_clang_tidy = pytest.mark.skipif(shutil.which("clang-tidy") is None, reason="clang-tidy not installed")
need_cppcheck = pytest.mark.skipif(shutil.which("cppcheck") is None, reason="cppcheck not installed")
