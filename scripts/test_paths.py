"""Regression check for local root and Pages project paths without changing dist/."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='journal-paths-') as tmp:
    project = Path(tmp)
    for folder in ('scripts', 'content', 'templates', 'assets'):
        shutil.copytree(ROOT / folder, project / folder)
    outputs = []
    for prefix in ('', '/naoki-journal'):
        env = dict(os.environ, JOURNAL_BASE_PATH=prefix,
                   JOURNAL_SITE_URL='https://naoki-suehiro.github.io/naoki-journal')
        for script in ('build.py', 'check.py'):
            subprocess.run([sys.executable, '-B', str(project / 'scripts' / script)], env=env, check=True)
        outputs.append({str(p.relative_to(project / 'dist')): p.read_bytes()
                        for p in (project / 'dist').rglob('*') if p.is_file()})
        # Simulate the original regression: a nested article points outside the mount.
        page = project / 'dist/stories/language-as-infrastructure/index.html'
        good = page.read_text()
        page.write_text(good.replace('href="' + prefix + '/assets/style.css"',
                                     'href="/wrong-root/assets/style.css"'))
        result = subprocess.run([sys.executable, '-B', str(project / 'scripts/check.py')],
                                env=env, capture_output=True)
        assert result.returncode != 0, 'Checker failed to catch broken asset path'
    assert outputs[0].keys() == outputs[1].keys()
    for path, local in outputs[0].items():
        pages = outputs[1][path]
        if path.endswith('.html'):
            pages = pages.replace(b'href="/naoki-journal/', b'href="/').replace(b'src="/naoki-journal/', b'src="/').replace(b'poster="/naoki-journal/', b'poster="/')
        assert pages == local, 'Unexpected content difference: ' + path
print('PASS: root/project builds match except URL prefixes; broken paths are rejected.')
