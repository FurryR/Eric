import contextlib
from base64 import b64encode
from pathlib import Path

import PIL
from PIL import Image
from lxml import etree
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style


class Icon(Element):
    svg: str | None
    img: Image.Image | None

    def __init__(self, *, svg: str = "", img: Image.Image = None):
        assert svg or img
        self.svg = svg
        self.img = img

    def __hash__(self):
        return hash(f"_Icon:{self.svg}:{hash(self.img)}")

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return set()

    @classmethod
    def from_file(cls, path: Path | str) -> Self:
        with contextlib.suppress(PIL.UnidentifiedImageError):
            return cls.from_image(path)
        return cls.from_svg(path)

    @classmethod
    def from_svg(cls, path: Path | str) -> Self:
        return Icon(svg=Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_image(cls, path: Path | str) -> Self:
        return Icon(img=Image.open(path))

    def _to_html_svg(self):
        return etree.XML(self.svg)

    def _to_html_img(self) -> str:
        data = self.img.tobytes()
        data = b64encode(data).decode("utf-8")
        return etree.XML(
            f'<img src="data:image/png;base64,{data}" '
            'style="width: 100%; height: 100%;" />'
        )

    def to_e(self, *_args, **_kwargs):
        return self._to_html_svg() if self.svg else self._to_html_img()
