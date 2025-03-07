import os.path

import pytest

import salt.modules.archive as archive
from salt.exceptions import CommandNotFoundError
from tests.support.mock import MagicMock, patch


class ZipFileMock(MagicMock):
    def __init__(self, files=None, **kwargs):  # pylint: disable=W0231
        if files is None:
            files = ["salt"]
        MagicMock.__init__(self, **kwargs)
        self._files = files
        self.external_attr = 0o0777 << 16

    def namelist(self):
        return self._files


@pytest.fixture
def configure_loader_modules():
    return {archive: {"__grains__": {"id": 0}}}


def test_tar():
    with patch("glob.glob", lambda pathname: [pathname]):
        with patch("salt.utils.path.which", lambda exe: exe):
            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.tar(
                    "-zcvf",
                    "foo.tar",
                    ["/tmp/something-to-compress-1", "/tmp/something-to-compress-2"],
                    template=None,
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "tar",
                        "-zcvf",
                        "foo.tar",
                        "/tmp/something-to-compress-1",
                        "/tmp/something-to-compress-2",
                    ],
                    runas=None,
                    python_shell=False,
                    template=None,
                    cwd=None,
                )

            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.tar(
                    "-zcvf",
                    "foo.tar",
                    "/tmp/something-to-compress-1,/tmp/something-to-compress-2",
                    template=None,
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "tar",
                        "-zcvf",
                        "foo.tar",
                        "/tmp/something-to-compress-1",
                        "/tmp/something-to-compress-2",
                    ],
                    runas=None,
                    python_shell=False,
                    template=None,
                    cwd=None,
                )


def test_tar_raises_exception_if_not_found():
    with patch("salt.utils.path.which", lambda exe: None):
        mock = MagicMock(return_value="salt")
        with patch.dict(archive.__salt__, {"cmd.run": mock}):
            with pytest.raises(CommandNotFoundError):
                archive.tar("zxvf", "foo.tar", "/tmp/something-to-compress")
            assert not mock.called


def test_gzip():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: exe):
            ret = archive.gzip("/tmp/something-to-compress")
            assert ["salt"] == ret
            mock.assert_called_once_with(
                ["gzip", "/tmp/something-to-compress"],
                runas=None,
                python_shell=False,
                template=None,
            )


def test_gzip_raises_exception_if_not_found():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: None):
            with pytest.raises(CommandNotFoundError):
                archive.gzip("/tmp/something-to-compress")
            assert not mock.called


def test_gunzip():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: exe):
            ret = archive.gunzip("/tmp/something-to-decompress.tar.gz")
            assert ["salt"] == ret
            mock.assert_called_once_with(
                ["gunzip", "/tmp/something-to-decompress.tar.gz"],
                runas=None,
                python_shell=False,
                template=None,
            )


def test_gunzip_raises_exception_if_not_found():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: None):
            with pytest.raises(CommandNotFoundError):
                archive.gunzip("/tmp/something-to-decompress.tar.gz")
            assert not mock.called


def test_cmd_zip():
    with patch("glob.glob", lambda pathname: [pathname]):
        with patch("salt.utils.path.which", lambda exe: exe):
            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.cmd_zip(
                    "/tmp/salt.{{grains.id}}.zip",
                    "/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
                    template="jinja",
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "zip",
                        "-r",
                        "/tmp/salt.{{grains.id}}.zip",
                        "/tmp/tmpePe8yO",
                        "/tmp/tmpLeSw1A",
                    ],
                    runas=None,
                    python_shell=False,
                    template="jinja",
                    cwd=None,
                )

            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.cmd_zip(
                    "/tmp/salt.{{grains.id}}.zip",
                    ["/tmp/tmpePe8yO", "/tmp/tmpLeSw1A"],
                    template="jinja",
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "zip",
                        "-r",
                        "/tmp/salt.{{grains.id}}.zip",
                        "/tmp/tmpePe8yO",
                        "/tmp/tmpLeSw1A",
                    ],
                    runas=None,
                    python_shell=False,
                    template="jinja",
                    cwd=None,
                )


def test_zip():
    with patch("glob.glob", lambda pathname: [pathname]):
        with patch.multiple(
            os.path,
            **{
                "isdir": MagicMock(return_value=False),
                "exists": MagicMock(return_value=True),
            }
        ):
            with patch("zipfile.ZipFile", MagicMock()):
                ret = archive.zip_(
                    "/tmp/salt.{{grains.id}}.zip",
                    "/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
                    template="jinja",
                )
                expected = [
                    os.path.join("tmp", "tmpePe8yO"),
                    os.path.join("tmp", "tmpLeSw1A"),
                ]
                assert expected == ret


def test_zip_raises_exception_if_not_found():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: None):
            with pytest.raises(CommandNotFoundError):
                archive.cmd_zip(
                    "/tmp/salt.{{grains.id}}.zip",
                    "/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
                    template="jinja",
                )
            assert not mock.called


def test_cmd_unzip():
    def _get_mock():
        """
        Create a new MagicMock for each scenario in this test, so that
        assert_called_once_with doesn't complain that the same mock object
        is called more than once.
        """
        return MagicMock(
            return_value={"stdout": "salt", "stderr": "", "pid": 12345, "retcode": 0}
        )

    with patch("salt.utils.path.which", lambda exe: exe):

        mock = _get_mock()
        with patch.dict(archive.__salt__, {"cmd.run_all": mock}):
            ret = archive.cmd_unzip(
                "/tmp/salt.{{grains.id}}.zip",
                "/tmp/dest",
                excludes="/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
                template="jinja",
            )
            assert ["salt"] == ret
            mock.assert_called_once_with(
                [
                    "unzip",
                    "/tmp/salt.{{grains.id}}.zip",
                    "-d",
                    "/tmp/dest",
                    "-x",
                    "/tmp/tmpePe8yO",
                    "/tmp/tmpLeSw1A",
                ],
                output_loglevel="debug",
                python_shell=False,
                redirect_stderr=True,
                runas=None,
                template="jinja",
            )

        mock = _get_mock()
        with patch.dict(archive.__salt__, {"cmd.run_all": mock}):
            ret = archive.cmd_unzip(
                "/tmp/salt.{{grains.id}}.zip",
                "/tmp/dest",
                excludes=["/tmp/tmpePe8yO", "/tmp/tmpLeSw1A"],
                template="jinja",
            )
            assert ["salt"] == ret
            mock.assert_called_once_with(
                [
                    "unzip",
                    "/tmp/salt.{{grains.id}}.zip",
                    "-d",
                    "/tmp/dest",
                    "-x",
                    "/tmp/tmpePe8yO",
                    "/tmp/tmpLeSw1A",
                ],
                output_loglevel="debug",
                python_shell=False,
                redirect_stderr=True,
                runas=None,
                template="jinja",
            )

        mock = _get_mock()
        with patch.dict(archive.__salt__, {"cmd.run_all": mock}):
            ret = archive.cmd_unzip(
                "/tmp/salt.{{grains.id}}.zip",
                "/tmp/dest",
                excludes="/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
                template="jinja",
                options="-fo",
            )
            assert ["salt"] == ret
            mock.assert_called_once_with(
                [
                    "unzip",
                    "-fo",
                    "/tmp/salt.{{grains.id}}.zip",
                    "-d",
                    "/tmp/dest",
                    "-x",
                    "/tmp/tmpePe8yO",
                    "/tmp/tmpLeSw1A",
                ],
                output_loglevel="debug",
                python_shell=False,
                redirect_stderr=True,
                runas=None,
                template="jinja",
            )

        mock = _get_mock()
        with patch.dict(archive.__salt__, {"cmd.run_all": mock}):
            ret = archive.cmd_unzip(
                "/tmp/salt.{{grains.id}}.zip",
                "/tmp/dest",
                excludes=["/tmp/tmpePe8yO", "/tmp/tmpLeSw1A"],
                template="jinja",
                options="-fo",
            )
            assert ["salt"] == ret
            mock.assert_called_once_with(
                [
                    "unzip",
                    "-fo",
                    "/tmp/salt.{{grains.id}}.zip",
                    "-d",
                    "/tmp/dest",
                    "-x",
                    "/tmp/tmpePe8yO",
                    "/tmp/tmpLeSw1A",
                ],
                output_loglevel="debug",
                python_shell=False,
                redirect_stderr=True,
                runas=None,
                template="jinja",
            )

        mock = _get_mock()
        with patch.dict(archive.__salt__, {"cmd.run_all": mock}):
            ret = archive.cmd_unzip(
                "/tmp/salt.{{grains.id}}.zip",
                "/tmp/dest",
                excludes=["/tmp/tmpePe8yO", "/tmp/tmpLeSw1A"],
                template="jinja",
                options="-fo",
                password="asdf",
            )
            assert ["salt"] == ret
            mock.assert_called_once_with(
                [
                    "unzip",
                    "-P",
                    "asdf",
                    "-fo",
                    "/tmp/salt.{{grains.id}}.zip",
                    "-d",
                    "/tmp/dest",
                    "-x",
                    "/tmp/tmpePe8yO",
                    "/tmp/tmpLeSw1A",
                ],
                output_loglevel="quiet",
                python_shell=False,
                redirect_stderr=True,
                runas=None,
                template="jinja",
            )


def test_unzip():
    mock = ZipFileMock()
    with patch("zipfile.ZipFile", mock):
        ret = archive.unzip(
            "/tmp/salt.{{grains.id}}.zip",
            "/tmp/dest",
            excludes="/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
            template="jinja",
            extract_perms=False,
        )
        assert ["salt"] == ret


def test_unzip_raises_exception_if_not_found():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: None):
            with pytest.raises(CommandNotFoundError):
                archive.cmd_unzip(
                    "/tmp/salt.{{grains.id}}.zip",
                    "/tmp/dest",
                    excludes="/tmp/tmpePe8yO,/tmp/tmpLeSw1A",
                    template="jinja",
                )
            assert not mock.called


def test_rar():
    with patch("glob.glob", lambda pathname: [pathname]):
        with patch("salt.utils.path.which", lambda exe: exe):
            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.rar(
                    "/tmp/rarfile.rar", "/tmp/sourcefile1,/tmp/sourcefile2"
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "rar",
                        "a",
                        "-idp",
                        "/tmp/rarfile.rar",
                        "/tmp/sourcefile1",
                        "/tmp/sourcefile2",
                    ],
                    runas=None,
                    python_shell=False,
                    template=None,
                    cwd=None,
                )

            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.rar(
                    "/tmp/rarfile.rar", ["/tmp/sourcefile1", "/tmp/sourcefile2"]
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "rar",
                        "a",
                        "-idp",
                        "/tmp/rarfile.rar",
                        "/tmp/sourcefile1",
                        "/tmp/sourcefile2",
                    ],
                    runas=None,
                    python_shell=False,
                    template=None,
                    cwd=None,
                )


def test_rar_raises_exception_if_not_found():
    mock = MagicMock(return_value="salt")
    with patch.dict(archive.__salt__, {"cmd.run": mock}):
        with patch("salt.utils.path.which", lambda exe: None):
            with pytest.raises(CommandNotFoundError):
                archive.rar("/tmp/rarfile.rar", "/tmp/sourcefile1,/tmp/sourcefile2")
            assert not mock.called


@pytest.mark.skip_if_binaries_missing("unrar", "rar", reason="unrar not installed")
def test_unrar():
    with patch(
        "salt.utils.path.which_bin",
        lambda exe: exe[0] if isinstance(exe, (list, tuple)) else exe,
    ):
        with patch(
            "salt.utils.path.which",
            lambda exe: exe[0] if isinstance(exe, (list, tuple)) else exe,
        ):
            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.unrar(
                    "/tmp/rarfile.rar", "/home/strongbad/", excludes="file_1,file_2"
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "unrar",
                        "x",
                        "-idp",
                        "/tmp/rarfile.rar",
                        "-x",
                        "file_1",
                        "-x",
                        "file_2",
                        "/home/strongbad/",
                    ],
                    runas=None,
                    python_shell=False,
                    template=None,
                )

            mock = MagicMock(return_value="salt")
            with patch.dict(archive.__salt__, {"cmd.run": mock}):
                ret = archive.unrar(
                    "/tmp/rarfile.rar",
                    "/home/strongbad/",
                    excludes=["file_1", "file_2"],
                )
                assert ["salt"] == ret
                mock.assert_called_once_with(
                    [
                        "unrar",
                        "x",
                        "-idp",
                        "/tmp/rarfile.rar",
                        "-x",
                        "file_1",
                        "-x",
                        "file_2",
                        "/home/strongbad/",
                    ],
                    runas=None,
                    python_shell=False,
                    template=None,
                )


def test_unrar_raises_exception_if_not_found():
    with patch("salt.utils.path.which_bin", lambda exe: None):
        mock = MagicMock(return_value="salt")
        with patch.dict(archive.__salt__, {"cmd.run": mock}):
            with pytest.raises(CommandNotFoundError):
                archive.unrar(
                    "/tmp/rarfile.rar",
                    "/home/strongbad/",
                )
            assert not mock.called


def test_trim_files():
    with patch("salt.utils.path.which_bin", lambda exe: exe):
        source = "file.tar.gz"
        tmp_dir = "temp"
        files = [
            "\n".join(["file1"] * 200),
            "\n".join(["file2"] * 200),
            "this\nthat\nother",
            "this\nthat\nother",
            "this\nthat\nother",
        ]
        trim_opt = [True, False, 3, 1, 0]
        trim_100 = ["file1"] * 100
        trim_100.append("List trimmed after 100 files.")
        expected = [
            trim_100,
            ["file2"] * 200,
            ["this", "that", "other"],
            ["this", "List trimmed after 1 files."],
            ["List trimmed after 0 files."],
        ]

        for test_files, test_trim_opts, test_expected in zip(files, trim_opt, expected):
            with patch.dict(
                archive.__salt__, {"cmd.run": MagicMock(return_value=test_files)}
            ):
                ret = archive.unrar(source, tmp_dir, trim_output=test_trim_opts)
                assert ret == test_expected
