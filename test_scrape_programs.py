import unittest

from scripts.scrape_programs import merge_programs


class MergeProgramsTests(unittest.TestCase):
    def test_duplicate_new_ids_update_instead_of_append(self):
        existing = [{"id": "existing", "name": "Existing"}]
        new = [
            {"id": "duplicate", "name": "First"},
            {"id": "duplicate", "name": "Latest"},
        ]

        merged = merge_programs(existing, new)

        self.assertEqual([program["id"] for program in merged], ["existing", "duplicate"])
        self.assertEqual(merged[1]["name"], "Latest")

    def test_duplicate_existing_ids_are_collapsed(self):
        existing = [
            {"id": "duplicate", "name": "First"},
            {"id": "duplicate", "name": "Latest"},
        ]

        merged = merge_programs(existing, [])

        self.assertEqual(merged, [{"id": "duplicate", "name": "Latest"}])

    def test_same_source_url_replaces_when_id_changes(self):
        existing = [
            {
                "id": "old-id",
                "name": "Reimagine learning",
                "company": "Canva",
                "source_url": "https://www.canva.com/education/",
            }
        ]
        new = [
            {
                "id": "new-id",
                "name": "Canva for Education",
                "company": "Canva",
                "source_url": "https://www.canva.com/education/",
            }
        ]

        merged = merge_programs(existing, new)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["id"], "new-id")
        self.assertEqual(merged[0]["name"], "Canva for Education")


if __name__ == "__main__":
    unittest.main()
