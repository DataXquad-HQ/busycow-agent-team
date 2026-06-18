#!/usr/bin/env python3
"""Sync a shared skill from the canonical ~/.hermes/skills layer into one or more
Hermes profile skill directories.

Default behavior:
- copy from canonical source
- if destination exists, require --force to overwrite
- optional timestamped backup before overwrite

Examples:
  python sync_shared_skill.py --skill core/routing-report-delivery --profiles leo maya rex --force --backup
  python sync_shared_skill.py --skill core/managing-shared-skills --profiles leo
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
CANONICAL_ROOT = HOME / '.hermes' / 'skills'
PROFILES_ROOT = HOME / '.hermes' / 'profiles'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--skill', required=True, help='Canonical skill path relative to ~/.hermes/skills, e.g. core/routing-report-delivery')
    p.add_argument('--profiles', nargs='+', required=True, help='Target profile names, e.g. leo maya rex')
    p.add_argument('--force', action='store_true', help='Overwrite destination if it already exists')
    p.add_argument('--backup', action='store_true', help='Create timestamped backup before overwrite')
    p.add_argument('--dry-run', action='store_true', help='Show actions without changing files')
    return p.parse_args()


def fail(msg: str) -> None:
    print(f'ERROR: {msg}', file=sys.stderr)
    raise SystemExit(1)


def backup_dir(path: Path, dry_run: bool) -> Path:
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = path.parent / f'{path.name}.backup-{stamp}'
    if dry_run:
        print(f'DRY-RUN backup {path} -> {backup}')
    else:
        shutil.copytree(path, backup)
        print(f'BACKUP {path} -> {backup}')
    return backup


def main() -> int:
    args = parse_args()
    src = CANONICAL_ROOT / args.skill
    if not src.is_dir():
        fail(f'Canonical skill not found: {src}')

    skill_name = src.name
    print(f'SOURCE {src}')

    for profile in args.profiles:
        profile_root = PROFILES_ROOT / profile
        if not profile_root.is_dir():
            fail(f'Profile not found: {profile_root}')

        skills_dir = profile_root / 'skills'
        if not skills_dir.is_dir():
            fail(f'Profile skills dir not found: {skills_dir}')

        dest = skills_dir / skill_name
        if dest.exists():
            if not args.force:
                fail(f'Destination exists: {dest} (use --force to overwrite)')
            if args.backup:
                backup_dir(dest, args.dry_run)
            if args.dry_run:
                print(f'DRY-RUN remove {dest}')
            else:
                shutil.rmtree(dest)
                print(f'REMOVED {dest}')

        if args.dry_run:
            print(f'DRY-RUN copy {src} -> {dest}')
        else:
            shutil.copytree(src, dest)
            print(f'COPIED {src} -> {dest}')

        skill_md = dest / 'SKILL.md'
        if args.dry_run:
            print(f'DRY-RUN verify {skill_md}')
        else:
            if not skill_md.is_file():
                fail(f'Missing SKILL.md after copy: {skill_md}')
            print(f'VERIFIED {skill_md}')

    print('DONE')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
