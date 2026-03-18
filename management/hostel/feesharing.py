# hostel/fee/utils.py

# from decimal import Decimal, ROUND_HALF_UP
# from datetime import datetime
# from django.db.models import Q

# def recalculate_fee_and_sharing(room, year: int, month: int):
#     """
#     【核心函数】手动触发：重新计算某个房间某月的总费用 + 个人分摊
#     所有视图中只要涉及“用量变更”、“计费项目变更”、“入住变更”，都调用这个函数！
#     """
#     from .models import feetype, useage, fee_record_one, occupancyrecord, sharing

#     # 1. 确定当月日期
#     month_date = datetime(year, month, 1)

#     # 2. 获取或创建当月费用记录
#     fee_record, _ = fee_record_one.objects.get_or_create(
#         room=room,
#         date=month_date,
#         defaults={'check_people': 'system', 'status': '0'}
#     )

#     total_amount = Decimal('0')
#     dynamic_fees = {}

#     # 3. 获取该区域所有启用计费项目
#     active_types = feetype.objects.filter(area=room.dorm.area, status='启用')

#     for ft in active_types:
#         if ft.is_sign:
#             # 固定费用
#             amount = Decimal(ft.fee or 0)
#         else:
#             # 按用量计费
#             usage_obj = useage.objects.filter(
#                 room=room,
#                 feetype=ft,
#                 check_in_date__year=year,
#                 check_in_date__month=month
#             ).first()
#             usage = usage_obj.usege if usage_obj and usage_obj.usege is not None else Decimal('0')
#             amount = (usage * Decimal(ft.fee or 0)).quantize(Decimal('0.00'))

#         dynamic_fees[ft.name] = float(amount)
#         total_amount += amount

#     # 4. 更新总费用记录
#     fee_record.dynamic_fees = dynamic_fees
#     fee_record.amount = total_amount.quantize(Decimal('0.00'))
#     fee_record.save()

#     # 5. 删除旧分摊，重新生成新分摊
#     sharing.objects.filter(fee_record=fee_record).delete()

#     if total_amount <= 0:
#         return

#     # 6. 计算当月实际在住人数（入住≤本月，且未退宿或退宿在本月之后）
#     occupants = occupancyrecord.objects.filter(
#         room=room,
#         status='0',
#         check_in_date__lte=month_date
#     ).exclude(
#         check_out_date__lt=month_date
#     )

#     if not occupants.exists():
#         return

#     per_person = (total_amount / occupants.count()).quantize(Decimal('0.00'), rounding='ROUND_HALF_UP')
#     per_person_float = float(per_person)

#     for occ in occupants:
#         detail = {}
#         for name, amt in dynamic_fees.items():
#             detail[name] = per_person_float if amt > 0 else 0.0

#         sharing.objects.create(
#             user=occ,
#             fee_record=fee_record,
#             details=detail,
#             total=per_person_float
#         )

# from decimal import Decimal, ROUND_HALF_UP
# from datetime import datetime
# from django.db.models import Q
# # 请根据你的项目路径调整模型导入（确保和实际模型名一致）

# def recalculate_fee_and_sharing(room, year: int, month: int):
#     """
#     核心计算函数：重新计算指定房间指定年月的总费用 + 个人分摊
#     适配逻辑：
#     1. 固定费用（is_sign=True）：直接取fee，不依赖用量表，新增费用在历史月份为0
#     2. 用量费用（is_sign=False）：用量×单价，无用量/无记录则为0
#     3. 房费折扣：Person.money=True时，房费×折扣率，其他费用不变
#     4. 历史月份新增费用类型自动为0，不影响原有数据
#     """
#     # ========== 1. 基础参数校验 + 生成当月第一天（适配fee_record_one.date的DateField） ==========
#     from .models import (
#         fee_record_one, useage, feetype,
#         occupancyrecord, sharing, Person, discount
#     )
#     try:
#         # 生成fee_record_one需要的date字段（当月第一天）
#         fee_date = datetime(year, month, 1).date()
#     except ValueError:
#         print(f"【{room}】{year}年{month}月为无效日期，跳过费用计算")
#         return

#     # ========== 2. 获取/创建该房间该月的费用记录（无则新建，有则更新） ==========
#     fee_record, created = fee_record_one.objects.get_or_create(
#         room=room,
#         date=fee_date,
#         defaults={
#             'check_people': 'system',  # 系统自动计算标记
#             'status': '0',             # 默认未缴
#             'amount': Decimal('0.00'), # 初始总金额为0
#             'dynamic_fees': {}         # 初始费用明细为空
#         }
#     )

#     # ========== 3. 初始化费用变量 ==========
#     total_amount = Decimal('0.00')    # 总金额（保留两位小数）
#     dynamic_fees = {}                # 费用明细（JSON格式，键=费用名称，值=金额）
#     area = room.dorm.area            # 房间所属区域

#     # ========== 4. 遍历该区域所有启用的计费项目，逐个计算费用 ==========
#     active_feetypes = feetype.objects.filter(area=area, status='启用')
#     for ft in active_feetypes:
#         if ft.is_sign:
#             try:
#                 # 严格处理fee字段：去空格 + 转Decimal，空值/非数字设为0
#                 fee_amount = Decimal(ft.fee.strip()) if (ft.fee and ft.fee.strip()) else Decimal('0.00')
#             except (ValueError, TypeError):
#                 fee_amount = Decimal('0.00')
#             print(f"【{room}】{year}年{month}月 - 固定费用-{ft.name}：{fee_amount}")
        
#         # ---------- 4.2 用量费用（is_sign=False）：依赖useage表，无记录则为0 ----------
#         else:
#             try:
#                 # 查找该房间+该费用类型+该月的用量记录（只取第一条，避免重复）
#                 usage_obj = useage.objects.filter(
#                     room=room,
#                     feetype=ft,
#                     check_in_date__year=year,
#                     check_in_date__month=month
#                 ).first()
                
#                 # 用量记录存在且useage有值才计算，否则金额为0
#                 if usage_obj and usage_obj.usege is not None and usage_obj.usege >= 0:
#                     # 处理单价：空值/非数字设为0
#                     price = Decimal(ft.fee.strip()) if (ft.fee and ft.fee.strip()) else Decimal('0.00')
#                     fee_amount = usage_obj.usege * price
#                 else:
#                     fee_amount = Decimal('0.00')
                
#                 print(f"【{room}】{year}年{month}月 - 用量费用-{ft.name}：单价{price} × 用量{usage_obj.usege if usage_obj else 0} = {fee_amount}")
#             except (ValueError, TypeError):
#                 # 单价/用量转换失败，金额设为0
#                 fee_amount = Decimal('0.00')

#         # ---------- 4.3 费用金额格式化 + 累加 ----------
#         # 保留两位小数（四舍五入，符合财务规范）
#         fee_amount = fee_amount.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
#         # 存入费用明细（转浮点型，适配JSONField）
#         dynamic_fees[ft.name] = float(fee_amount)
#         # 累加总金额
#         total_amount += fee_amount

#     # ========== 5. 更新fee_record_one（费用记录） ==========
#     fee_record.dynamic_fees = dynamic_fees
#     fee_record.amount = total_amount.quantize(Decimal('0.00'))  # 总金额保留两位小数
#     fee_record.save()
#     print(f"【{room}】{year}年{month}月 - 费用记录更新完成：总金额{fee_record.amount}，明细{fee_record.dynamic_fees}")

#     calculate_sharing(fee_record, year, month)


# def calculate_sharing(fee_record, year: int, month: int):
#     """
#     辅助函数：计算个人分摊记录，房费折扣逻辑
#     :param fee_record: 已更新的fee_record_one实例
#     :param year: 年份
#     :param month: 月份
#     """
#     # ---------- 6.1 前置校验：总金额为0/无在住人员，无需分摊 ----------
#     if fee_record.amount <= Decimal('0.00'):
#         print(f"【{fee_record.room}】{year}年{month}月 - 总金额为0，跳过分摊")
#         return
    
#     # 获取该房间当月在住人员（入住时间≤当月，退房时间为空/≥当月）
#     occupants = occupancyrecord.objects.filter(
#         room=fee_record.room,
#         check_in_date__lte=fee_record.date,
#         status="0"
#     )
#     occupant_count = occupants.count()
#     if occupant_count == 0:
#         print(f"【{fee_record.room}】{year}年{month}月 - 无在住人员，跳过分摊")
#         return

#     # ---------- 6.2 获取房费折扣率（默认1.0=无折扣） ----------
#     room_fee_discount = Decimal('1.00')
#     try:
#         # 查找房费类型（名称可根据实际业务调整，比如"租金"）
#         room_fee_type = feetype.objects.get(
#             name="房费", 
#             area=fee_record.room.dorm.area, 
#             status='启用'
#         )
#         # 查找该房费该年月的折扣（discount表date字段格式：YYYY-MM）
#         discount_obj = discount.objects.get(
#             fee_type=room_fee_type,
#             date=f"{year}-{month:02d}"
#         )
#         # 折扣率转换（比如80=8折 → 0.8）
#         room_fee_discount = Decimal(discount_obj.rate) / Decimal('100')
#         # 保障折扣率合法（0-1之间）
#         room_fee_discount = max(Decimal('0.00'), min(room_fee_discount, Decimal('1.00')))
#     except (feetype.DoesNotExist, discount.DoesNotExist, ValueError):
#         # 无房费/无折扣/折扣值无效，用默认1.0
#         pass

#     # ---------- 6.3 先删除旧分摊记录，避免重复 ----------
#     sharing.objects.filter(fee_record=fee_record).delete()

#     # ---------- 6.4 逐个计算在住人员的分摊金额 ----------
#     for occupant in occupants:
#         try:
#             # 获取入住人员的Person信息
#             person = Person.objects.get(id=occupant.user_id)
#             person_share_detail = {}  # 个人分摊明细
#             person_total_share = Decimal('0.00')  # 个人总分摊金额

#             # 按费用类型拆分分摊
#             for fee_name, fee_amt_float in fee_record.dynamic_fees.items():
#                 fee_amt = Decimal(str(fee_amt_float))
#                 # 基础分摊：总金额 / 入住人数（四舍五入保留两位）
#                 per_person_amt = (fee_amt / Decimal(occupant_count)).quantize(
#                     Decimal('0.00'), 
#                     rounding=ROUND_HALF_UP
#                 )

#                 # 房费特殊处理：Person.money=True时应用折扣
#                 if fee_name == "房费" and person.money:
#                     per_person_amt = (per_person_amt * room_fee_discount).quantize(
#                         Decimal('0.00'), 
#                         rounding=ROUND_HALF_UP
#                     )

#                 # 存入个人分摊明细
#                 person_share_detail[fee_name] = float(per_person_amt)
#                 # 累加个人总分摊
#                 person_total_share += per_person_amt

#             # ---------- 6.5 创建分摊记录 ----------
#             sharing.objects.create(
#                 user=occupant,               # 入住人员
#                 fee_record=fee_record,       # 关联的费用记录
#                 details=person_share_detail, # 分摊明细（JSON格式）
#                 total=float(person_total_share)  # 个人总分摊金额
#             )
#             print(f"【{fee_record.room}】{year}年{month}月 - {person} 分摊完成：{person_total_share}")

#         except Person.DoesNotExist:
#             print(f"【{occupant.user_id}】人员信息不存在，跳过分摊")
#             continue
#         except Exception as e:
#             print(f"【{occupant.user_id}】分摊计算失败：{str(e)}")
#             continue