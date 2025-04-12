from eval.base import NLU


class JudgementEval(NLU):
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