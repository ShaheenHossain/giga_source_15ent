# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
import json
import base64

from freezegun import freeze_time
from uuid import uuid4

from .common import SpreadsheetTestCommon, TEXT
from giga.tests.common import new_test_user, tagged
from giga.exceptions import AccessError


@tagged("collaborative_spreadsheet")
class SpreadsheetCollaborative(SpreadsheetTestCommon):
    def test_compute_revision_without_session(self):
        spreadsheet = self.create_spreadsheet()
        self.assertEqual(self.get_revision(spreadsheet), "START_REVISION")

    def test_compute_revision_with_session(self):
        spreadsheet = self.create_spreadsheet()
        spreadsheet.join_spreadsheet_session()
        commands = self.new_revision_data(spreadsheet)
        spreadsheet.dispatch_spreadsheet_message(commands)
        revision_data2 = self.new_revision_data(spreadsheet, nextRevisionId="nextone")
        spreadsheet.dispatch_spreadsheet_message(revision_data2)
        self.assertEqual(self.get_revision(spreadsheet), "nextone")

    def test_dispatch_new_revision(self):
        spreadsheet = self.create_spreadsheet()
        commands = self.new_revision_data(spreadsheet)
        spreadsheet.join_spreadsheet_session()
        spreadsheet.dispatch_spreadsheet_message(commands)
        self.assertEqual(
            len(spreadsheet.spreadsheet_revision_ids),
            1,
            "It should have recorded one revision",
        )
        self.assertEqual(
            self.get_revision(spreadsheet),
            commands["nextRevisionId"],
            "It should have updated its revision",
        )
        self.assertEqual(
            json.loads(spreadsheet.spreadsheet_revision_ids.commands),
            {"commands": commands["commands"], "type": commands["type"]},
            "It should have saved the revision data",
        )

    def test_dispatch_revision_concurrent_first_revision_id(self):
        spreadsheet = self.create_spreadsheet()
        spreadsheet.join_spreadsheet_session()
        start_revision = self.get_revision(spreadsheet)
        revision1 = self.new_revision_data(spreadsheet, serverRevisionId=start_revision)
        spreadsheet.dispatch_spreadsheet_message(revision1)
        self.assertEqual(
            len(spreadsheet.spreadsheet_revision_ids),
            1,
            "It should have recorded the revision",
        )
        revision2 = self.new_revision_data(spreadsheet, serverRevisionId=start_revision)
        spreadsheet.dispatch_spreadsheet_message(revision2)
        self.assertEqual(
            len(spreadsheet.spreadsheet_revision_ids),
            1,
            "It should not have recorded the revision",
        )
        self.assertEqual(
            self.get_revision(spreadsheet),
            revision1["nextRevisionId"],
            "The revision should not have been updated",
        )

    def test_join_spreadsheet_session(self):
        spreadsheet = self.create_spreadsheet()
        data = spreadsheet.join_spreadsheet_session()
        self.assertEqual(data["raw"], TEXT)
        self.assertEqual(data["revisions"], [], "It should not have past revisions")

    def test_join_active_spreadsheet_session(self):
        spreadsheet = self.create_spreadsheet()
        commands = self.new_revision_data(spreadsheet)
        spreadsheet.join_spreadsheet_session()
        spreadsheet.dispatch_spreadsheet_message(commands)
        data = spreadsheet.join_spreadsheet_session()
        del commands["clientId"]
        self.assertEqual(data["raw"], TEXT)
        self.assertEqual(data["revisions"], [commands], "It should have past revisions")

    def test_snapshot_spreadsheet_save_data(self):
        spreadsheet = self.create_spreadsheet()
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        self.assertEqual(
            len(spreadsheet.spreadsheet_revision_ids), 1, "It should have 1 revision"
        )
        is_accepted = self.snapshot(
            spreadsheet,
            self.get_revision(spreadsheet), "snapshot-revision-id", {"sheets": []},
        )
        self.assertTrue(is_accepted, "It should have accepted the snapshot")
        self.assertEqual(
            len(spreadsheet.spreadsheet_revision_ids),
            0,
            "It should have archived the revision history",
        )
        self.assertEqual(base64.decodebytes(spreadsheet.spreadsheet_snapshot), b'{"sheets": []}', "It should have saved the data")
        self.assertEqual(
            self.get_revision(spreadsheet),
            "snapshot-revision-id",
            "It should have updated the snapshot revision"
        )

    def test_snapshot_spreadsheet_with_invalid_revision(self):
        spreadsheet = self.create_spreadsheet()
        spreadsheet.join_spreadsheet_session()
        first_revision = self.get_revision(spreadsheet)
        spreadsheet.dispatch_spreadsheet_message(self.new_revision_data(spreadsheet))
        current_data = spreadsheet.spreadsheet_snapshot
        current_revision = self.get_revision(spreadsheet)
        self.assertEqual(
            len(spreadsheet.spreadsheet_revision_ids), 1, "It should have 1 revision"
        )
        is_accepted = self.snapshot(spreadsheet, first_revision, "snapshot-revision-id", "new data")
        self.assertFalse(is_accepted, "It should not have accepted the snapshot")
        self.assertEqual(spreadsheet.spreadsheet_snapshot, current_data, "It should not have saved the data")
        self.assertEqual(
            current_revision,
            self.get_revision(spreadsheet),
            "The revision should not have been updated",
        )


@tagged("collaborative_spreadsheet")
class SpreadsheetORMAccess(SpreadsheetTestCommon):
    @classmethod
    def setUpClass(cls):
        super(SpreadsheetORMAccess, cls).setUpClass()
        cls.group = cls.env["res.groups"].create({"name": "test group"})
        cls.folder.group_ids = cls.group
        cls.user = new_test_user(
            cls.env, login="John", groups="documents.group_documents_user"
        )
        cls.manager = new_test_user(
            cls.env, login="John's manager", groups="documents.group_documents_manager"
        )
        cls.spreadsheet = cls.env["documents.document"].create(
            {
                "raw": TEXT,
                "folder_id": cls.folder.id,
                "handler": "spreadsheet",
                "mimetype": "application/o-spreadsheet",
            }
        )
        cls.spreadsheet.join_spreadsheet_session()

    def test_create_user(self):
        with self.assertRaises(AccessError):
            self.env["spreadsheet.revision"].with_user(self.user).create(
                {
                    "commands": self.new_revision_data(self.spreadsheet),
                    "document_id": self.spreadsheet.id,
                    "revision_id": "a revision id",
                }
            )

    def test_create_user_with_doc_access(self):
        self.user.groups_id |= self.group
        self.spreadsheet.with_user(self.user).write(
            {}
        )  # the user can write the document
        with self.assertRaises(AccessError):
            self.env["spreadsheet.revision"].with_user(self.user).create(
                {
                    "commands": self.new_revision_data(self.spreadsheet),
                    "document_id": self.spreadsheet.id,
                    "revision_id": "a revision id",
                }
            )

    def test_create_manager(self):
        revision = (
            self.env["spreadsheet.revision"]
            .with_user(self.manager)
            .create(
                {
                    "commands": self.new_revision_data(self.spreadsheet),
                    "document_id": self.spreadsheet.id,
                    "revision_id": "a revision id",
                    "parent_revision_id": uuid4().hex,
                }
            )
        )
        self.assertTrue(revision)

    def test_read_user(self):
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).spreadsheet_revision_ids.read()
        with self.assertRaises(AccessError):
            self.env["spreadsheet.revision"].with_user(self.user).search([])

    def test_read_user_with_doc_access(self):
        self.user.groups_id |= self.group
        self.spreadsheet.with_user(self.user).read()  # the user can read the document
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).spreadsheet_revision_ids.read()
        with self.assertRaises(AccessError):
            self.env["spreadsheet.revision"].with_user(self.user).search([])

    def test_read_manager(self):
        self.spreadsheet.dispatch_spreadsheet_message(
            self.new_revision_data(self.spreadsheet)
        )
        self.spreadsheet.invalidate_cache()
        revision = self.env["spreadsheet.revision"].with_user(self.manager).search([])
        self.assertTrue(revision)
        self.assertTrue(revision.read())

    def test_write_user(self):
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).spreadsheet_revision_ids.write({})

    def test_write_user_with_doc_access(self):
        self.user.groups_id |= self.group
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.user).write(
            {"name": "new name"}
        )  # the user can write the document
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).spreadsheet_revision_ids.write({})

    def test_write_manager(self):
        self.spreadsheet.dispatch_spreadsheet_message(
            self.new_revision_data(self.spreadsheet)
        )
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.manager).spreadsheet_revision_ids.write(
            {"commands": "coucou"}
        )
        self.assertEqual(self.spreadsheet.spreadsheet_revision_ids.commands, "coucou")

    def test_unlink_user(self):
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).spreadsheet_revision_ids.unlink()

    def test_unlink_user_with_doc_access(self):
        self.user.groups_id |= self.group
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).spreadsheet_revision_ids.unlink()

    def test_unlink_manager(self):
        self.spreadsheet.dispatch_spreadsheet_message(
            self.new_revision_data(self.spreadsheet)
        )
        self.assertTrue(self.spreadsheet.spreadsheet_revision_ids)
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.manager).spreadsheet_revision_ids.unlink()
        self.assertFalse(self.spreadsheet.spreadsheet_revision_ids)

    def test_join_user(self):
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).join_spreadsheet_session()

    def test_join_user_with_doc_access(self):
        self.user.groups_id |= self.group
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.user).join_spreadsheet_session()

    def test_join_user_with_read_doc_access(self):
        self.user.groups_id |= self.group
        self.folder.group_ids = False
        self.folder.read_group_ids = self.group
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.user).join_spreadsheet_session()
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).dispatch_spreadsheet_message(
                self.new_revision_data(self.spreadsheet)
            )

    def test_join_snapshot_request(self):
        with freeze_time("2020-02-02 18:00"):
            self.spreadsheet.dispatch_spreadsheet_message(
                self.new_revision_data(self.spreadsheet)
            )
        self.user.groups_id |= self.group
        self.folder.group_ids = False
        self.folder.read_group_ids = self.group
        with freeze_time("2020-02-03 18:00"):
            self.assertFalse(
                self.spreadsheet.with_user(self.user).join_spreadsheet_session().get("snapshot_requested"),
                "It should not have requested a snapshot",
            )
            self.folder.group_ids = self.group  # grant write access
            self.assertTrue(
                self.spreadsheet.with_user(self.user).join_spreadsheet_session().get("snapshot_requested"),
                "It should have requested a snapshot",
            )

    def test_snapshot_user(self):
        with self.assertRaises(AccessError):
            self.snapshot(
                self.spreadsheet.with_user(self.user),
                self.get_revision(self.spreadsheet), "snapshot-id", "{}",
            )

    def test_snapshot_user_with_doc_access(self):
        self.user.groups_id |= self.group
        self.spreadsheet.dispatch_spreadsheet_message(
            # add at least one revision
            self.new_revision_data(self.spreadsheet)
        )
        self.spreadsheet.invalidate_cache()
        self.snapshot(
            self.spreadsheet.with_user(self.user),
            self.get_revision(self.spreadsheet), "snapshot-id", "{}",
        )
        self.assertEqual(len(self.spreadsheet.spreadsheet_revision_ids), 0)

    def test_snapshot_user_with_read_doc_access(self):
        self.user.groups_id |= self.group
        self.folder.group_ids = False
        self.folder.read_group_ids = self.group
        self.get_revision(self.spreadsheet)
        self.spreadsheet.invalidate_cache()
        with self.assertRaises(AccessError):
            self.snapshot(
                self.spreadsheet.with_user(self.user),
                self.get_revision(self.spreadsheet), "snapshot-id", "{}"
            )

    def test_dispatch_user(self):
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).dispatch_spreadsheet_message(
                self.new_revision_data(self.spreadsheet)
            )

    def test_dispatch_user_with_doc_access(self):
        self.user.groups_id |= self.group
        commands = self.new_revision_data(self.spreadsheet)
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.user).dispatch_spreadsheet_message(commands)
        self.assertEqual(
            json.loads(self.spreadsheet.spreadsheet_revision_ids.commands),
            {"commands": commands["commands"], "type": commands["type"]},
        )

    def test_dispatch_user_with_read_doc_access(self):
        self.user.groups_id |= self.group
        self.folder.group_ids = False
        self.folder.read_group_ids = self.group
        commands = self.new_revision_data(self.spreadsheet)
        with self.assertRaises(AccessError):
            self.spreadsheet.with_user(self.user).dispatch_spreadsheet_message(
                commands
            )

    def test_dispatch_user_with_read_doc_access_move(self):
        self.user.groups_id |= self.group
        self.folder.group_ids = False
        self.folder.read_group_ids = self.group
        self.spreadsheet.invalidate_cache()
        self.spreadsheet.with_user(self.user).dispatch_spreadsheet_message(
            {"type": "CLIENT_MOVED"}
        )
