# 测试文档

## 1. 测试策略

### 1.1 测试目标
确保系统功能正确性、性能稳定性、用户体验友好性，覆盖核心业务场景。

### 1.2 测试范围
- 单元测试：核心算法和函数
- 集成测试：API接口和数据库交互
- 端到端测试：完整业务流程
- 性能测试：系统响应时间和并发能力
- 安全测试：权限控制和数据保护

## 2. 测试环境

### 2.1 硬件环境
- **CPU**: Intel i5 或以上
- **内存**: 8GB 或以上
- **存储**: 10GB 可用空间

### 2.2 软件环境
- **操作系统**: Windows 10/11, macOS 11+, Ubuntu 20.04+
- **Python**: 3.10+
- **Node.js**: 18.0+
- **数据库**: SQLite 3.40+, PostgreSQL 13+

### 2.3 测试工具
- **后端测试**: pytest, pytest-asyncio
- **前端测试**: Jest, Vue Test Utils
- **API测试**: Postman, curl
- **性能测试**: Apache JMeter, locust
- **代码质量**: flake8, pylint, ESLint

## 3. 单元测试

### 3.1 后端单元测试

#### 3.1.1 数据模型测试
```python
# tests/test_models/test_student.py
import pytest
from app.models.student import Student
from app.core.database import SessionLocal

def test_create_student():
    """测试学生创建"""
    student = Student(
        student_no="2021001",
        name="张三",
        class_name="计算机2101",
        major="计算机科学与技术",
        grade_year="2021"
    )
    assert student.student_no == "2021001"
    assert student.name == "张三"
```

#### 3.1.2 分析算法测试
```python
# tests/test_analysis/test_metrics.py
import pytest
import numpy as np
from app.analysis.metrics import calculate_difficulty, calculate_discrimination

def test_difficulty_calculation():
    """测试难度系数计算"""
    scores = [8, 9, 7, 10, 8]  # 平均8.4分
    max_score = 10
    difficulty = calculate_difficulty(scores, max_score)
    assert abs(difficulty - 0.84) < 0.01

def test_discrimination_calculation():
    """测试区分度计算"""
    high_group = [9, 10, 9, 8, 10]  # 高分组
    low_group = [6, 5, 7, 6, 5]     # 低分组
    discrimination = calculate_discrimination(high_group, low_group)
    assert discrimination > 0.3
```

#### 3.1.3 工具函数测试
```python
# tests/test_utils/test_data_processing.py
import pytest
import pandas as pd
from app.utils.data_processing import clean_data, validate_scores

def test_clean_data():
    """测试数据清洗"""
    df = pd.DataFrame({
        'student_no': ['2021001', '2021002', None],
        'score': [85, None, 90]
    })
    cleaned_df = clean_data(df)
    assert len(cleaned_df) == 1
    assert cleaned_df.iloc[0]['student_no'] == '2021001'

def test_validate_scores():
    """测试成绩验证"""
    valid_scores = [85, 90, 75, 60, 100]
    invalid_scores = [85, 90, 75, 60, 100, 105, -5]

    assert validate_scores(valid_scores) == True
    assert validate_scores(invalid_scores) == False
```

### 3.2 前端单元测试

#### 3.2.1 组件测试
```typescript
// tests/unit/StudentForm.spec.ts
import { mount } from '@vue/test-utils'
import StudentForm from '@/components/StudentForm.vue'

describe('StudentForm', () => {
  it('验证表单输入', () => {
    const wrapper = mount(StudentForm)
    const input = wrapper.find('input[type="text"]')

    input.setValue('2021001')
    expect(input.element.value).toBe('2021001')
  })

  it('提交表单事件', async () => {
    const wrapper = mount(StudentForm)
    const submitButton = wrapper.find('button[type="submit"]')

    await submitButton.trigger('click')
    expect(wrapper.emitted('submit')).toBeTruthy()
  })
})
```

#### 3.2.2 API调用测试
```typescript
// tests/unit/api.spec.ts
import { fetchStudents } from '@/api/analysis'
import axios from 'axios'

jest.mock('axios')

describe('API测试', () => {
  it('获取学生列表', async () => {
    const mockData = {
      data: {
        students: [
          { id: 1, student_no: '2021001', name: '张三' }
        ]
      }
    }

    ;(axios.get as jest.Mock).mockResolvedValue(mockData)

    const result = await fetchStudents({})
    expect(result).toEqual(mockData.data)
  })
})
```

## 4. 集成测试

### 4.1 API集成测试

#### 4.1.1 学生管理流程
```python
# tests/integration/test_student_workflow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal

client = TestClient(app)

def test_student_crud_workflow():
    """测试学生CRUD完整流程"""
    # 创建学生
    response = client.post("/api/v1/analysis/students", json={
        "student_no": "2021001",
        "name": "张三",
        "class_name": "计算机2101",
        "major": "计算机科学与技术",
        "grade_year": "2021"
    })
    assert response.status_code == 200
    student_id = response.json()["data"]["id"]

    # 获取学生信息
    response = client.get(f"/api/v1/analysis/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["data"]["student_no"] == "2021001"

    # 更新学生信息
    response = client.put(f"/api/v1/analysis/students/{student_id}", json={
        "name": "张三丰"
    })
    assert response.status_code == 200

    # 删除学生
    response = client.delete(f"/api/v1/analysis/students/{student_id}")
    assert response.status_code == 200

    # 验证删除成功
    response = client.get(f"/api/v1/analysis/students/{student_id}")
    assert response.status_code == 404
```

#### 4.1.2 数据分析流程
```python
# tests/integration/test_analysis_workflow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_score_analysis_workflow():
    """测试成绩分析完整流程"""
    # 创建课程
    response = client.post("/api/v1/analysis/courses", json={
        "course_code": "CS101",
        "course_name": "数据结构",
        "term": "2024-2025-1",
        "department": "计算机学院",
        "major": "计算机科学与技术",
        "credit": 3.0
    })
    course_id = response.json()["data"]["id"]

    # 创建考试
    response = client.post("/api/v1/analysis/exams", json={
        "course_id": course_id,
        "exam_type": "final",
        "name": "期末考试",
        "date": "2025-01-10",
        "total_score": 100
    })
    exam_id = response.json()["data"]["id"]

    # 批量导入成绩
    response = client.post("/api/v1/analysis/student-exam-scores/batch", json={
        "scores": [
            {"student_id": 1, "exam_id": exam_id, "total_score": 85},
            {"student_id": 2, "exam_id": exam_id, "total_score": 92}
        ]
    })
    assert response.status_code == 200

    # 获取分析结果
    response = client.get(f"/api/v1/analysis/score-statistics?course_id={course_id}")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["basic_stats"]["total_students"] == 2
    assert abs(data["basic_stats"]["average_score"] - 88.5) < 0.1
```

### 4.2 数据库集成测试

#### 4.2.1 数据一致性测试
```python
# tests/integration/test_database_consistency.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.student import Student

def test_database_operations():
    """测试数据库操作一致性"""
    # 创建测试数据库
    engine = create_engine("sqlite:///./test.db")
    TestingSessionLocal = sessionmaker(bind=engine)

    # 创建表
    Base.metadata.create_all(bind=engine)

    # 测试数据操作
    db = TestingSessionLocal()

    # 创建学生
    student = Student(
        student_no="2021001",
        name="张三",
        class_name="计算机2101",
        major="计算机科学与技术",
        grade_year="2021"
    )
    db.add(student)
    db.commit()

    # 查询验证
    result = db.query(Student).filter(Student.student_no == "2021001").first()
    assert result is not None
    assert result.name == "张三"

    # 清理
    db.delete(result)
    db.commit()
    db.close()
```

## 5. 系统测试

### 5.1 端到端测试

#### 5.1.1 完整业务流程
```typescript
// tests/e2e/student_analysis.spec.ts
import { test, expect } from '@playwright/test'

test('完整的学生分析流程', async ({ page }) => {
  // 登录系统
  await page.goto('http://localhost:5173')
  await expect(page).toHaveTitle('OBE试卷分析系统')

  // 导入学生数据
  await page.click('text=数据导入')
  await page.setInputFiles('input[type="file"]', 'sample_data/students.csv')
  await page.click('text=上传')
  await expect(page.locator('text=导入成功')).toBeVisible()

  // 创建课程
  await page.click('text=课程管理')
  await page.click('text=添加课程')
  await page.fill('input[name="course_code"]', 'CS101')
  await page.fill('input[name="course_name"]', '数据结构')
  await page.click('text=保存')
  await expect(page.locator('text=数据结构')).toBeVisible()

  // 查看分析结果
  await page.click('text=成绩分析')
  await expect(page.locator('.chart-container')).toBeVisible()
  await expect(page.locator('.stat-card')).toHaveCount(4)
})
```

### 5.2 性能测试

#### 5.2.1 API性能测试
```python
# tests/performance/test_api_performance.py
import locust
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_students(self):
        """测试获取学生列表性能"""
        self.client.get("/api/v1/analysis/students")

    @task
    def get_analysis(self):
        """测试获取分析结果性能"""
        self.client.get("/api/v1/analysis/score-statistics?course_id=1")

    @task(3)
    def upload_scores(self):
        """测试批量上传成绩性能"""
        self.client.post("/api/v1/analysis/student-exam-scores/batch", json={
            "scores": [{"student_id": i, "exam_id": 1, "total_score": 80 + i % 20} for i in range(50)]
        })

# 运行命令: locust -f tests/performance/test_api_performance.py
```

#### 5.2.2 数据库性能测试
```python
# tests/performance/test_database_performance.py
import time
import pytest
from app.core.database import SessionLocal
from app.models.student import Student

def test_database_query_performance():
    """测试数据库查询性能"""
    db = SessionLocal()

    # 插入测试数据
    start_time = time.time()
    for i in range(1000):
        student = Student(
            student_no=f"TEST{i:04d}",
            name=f"测试{i}",
            class_name="测试班级",
            major="测试专业",
            grade_year="2021"
        )
        db.add(student)
    db.commit()
    insert_time = time.time() - start_time

    # 查询性能测试
    start_time = time.time()
    for i in range(100):
        db.query(Student).filter(Student.class_name == "测试班级").all()
    query_time = time.time() - start_time

    db.close()

    assert insert_time < 10  # 插入1000条不超过10秒
    assert query_time < 1    # 100次查询不超过1秒
```

### 5.3 安全测试

#### 5.3.1 权限测试
```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_unauthorized_access():
    """测试未授权访问"""
    # 未登录访问需要认证的接口
    response = client.get("/api/v1/analysis/students")
    assert response.status_code == 401

def test_authorized_access():
    """测试授权访问"""
    # 登录获取token
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["data"]["token"]

    # 使用token访问
    response = client.get("/api/v1/analysis/students", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
```

#### 5.3.2 输入验证测试
```python
# tests/security/test_input_validation.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sql_injection_protection():
    """测试SQL注入防护"""
    response = client.post("/api/v1/analysis/students", json={
        "student_no": "2021001'; DROP TABLE students; --",
        "name": "张三",
        "class_name": "计算机2101",
        "major": "计算机科学与技术",
        "grade_year": "2021"
    })
    assert response.status_code == 400  # 应该被拒绝

def test_xss_protection():
    """测试XSS防护"""
    response = client.post("/api/v1/analysis/students", json={
        "student_no": "2021001",
        "name": "<script>alert('XSS')</script>",
        "class_name": "计算机2101",
        "major": "计算机科学与技术",
        "grade_year": "2021"
    })
    assert response.status_code == 400  # 应该被拒绝
```

## 6. 测试用例汇总

### 6.1 功能测试用例

| 模块 | 测试用例 | 优先级 | 状态 |
|------|----------|--------|------|
| 学生管理 | 添加学生 | 高 | 待执行 |
| 学生管理 | 修改学生信息 | 高 | 待执行 |
| 学生管理 | 删除学生 | 高 | 待执行 |
| 学生管理 | 查询学生列表 | 高 | 待执行 |
| 课程管理 | 添加课程 | 高 | 待执行 |
| 课程管理 | 设置课程目标 | 中 | 待执行 |
| 成绩管理 | 录入成绩 | 高 | 待执行 |
| 成绩管理 | 批量导入成绩 | 高 | 待执行 |
| 成绩分析 | 统计计算 | 高 | 待执行 |
| 成绩分析 | 难度分析 | 高 | 待执行 |
| 成绩分析 | 区分度分析 | 高 | 待执行 |
| OBE分析 | 达成度计算 | 高 | 待执行 |
| 学情预警 | 预警生成 | 高 | 待执行 |
| 学情预警 | 预警处理 | 中 | 待执行 |
| 报表导出 | Excel导出 | 中 | 待执行 |
| 文件上传 | CSV上传 | 高 | 待执行 |
| 文件上传 | Excel上传 | 高 | 待执行 |

### 6.2 性能测试用例

| 测试场景 | 并发数 | 预期响应时间 | 预期吞吐量 |
|----------|--------|--------------|------------|
| 获取学生列表 | 10 | < 200ms | 50 req/s |
| 批量导入成绩 | 5 | < 5s | 10 req/s |
| 成绩分析计算 | 3 | < 10s | 3 req/s |
| 预警生成 | 5 | < 3s | 15 req/s |

## 7. 测试执行计划

### 7.1 第一阶段：单元测试（第1-2周）
- **目标**: 完成所有核心模块的单元测试
- **覆盖率**: 目标80%以上
- **重点**: 数据模型、分析算法、工具函数

### 7.2 第二阶段：集成测试（第3-4周）
- **目标**: 完成API接口集成测试
- **覆盖率**: 所有主要API接口
- **重点**: CRUD操作、数据分析流程、文件上传

### 7.3 第三阶段：系统测试（第5-6周）
- **目标**: 完成端到端测试和性能测试
- **覆盖率**: 主要业务流程
- **重点**: 完整业务流程、系统性能、安全测试

### 7.4 第四阶段：回归测试（持续）
- **目标**: 每次代码变更后执行回归测试
- **范围**: 核心功能测试
- **自动化**: 使用CI/CD自动化测试

## 8. 测试报告

### 8.1 测试执行报告
每次测试执行后生成报告，包括：
- 测试用例执行结果
- 代码覆盖率
- 性能指标
- 缺陷列表
- 风险分析

### 8.2 缺陷管理
使用缺陷跟踪系统记录和管理缺陷：
- **严重程度**: 致命、严重、一般、轻微
- **优先级**: 高、中、低
- **状态**: 新建、处理中、已解决、已验证、已关闭

### 8.3 测试总结报告
项目测试结束后生成总结报告：
- 测试覆盖率总结
- 缺陷分析
- 质量评估
- 改进建议

## 9. 测试工具配置

### 9.1 pytest配置
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=app --cov-report=html --cov-report=term
```

### 9.2 Jest配置
```json
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  testMatch: ['**/tests/**/*.spec.(js|jsx|ts|tsx)'],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
  ],
}
```

## 10. 持续集成

### 10.1 GitHub Actions配置
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run backend tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install frontend dependencies
      run: |
        cd frontend
        npm install

    - name: Run frontend tests
      run: |
        cd frontend
        npm test

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 10.2 代码质量检查
```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Python lint
      run: |
        cd backend
        pip install flake8 black
        flake8 app/
        black --check app/

    - name: TypeScript lint
      run: |
        cd frontend
        npm install
        npm run lint
```

## 11. 测试数据管理

### 11.1 测试数据生成
```python
# tests/utils/data_generator.py
import pandas as pd
import numpy as np

def generate_students(num=100):
    """生成测试学生数据"""
    students = []
    for i in range(num):
        students.append({
            'student_no': f'2021{i:03d}',
            'name': f'学生{i}',
            'class_name': f'班级{i % 5 + 1}',
            'major': '计算机科学与技术',
            'grade_year': '2021'
        })
    return pd.DataFrame(students)

def generate_scores(student_ids, exam_ids, min_score=40, max_score=100):
    """生成测试成绩数据"""
    scores = []
    for student_id in student_ids:
        for exam_id in exam_ids:
            scores.append({
                'student_id': student_id,
                'exam_id': exam_id,
                'total_score': np.random.randint(min_score, max_score)
            })
    return scores
```

### 11.2 测试数据清理
```python
# tests/utils/cleanup.py
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.course import Course

def cleanup_test_data():
    """清理测试数据"""
    db = SessionLocal()

    # 删除测试学生
    db.query(Student).filter(Student.student_no.like('TEST%')).delete()

    # 删除测试课程
    db.query(Course).filter(Course.course_code.like('TEST%')).delete()

    db.commit()
    db.close()
```

## 12. 测试最佳实践

### 12.1 测试编写规范
- 每个测试用例只测试一个功能
- 测试名称清晰表达测试意图
- 使用Arrange-Act-Assert模式
- 避免测试之间的依赖关系

### 12.2 测试数据管理
- 使用独立的测试数据库
- 测试前后清理测试数据
- 使用工厂模式生成测试数据
- 避免硬编码测试数据

### 12.3 测试执行优化
- 并行执行测试
- 使用测试分组
- 优先执行高优先级测试
- 及时清理测试环境

### 12.4 测试维护
- 定期重构测试代码
- 删除过时的测试用例
- 更新测试以适应需求变化
- 保持测试代码的高质量