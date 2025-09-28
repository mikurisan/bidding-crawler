# bidding-crawler

该项目使用 [Crawl4AI](https://docs.crawl4ai.com/) 框架, 对某招投标网站动态页面进行爬取.

涉及到以下内容:

- 二维码扫码登录
- 持久化登录信息
- 动态搜索
- 点击详情
- 大模型对异构或复杂数据的压缩和提取
- 自动翻页
- 末页判断

## 项目启动

**获取 Libraries**

在 `main.py` 所在目录执行

```shell
pip install pipreqs
pipreqs . --encoding=utf8
```

获取 `requirements.txt` .

构建 `Dockerfile` .

导入环境变量:

```
 export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/mydb?charset=utf8mb4"

 export ALI_API_KEY="sk-98c4xxxxxxx524b5ec"
```

## 整体实现

### 步骤

**Step 1**: 进入'招标'页面后, 输入关键字后'搜索', 开始逐一爬取每一页中的招标 item.

![Step 2](images/img2509191430.png)
**Step 2**: 进入第一个 item.


![Step 3](images/img2509191440.png)
**Step 3**: 来到 detail 界面, 点击"查看了联系人详情"加载联系信息.


![Step 3](images/img2509191444.png)
加载得到联系信息.


![Step 4](images/img2509191446.png)
**Step 4**: 随后分别获取各个部分的信息.

### 数据格式

**head**

```json
{
    "title": "2025年广东产互新型工业化...",
    "type": "招标公告",
    "area": "广东-广州-海珠区",
    "date": "2025/09/10"
}
```

**abstract**

```json
{
    "project_number": "BS-01-26-B",
    "estimated_amount": "405.00万元",
    "bidding_org": "BS-01-26-B",
    "agency": "肇庆市公共资源交...",
    "registration_ddl": "2025年09月26日",
    "bidding_ddl": "2025年10月15日"
}
```

**content**

```json
{
    "summaried_content": "肇庆鼎湖区两....",
    "error": false
}
```

这里对公告内容进行了 summarized.

**contact**

```json
{
    "name": "张先生",
    "telphone": "0758-1234657",
    "error": false
}
```

这里只获取第一个电话不被遮掩的联系人信息.

### 信息存储

将上述内容存储到 MySQL 中.

**head**

```sql
CREATE TABLE qianlima_bidding_detail_head (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    url VARCHAR(2048) NOT NULL,
    type VARCHAR(15),
    area VARCHAR(100),
    released_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci ;
```

**abstract**

```sql
CREATE TABLE qianlima_bidding_detail_abstract (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    head_id BIGINT UNSIGNED,
    project_number VARCHAR(255),
    estimated_amount VARCHAR(255),
    bidding_org VARCHAR(255),
    agency VARCHAR(255),
    registration_ddl DATE,
    bidding_ddl DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci ;
```

**content**

```sql
CREATE TABLE qianlima_bidding_detail_content (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    head_id BIGINT UNSIGNED,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci ;
```

**contact**

```sql
CREATE TABLE qianlima_bidding_detail_contact (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    head_id BIGINT UNSIGNED,
    name VARCHAR(10),
    telphone VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci ;
```

### CRM 推送

采用定期扫描数据表进行推送, 而不是爬取到一条就推送一条, 为此创建一个表用于记录推送情况.

```sql
CREATE TABLE qianlima_bidding_details_to_crm (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    head_id BIGINT UNSIGNED,
    company_name VARCHAR(255),
    description TEXT,
    phone_number VARCHAR(100),
    province VARCHAR(100),
    user_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci ;
```