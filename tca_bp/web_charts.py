"""Read chart cache positions without inventing or compressing missing values."""
import math

NS = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}


def cached_points(container, *, numeric=False, limit=1000):
    if container is None:
        return []
    count = 0
    marker = container.find('.//c:ptCount', NS)
    if marker is not None:
        try:
            count = max(0, min(limit, int(marker.get('val', '0'))))
        except ValueError:
            pass
    indexed = {}
    for point in container.findall('.//c:pt', NS):
        try:
            index = int(point.get('idx', '-1'))
        except ValueError:
            continue
        if not 0 <= index < limit:
            continue
        value = point.find('c:v', NS)
        text = value.text if value is not None else None
        if numeric:
            try:
                value = float(text)
                if not math.isfinite(value):
                    value = None
            except (ValueError, TypeError):
                value = None
        else:
            value = text or ''
        indexed[index] = value
        count = max(count, index + 1)
    return [indexed.get(index, None if numeric else '') for index in range(count)]
