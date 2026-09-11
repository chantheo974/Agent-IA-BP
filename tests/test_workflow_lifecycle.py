"""Bornes du runner de cycle ; pas de modèle client ni d’Excel."""
from pathlib import Path
import tempfile
import unittest
from tools.validate_workflow_lifecycle import definition, target_directory


class WorkflowLifecycleTests(unittest.TestCase):
    def test_runner_never_targets_existing_or_client_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / 'runtime' / 'recette_cycle_fixture'
            self.assertEqual(target_directory(root, valid), valid.resolve())
            for path in (root, root / 'clients' / 'recette_cycle_fake', root / 'runtime' / 'recette_other',
                         root / 'runtime' / 'recette_cycle_parent' / 'recette_cycle_child'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    target_directory(root, path)
            valid.mkdir(parents=True)
            with self.assertRaises(ValueError):
                target_directory(root, valid)

    def test_three_event_definitions_include_null_activity_calendar_and_distinct_activation(self):
        specs = [definition(name) for name in ('services', 'fabrication', 'recherche')]
        self.assertEqual({s['horizon'] for s in specs}, {1, 3, 10})
        self.assertEqual({s['sheet'] for s in specs}, {'DATA Contrats', 'DATA CAPEX', 'Financement Dette'})
        for spec in specs:
            zero = {(u['sheet'], u['cell']): u['value'] for u in spec['zero_values']}
            self.assertTrue(all(zero['Assumptions', 'C' + str(row)] == 0 for row in range(15, 28)))
            self.assertNotIn(('Assumptions', 'F15'), zero)
            self.assertEqual(zero['Control', 'C10'], spec['start'])
            self.assertLess(len(spec['partial']), len(spec['values']))
            self.assertNotEqual(spec['scenario'], 'Central')


if __name__ == '__main__':
    unittest.main()
