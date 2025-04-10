from eval.basetests import NLU

# ---------------------------------------------------


class TerminalTasks(TaskUnittest):
    def test_gpu_research(self):
        query = ('The #msg provides information about the GPU model. It states that the grpahics card is'
                    'an NVIDIA GeForce GTX 1060')

        gpu_research = self.evaluate_task_performance(task_name='simplehardware', prop=query)
        self.assertTrue(gpu_research)

    def test_hardware_summary(self):
        query = ('The #msg gives information about each of the following hardware devices:'
                    'CPU, GPU, RAM, Disks and Motherboard')
        is_successful = self.evaluate_task_performance(task_name='hardware', prop=query)
        self.assertTrue(is_successful)


class BrowserTasks(TaskUnittest):
    def test_cat_search(self):
        query = 'What is the first result from your search for cat videos?'
        is_successful = self.evaluate_task_performance(task_name='cat', prop=query)
        self.assertTrue(is_successful)

    def test_stackexchange(self):
        pass




if __name__ == "__main__":
    # TerminalTasks.execute_all()
    bt = BrowserTasks()
    bt.setUpClass()
    bt.setUp()
