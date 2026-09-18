from unittest import TestCase
from xml.etree import ElementTree as ET
from tca_bp.web_charts import cached_points


class ChartCacheTests(TestCase):
    def test_sparse_cache_keeps_zeros_and_missing_positions_aligned(self):
        node = ET.fromstring('''<val xmlns="http://schemas.openxmlformats.org/drawingml/2006/chart"><numCache>
          <ptCount val="5"/><pt idx="3"><v>120</v></pt><pt idx="0"><v>0</v></pt><pt idx="2"><v>#N/A</v></pt>
        </numCache></val>''')
        self.assertEqual(cached_points(node,numeric=True), [0, None, None, 120, None])

    def test_categories_keep_missing_labels_and_limits(self):
        node = ET.fromstring('''<cat xmlns="http://schemas.openxmlformats.org/drawingml/2006/chart"><strCache>
          <ptCount val="999999"/><pt idx="2"><v>2028</v></pt><pt idx="0"><v>2026</v></pt>
        </strCache></cat>''')
        self.assertEqual(cached_points(node,limit=3), ['2026', '', '2028'])
