from wfeval import WorkflowEval
from frame.build import TestNVDATicker

class BuildEval(WorkflowEval):
    def test_build_nvda_ticker(self):
        success = self.evaluate_unittest(unittest=TestNVDATicker)
        if not success:
            self.fail('Failed to pass unittest')


if __name__ == '__main__':
    BuildEval.execute_all()