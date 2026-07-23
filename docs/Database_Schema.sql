-- BlendiOS SQLite Database Schema
-- Version: 1.0.0
-- Description: Complete database schema for users, sessions, VFS, settings,
--              processes, logs, installed apps, and themes.

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Table: users
-- Stores system user accounts with role and security metadata.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    email           TEXT UNIQUE,
    full_name       TEXT,
    hashed_password TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('admin', 'user', 'guest')),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
    is_locked       INTEGER NOT NULL DEFAULT 0 CHECK(is_locked IN (0, 1)),
    failed_logins   INTEGER NOT NULL DEFAULT 0,
    last_login_at   TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- ---------------------------------------------------------------------------
-- Table: sessions
-- Active and expired login sessions / bearer tokens.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    token           TEXT NOT NULL UNIQUE,
    refresh_token   TEXT UNIQUE,
    ip_address      TEXT,
    user_agent      TEXT,
    issued_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP NOT NULL,
    refresh_expires_at TIMESTAMP,
    is_revoked      INTEGER NOT NULL DEFAULT 0 CHECK(is_revoked IN (0, 1)),
    revoked_at      TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

-- ---------------------------------------------------------------------------
-- Table: folders
-- Virtual folder metadata for the VFS.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS folders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id       INTEGER,
    name            TEXT NOT NULL,
    path            TEXT NOT NULL UNIQUE,
    owner_id        INTEGER NOT NULL,
    group_id        INTEGER,
    permissions     TEXT NOT NULL DEFAULT '755',
    is_encrypted    INTEGER NOT NULL DEFAULT 0 CHECK(is_encrypted IN (0, 1)),
    is_compressed   INTEGER NOT NULL DEFAULT 0 CHECK(is_compressed IN (0, 1)),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_folders_path ON folders(path);
CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_id);
CREATE INDEX IF NOT EXISTS idx_folders_owner ON folders(owner_id);

-- ---------------------------------------------------------------------------
-- Table: files
-- Virtual file metadata and content reference for the VFS.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS files (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_id       INTEGER NOT NULL,
    name            TEXT NOT NULL,
    path            TEXT NOT NULL UNIQUE,
    owner_id        INTEGER NOT NULL,
    group_id        INTEGER,
    permissions     TEXT NOT NULL DEFAULT '644',
    size_bytes      INTEGER NOT NULL DEFAULT 0,
    mime_type       TEXT,
    content_ref     TEXT,                   -- host filesystem path or blob reference
    checksum        TEXT,                   -- sha256 of decrypted content
    is_encrypted    INTEGER NOT NULL DEFAULT 0 CHECK(is_encrypted IN (0, 1)),
    is_compressed   INTEGER NOT NULL DEFAULT 0 CHECK(is_compressed IN (0, 1)),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
CREATE INDEX IF NOT EXISTS idx_files_folder ON files(folder_id);
CREATE INDEX IF NOT EXISTS idx_files_owner ON files(owner_id);
CREATE INDEX IF NOT EXISTS idx_files_mime ON files(mime_type);

-- ---------------------------------------------------------------------------
-- Table: settings
-- Key-value store for system and user preferences.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS settings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER,                -- NULL for global settings
    key             TEXT NOT NULL,
    value           TEXT,
    value_type      TEXT NOT NULL DEFAULT 'string' CHECK(value_type IN ('string', 'int', 'float', 'bool', 'json')),
    category        TEXT NOT NULL DEFAULT 'general',
    is_editable     INTEGER NOT NULL DEFAULT 1 CHECK(is_editable IN (0, 1)),
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_settings_user_key ON settings(user_id, key);
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);

-- ---------------------------------------------------------------------------
-- Table: processes
-- Running and historical process records.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS processes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pid             INTEGER NOT NULL UNIQUE,-- simulated process ID
    app_id          TEXT NOT NULL,
    user_id         INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'running' CHECK(status IN ('running', 'sleeping', 'stopped', 'terminated', 'crashed')),
    priority        INTEGER NOT NULL DEFAULT 5,
    memory_mb       INTEGER NOT NULL DEFAULT 0,
    cpu_percent     REAL DEFAULT 0.0,
    started_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at        TIMESTAMP,
    exit_code       INTEGER,
    command_line    TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_processes_pid ON processes(pid);
CREATE INDEX IF NOT EXISTS idx_processes_user ON processes(user_id);
CREATE INDEX IF NOT EXISTS idx_processes_status ON processes(status);
CREATE INDEX IF NOT EXISTS idx_processes_app ON processes(app_id);

-- ---------------------------------------------------------------------------
-- Table: logs
-- Audit and system event logs.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    level           TEXT NOT NULL DEFAULT 'INFO' CHECK(level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    category        TEXT NOT NULL DEFAULT 'system',
    user_id         INTEGER,
    session_id      INTEGER,
    source          TEXT NOT NULL,          -- module or component name
    message         TEXT NOT NULL,
    details         TEXT,                   -- JSON-encoded extra data
    ip_address      TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_category ON logs(category);
CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);

-- ---------------------------------------------------------------------------
-- Table: installed_apps
-- Installed applications and plugins metadata.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS installed_apps (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id          TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    version         TEXT NOT NULL,
    description     TEXT,
    author          TEXT,
    category        TEXT,
    entry_point     TEXT NOT NULL,          -- module path or plugin reference
    icon_path       TEXT,
    is_system       INTEGER NOT NULL DEFAULT 0 CHECK(is_system IN (0, 1)),
    is_plugin       INTEGER NOT NULL DEFAULT 0 CHECK(is_plugin IN (0, 1)),
    permissions     TEXT,                   -- JSON array of required permissions
    install_path    TEXT,
    installed_by    INTEGER NOT NULL,
    installed_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (installed_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_installed_apps_app_id ON installed_apps(app_id);
CREATE INDEX IF NOT EXISTS idx_installed_apps_category ON installed_apps(category);

-- ---------------------------------------------------------------------------
-- Table: themes
-- Installed theme definitions.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS themes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_id        TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    is_builtin      INTEGER NOT NULL DEFAULT 0 CHECK(is_builtin IN (0, 1)),
    is_custom       INTEGER NOT NULL DEFAULT 0 CHECK(is_custom IN (0, 1)),
    source_path     TEXT,
    palette_json    TEXT NOT NULL,          -- JSON theme definition
    fonts_json      TEXT,
    spacing_json    TEXT,
    created_by      INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_themes_theme_id ON themes(theme_id);

-- ---------------------------------------------------------------------------
-- Table: trash
-- Deleted files/folders pending permanent removal or restore.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trash (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path   TEXT NOT NULL,
    storage_path    TEXT NOT NULL,
    node_type       TEXT NOT NULL CHECK(node_type IN ('file', 'folder')),
    owner_id        INTEGER NOT NULL,
    deleted_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_trash_owner ON trash(owner_id);
CREATE INDEX IF NOT EXISTS idx_trash_expires ON trash(expires_at);

-- ---------------------------------------------------------------------------
-- Seed Data: Default Admin User
-- Password must be changed on first login. The placeholder hash below is
-- intentionally invalid; it should be generated by the auth service.
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO users (id, username, full_name, role, hashed_password)
VALUES (1, 'admin', 'System Administrator', 'admin', '__CHANGE_ME__');

-- Seed Data: Default Themes
INSERT OR IGNORE INTO themes (theme_id, name, is_builtin, palette_json)
VALUES (
    'dark',
    'Dark',
    1,
    '{"window":"#1e1e1e","window_text":"#ffffff","base":"#252526","alternate_base":"#2d2d30","accent":"#0078d4","button":"#3c3c3c","button_text":"#ffffff","border":"#5a5a5a","error":"#f44336","warning":"#ff9800","success":"#4caf50"}'
);

INSERT OR IGNORE INTO themes (theme_id, name, is_builtin, palette_json)
VALUES (
    'light',
    'Light',
    1,
    '{"window":"#ffffff","window_text":"#000000","base":"#f5f5f5","alternate_base":"#e0e0e0","accent":"#0078d4","button":"#e1e1e1","button_text":"#000000","border":"#bdbdbd","error":"#d32f2f","warning":"#f57c00","success":"#388e3c"}'
);

-- ---------------------------------------------------------------------------
-- Seed Data: Global Settings
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO settings (key, value, value_type, category)
VALUES
    ('theme', 'dark', 'string', 'appearance'),
    ('language', 'en', 'string', 'locale'),
    ('animations_enabled', 'true', 'bool', 'appearance'),
    ('notification_do_not_disturb', 'false', 'bool', 'notifications'),
    ('max_failed_logins', '5', 'int', 'security'),
    ('session_ttl_minutes', '60', 'int', 'security'),
    ('default_scheduler', 'round_robin', 'string', 'kernel'),
    ('total_ram_mb', '4096', 'int', 'kernel');
