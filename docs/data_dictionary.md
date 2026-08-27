# Olist 数据字典

## 数据概览

| 文件 | 行数 | 一行代表 | 业务主键/关联键 | 主要用途 |
|---|---:|---|---|---|
| `olist_orders_dataset.csv` | 99,441 | 一笔订单 | `order_id`；`customer_id` | 订单状态、购买时间、履约时效 |
| `olist_customers_dataset.csv` | 99,441 | 一个订单收货客户身份 | `customer_id`；用户分析用 `customer_unique_id` | 用户、州、市、邮编 |
| `olist_order_items_dataset.csv` | 112,650 | 一笔订单中的一件商品明细 | `order_id`、`order_item_id` | 商品、金额、运费、卖家 |
| `olist_order_payments_dataset.csv` | 103,886 | 一笔支付记录 | `order_id`、`payment_sequential` | 支付方式、实付金额、分期 |
| `olist_order_reviews_dataset.csv` | 99,224 | 一条订单评价 | `order_id`；`review_id` 不作为唯一业务键 | 评分、差评、评论文本 |
| `olist_products_dataset.csv` | 32,951 | 一个商品 | `product_id` | 品类、商品描述和尺寸 |
| `olist_sellers_dataset.csv` | 3,095 | 一个卖家 | `seller_id` | 卖家位置、卖家绩效 |
| `olist_geolocation_dataset.csv` | 1,000,163 | 一个邮编对应的一条地理观测 | `geolocation_zip_code_prefix` 非唯一 | 地理位置、区域分析 |
| `product_category_name_translation.csv` | 71 | 一个葡语品类的英文翻译 | `product_category_name` | 品类名称标准化 |

## 1. 订单表：`olist_orders_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `order_id` | 订单唯一标识 | 字符串；主键 |
| `customer_id` | 该订单对应的收货客户身份 | 字符串；关联 customers |
| `order_status` | 订单状态 | created、approved、invoiced、processing、shipped、delivered、canceled、unavailable |
| `order_purchase_timestamp` | 下单时间 | 时间字段；趋势分析主时间 |
| `order_approved_at` | 订单付款/审批时间 | 时间字段；可能为空 |
| `order_delivered_carrier_date` | 交给物流承运商时间 | 时间字段；可能为空 |
| `order_delivered_customer_date` | 客户签收时间 | 时间字段；可能为空 |
| `order_estimated_delivery_date` | 预计送达时间 | 时间字段；用于判断延迟 |

## 2. 客户表：`olist_customers_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `customer_id` | 订单收货身份标识 | 字符串；与订单一对一关联 |
| `customer_unique_id` | 跨订单的真实用户标识 | 字符串；复购、RFM 必须使用 |
| `customer_zip_code_prefix` | 客户邮编前缀 | 文本；保留前导零 |
| `customer_city` | 客户城市 | 文本 |
| `customer_state` | 客户州 | 巴西州缩写 |

## 3. 订单商品表：`olist_order_items_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `order_id` | 订单标识 | 关联 orders；一订单可多行 |
| `order_item_id` | 订单内商品序号 | 与 `order_id` 组合定位明细 |
| `product_id` | 商品标识 | 关联 products |
| `seller_id` | 卖家标识 | 关联 sellers |
| `shipping_limit_date` | 卖家应发货截止时间 | 时间字段 |
| `price` | 商品价格 | 数值；商品 GMV 的基础 |
| `freight_value` | 该商品分摊的运费 | 数值；与 price 分开分析 |

## 4. 支付表：`olist_order_payments_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `order_id` | 订单标识 | 一订单可多笔支付 |
| `payment_sequential` | 同一订单内支付序号 | 与 `order_id` 组合定位支付 |
| `payment_type` | 支付方式 | credit_card、boleto、voucher、debit_card、not_defined |
| `payment_installments` | 分期期数 | 数值 |
| `payment_value` | 该笔支付金额 | 数值；使用前先按订单汇总 |

## 5. 评价表：`olist_order_reviews_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `review_id` | 评价标识 | 源数据存在重复，不作为唯一键 |
| `order_id` | 被评价订单 | 主要业务关联键 |
| `review_score` | 1-5 分评价 | 评分；1-2 分定义为差评 |
| `review_comment_title` | 评价标题 | 文本；缺失较多 |
| `review_comment_message` | 评价正文 | 文本；缺失较多 |
| `review_creation_date` | 评价创建时间 | 时间字段 |
| `review_answer_timestamp` | 商家/平台回复时间 | 时间字段 |

## 6. 商品表：`olist_products_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `product_id` | 商品标识 | 主键 |
| `product_category_name` | 葡萄牙语品类 | 关联翻译表；可能为空 |
| `product_name_lenght` | 商品名称长度 | 源字段拼写为 `lenght`，原始层保留 |
| `product_description_lenght` | 商品描述长度 | 源字段拼写为 `lenght`，原始层保留 |
| `product_photos_qty` | 商品图片数量 | 数值 |
| `product_weight_g` | 商品重量（克） | 数值；可能为空 |
| `product_length_cm` | 商品长度（厘米） | 数值 |
| `product_height_cm` | 商品高度（厘米） | 数值 |
| `product_width_cm` | 商品宽度（厘米） | 数值 |

## 7. 卖家表：`olist_sellers_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `seller_id` | 卖家标识 | 主键 |
| `seller_zip_code_prefix` | 卖家邮编前缀 | 文本；保留前导零 |
| `seller_city` | 卖家城市 | 文本 |
| `seller_state` | 卖家州 | 州缩写 |

## 8. 地理表：`olist_geolocation_dataset.csv`

| 字段 | 含义 | 类型/注意事项 |
|---|---|---|
| `geolocation_zip_code_prefix` | 邮编前缀 | 非唯一；关联前必须聚合 |
| `geolocation_lat` | 纬度 | 数值 |
| `geolocation_lng` | 经度 | 数值 |
| `geolocation_city` | 地理城市 | 文本 |
| `geolocation_state` | 地理州 | 文本 |

## 9. 品类翻译表：`product_category_name_translation.csv`

| 字段 | 含义 |
|---|---|
| `product_category_name` | 葡萄牙语品类名；关联 products |
| `product_category_name_english` | 英文品类名 |

## 10. 关联规则

```text
orders ── customer_id ── customers ── customer_unique_id（用户主身份）
orders ── order_id ── order_items ── product_id ── products ── 品类翻译
                         └──────── seller_id ── sellers
orders ── order_id ── payments（先聚合）
orders ── order_id ── reviews（先聚合）
customers/sellers ── 邮编前缀 ── geolocation（先去重/聚合）
```

## 11. 关联禁忌

- 不要把订单、商品明细、支付和评价四张明细表直接同时连接。
- 不要用 `customer_id` 计算复购；同一用户可能拥有多个收货身份。
- 不要把地理表原始明细直接连接到订单；同一邮编多行会放大订单量。
- 不要把 `payment_value` 直接当作商品 GMV；两者分别呈现并说明口径。
