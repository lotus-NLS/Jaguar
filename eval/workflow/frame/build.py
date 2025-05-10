from holytools.devtools import Unittest
from project.build import NVDATicker

class TestNVDATicker(Unittest):
    def test_value(self):
        target_value = 105.0
        actual_value = NVDATicker.get_05_05_2025_close()

        self.assertAlmostEqual(target_value, actual_value, 3)

if __name__ == '__main__':
    integrity = TestNVDATicker.execute_all()
    print(f'-Integrity = {integrity}')
    if not integrity:
        raise ValueError(f'Test failed')