# Code Style & Standards Skill

**版本**: v1.0.0  
**创建日期**: 2026-03-05  
**目标**: 统一代码风格，提高代码质量，减少代码审查成本

---

## 🎯 核心原则

### 1. 一致性 (Consistency)
- 整个项目使用统一的代码风格
- 遵循语言/框架的最佳实践
- 自动化检查代替人工审查

### 2. 可读性 (Readability)
- 代码是写给人看的
- 清晰的命名和结构
- 适当的注释和文档

### 3. 可维护性 (Maintainability)
- 模块化设计
- 单一职责原则
- 易于测试和重构

---

## 📋 代码规范

### TypeScript/JavaScript

#### 命名规范

```typescript
// ✅ 好的命名
const userName = 'John';           // 变量：camelCase
class UserService {}               // 类：PascalCase
function getUserInfo() {}          // 函数：camelCase
const API_BASE_URL = '...';        // 常量：UPPER_SNAKE_CASE
interface UserInfo {}              // 接口：PascalCase
type UserStatus = 'active' | 'inactive';  // 类型：PascalCase

// ❌ 坏的命名
const user_name = 'John';          // 不要用 snake_case
const UserName = 'John';           // 变量不要用 PascalCase
const apiBaseURL = '...';          // 常量要用大写
```

#### 代码格式

```typescript
// ✅ 好的格式
interface User {
  id: number;
  name: string;
  email?: string;  // 可选属性
}

function greet(user: User): string {
  return `Hello, ${user.name}!`;
}

// ❌ 坏的格式
interface User{id:number;name:string;email?:string;}
function greet(user:User):string{return `Hello, ${user.name}!`;}
```

#### 类型注解

```typescript
// ✅ 明确的类型注解
function add(a: number, b: number): number {
  return a + b;
}

// ✅ 使用类型别名
type UserID = string | number;
type Callback<T> = (result: T) => void;

// ❌ 避免使用 any
function process(data: any) {  // ❌
  return data;
}

// ✅ 使用 unknown 代替 any
function process(data: unknown) {  // ✅
  if (typeof data === 'string') {
    return data.toUpperCase();
  }
  return data;
}
```

### Python

#### 命名规范 (PEP 8)

```python
# ✅ 好的命名
user_name = 'John'           # 变量：snake_case
class UserService:           # 类：PascalCase
def get_user_info():         # 函数：snake_case
API_BASE_URL = '...'         # 常量：UPPER_SNAKE_CASE
_private_var = 'hidden'      # 私有：前缀下划线

# ❌ 坏的命名
userName = 'John'            # 不要用 camelCase
class userService:           # 类要用 PascalCase
```

#### 代码格式

```python
# ✅ 好的格式
def greet(user: dict) -> str:
    """Say hello to user."""
    return f"Hello, {user['name']}!"

class UserService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_user(self, user_id: int) -> dict:
        return self.db.query(user_id)

# ❌ 坏的格式
def greet(user):return f"Hello, {user['name']}!"
class UserService:
    def __init__(self,db):self.db=db
```

#### 文档字符串

```python
# ✅ 完整的文档字符串
def calculate_total(items: list[float], tax_rate: float) -> float:
    """
    Calculate total price with tax.
    
    Args:
        items: List of item prices
        tax_rate: Tax rate (e.g., 0.1 for 10%)
    
    Returns:
        Total price including tax
    
    Raises:
        ValueError: If tax_rate is negative
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

---

## 🛠️ 工具配置

### ESLint (TypeScript/JavaScript)

**位置**: `.eslintrc.json`

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "error",
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

### Prettier

**位置**: `.prettierrc`

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true
}
```

### Python (Black + Flake8)

**位置**: `pyproject.toml`

```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.flake8]
max-line-length = 88
extend-ignore = ['E203', 'W503']
```

---

## 📝 Git 提交规范

### Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Type 类型

| Type | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(api): 添加用户认证` |
| `fix` | Bug 修复 | `fix(memory): 修复内存泄漏` |
| `docs` | 文档更新 | `docs(readme): 更新安装说明` |
| `style` | 代码格式 | `style(css): 格式化样式代码` |
| `refactor` | 重构 | `refactor(core): 优化架构` |
| `perf` | 性能优化 | `perf(db): 优化数据库查询` |
| `test` | 测试相关 | `test(unit): 添加单元测试` |
| `chore` | 构建/工具 | `chore(deps): 更新依赖` |

#### 示例

```bash
# ✅ 好的提交信息
git commit -m "feat(auth): 添加 JWT 认证支持"
git commit -m "fix(api): 修复用户列表分页错误"
git commit -m "docs(readme): 添加快速开始指南"

# ❌ 坏的提交信息
git commit -m "更新代码"
git commit -m "fix bug"
git commit -m "asdfasdf"
```

---

## 🔍 代码审查清单

### 通用检查

- [ ] 代码符合命名规范
- [ ] 函数/方法长度合理 (< 50 行)
- [ ] 类职责单一
- [ ] 错误处理完善
- [ ] 日志记录适当
- [ ] 无硬编码值
- [ ] 无敏感信息泄露

### TypeScript/JavaScript 检查

- [ ] 使用严格模式
- [ ] 类型注解完整
- [ ] 避免使用 `any`
- [ ] Promise 正确处理
- [ ] 异步代码使用 async/await

### Python 检查

- [ ] 遵循 PEP 8
- [ ] 类型注解完整
- [ ] 文档字符串完整
- [ ] 异常处理适当
- [ ] 使用 context manager

---

## 🚀 自动化检查

### Git Hooks (Husky)

**位置**: `.husky/pre-commit`

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# TypeScript/JavaScript
npm run lint
npm run format:check

# Python
black --check .
flake8 .

# 提交信息检查
npx commitlint --edit
```

### CI/CD 检查

**位置**: `.github/workflows/lint.yml`

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run ESLint
        run: npm run lint
      
      - name: Run Prettier check
        run: npm run format:check
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Python tools
        run: pip install black flake8
      
      - name: Run Black
        run: black --check .
      
      - name: Run Flake8
        run: flake8 .
```

---

## 📚 最佳实践

### 1. DRY (Don't Repeat Yourself)

```typescript
// ❌ 重复代码
function getUserName(user: User): string {
  return user.firstName + ' ' + user.lastName;
}

function formatUserName(first: string, last: string): string {
  return first + ' ' + last;
}

// ✅ 提取公共逻辑
function formatName(first: string, last: string): string {
  return `${first} ${last}`;
}

function getUserName(user: User): string {
  return formatName(user.firstName, user.lastName);
}
```

### 2. SOLID 原则

#### 单一职责原则 (SRP)

```python
# ❌ 多个职责
class UserService:
    def get_user(self, user_id): ...
    def save_user(self, user): ...
    def send_email(self, user, message): ...
    def log_action(self, action): ...

# ✅ 单一职责
class UserRepository:
    def get_user(self, user_id): ...
    def save_user(self, user): ...

class EmailService:
    def send_email(self, user, message): ...

class AuditLogger:
    def log_action(self, action): ...
```

### 3. 错误处理

```typescript
// ❌ 忽略错误
async function fetchData() {
  const data = await api.get('/data');
  return data;
}

// ✅ 正确处理错误
async function fetchData(): Promise<Data> {
  try {
    const response = await api.get('/data');
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch data', error);
    throw new DataFetchError('Unable to load data', error);
  }
}
```

---

## 🎓 学习资源

### 官方文档
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### 书籍
- 《Clean Code》- Robert C. Martin
- 《The Pragmatic Programmer》- Andrew Hunt
- 《Code Complete》- Steve McConnell

### 工具
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)
- [Black](https://black.readthedocs.io/)
- [Husky](https://typicode.github.io/husky/)

---

## 🔧 快速开始

### 1. 安装工具

```bash
# TypeScript/JavaScript
npm install -D eslint prettier @typescript-eslint/parser

# Python
pip install black flake8 mypy

# Git Hooks
npm install -D husky lint-staged
```

### 2. 配置文件

```bash
# 复制配置模板
cp config/templates/.eslintrc.json .
cp config/templates/.prettierrc .
cp config/templates/pyproject.toml .
```

### 3. 运行检查

```bash
# 手动检查
npm run lint
black --check .

# 自动修复
npm run lint:fix
black .
```

---

## 📊 质量指标

### 代码质量评分

| 指标 | 目标 | 检查命令 |
|------|------|---------|
| ESLint 错误 | 0 | `npm run lint` |
| Prettier 格式 | 100% | `npm run format:check` |
| 测试覆盖率 | > 80% | `npm run test:coverage` |
| 类型覆盖率 | > 90% | `tsc --noEmit` |
| 重复代码 | < 5% | `npm run dupcheck` |

---

*此技能持续改进中，欢迎反馈和建议。*

**维护者**: FullStack Engineer with Memory Intelligence  
**最后更新**: 2026-03-05  
**版本**: 1.0.0
