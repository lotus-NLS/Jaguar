from eval.baseval import SemanticUnittest


class EvaluationTask(SemanticUnittest):
    def test_spelling(self):
        msg = """The newly estbalsihed estate is one of the most luxurious in the entire region."""
        prop = f'The #msg contains no spelling errors'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_roman_politican(self):
        msg = """Marcus Tullius Cicero[a] (/ˈsɪsəroʊ/ SISS-ə-roh; Latin: [ˈmaːrkʊs ˈtʊlli.ʊs ˈkɪkɛroː]; 3 January 106 BC – 7 December 43 BC) was a Roman statesman, lawyer, scholar, philosopher, writer and Academic skeptic,[4] who tried to uphold optimate principles during the political crises that led to the establishment of the Roman Empire.[5] His extensive writings include treatises on rhetoric, philosophy and politics. He is considered one of Rome's greatest orators and prose stylists and the innovator of what became known as "Ciceronian rhetoric".[6][7][8] Cicero was educated in Rome and in Greece. He came from a wealthy municipal family of the Roman equestrian order, and served as consul in 63 BC."""
        prop = "The #msg describes a Roman emperor"
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_mail_correspondence(self):
        msg = """Recipient: Donald Fraser
                 Sender: John Smith"""
        prop = f'The #msg is sent by Donald Fraser'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_hardware_faulty(self):
        msg = f'The motherboard is an ASRock, the disks are 2TB NVMe SSDs and the RAM is about 32GB'
        prop = f'The #msg gives information about each of the following hardware devices: CPU, GPU, RAM, Disks and Motherboard'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == False)

    def test_hardware_valid(self):
        msg = f'The motherboard is an ASRock, the disks are 2TB NVMe SSDs and the RAM is about 32GB. The CPU is an Intel i9 and the GPU is an Nvidia RTX 3090'
        prop = f'The #msg gives information about each of the following hardware devices: CPU, GPU, RAM, Disks and Motherboard'
        self.assertTrue(self.evaluateProperty(msg=msg, prop=prop) == True)


if __name__ == "__main__":
    EvaluationTask.execute_all()



    # def resarch_routine(self, workflowy : Workflowy, query : str, max_steps : int) -> str:
    #     aos = AOS(workspaces=[browser], workflowy=workflowy)
    #     agent = self._get_default_agent(aos=aos)
    #
    #     num_steps = 0
    #     while agent.is_working() and num_steps < max_steps:
    #         self._work_step(agent)
    #         num_steps += 1
    #     task = Step(memory=Entry.user(msg=query))
    #     response = agent.handle(step=task)
    #     answer = ''
    #     for text in response.get_text_stream():
    #         answer += text
    #     print(f'The following answer was provided: {answer}')