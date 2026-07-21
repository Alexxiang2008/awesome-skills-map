"""
test_shared.py - _shared.py 公共函数测试

最薄烟雾测试：每个公共函数 1 个 test
"""
import sys
from pathlib import Path

# 让 _shared 可被 import
sys.path.insert(0, str(Path(__file__).parent))

from _shared import (
    cache_key,
    err_msg,
    warn_msg,
    ok_msg,
    render_card_html,
)


# ============================================================
# cache_key
# ============================================================

def test_cache_key_repo():
    """cache_key('repo', 'owner/repo') 应返回 'repo:owner/repo'"""
    assert cache_key('repo', 'owner/repo') == 'repo:owner/repo'


def test_cache_key_desc():
    """cache_key('desc', 'hello') 应返回 'desc:hello'"""
    assert cache_key('desc', 'hello') == 'desc:hello'


def test_cache_key_special_chars():
    """特殊字符（中文/引号/换行）应原样保留"""
    text = '含"中文"和\n换行'
    key = cache_key('desc', text)
    assert key == f'desc:{text}'
    assert '含' in key


# ============================================================
# 错误消息函数
# ============================================================

def test_err_msg():
    """err_msg 应以 ❌ 开头"""
    assert err_msg('something failed') == '❌ something failed'


def test_warn_msg():
    """warn_msg 应以 ⚠️ 开头"""
    assert warn_msg('something suspicious') == '⚠️ something suspicious'


def test_ok_msg():
    """ok_msg 应以 ✅ 开头"""
    assert ok_msg('done') == '✅ done'


# ============================================================
# render_card_html
# ============================================================

def test_render_card_minimal():
    """最简卡片（只 name + url）应生成有效 HTML"""
    html = render_card_html(
        skill_id='test-skill',
        name='Test Skill',
        url='https://github.com/test/skill',
        desc='A test description',
        category='test_category',
    )
    assert 'data-id="Test Skill"' in html  # 注意：name 会被 escape
    assert 'Test Skill' in html
    assert 'https://github.com/test/skill' in html
    assert 'A test description' in html
    assert 'test_category' in html
    assert 'card-checkbox' in html
    assert 'class="card"' in html


def test_render_card_escapes_quotes():
    """卡片名含引号应被转义（不破坏 HTML attribute）"""
    html = render_card_html(
        skill_id='q',
        name='name with "quotes"',
        url='u',
        desc='d',
        category='c',
    )
    # 应该有 &quot; 而不是裸的 "
    assert '&quot;' in html
    # 不能破坏 HTML structure
    assert html.count('<div class="card">') == 1


def test_render_card_extra_badge():
    """extra_badge 参数应插入到 name 后面"""
    html = render_card_html(
        skill_id='b',
        name='badge test',
        url='u',
        desc='d',
        category='c',
        extra_badge='<span class="test-badge">🆕</span>',
    )
    assert 'test-badge' in html
    assert '🆕' in html


# ============================================================
# taxonomy 数据完整性（不依赖外部 import）
# ============================================================

def test_taxonomy_loads():
    """taxonomy.yaml 应能被 PyYAML 解析"""
    import yaml
    path = Path(__file__).parent / 'taxonomy.yaml'
    if not path.exists():
        return  # 跳过（不一定存在）
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    assert 'skills' in data
    assert isinstance(data['skills'], list)
    assert len(data['skills']) > 0


def test_taxonomy_no_duplicate_ids():
    """taxonomy.yaml 的 skill id 应该唯一"""
    import yaml
    path = Path(__file__).parent / 'taxonomy.yaml'
    if not path.exists():
        return
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    ids = [s.get('id') for s in data.get('skills', []) if s.get('id')]
    assert len(ids) == len(set(ids)), f"重复 id: {[i for i in ids if ids.count(i) > 1]}"


def test_taxonomy_required_fields():
    """每个 skill 应有 id / name / author / tags / primary_category / type"""
    import yaml
    path = Path(__file__).parent / 'taxonomy.yaml'
    if not path.exists():
        return
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    required = ['id', 'name', 'author', 'tags', 'primary_category', 'type']
    for s in data.get('skills', []):
        for f in required:
            assert f in s and s[f], f"skill {s.get('id')} 缺 {f}"
