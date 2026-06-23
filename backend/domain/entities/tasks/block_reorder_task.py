from domain.entities.tasks.base_task import BaseTask
from shared.enums import Difficulty, TaskType
from domain.entities.construction import Construction
import re


class BlockReorderTask(BaseTask):
    def __init__(
        self,
        id: int | None,
        teacher_id: int,
        title: str,
        description: str,
        difficulty: Difficulty,
        task_type: TaskType,
        original_code: str,
        template: str | None,
        blocks: list[str],
        correct_order: list[int],
        language: str,
        language_variants: dict | None = None,
        constructions: list[Construction] | None = None,
    ):
        super().__init__(
            id,
            teacher_id,
            title,
            difficulty,
            description,
            task_type,
            constructions,
        )
        self.original_code = original_code
        self.template = template
        self.blocks = blocks
        self.correct_order = correct_order
        self.language = language
        self.language_variants = language_variants or {}

    @staticmethod
    def create(
        teacher_id: int,
        title: str,
        description: str,
        difficulty: Difficulty,
        original_code: str,
        template: str | None,
        blocks: list[str],
        correct_order: list[int],
        language: str,
        language_variants: dict | None = None,
        constructions: list[Construction] | None = None,
    ) -> "BlockReorderTask":
        return BlockReorderTask(
            id=None,
            teacher_id=teacher_id,
            title=title,
            description=description,
            difficulty=difficulty,
            task_type=TaskType.BLOCK_REORDER,
            original_code=original_code,
            template=template,
            blocks=blocks,
            correct_order=correct_order,
            language=language,
            language_variants=language_variants,
            constructions=constructions,
        )

    def _get_slot_indent(self, template: str, slot_index: int) -> str:
        """Return the leading whitespace on the line containing {slot_index}."""
        slot_token = "{" + str(slot_index) + "}"
        pos = template.find(slot_token)
        if pos == -1:
            return ""
        line_start = template.rfind("\n", 0, pos) + 1
        indent = ""
        for ch in template[line_start:pos]:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break
        return indent

    def _apply_indent_to_block(self, block: str, indent: str) -> str:
        """Prepend indent to every line of block except the first (template provides first-line indent)."""
        if not indent or "\n" not in block:
            return block
        lines = block.split("\n")
        return ("\n" + indent).join(lines)

    def _apply_manual_indent_level(self, block: str, level: int) -> str:
        if level <= 0:
            return block
        # One indent level equals one space to keep visual indentation predictable.
        prefix = " " * level
        return "\n".join(
            (f"{prefix}{line}" if line else line) for line in block.split("\n")
        )

    @staticmethod
    def _template_has_slots(template: str | None) -> bool:
        return bool(template and re.search(r"\{\d+\}", template))

    def build_code(
        self,
        user_order: list[int],
        language: str | None = None,
        indents: list[int] | None = None,
    ) -> str:
        variant = self._get_variant(language)
        blocks = variant["blocks"]
        template = variant.get("template") or self.template

        selected = [blocks[index] for index in user_order]
        if indents is None:
            indents = []

        if not template and indents:
            selected = [
                self._apply_manual_indent_level(
                    block, int(indents[idx] if idx < len(indents) else 0)
                )
                for idx, block in enumerate(selected)
            ]

        if template and self._template_has_slots(template):
            try:
                result = template
                for i, block_text in enumerate(selected):
                    slot_token = "{" + str(i) + "}"
                    indent = self._get_slot_indent(result, i)
                    indented_block = self._apply_indent_to_block(block_text, indent)
                    result = result.replace(slot_token, indented_block, 1)
                return result
            except Exception:
                return "\n".join(selected)
        return "\n".join(selected)

    def _get_variant(self, language: str | None) -> dict:
        """Return {blocks, correct_order, template} for the requested language."""
        if language and language != self.language and self.language_variants:
            v = self.language_variants.get(language)
            if v:
                return {
                    "blocks": v.get("blocks", self.blocks),
                    "correct_order": v.get("correct_order", self.correct_order),
                    "template": v.get("template", self.template),
                }
        return {
            "blocks": self.blocks,
            "correct_order": self.correct_order,
            "template": self.template,
        }

    def validate_answer(
        self, user_order: list[int], language: str | None = None
    ) -> bool:
        variant = self._get_variant(language)
        correct = variant["correct_order"]
        if list(user_order) == list(correct):
            return True
        blocks = variant["blocks"]
        template = variant.get("template") or self.template
        if (
            self._template_has_slots(template)
            and len(user_order) == len(correct)
        ):
            return all(
                0 <= user_order[i] < len(blocks)
                and 0 <= correct[i] < len(blocks)
                and blocks[user_order[i]].strip() == blocks[correct[i]].strip()
                for i in range(len(correct))
            )
        return False

    def validate_partial(
        self, user_order: list[int], language: str | None = None
    ) -> list[bool]:
        correct = self._get_variant(language)["correct_order"]
        length = min(len(user_order), len(correct))
        result = [user_order[i] == correct[i] for i in range(length)]
        if len(correct) > length:
            result.extend([False] * (len(correct) - length))
        return result

    def to_public_payload(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "type": "block_reorder",
            "template": self.template,
            "blocks": self.blocks,
            "language": self.language,
            "language_variants": self.language_variants,
        }

    def update(self, data: "BlockReorderTask") -> "BlockReorderTask":
        self.title = data.title
        self.description = data.description
        self.difficulty = data.difficulty
        self.original_code = data.original_code
        self.template = data.template
        self.blocks = data.blocks
        self.correct_order = data.correct_order
        self.language = data.language
        self.language_variants = data.language_variants
        self.constructions = data.constructions
        return self
