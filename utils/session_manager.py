"""세션 관리 시스템 - 프로젝트별 데이터 저장 및 복원."""

import json
import hashlib
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class SessionManager:
    """
    프로젝트별 세션 데이터를 관리합니다.

    저장되는 데이터:
    - 분석된 파일 목록
    - RAG 인덱스 위치
    - 대화 히스토리
    - 프로젝트 설정
    - 마지막 액세스 시간

    캐시 구조:
    .agent_cache/
    └── {project_hash}/
        ├── session.json         # 세션 메타데이터
        ├── analyzed_files.json  # 분석된 파일 목록
        ├── rag_index/           # RAG 벡터 저장소
        └── history.json         # 대화 히스토리
    """

    def __init__(self, cache_dir: str = ".agent_cache"):
        """
        Args:
            cache_dir: 캐시 디렉토리 경로 (프로젝트 루트 기준)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_project_hash(self, project_path: str) -> str:
        """
        프로젝트 경로를 기반으로 고유 해시 생성.

        Args:
            project_path: 프로젝트 절대 경로

        Returns:
            8자리 해시 문자열
        """
        # 절대 경로로 정규화
        abs_path = str(Path(project_path).resolve())

        # SHA256 해시 생성 (처음 8자리만 사용)
        hash_obj = hashlib.sha256(abs_path.encode())
        return hash_obj.hexdigest()[:8]

    def _get_project_cache_dir(self, project_path: str) -> Path:
        """
        프로젝트별 캐시 디렉토리 경로 반환.

        Args:
            project_path: 프로젝트 경로

        Returns:
            캐시 디렉토리 Path 객체
        """
        project_hash = self._get_project_hash(project_path)
        cache_path = self.cache_dir / project_hash
        cache_path.mkdir(exist_ok=True)
        return cache_path

    async def save_session(
        self,
        project_path: str,
        analyzed_files: Optional[List[str]] = None,
        settings: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        세션 데이터를 저장합니다.

        Args:
            project_path: 프로젝트 경로
            analyzed_files: 분석된 파일 목록
            settings: 프로젝트 설정
            history: 대화 히스토리
            custom_data: 추가 데이터

        Returns:
            저장 결과 딕셔너리
        """
        cache_dir = self._get_project_cache_dir(project_path)

        # 세션 메타데이터
        session_data = {
            "project_path": str(Path(project_path).resolve()),
            "project_hash": self._get_project_hash(project_path),
            "last_accessed": datetime.now().isoformat(),
            "analyzed_files_count": len(analyzed_files) if analyzed_files else 0,
            "history_count": len(history) if history else 0,
            "settings": settings or {},
            "custom_data": custom_data or {}
        }

        # session.json 저장
        session_file = cache_dir / "session.json"
        async with aiofiles.open(session_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(session_data, indent=2, ensure_ascii=False))

        # analyzed_files.json 저장
        if analyzed_files is not None:
            files_file = cache_dir / "analyzed_files.json"
            files_data = {
                "files": analyzed_files,
                "count": len(analyzed_files),
                "saved_at": datetime.now().isoformat()
            }
            async with aiofiles.open(files_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(files_data, indent=2, ensure_ascii=False))

        # history.json 저장
        if history is not None:
            history_file = cache_dir / "history.json"
            history_data = {
                "history": history,
                "count": len(history),
                "saved_at": datetime.now().isoformat()
            }
            async with aiofiles.open(history_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(history_data, indent=2, ensure_ascii=False))

        return {
            "success": True,
            "cache_dir": str(cache_dir),
            "project_hash": self._get_project_hash(project_path),
            "saved_files": [
                "session.json",
                "analyzed_files.json" if analyzed_files else None,
                "history.json" if history else None
            ]
        }

    async def load_session(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        저장된 세션 데이터를 로드합니다.

        Args:
            project_path: 프로젝트 경로

        Returns:
            세션 데이터 딕셔너리 또는 None (세션이 없는 경우)
        """
        cache_dir = self._get_project_cache_dir(project_path)
        session_file = cache_dir / "session.json"

        # 세션 파일이 없으면 None 반환
        if not session_file.exists():
            return None

        # session.json 로드
        async with aiofiles.open(session_file, "r", encoding="utf-8") as f:
            content = await f.read()
            session_data = json.loads(content)

        # analyzed_files.json 로드
        files_file = cache_dir / "analyzed_files.json"
        if files_file.exists():
            async with aiofiles.open(files_file, "r", encoding="utf-8") as f:
                content = await f.read()
                files_data = json.loads(content)
                session_data["analyzed_files"] = files_data["files"]
        else:
            session_data["analyzed_files"] = []

        # history.json 로드
        history_file = cache_dir / "history.json"
        if history_file.exists():
            async with aiofiles.open(history_file, "r", encoding="utf-8") as f:
                content = await f.read()
                history_data = json.loads(content)
                session_data["history"] = history_data["history"]
        else:
            session_data["history"] = []

        # RAG 인덱스 디렉토리 경로 추가
        rag_dir = cache_dir / "rag_index"
        session_data["rag_index_path"] = str(rag_dir)
        session_data["has_rag_index"] = rag_dir.exists()

        # 캐시 디렉토리 경로 추가
        session_data["cache_dir"] = str(cache_dir)

        return session_data

    async def session_exists(self, project_path: str) -> bool:
        """
        세션이 존재하는지 확인합니다.

        Args:
            project_path: 프로젝트 경로

        Returns:
            세션 존재 여부
        """
        cache_dir = self._get_project_cache_dir(project_path)
        session_file = cache_dir / "session.json"
        return session_file.exists()

    async def delete_session(self, project_path: str) -> bool:
        """
        세션 데이터를 삭제합니다.

        Args:
            project_path: 프로젝트 경로

        Returns:
            삭제 성공 여부
        """
        import shutil

        cache_dir = self._get_project_cache_dir(project_path)

        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            return True

        return False

    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        저장된 모든 세션 목록을 반환합니다.

        Returns:
            세션 정보 리스트
        """
        sessions = []

        for project_dir in self.cache_dir.iterdir():
            if project_dir.is_dir():
                session_file = project_dir / "session.json"
                if session_file.exists():
                    async with aiofiles.open(session_file, "r", encoding="utf-8") as f:
                        content = await f.read()
                        session_data = json.loads(content)
                        sessions.append({
                            "project_hash": project_dir.name,
                            "project_path": session_data.get("project_path"),
                            "last_accessed": session_data.get("last_accessed"),
                            "analyzed_files_count": session_data.get("analyzed_files_count", 0),
                            "history_count": session_data.get("history_count", 0)
                        })

        # 마지막 액세스 시간 기준 정렬
        sessions.sort(key=lambda x: x.get("last_accessed", ""), reverse=True)

        return sessions

    def get_rag_index_path(self, project_path: str) -> str:
        """
        프로젝트의 RAG 인덱스 저장 경로를 반환합니다.

        Args:
            project_path: 프로젝트 경로

        Returns:
            RAG 인덱스 디렉토리 경로
        """
        cache_dir = self._get_project_cache_dir(project_path)
        rag_dir = cache_dir / "rag_index"
        rag_dir.mkdir(exist_ok=True)
        return str(rag_dir)

    async def update_last_accessed(self, project_path: str) -> bool:
        """
        마지막 액세스 시간을 업데이트합니다.

        Args:
            project_path: 프로젝트 경로

        Returns:
            업데이트 성공 여부
        """
        cache_dir = self._get_project_cache_dir(project_path)
        session_file = cache_dir / "session.json"

        if not session_file.exists():
            return False

        # 기존 세션 로드
        async with aiofiles.open(session_file, "r", encoding="utf-8") as f:
            content = await f.read()
            session_data = json.loads(content)

        # 시간 업데이트
        session_data["last_accessed"] = datetime.now().isoformat()

        # 저장
        async with aiofiles.open(session_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(session_data, indent=2, ensure_ascii=False))

        return True


# 싱글톤 인스턴스
_session_manager = None


def get_session_manager() -> SessionManager:
    """SessionManager 싱글톤 인스턴스를 반환합니다."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
