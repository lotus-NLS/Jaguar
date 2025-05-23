from __future__ import annotations

import os
from typing import Optional

from pylint import lint
from pylint.reporters import CollectingReporter
from holytools.userIO import MessageFormatter

# -----------------------------------------------------

class PythonEditor:
    @staticmethod
    def get_info(proj_dirpath : str, venv_dirpath: Optional[str] = None) -> str:
        metadata = (f'{"Project name":<20}: {os.path.basename(proj_dirpath)}'
                    f'\n{"Project dirpath":<20}: {proj_dirpath}')
        if not venv_dirpath is None:
            metadata += f'\n{"Virtual environment":<20}: {venv_dirpath}'

        return metadata

    @classmethod
    def get_editor(cls, open_fpaths: list[str], run_output: dict[str, str]) -> str:
        all_contents = ''
        for j, path in enumerate(open_fpaths):
            fname = os.path.basename(path)
            texts = [cls._get_file_with_lineno(fpath=path), cls._get_inspections(fpath=path)]
            headlines = [f'[{fname} (fileNo: {j})]', 'Problems']

            if path in run_output:
                texts.append(run_output[path])
                headlines.append('Execution output')

            all_contents += MessageFormatter.multi_section_box(texts=texts, headlines=headlines)

        return all_contents

    @staticmethod
    def _get_inspections(fpath: str) -> str:
        reporter = CollectingReporter()
        lint.Run([fpath] + ['--disable=C,R'], reporter=reporter, exit=False)
        criticalility_dict = {'W': '⚠️', 'E': '🛑'}

        formatted_inspections = ''
        for m in reporter.messages:
            symbol = criticalility_dict[m.C]
            formatted_inspections += f' {symbol} l.{m.line:<4}| {m.msg}\n'

        return formatted_inspections


    @staticmethod
    def _get_file_with_lineno(fpath: str) -> str:
        with open(fpath, 'r') as f:
            c = f.read()
        lines = c.split('\n')

        enumerated_content = ''
        for n, l in enumerate(lines):
            enumerated_content += f'{n + 1:< 5}| {l}\n'
        enumerated_content = enumerated_content.rstrip('\n')
        return enumerated_content



