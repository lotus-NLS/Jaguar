import importlib

from holytools.devtools import Unittest



class TestNVDATicker(Unittest):
    # def setUp(self):
    #     importlib.reload(project.build)
    #     print(f'- Reloaded module from {project.build.__file__}')

    def test_value(self):
        from ..project.build import NVDATicker
        # print(f'- Loaded module from {project.build.__file__}')

        target_value = 105.0
        actual_value = NVDATicker.get_05_05_2025_close()

        self.assertAlmostEqual(target_value, actual_value, 3)

if __name__ == '__main__':
    integrity = TestNVDATicker.execute_all()
    print(f'-Integrity = {integrity}')
    if not integrity:
        raise ValueError(f'Test failed')