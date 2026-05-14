import importlib.util
from pathlib import Path


def test_ensure_local_jwt_secret_creates_and_persists_secret(tmp_path):
    backend_root = tmp_path / "backend"
    config_dir = backend_root / "app" / "core"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.py"

    source = Path("app/core/config.py").read_text(encoding="utf-8")
    config_file.write_text(source, encoding="utf-8")
    (backend_root / ".env.example").write_text(
        "APP_NAME=AI Resume Intelligence\nJWT_SECRET=auto-generate-for-local-dev\n",
        encoding="utf-8",
    )

    spec = importlib.util.spec_from_file_location("temp_config", config_file)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    env_file = backend_root / ".env"
    env_text = env_file.read_text(encoding="utf-8")
    assert "JWT_SECRET=auto-generate-for-local-dev" not in env_text
    assert "JWT_SECRET=" in env_text
    secret_line = [line for line in env_text.splitlines() if line.startswith("JWT_SECRET=")][0]
    assert len(secret_line.split("=", 1)[1]) >= 32


def test_ensure_local_jwt_secret_does_not_overwrite_existing_secret(tmp_path):
    backend_root = tmp_path / "backend"
    config_dir = backend_root / "app" / "core"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.py"

    source = Path("app/core/config.py").read_text(encoding="utf-8")
    config_file.write_text(source, encoding="utf-8")
    (backend_root / ".env").write_text(
        "JWT_SECRET=my-existing-secret-1234567890\n",
        encoding="utf-8",
    )

    spec = importlib.util.spec_from_file_location("temp_config_existing", config_file)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    env_text = (backend_root / ".env").read_text(encoding="utf-8")
    assert "JWT_SECRET=my-existing-secret-1234567890" in env_text
