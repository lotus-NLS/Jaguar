from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolCall
from engine.l3_aos.workspace import Workspace
from tests.basetests import CredTest


class TestAOS(CredTest):
    def setUp(self):
        self.empty_aos : AOS = AOS.empty()
        self.full_aos : AOS = AOS.full(google_api_key=self.google_api_key, searchengine_id=self.searchengine_id)


    def test_process_nonexistent(self):
        tc = ToolCall(name='NOTOOL')
        outputs = self.empty_aos.process(tool_calls=[tc])

        for o in outputs:
            for update in o.prog_updates:
                update_str = str(update)
                self.info(str(update))
                self.assertTrue('NOTOOL' in update_str)

    def test_process_err(self):
        self.empty_aos.add_workspace(ws=ErrorWS())
        tc = ToolCall(name='ErrorWS_open')
        outputs = self.empty_aos.process(tool_calls=[tc])

        for o in outputs:
            for update in o.prog_updates:
                update_str = str(update)
                self.info(update_str)
                self.assertTrue('ErrorWS_open' in update_str)


class ErrorWS(Workspace):
    def open(self, *args, **kwargs):
        raise ValueError(f'Error in {self.get_name()}')

    def close(self, *args, **kwargs):
        pass

    def get_text(self) -> str:
        return ''

    def get_image(self) -> Optional[PILImage]:
        return None


if __name__ == "__main__":
    TestAOS.execute_all()
