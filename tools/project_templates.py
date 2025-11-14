"""프로젝트 템플릿 생성기

FastAPI, Flask, Django, CLI 등 다양한 프로젝트 템플릿을 생성합니다.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Template:
    """프로젝트 템플릿"""
    name: str
    description: str
    files: Dict[str, str]  # 파일 경로: 내용
    directories: List[str]


class ProjectTemplates:
    """프로젝트 템플릿 관리자"""

    def __init__(self):
        self.templates = {
            "fastapi": self._get_fastapi_template(),
            "flask": self._get_flask_template(),
            "cli": self._get_cli_template(),
            "library": self._get_library_template()
        }

    async def create_project(
        self,
        template_name: str,
        project_name: str,
        output_dir: str = "."
    ) -> Dict[str, any]:
        """프로젝트 생성

        Args:
            template_name: 템플릿 이름 (fastapi, flask, cli, library)
            project_name: 프로젝트 이름
            output_dir: 출력 디렉토리

        Returns:
            생성 결과
        """
        if template_name not in self.templates:
            return {
                "success": False,
                "error": f"Unknown template: {template_name}"
            }

        template = self.templates[template_name]

        output_path = Path(output_dir) / project_name
        output_path.mkdir(parents=True, exist_ok=True)

        created_files = []

        # 디렉토리 생성
        for directory in template.directories:
            dir_path = output_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # 파일 생성
        for file_path, content in template.files.items():
            full_path = output_path / file_path

            # 템플릿 변수 치환
            content = content.replace("{{project_name}}", project_name)
            content = content.replace("{{project_name_lower}}", project_name.lower())
            content = content.replace("{{project_name_upper}}", project_name.upper())

            with open(full_path, 'w') as f:
                f.write(content)

            created_files.append(str(full_path))

        return {
            "success": True,
            "project_path": str(output_path),
            "template": template_name,
            "files_created": len(created_files),
            "files": created_files
        }

    def _get_fastapi_template(self) -> Template:
        """FastAPI 프로젝트 템플릿"""
        return Template(
            name="FastAPI",
            description="FastAPI 웹 API 프로젝트",
            directories=["app", "app/routers", "app/models", "tests"],
            files={
                "app/__init__.py": "",
                "app/main.py": '''"""FastAPI 메인 애플리케이션"""

from fastapi import FastAPI
from app.routers import items

app = FastAPI(
    title="{{project_name}} API",
    description="{{project_name}} API Documentation",
    version="1.0.0"
)

# 라우터 등록
app.include_router(items.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Welcome to {{project_name}} API"}


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "ok"}
''',
                "app/routers/__init__.py": "",
                "app/routers/items.py": '''"""아이템 라우터"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/items", tags=["items"])


class Item(BaseModel):
    """아이템 모델"""
    id: int
    name: str
    description: str | None = None
    price: float


# 임시 데이터
items_db = []


@router.get("/", response_model=List[Item])
async def get_items():
    """모든 아이템 조회"""
    return items_db


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """특정 아이템 조회"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/", response_model=Item, status_code=201)
async def create_item(item: Item):
    """아이템 생성"""
    items_db.append(item)
    return item


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """아이템 수정"""
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            items_db[i] = item
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """아이템 삭제"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Item not found")
''',
                "app/models/__init__.py": "",
                "requirements.txt": '''fastapi>=0.115.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
''',
                "tests/__init__.py": "",
                "tests/test_main.py": '''"""메인 애플리케이션 테스트"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
''',
                "README.md": '''# {{project_name}}

FastAPI 프로젝트

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
uvicorn app.main:app --reload
```

API 문서: http://localhost:8000/docs

## 테스트

```bash
pytest
```
''',
                ".gitignore": '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
'''
            }
        )

    def _get_flask_template(self) -> Template:
        """Flask 프로젝트 템플릿"""
        return Template(
            name="Flask",
            description="Flask 웹 애플리케이션",
            directories=["app", "app/routes", "app/templates", "tests"],
            files={
                "app/__init__.py": '''"""Flask 애플리케이션 팩토리"""

from flask import Flask


def create_app():
    """애플리케이션 생성"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'

    from app.routes import main
    app.register_blueprint(main.bp)

    return app
''',
                "app/routes/__init__.py": "",
                "app/routes/main.py": '''"""메인 라우트"""

from flask import Blueprint, render_template, jsonify

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """홈 페이지"""
    return render_template('index.html')


@bp.route('/api/hello')
def hello():
    """API 엔드포인트"""
    return jsonify({"message": "Hello from {{project_name}}!"})
''',
                "app/templates/index.html": '''<!DOCTYPE html>
<html>
<head>
    <title>{{project_name}}</title>
</head>
<body>
    <h1>Welcome to {{project_name}}!</h1>
    <p>Flask application is running.</p>
</body>
</html>
''',
                "run.py": '''"""애플리케이션 실행"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
''',
                "requirements.txt": '''Flask>=3.0.0
''',
                "README.md": '''# {{project_name}}

Flask 웹 애플리케이션

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
python run.py
```

## 테스트

```bash
pytest
```
''',
                ".gitignore": '''__pycache__/
*.py[cod]
instance/
.env
'''
            }
        )

    def _get_cli_template(self) -> Template:
        """CLI 애플리케이션 템플릿"""
        return Template(
            name="CLI",
            description="CLI 애플리케이션 (typer)",
            directories=["src/{{project_name_lower}}", "tests"],
            files={
                "src/{{project_name_lower}}/__init__.py": '''"""{{project_name}} CLI"""

__version__ = "0.1.0"
''',
                "src/{{project_name_lower}}/cli.py": '''"""CLI 엔트리포인트"""

import typer
from typing import Optional

app = typer.Typer(
    name="{{project_name_lower}}",
    help="{{project_name}} CLI application"
)


@app.command()
def hello(name: str = typer.Argument("World")):
    """인사 메시지 출력"""
    typer.echo(f"Hello {name}!")


@app.command()
def process(
    input_file: str = typer.Option(..., "--input", "-i", help="Input file"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode")
):
    """파일 처리"""
    if verbose:
        typer.echo(f"Processing {input_file}...")

    # TODO: 실제 처리 로직 구현

    typer.echo("Done!")


if __name__ == "__main__":
    app()
''',
                "pyproject.toml": '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{project_name_lower}}"
version = "0.1.0"
description = "{{project_name}} CLI application"
requires-python = ">=3.8"
dependencies = [
    "typer>=0.9.0",
]

[project.scripts]
{{project_name_lower}} = "{{project_name_lower}}.cli:app"
''',
                "README.md": '''# {{project_name}}

CLI 애플리케이션

## 설치

```bash
pip install -e .
```

## 사용법

```bash
# 헬프 보기
{{project_name_lower}} --help

# 인사 메시지
{{project_name_lower}} hello Alice

# 파일 처리
{{project_name_lower}} process -i input.txt -o output.txt -v
```
''',
                ".gitignore": '''__pycache__/
*.egg-info/
dist/
build/
'''
            }
        )

    def _get_library_template(self) -> Template:
        """라이브러리 템플릿"""
        return Template(
            name="Library",
            description="Python 라이브러리 패키지",
            directories=["src/{{project_name_lower}}", "tests", "docs"],
            files={
                "src/{{project_name_lower}}/__init__.py": '''"""{{project_name}} library"""

__version__ = "0.1.0"

from .core import main_function

__all__ = ["main_function"]
''',
                "src/{{project_name_lower}}/core.py": '''"""핵심 기능"""


def main_function(x: int, y: int) -> int:
    """메인 함수

    Args:
        x: 첫 번째 숫자
        y: 두 번째 숫자

    Returns:
        합계
    """
    return x + y
''',
                "tests/test_core.py": '''"""코어 기능 테스트"""

from {{project_name_lower}}.core import main_function


def test_main_function():
    """메인 함수 테스트"""
    assert main_function(2, 3) == 5
''',
                "pyproject.toml": '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{project_name_lower}}"
version = "0.1.0"
description = "{{project_name}} library"
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
    "flake8>=7.0.0",
]
''',
                "README.md": '''# {{project_name}}

Python 라이브러리

## 설치

```bash
pip install {{project_name_lower}}
```

## 사용법

```python
from {{project_name_lower}} import main_function

result = main_function(2, 3)
print(result)  # 5
```

## 개발

```bash
# 개발 모드 설치
pip install -e .[dev]

# 테스트
pytest

# 포매팅
black src/
```
''',
                ".gitignore": '''__pycache__/
*.egg-info/
dist/
build/
.pytest_cache/
'''
            }
        )

    def list_templates(self) -> List[Dict[str, str]]:
        """사용 가능한 템플릿 목록"""
        return [
            {
                "name": name,
                "title": template.name,
                "description": template.description
            }
            for name, template in self.templates.items()
        ]


# 편의 함수

async def create_project(template: str, name: str, output: str = ".") -> Dict[str, any]:
    """편의 함수: 프로젝트 생성"""
    templates = ProjectTemplates()
    return await templates.create_project(template, name, output)
