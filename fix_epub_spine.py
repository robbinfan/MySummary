#!/usr/bin/env python3
"""
修复 Sphinx 9.x epub builder 生成的 content.opf 中
spine 包含 manifest 里不存在的 itemref 的 bug。
"""
import sys
import re
import zipfile
import os

def fix_epub_spine(epub_path):
    tmp_path = epub_path + '.tmp'
    with zipfile.ZipFile(epub_path, 'r') as zin:
        with zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'content.opf':
                    opf = data.decode('utf-8')
                    manifest_ids = set(re.findall(r'<item[^>]+id="([^"]+)"', opf))
                    before = len(re.findall(r'<itemref ', opf))
                    def keep_ref(m):
                        idref = re.search(r'idref="([^"]+)"', m.group(0))
                        if idref and idref.group(1) in manifest_ids:
                            return m.group(0)
                        return ''
                    opf = re.sub(r'<itemref[^/]*/>', keep_ref, opf)
                    after = len(re.findall(r'<itemref ', opf))
                    print(f'Fixed spine: {before} -> {after} items (removed {before - after} invalid)')
                    data = opf.encode('utf-8')
                zout.writestr(item, data)
    os.replace(tmp_path, epub_path)
    print(f'Saved: {epub_path}')

if __name__ == '__main__':
    fix_epub_spine(sys.argv[1])
