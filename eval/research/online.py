from engine import LotusEngine
from eval.nl import NLU

# ---------------------------------------------------

class CatTask(NLU):
    def setUp(self):
        super().setUpClass()
        self.engine = LotusEngine()

    def test_search_for_cat(self):
        task = self.task_provider.get_task('cat')
        self.engine.do_task(task=task, max_steps=10)
        user_msg = f'What is the first result from your search for cat videos?'
        answer = self.engine.converse(msg=user_msg)

        print(f'+------------------------+')
        print(f'User: {user_msg}')
        print(f'Agent: {answer}')

        property_query = 'The #msg provides information about the GPU model'
        evaluation = self.evaluateProperty(msg=answer.msg, prop=property_query)
        self.assertTrue(evaluation == True)


if __name__ == "__main__":
    hw_test = CatTask()
    hw_test.setUp()
    hw_test.test_search_for_cat()
