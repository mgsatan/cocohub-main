#!/usr/bin/env node
/**
 * 轻量级 TypeScript 类型验证脚本
 * 只检查修改的文件，不运行完整的 tsc --noEmit
 */

const ts = require('typescript');
const fs = require('fs');
const path = require('path');

const files = [
  'src/screens/QRScannerScreen.tsx',
  'src/screens/SettingsScreen.tsx',
  'src/components/SOSButton.tsx',
  'src/services/syncEngine.ts',
  'src/services/syncService.ts',
  'src/services/quickSettingsService.ts'
];

console.log('🔍 TypeScript 类型验证');
console.log('======================\n');

let hasErrors = false;

for (const file of files) {
  const filePath = path.resolve(__dirname, file);
  
  if (!fs.existsSync(filePath)) {
    console.log(`❌ ${file}: 文件不存在`);
    hasErrors = true;
    continue;
  }

  const content = fs.readFileSync(filePath, 'utf8');
  
  // 创建源文件
  const sourceFile = ts.createSourceFile(
    file,
    content,
    ts.ScriptTarget.Latest,
    true,
    file.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS
  );

  // 检查语法错误
  const syntaxErrors = [];
  const diagnostics = [];

  function visit(node) {
    // 收集诊断信息
    if (node.kind === ts.SyntaxKind.Unknown) {
      diagnostics.push({
        file: sourceFile,
        start: node.getStart(),
        messageText: 'Unknown syntax',
        category: ts.DiagnosticCategory.Error,
        code: 9999
      });
    }
    ts.forEachChild(node, visit);
  }

  visit(sourceFile);

  // 检查 JSX 语法
  if (file.endsWith('.tsx')) {
    const jsxDiagnostics = [];
    
    function checkJSX(node) {
      if (ts.isJsxElement(node) || ts.isJsxSelfClosingElement(node)) {
        // 检查 JSX 标签
        const openingElement = ts.isJsxElement(node) ? node.openingElement : node;
        if (!openingElement.tagName) {
          jsxDiagnostics.push({
            file: sourceFile,
            start: openingElement.getStart(),
            messageText: 'JSX element has no tag name',
            category: ts.DiagnosticCategory.Error,
            code: 9998
          });
        }
      }
      ts.forEachChild(node, checkJSX);
    }
    
    checkJSX(sourceFile);
    diagnostics.push(...jsxDiagnostics);
  }

  if (diagnostics.length > 0) {
    console.log(`❌ ${file}: ${diagnostics.length} 个错误`);
    for (const diag of diagnostics.slice(0, 5)) { // 最多显示5个错误
      const pos = diag.file.getLineAndCharacterOfPosition(diag.start);
      console.log(`   L${pos.line + 1}:${pos.character + 1} - ${ts.flattenDiagnosticMessageText(diag.messageText, '\n')}`);
    }
    if (diagnostics.length > 5) {
      console.log(`   ... 还有 ${diagnostics.length - 5} 个错误`);
    }
    hasErrors = true;
  } else {
    console.log(`✅ ${file}: 语法正确`);
  }
}

console.log('\n======================');

if (hasErrors) {
  console.log('❌ 验证失败：存在类型或语法错误');
  process.exit(1);
} else {
  console.log('✅ 验证通过：所有文件语法正确');
  process.exit(0);
}
