from eval.basetests import TaskUnittest


# ---------------------------------------------------


class TerminalTasks(TaskUnittest):
    def test_gpu_research(self):
        prop = ('The #msg provides information about the GPU model. It states that the grpahics card is'
                    'an NVIDIA GeForce GTX 1060')
        report_query = 'Please state the model of the GPU that you found'

        gpu_research = self.evaluate_task_performance(task_name='simplehardware', prop=prop, query=report_query)
        self.assertTrue(gpu_research)

    def test_hardware_summary(self):
        prop = ('The #msg gives information about each of the following hardware devices:'
                    'CPU, GPU, RAM, Disks and Motherboard')
        report_query = ('Please summarize the hardware information that you found. '
                        'Include the CPU, GPU, RAM, Disks and Motherboard')
        is_successful = self.evaluate_task_performance(task_name='hardware', prop=prop, query=report_query)
        self.assertTrue(is_successful)


class BrowserTasks(TaskUnittest):
    def test_cat_search(self):
        prop = 'The #msg provides information about the first result of the search. '
        query = 'Please summarize the first result from your search for cat videos'
        is_successful = self.evaluate_task_performance(task_name='cat', prop=prop, query=query)
        self.assertTrue(is_successful)

    def test_stackexchange(self):
        query = 'What is the first word  from your search for stackexchange?'
        prop = 'The #msg provides information about the first result of the search. '
        is_successful = self.evaluate_task_performance(task_name='stackexchange', prop=prop, query=query)
        self.assertTrue(is_successful)


if __name__ == "__main__":
    # TerminalTasks.execute_all()
    bt = BrowserTasks()
    bt.setUpClass()
    bt.setUp()
