"""
integration tests for mac_softwareupdate
"""

import pytest

from tests.support.case import ModuleCase
from tests.support.helpers import runs_on


@pytest.mark.skip_if_not_root
@runs_on(kernel="Darwin")
@pytest.mark.skip_if_binaries_missing("softwareupdate")
class MacSoftwareUpdateModuleTest(ModuleCase):
    """
    Validate the mac_softwareupdate module
    """

    IGNORED_LIST = []
    SCHEDULE = False
    CATALOG = ""

    def setUp(self):
        """
        Get current settings
        """
        self.IGNORED_LIST = self.run_function("softwareupdate.list_ignored")
        self.SCHEDULE = self.run_function("softwareupdate.schedule")
        self.CATALOG = self.run_function("softwareupdate.get_catalog")

        super().setUp()

    def tearDown(self):
        """
        Reset to original settings
        """
        if self.IGNORED_LIST:
            for item in self.IGNORED_LIST:
                self.run_function("softwareupdate.ignore", [item])
        else:
            self.run_function("softwareupdate.reset_ignored")

        self.run_function("softwareupdate.schedule", [self.SCHEDULE])

        if self.CATALOG == "Default":
            self.run_function("softwareupdate.reset_catalog")
        else:
            self.run_function("softwareupdate.set_catalog", [self.CATALOG])

        super().tearDown()

    @pytest.mark.slow_test
    def test_list_available(self):
        """
        Test softwareupdate.list_available
        """
        # Can't predict what will be returned, so can only test that the return
        # is the correct type, dict
        self.assertIsInstance(self.run_function("softwareupdate.list_available"), dict)

    @pytest.mark.destructive_test
    @pytest.mark.slow_test
    def test_ignore(self):
        """
        Test softwareupdate.ignore
        Test softwareupdate.list_ignored
        Test softwareupdate.reset_ignored
        """
        # Test reset_ignored
        self.assertTrue(self.run_function("softwareupdate.reset_ignored"))
        self.assertEqual(self.run_function("softwareupdate.list_ignored"), [])

        # Test ignore
        self.assertTrue(self.run_function("softwareupdate.ignore", ["spongebob"]))
        self.assertTrue(self.run_function("softwareupdate.ignore", ["squidward"]))

        # Test list_ignored and verify ignore
        self.assertIn("spongebob", self.run_function("softwareupdate.list_ignored"))
        self.assertIn("squidward", self.run_function("softwareupdate.list_ignored"))

    @pytest.mark.destructive_test
    @pytest.mark.slow_test
    def test_schedule(self):
        """
        Test softwareupdate.schedule_enable
        Test softwareupdate.schedule_enabled
        """
        # Test enable
        self.assertTrue(self.run_function("softwareupdate.schedule_enable", [True]))
        self.assertTrue(self.run_function("softwareupdate.schedule_enabled"))

        # Test disable in case it was already enabled
        self.assertTrue(self.run_function("softwareupdate.schedule_enable", [False]))
        self.assertFalse(self.run_function("softwareupdate.schedule_enabled"))

    @pytest.mark.destructive_test
    @pytest.mark.slow_test
    def test_update(self):
        """
        Test softwareupdate.update_all
        Test softwareupdate.update
        Test softwareupdate.update_available

        Need to know the names of updates that are available to properly test
        the update functions...
        """
        # There's no way to know what the dictionary will contain, so all we can
        # check is that the return is a dictionary
        self.assertIsInstance(self.run_function("softwareupdate.update_all"), dict)

        # Test update_available
        self.assertFalse(
            self.run_function("softwareupdate.update_available", ["spongebob"])
        )

        # Test update not available
        self.assertIn(
            "Update not available",
            self.run_function("softwareupdate.update", ["spongebob"]),
        )

    @pytest.mark.slow_test
    def test_list_downloads(self):
        """
        Test softwareupdate.list_downloads
        """
        self.assertIsInstance(self.run_function("softwareupdate.list_downloads"), list)

    @pytest.mark.destructive_test
    @pytest.mark.slow_test
    def test_download(self):
        """
        Test softwareupdate.download

        Need to know the names of updates that are available to properly test
        the download function
        """
        # Test update not available
        self.assertIn(
            "Update not available",
            self.run_function("softwareupdate.download", ["spongebob"]),
        )

    @pytest.mark.destructive_test
    @pytest.mark.slow_test
    def test_download_all(self):
        """
        Test softwareupdate.download_all
        """
        self.assertIsInstance(self.run_function("softwareupdate.download_all"), list)

    @pytest.mark.destructive_test
    @pytest.mark.slow_test
    def test_get_set_reset_catalog(self):
        """
        Test softwareupdate.download_all
        """
        # Reset the catalog
        self.assertTrue(self.run_function("softwareupdate.reset_catalog"))
        self.assertEqual(self.run_function("softwareupdate.get_catalog"), "Default")

        # Test setting and getting the catalog
        self.assertTrue(self.run_function("softwareupdate.set_catalog", ["spongebob"]))
        self.assertEqual(self.run_function("softwareupdate.get_catalog"), "spongebob")

        # Test reset the catalog
        self.assertTrue(self.run_function("softwareupdate.reset_catalog"))
        self.assertEqual(self.run_function("softwareupdate.get_catalog"), "Default")
