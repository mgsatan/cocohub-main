#!/usr/bin/env python3
"""
验证修复代码的静态分析脚本
检查四个关键修改是否正确实现
"""

import re
import json
from pathlib import Path

class CodeValidator:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def check_file(self, filepath, checks):
        """检查单个文件的多个验证点"""
        file_path = Path(filepath)
        if not file_path.exists():
            self.record_check(f"文件存在: {filepath}", False, "文件不存在")
            return

        content = file_path.read_text(encoding='utf-8')
        self.record_check(f"文件存在: {filepath}", True)

        for check_name, check_fn in checks.items():
            try:
                result = check_fn(content)
                self.record_check(check_name, result['passed'], result.get('reason', ''))
            except Exception as e:
                self.record_check(check_name, False, f"检查失败: {str(e)}")

    def record_check(self, name, passed, reason=''):
        """记录检查结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            'name': name,
            'passed': passed,
            'reason': reason,
            'status': status
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status} - {name}")
        if reason:
            print(f"    └─ {reason}")

    def print_summary(self):
        """打印验证总结"""
        print("\n" + "="*60)
        print("验证总结")
        print("="*60)
        print(f"总检查项: {self.passed + self.failed}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print("="*60)

        if self.failed == 0:
            print("🎉 所有验证通过！代码修改符合要求。")
        else:
            print("⚠️  存在验证失败项，请检查上述失败原因。")
        print("="*60 + "\n")

def validate_qr_scanner():
    """验证 QRScannerScreen.tsx 的修改"""
    print("\n【验证 QRScannerScreen.tsx - #51 iOS Torch 修复】")

    def check_usecallback_import(content):
        has_import = 'useCallback' in content and 'from \'react\'' in content
        return {'passed': has_import, 'reason': '' if has_import else '缺少 useCallback 导入'}

    def check_usecallback_usage(content):
        # 检查 toggleTorch 是否使用 useCallback
        pattern = r'const\s+toggleTorch\s*=\s*useCallback\('
        has_usecallback = bool(re.search(pattern, content))
        return {'passed': has_usecallback, 'reason': '' if has_usecallback else 'toggleTorch 未使用 useCallback'}

    def check_functional_update(content):
        # 检查是否使用函数式更新
        has_functional = 'setTorchEnabled(prev => !prev)' in content or 'setTorchEnabled((prev) => !prev)' in content
        return {'passed': has_functional, 'reason': '' if has_functional else '未使用函数式状态更新'}

    return {
        '导入 useCallback': check_usecallback_import,
        '使用 useCallback': check_usecallback_usage,
        '函数式状态更新': check_functional_update,
    }

def validate_settings_screen():
    """验证 SettingsScreen.tsx 的修改"""
    print("\n【验证 SettingsScreen.tsx - #39 暗色模式修复】")

    def check_use_theme(content):
        has_use_theme = 'useAppTheme()' in content
        return {'passed': has_use_theme, 'reason': '' if has_use_theme else '缺少 useAppTheme 调用'}

    def check_no_hardcoded_colors(content):
        # 检查是否还有硬编码颜色（排除注释）
        lines = content.split('\n')
        hardcoded = []
        for i, line in enumerate(lines, 1):
            if '//' in line or '*' in line:
                continue
            if re.search(r'color:\s*[\'"]#[0-9a-fA-F]{3,6}[\'"]', line):
                hardcoded.append(f"Line {i}")

        has_no_hardcoded = len(hardcoded) == 0
        reason = f"发现 {len(hardcoded)} 处硬编码颜色" if hardcoded else ''
        return {'passed': has_no_hardcoded, 'reason': reason}

    def check_theme_colors_used(content):
        # 检查是否使用了主题颜色变量
        # 匹配 style={[styles.xxx, { color: colors.xxx }]} 这样的模式
        uses_theme = re.search(r'\{\s*color:\s*colors\.\w+', content) is not None
        return {'passed': uses_theme, 'reason': '' if uses_theme else '未使用主题颜色变量'}

    return {
        '使用 useAppTheme': check_use_theme,
        '无硬编码颜色': check_no_hardcoded_colors,
        '使用主题颜色': check_theme_colors_used,
    }

def validate_sync_service():
    """验证 syncService.ts 的修改"""
    print("\n【验证 syncService.ts - #52 同步队列修复】")

    def check_success_tracking(content):
        # 检查是否有成功追踪逻辑
        has_tracking = 'succeeded.push' in content and 'succeeded: string[]' in content
        return {'passed': has_tracking, 'reason': '' if has_tracking else '缺少成功追踪逻辑'}

    def check_queue_clear(content):
        # 检查是否清除成功的项目
        # 实际实现：只保留失败项，成功项通过不保留来清除
        has_clear = 'setItem(SYNC_QUEUE_KEY, JSON.stringify(failed))' in content
        return {'passed': has_clear, 'reason': '' if has_clear else '未实现队列清除逻辑'}

    def check_failed_retry(content):
        # 检查失败重试逻辑
        has_retry = 'item.retries += 1' in content and 'failed.push(item)' in content
        return {'passed': has_retry, 'reason': '' if has_retry else '缺少失败重试逻辑'}

    return {
        '成功追踪': check_success_tracking,
        '队列清除': check_queue_clear,
        '失败重试': check_failed_retry,
    }

def validate_sync_engine():
    """验证 syncEngine.ts 的修改"""
    print("\n【验证 syncEngine.ts - #52 同步队列修复】")

    def check_http_status_validation(content):
        # 检查 HTTP 状态码验证
        has_validation = 'response.status < 200 || response.status >= 300' in content
        return {'passed': has_validation, 'reason': '' if has_validation else '缺少 HTTP 状态码验证'}

    def check_explicit_status_check(content):
        # 检查明确的状态检查
        has_check = "first.status !== 'success' && first.status !== 'conflict'" in content
        return {'passed': has_check, 'reason': '' if has_check else '缺少明确的状态检查'}

    return {
        'HTTP 状态码验证': check_http_status_validation,
        '明确状态检查': check_explicit_status_check,
    }

def validate_quick_settings():
    """验证 quickSettingsService.ts 的修改"""
    print("\n【验证 quickSettingsService.ts - #50 Android 锁屏 SOS】")

    def check_file_exists(filepath):
        exists = Path(filepath).exists()
        return {'passed': exists, 'reason': '' if exists else '文件不存在'}

    def check_platform_check(content):
        # 检查平台检查
        has_check = "Platform.OS !== 'android'" in content
        return {'passed': has_check, 'reason': '' if has_check else '缺少平台检查'}

    def check_tile_registration(content):
        # 检查磁贴注册
        has_registration = 'registerSOSTile' in content and 'SOSTileService' in content
        return {'passed': has_registration, 'reason': '' if has_registration else '缺少磁贴注册逻辑'}

    def check_sos_trigger(content):
        # 检查 SOS 触发逻辑
        has_trigger = 'triggerSOS' in content
        return {'passed': has_trigger, 'reason': '' if has_trigger else '缺少 SOS 触发逻辑'}

    filepath = 'D:/hermesagent/cocohub-work/src/services/quickSettingsService.ts'
    file_exists = Path(filepath).exists()

    if not file_exists:
        return {
            '文件存在': check_file_exists,
            '平台检查': lambda c: {'passed': False, 'reason': '文件不存在'},
            '磁贴注册': lambda c: {'passed': False, 'reason': '文件不存在'},
            'SOS 触发': lambda c: {'passed': False, 'reason': '文件不存在'},
        }

    content = Path(filepath).read_text(encoding='utf-8')
    return {
        '平台检查': check_platform_check,
        '磁贴注册': check_tile_registration,
        'SOS 触发': check_sos_trigger,
    }

def main():
    """主验证流程"""
    print("\n" + "="*60)
    print("CocoHub 代码修复验证")
    print("="*60)

    validator = CodeValidator()

    # 验证各个文件的修改
    validator.check_file(
        'D:/hermesagent/cocohub-work/src/screens/QRScannerScreen.tsx',
        validate_qr_scanner()
    )

    validator.check_file(
        'D:/hermesagent/cocohub-work/src/screens/SettingsScreen.tsx',
        validate_settings_screen()
    )

    validator.check_file(
        'D:/hermesagent/cocohub-work/src/services/syncService.ts',
        validate_sync_service()
    )

    validator.check_file(
        'D:/hermesagent/cocohub-work/src/services/syncEngine.ts',
        validate_sync_engine()
    )

    validator.check_file(
        'D:/hermesagent/cocohub-work/src/services/quickSettingsService.ts',
        validate_quick_settings()
    )

    validator.print_summary()

    return validator.failed == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
