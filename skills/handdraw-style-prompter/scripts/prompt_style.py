#!/usr/bin/env python3
"""Create a deterministic bilingual prompt draft from a validated style number."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from layout_library import detect_language, resolve_layout
from resolve_reference import resolve

SKILL = Path(__file__).resolve().parents[1]

REFERENCE_ISOLATION_ZH = (
    "所附图片仅用于参考画风。只提取参考图的风格特征，例如线条、笔触、媒介、材质、色彩倾向和整体视觉语言；"
    "不要使用、复制或延续参考图中的任何主体、人物、动物、服装、道具、动作、姿态、场景、背景、构图、布局、文字或故事。"
    "最终画面内容完全以用户提供的主题为准。"
)
REFERENCE_ISOLATION_EN = (
    "Use the attached image only as a style reference. Extract only its stylistic qualities, such as linework, brushwork, medium, "
    "material texture, color tendencies, and overall visual language. Do not use, copy, or carry over any subject, person, animal, "
    "clothing, prop, action, pose, setting, background, composition, layout, text, or story from the reference image. "
    "The user's written theme is the sole source for the image content."
)
GRAPHIC_TEXT_SUFFIX = "【如果主题直白包含画面元素那就按主题出图，文案由你来升华，但是不要直接描述画面。 如果主题比较概念化，那么文案和主题尽量保持一致，如果文案较长由你提炼，由你先设计画面隐喻（人类和非人类都行）再出图   。    文字参与构图，图文一体】"


def resolve_single_color(query_str: str, colors_list: list[dict]) -> dict[str, str]:
    q = query_str.strip().lower()
    is_id_pattern = q.startswith("c-")
    q_num = q.replace("c-", "").lstrip("0") if is_id_pattern else ""
    for c in colors_list:
        cid = c["id"].lower()
        c_num = cid.replace("c-", "").lstrip("0")
        if q == cid or (q_num and q_num == c_num) or q in c["name_zh"].lower() or q in c["name_en"].lower():
            return c
    if is_id_pattern:
        raise ValueError(f"Unknown color ID: {query_str}. Use a listed C-01 to C-30 identifier or color name.")
    name = query_str.strip()
    return {
        "id": "",
        "name_zh": name,
        "name_en": name,
        "prompt_zh": f"主题色：{name}。",
        "prompt_en": f"Theme color: {name}."
    }


def resolve_color(query_str: str) -> dict[str, str]:
    colors_file = SKILL / "references" / "colors.json"
    colors_list = json.loads(colors_file.read_text(encoding="utf-8")) if colors_file.exists() else []
    import re
    tokens = [t.strip() for t in re.split(r'[,+、/]+', query_str) if t.strip()]
    if len(tokens) <= 1:
        return resolve_single_color(query_str, colors_list)

    resolved = [resolve_single_color(t, colors_list) for t in tokens]
    c_ids = [r["id"] for r in resolved if r.get("id")]
    id_str = " + ".join(c_ids) if c_ids else ""
    zh_names = [f"{r['name_zh']}（{r['name_en']}）" if r.get('name_en') else r['name_zh'] for r in resolved]
    en_names = [r['name_en'] for r in resolved]

    if len(resolved) == 2:
        prompt_zh = f"主题色：主色为{resolved[0]['name_zh']}（{resolved[0]['name_en']}），点缀色为{resolved[1]['name_zh']}（{resolved[1]['name_en']}）。"
        prompt_en = f"Theme color: {resolved[0]['name_en']} as primary tone, accented with {resolved[1]['name_en']}."
    else:
        prompt_zh = f"主题色：{' 搭配 '.join(zh_names)}。"
        prompt_en = f"Theme color: {' paired with '.join(en_names)}."

    return {
        "id": id_str,
        "name_zh": " 搭配 ".join(r["name_zh"] for r in resolved),
        "name_en": " + ".join(en_names),
        "prompt_zh": prompt_zh,
        "prompt_en": prompt_en,
    }


def recommend_combination(theme: str, user_style: str | None, user_color: str | None) -> tuple[str, str, str]:
    t = theme.lower()
    styles_file = SKILL / "references" / "styles.json"
    styles = json.loads(styles_file.read_text(encoding="utf-8")) if styles_file.exists() else []

    # 1. 儿童 / 绘本 / 亲子启蒙 (优先捕获带有绘本、儿童属性的主题)
    if any(k in t for k in ["儿童", "绘本", "童年", "故事书", "亲子", "幼儿园", "启蒙", "益智", "童话", "玩具", "少年", "小朋友", "children", "kids", "picturebook", "fairytale", "storybook"]):
        if any(k in t for k in ["剪影", "高饱和", "色块", "明快", "认知"]):
            s_id = "046"
            c_id = "C-25 + C-06"
            rationale = "针对儿童启蒙与绘本视觉，推荐大胆几何块面剪影风 (#046 · Chris Haughton) 搭配爱马仕橙 (C-25) 与孔雀蓝 (C-06)，以高饱和纯色块与极简大轮廓激发纯真想象力。"
        elif any(k in t for k in ["自然", "动物", "森林", "植物"]):
            s_id = "266"
            c_id = "C-09 + C-27"
            rationale = "针对儿童自然与温润绘本主题，推荐新自然系森系儿童插画 (#266) 搭配薄荷绿 (C-09) 与那不勒斯黄 (C-27)，以嫩绿柔和的色调与植物环绕构图营造充盈的自然童趣。"
        else:
            s_id = "218"
            c_id = "C-27 + C-09"
            rationale = "针对温馨儿童故事与童趣主题，推荐60-70年代复古儿童绘本风 (#218) 搭配那不勒斯黄 (C-27) 与薄荷绿 (C-09)，质朴的色铅笔/蜡笔颗粒与生动夸张的面部表情带来浓郁童趣。"

    # 2. 汽车 / 新能源 / 工业造车 / 智能出行
    elif any(k in t for k in ["比亚迪", "byd", "特斯拉", "tesla", "汽车", "轿车", "跑车", "suv", "电动车", "新能源", "造车", "电池", "刀片电池", "智驾", "自动驾驶", "无人驾驶", "智能出行", "出行", "引擎", "发动机", "机械制造", "工业制造", "交通", "高铁", "航天", "工业设计", "车载", "车联网", "动力", "纯电", "混动", "增程", "充电桩", "电驱", "底盘", "装配", "车展", "car", "auto", "vehicle", "ev", "mobility"]):
        if any(k in t for k in ["新能源", "电动", "纯电", "电池", "清洁能源", "绿色出行", "比亚迪", "byd", "生态"]):
            s_id = "054"
            c_id = "C-01 + C-09"
            rationale = "针对新能源汽车与智能出行主题，推荐几何化现代主义清线 (#054 · Joost Swarte) 搭配克莱因蓝 (C-01) 与薄荷绿 (C-09)，以欧洲清线学派的严谨秩序与清爽平涂展现工业美学，蓝绿双色呼应“纯净电能 + 生态出行”的核心科技理念。"
        elif any(k in t for k in ["智驾", "自动驾驶", "无人驾驶", "未来", "概念车", "科幻", "航天"]):
            s_id = "052"
            c_id = "C-01 + C-08"
            rationale = "针对未来出行与智能科技主题，推荐干净细线科幻探索风 (#052 · Moebius) 搭配克莱因蓝 (C-01) 与湖蓝 (C-08)，轻科技感线条与浩瀚留白相结合，营造先锋而深邃的未来探索感。"
        elif any(k in t for k in ["制造", "重工", "机械", "引擎", "硬核", "装配", "底盘", "车间"]):
            s_id = "275"
            c_id = "C-03 + C-25"
            rationale = "针对硬核工业制造与机械动力主题，推荐复古丝网印刷与大面积负空间风格 (#275) 搭配普鲁士蓝 (C-03) 与爱马仕橙 (C-25)，以工业级套印质感与高张力冷暖对比传递力量与精密制造。"
        else:
            s_id = "054"
            c_id = "C-01 + C-08"
            rationale = "针对汽车与出行工业主题，推荐几何化现代主义清线 (#054 · Joost Swarte) 搭配克莱因蓝 (C-01) 与湖蓝 (C-08)，以清晰的现代几何线条与纯净冷调凸显工业设计质感。"

    # 3. 潮流 / 街头 / 摇滚 / 青年文化 / 幽默荒诞
    elif any(k in t for k in ["街头", "涂鸦", "朋克", "摇滚", "音乐节", "乐队", "电音", "livehouse", "滑板", "嘻哈", "潮流", "亚文化", "青年", "派对", "吐槽", "梗", "荒诞", "搞笑", "幽默", "pop", "street", "graffiti", "punk", "youth", "rock", "party", "funny", "meme"]):
        if any(k in t for k in ["街头", "涂鸦", "滑板", "嘻哈", "原始", "爆裂"]):
            s_id = "072"
            c_id = "C-01 + C-25"
            rationale = "针对街头潮流与极限表达主题，推荐表现主义原始符号涂鸦风 (#072 · Basquiat) 搭配克莱因蓝 (C-01) 与爱马仕橙 (C-25)，以皇冠符号、粗粝文字与高饱和撞色释放纯粹年轻荷尔蒙。"
        elif any(k in t for k in ["摇滚", "音乐节", "乐队", "派对", "潮流", "波普", "杂志"]):
            s_id = "056"
            c_id = "C-20 + C-28"
            rationale = "针对摇滚音乐节与潮酷青年文化，推荐波普杂志涂鸦风 (#056 · Hattie Stewart) 搭配洋红 (C-20) 与芥末黄 (C-28)，俏皮恶搞的卡通大眼嘴唇与高能量波普撞色冲击力十足。"
        else:
            s_id = "011"
            c_id = "C-01 + C-25"
            rationale = "针对荒诞幽默与网络流行梗，推荐故意画坏幼稚黑线风 (#011 · David Shrigley) 搭配克莱因蓝 (C-01) 与爱马仕橙 (C-25)，以极简粗粝线条与反精致态度直击人心。"

    # 4. 硬核科技 / AI / 编程 / 数据 / 数字化
    elif any(k in t for k in ["科技", "智能", "人工智能", "ai", "大模型", "llm", "算法", "代码", "程序员", "编程", "软件", "数据", "架构", "云计算", "量子", "赛博", "芯片", "半导体", "互联网", "数字化", "虚拟现实", "vr", "ar", "元宇宙", "区块链", "信息安全", "黑客", "tech", "technology", "artificial intelligence", "algorithm", "code", "coding", "software", "cyber", "quantum", "data"]):
        if any(k in t for k in ["代码", "程序员", "编程", "bug", "加班", "自嘲", "debug", "码农"]):
            s_id = "011"
            c_id = "C-01"
            rationale = "针对程序员代码与自嘲幽默主题，推荐故意画坏幼稚黑线风 (#011 · David Shrigley) 搭配克莱因蓝 (C-01)，以极简粗糙线条与荒诞反差感精准击中技术人痛点。"
        elif any(k in t for k in ["学术", "科技梗", "理智", "数学", "算法", "研究", "逻辑"]):
            s_id = "010"
            c_id = "C-03 + C-27"
            rationale = "针对理性逻辑与科技深度思考主题，推荐极小几何人物与冷面幽默风 (#010 · Tom Gauld) 搭配普鲁士蓝 (C-03) 与那不勒斯黄 (C-27)，画面克制而充满智性趣味。"
        elif any(k in t for k in ["赛博", "未来都市", "科幻", "机甲", "虚拟"]):
            s_id = "239"
            c_id = "C-05 + C-20"
            rationale = "针对赛博与未来科幻主题，推荐80年代末赛博朋克深邃科技动画风 (#239) 搭配群青 (C-05) 与洋红 (C-20)，以经典霓虹暗调与手绘赛璐珞质感营造沉浸式科幻世界观。"
        else:
            s_id = "154"
            c_id = "C-01 + C-06"
            rationale = "针对现代数字科技与智能创新主题，推荐当代商业都市科技风 (#154 · 插画师卷耳) 搭配克莱因蓝 (C-01) 与孔雀蓝 (C-06)，以清晰利落的现代平面语言呈现科技专业感。"

    # 5. 国风 / 传统 / 非遗 / 东方神话 / 传统节气
    elif any(k in t for k in ["国潮", "传统", "民俗", "东方", "非遗", "神话", "戏曲", "志怪", "古风", "故宫", "水墨", "茶道", "汉服", "节气", "敦煌", "历史", "武侠", "诗词", "陶瓷", "剪纸", "古代", "中华", "中式", "仙侠", "三国", "山海经", "秋分", "春分", "冬至", "夏至", "立秋", "立春", "立夏", "立冬", "处暑", "白露", "寒露", "霜降", "小雪", "大雪", "小寒", "大寒", "雨水", "惊蛰", "清明", "谷雨", "小满", "芒种", "小暑", "大暑", "中秋", "重阳", "端午", "除夕", "元宵", "春节", "traditional", "chinese", "heritage", "folk", "myth", "ink"]):
        if any(k in t for k in ["节气", "秋分", "春分", "冬至", "夏至", "立秋", "处暑", "白露", "寒露", "霜降", "中秋", "重阳", "文人", "闲适", "水墨漫画"]):
            s_id = "268"
            c_id = "C-26 + C-03"
            rationale = "针对传统节气与金秋时令主题，推荐当代人文水墨漫画 (#268) 搭配柿子橙 (C-26) 与普鲁士蓝 (C-03)，以松弛写意的毛笔墨线与大面积温润留白营造闲适意境，暖橙与墨蓝冷暖均衡，精准呼应秋分“阴阳相半、昼夜均平、秋水长天”的节气哲学。"
        elif any(k in t for k in ["民俗", "木偶", "志怪", "民间", "传奇", "皮影", "山海经", "老式"]):
            s_id = "277"
            c_id = "C-15 + C-29"
            rationale = "针对传统民俗与传奇志怪主题，推荐中国老式手工木偶定格动画风 (#277) 搭配朱砂红 (C-15) 与赭石 (C-29)，以质朴的人偶肌理与淡雅妆容呈现深厚神秘的东方民间质感。"
        elif any(k in t for k in ["水墨", "写意", "禅意", "茶", "书法", "山水", "极简"]):
            s_id = "255"
            c_id = "C-16 + C-03"
            rationale = "针对东方禅意与写意水墨主题，推荐现代极简水墨与红黑水粉撞色插画 (#255) 搭配中国红 (C-16) 与普鲁士蓝 (C-03)，宣纸焦墨飞白与现代几何构图碰撞出先锋东方美感。"
        else:
            s_id = "132"
            c_id = "C-15 + C-03"
            rationale = "针对国潮与传统文化盛典主题，推荐当代装饰国潮插画 (#132 · 奇舫社) 搭配朱砂红 (C-15) 与普鲁士蓝 (C-03)，以华丽的人物轮廓、建筑线条与经典青红套印传递盛世气象。"

    # 6. 商业 / 财经 / 职场 / 咨询 / 战略
    elif any(k in t for k in ["商业", "金融", "投资", "银行", "股市", "股票", "基金", "理财", "经济", "职场", "战略", "管理", "咨询", "创业", "汇报", "增长", "市场", "营销", "上市", "财报", "效率", "商务", "办公", "会议", "business", "finance", "economy", "investment", "workplace", "strategy", "management"]):
        if any(k in t for k in ["战略", "概念", "思考", "咨询", "隐喻", "商业洞察"]):
            s_id = "012"
            c_id = "C-03 + C-25"
            rationale = "针对商业战略与深度洞察主题，推荐殿堂级极简视觉双关社论插画 (#012 · Christoph Niemann) 搭配普鲁士蓝 (C-03) 与爱马仕橙 (C-25)，用绝妙的物体再解释与概念隐喻呈现智性商业美学。"
        elif any(k in t for k in ["体制", "职场关系", "人与空间", "职场观察", "现代人"]):
            s_id = "002"
            c_id = "C-01 + C-30"
            rationale = "针对职场生态与现代人际关系主题，推荐概念连续线社论风 (#002 · Saul Steinberg) 搭配克莱因蓝 (C-01) 与象牙白 (C-30)，以智性线描与留白构建耐人寻味的现代社会寓言。"
        else:
            s_id = "082"
            c_id = "C-03 + C-25"
            rationale = "针对商业与财经综合主题，推荐复古丝网印刷几何大块面 (#082 · Blexbolex) 搭配普鲁士蓝 (C-03) 与爱马仕橙 (C-25)，以厚重色层与版画纸本颗粒打造高辨识度商业海报。"

    # 7. 自然 / 生态 / 田园菜园 / 户外探险
    elif any(k in t for k in ["自然", "森林", "环保", "生态", "植物", "露营", "徒步", "户外", "农业", "绿色", "园艺", "花卉", "春天", "山野", "海洋", "大地", "农场", "动物", "观鸟", "荒野", "探险", "登山", "菜园", "蔬菜", "种菜", "田园", "农家", "果园", "庄稼", "农作物", "瓜果", "nature", "forest", "green", "outdoor", "camping", "hiking", "plant", "ecology", "spring", "garden"]):
        if any(k in t for k in ["菜园", "蔬菜", "种菜", "田园", "农家", "农园", "瓜果", "果实"]):
            s_id = "266"
            c_id = "C-10 + C-26"
            rationale = "针对菜园与田园生机主题，推荐新自然系森系儿童插画 (#266) 搭配鼠尾草绿 (C-10) 与柿子橙 (C-26)，以圆润童趣的几何植物线条与大块温润纯色呈现自然生机，舒缓绿意与丰收暖橙相映成趣。"
        elif any(k in t for k in ["动物", "飞鸟", "几何自然", "科普", "生物"]):
            s_id = "062"
            c_id = "C-10 + C-14"
            rationale = "针对自然生物与生态科普主题，推荐大师级极端几何化自然插画 (#062 · Charley Harper) 搭配鼠尾草绿 (C-10) 与森林绿 (C-14)，以极简平面图形还原动植物神韵，纯粹优雅。"
        elif any(k in t for k in ["北欧", "原野", "野外", "林间"]):
            s_id = "037"
            c_id = "C-10 + C-08"
            rationale = "针对北欧自然原野与林间探险主题，推荐北欧细线奇趣手绘风 (#037 · Tove Jansson) 搭配鼠尾草绿 (C-10) 与湖蓝 (C-08)，以诗意细腻的钢笔墨线再现清澈纯粹的荒野呼吸。"
        else:
            s_id = "229"
            c_id = "C-10 + C-14"
            rationale = "针对自然生态与户外主题，推荐现代极简有机几何编辑插画 (#229) 搭配鼠尾草绿 (C-10) 与森林绿 (C-14)，以轻细墨线、抽象有机形状与纸本噪点带来舒缓的生命质感。"

    # 8. 生活 / 治愈 / 咖啡 / 美食 / 宠物
    elif any(k in t for k in ["咖啡", "奶茶", "美食", "面包", "烘焙", "甜点", "治愈", "温暖", "宠物", "猫", "狗", "慢生活", "下午茶", "早餐", "疗愈", "慵懒", "日常", "家居", "烹饪", "餐厅", "居酒屋", "生活", "做饭", "小确幸", "coffee", "tea", "food", "cafe", "warm", "cozy", "pet", "cat", "dog", "bakery"]):
        if any(k in t for k in ["猫", "狗", "宠物", "日常吐槽", "小动物"]):
            s_id = "001"
            c_id = "C-26 + C-29"
            rationale = "针对萌宠与生活日常吐槽主题，推荐萌趣冷幽默手绘风 (#001 · Gemma Correll) 搭配柿子橙 (C-26) 与赭石 (C-29)，以松散黑线与搞怪小表情展现轻松惬意的生活态度。"
        elif any(k in t for k in ["毛绒", "手作", "立体", "软萌", "冬日", "抱抱"]):
            s_id = "232"
            c_id = "C-21 + C-27"
            rationale = "针对极致软萌与手作治愈主题，推荐毛绒玩具与雪尼尔毛线3D人偶风 (#232) 搭配珊瑚粉 (C-21) 与那不勒斯黄 (C-27)，触感逼真的蓬松纤维与明快马卡龙色带来爆棚的幸福感。"
        else:
            s_id = "018"
            c_id = "C-26 + C-28"
            rationale = "针对咖啡与都市慢生活日常，推荐微冷幽默极简对白漫画 (#018) 搭配柿子橙 (C-26) 与芥末黄 (C-28)，以极简线条与温暖大地色系传递松弛治愈的生活温度。"

    # 9. 浪漫 / 情感 / 梦幻 / 诗意 / 心理
    elif any(k in t for k in ["浪漫", "爱情", "恋爱", "梦境", "诗意", "唯美", "星空", "心理", "疗愈", "情绪", "独处", "心灵", "少女", "柔情", "约会", "七夕", "情人节", "玫瑰", "告白", "晚安", "思念", "古典乐", "民谣", "romance", "love", "dream", "poetry", "emotional", "starry", "romantic"]):
        if any(k in t for k in ["艺术", "抽象", "极简", "身体", "线条", "爱"]):
            s_id = "070"
            c_id = "C-22 + C-07"
            rationale = "针对纯粹爱意与现代艺术表达，推荐大师级极简抽象连续线 (#070 · Picasso) 搭配灰粉 (C-22) 与蒂芙尼蓝 (C-07)，一笔到底的灵动线条勾勒细腻的情感流动与张力。"
        elif any(k in t for k in ["梦境", "符号", "童真", "童话", "星空", "夜"]):
            s_id = "078"
            c_id = "C-23 + C-05"
            rationale = "针对梦境、星空与心灵诗意主题，推荐诗意几何符号大师风 (#078 · Paul Klee) 搭配薰衣草紫 (C-23) 与深邃群青 (C-05)，童真符号与音乐律动般的色块交织出迷人的梦幻之境。"
        else:
            s_id = "229"
            c_id = "C-23 + C-21"
            rationale = "针对温润浪漫与诗意情感主题，推荐现代极简有机几何编辑插画 (#229) 搭配薰衣草紫 (C-23) 与珊瑚粉 (C-21)，柔和莫兰迪粉彩色调与微颗粒纸本噪点尽显诗意与优雅。"

    # 10. 设计 / 建筑 / 包豪斯 / 空间美学
    elif any(k in t for k in ["设计", "建筑", "空间", "展讯", "包豪斯", "现代主义", "构成", "几何", "极简", "室内", "艺术展", "工业风", "结构", "城市规划", "美学", "typography", "design", "architecture", "bauhaus", "modernist", "minimalism"]):
        if any(k in t for k in ["剪纸", "符号", "电影海报", "构成", "粗粝"]):
            s_id = "063"
            c_id = "C-18 + C-03"
            rationale = "针对现代主义构成与强符号海报，推荐粗粝剪纸现代主义图形风 (#063 · Saul Bass) 搭配庞贝红 (C-18) 与普鲁士蓝 (C-03)，以电影大师级的极简象征与硬朗几何剪影掌控视觉中心。"
        elif any(k in t for k in ["负空间", "概念图形", "双关"]):
            s_id = "060"
            c_id = "C-01 + C-28"
            rationale = "针对极简平面图形与智性设计，推荐大师级负空间双关概念插画 (#060 · Noma Bar) 搭配克莱因蓝 (C-01) 与芥末黄 (C-28)，正负形无缝咬合，视觉洗练耐人寻味。"
        else:
            s_id = "054"
            c_id = "C-03 + C-27"
            rationale = "针对建筑空间与包豪斯设计主题，推荐几何化现代主义清线 (#054 · Joost Swarte) 搭配普鲁士蓝 (C-03) 与那不勒斯黄 (C-27)，以欧洲清线学派的严谨空间结构与建筑感线条展现理性之美。"

    # 11. 全库 277 风格关键词匹配与通用海报兜底
    else:
        ngrams = [t[i:i+n] for n in [2, 3, 4] for i in range(len(t)-n+1)]
        scored = []
        for s in styles:
            score = 0
            haystack = (s["generation_name"] + " " + s["reference"] + " " + s["traits"] + " " + s.get("group", "")).lower()
            for ng in ngrams:
                if ng in haystack:
                    score += 2
                    if ng in s["generation_name"].lower() or ng in s["reference"].lower():
                        score += 3
            if score > 0:
                scored.append((score, s["number"], s["generation_name"]))
        
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            best_num = scored[0][1]
            best_name = scored[0][2]
            s_id = best_num
            c_id = "C-01 + C-25"
            rationale = f"语义深度匹配到专属画风 #{best_num}（{best_name}），搭配经典瞩目的克莱因蓝 (C-01) 与爱马仕橙 (C-25)，高度契合画面特定语境。"
        else:
            candidates = [
                ("012", "C-01 + C-25", "针对开放与概念化主题，推荐殿堂级极简视觉双关社论 (#012 · Christoph Niemann) 搭配克莱因蓝 (C-01) 与爱马仕橙 (C-25)，用绝妙的画面隐喻与双关构图赋予海报高级的智性魅力。"),
                ("002", "C-03 + C-27", "针对深刻的人文与思辨主题，推荐概念连续线社论风 (#002 · Saul Steinberg) 搭配普鲁士蓝 (C-03) 与那不勒斯黄 (C-27)，以极简哲学线描与高比例留白传递深远意境。"),
                ("275", "C-03 + C-21", "针对艺术质感与叙事表达，推荐复古丝网印刷与大面积负空间风格 (#275) 搭配普鲁士蓝 (C-03) 与珊瑚粉 (C-21)，以细腻的版画纸纹与质朴双色套印打造经典纸媒海报质感。"),
                ("054", "C-01 + C-08", "针对结构与现代主义表达，推荐几何化现代主义清线 (#054 · Joost Swarte) 搭配克莱因蓝 (C-01) 与湖蓝 (C-08)，以欧洲清线学派的严谨空间秩序展现洗练视觉语言。"),
            ]
            idx = sum(ord(c) for c in t) % len(candidates)
            s_id, c_id, rationale = candidates[idx]

    final_style = user_style if user_style else s_id
    final_color = user_color if user_color else c_id

    if user_style and user_color:
        rationale = f"已采用您指定的手绘风格 #{user_style} 与主题色 {user_color}。"
    elif user_style:
        rationale = f"已采用您指定的手绘风格 #{user_style}，为您智能匹配推荐主题色 {c_id}。{rationale}"
    elif user_color:
        rationale = f"已采用您指定的主题色 {user_color}，为您智能匹配推荐手绘风格 #{s_id}。{rationale}"

    return final_style, final_color, rationale


def main() -> None:
    styles = json.loads((SKILL / "references" / "styles.json").read_text(encoding="utf-8"))
    max_num = len(styles)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", help=f"Optional style number from 001 to {max_num:03}")
    parser.add_argument("--layout", help="Optional layout ID")
    parser.add_argument("--color", help="Optional color ID  or color name.")
    parser.add_argument("--auto", "--recommend", action="store_true", help="Automatically recommend an optimal style and theme color combination based on theme semantics.")
    parser.add_argument("--theme", required=True)
    parser.add_argument("--ratio")
    parser.add_argument("--subject")
    parser.add_argument("--text")
    parser.add_argument("--model", default="gpt-image-2", help="Model capability profile; defaults to gpt-image-2.")
    parser.add_argument("--mode", choices=("pure-image", "graphic-text"), default="pure-image")
    parser.add_argument("--language", choices=("auto", "zh", "en"), default="auto")
    args = parser.parse_args()

    recommendation_banner = None
    if args.auto:
        rec_s, rec_c, rationale = recommend_combination(args.theme, args.style, args.color)
        if not args.style:
            args.style = rec_s
        if not args.color:
            args.color = rec_c
        recommendation_banner = rationale
    elif not args.style and not args.layout and not args.color:
        raise SystemExit("Provide --style, --layout, or both (or --color, or use --auto).")
    if args.color:
        try:
            color_info = resolve_color(args.color)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    else:
        color_info = None
    selected = None
    number = None
    if args.style:
        try:
            val = int(args.style)
            if not 1 <= val <= max_num:
                raise ValueError()
            number = f"{val:03}"
        except (ValueError, TypeError) as exc:
            raise SystemExit(f"Style must be a number from 001 to {max_num:03}.") from exc
        selected = next((item for item in styles if item["number"] == number), None)
        if selected is None:
            raise SystemExit(f"Style must be a number from 001 to {max_num:03}.")
    extra_zh = "；".join(filter(None, [f"画幅：{args.ratio}" if args.ratio else "", f"主体限制：{args.subject}" if args.subject else "", f"文字要求：{args.text}" if args.text else ""]))
    extra_en = "; ".join(filter(None, [f"aspect ratio: {args.ratio}" if args.ratio else "", f"subject constraints: {args.subject}" if args.subject else "", f"text requirement: {args.text}" if args.text else ""]))
    if args.layout:
        try:
            layout = resolve_layout(args.layout)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        language = detect_language(args.theme) if args.language == "auto" else args.language
        layout_prompt = layout["prompts"][language]
        if language == "zh":
            parts = [
                f"图型：{layout['id']} · {layout['name']}。",
                f"主题：{args.theme}。",
                f"排版要求：{layout_prompt}",
            ]
        else:
            parts = [
                f"Layout: {layout['id']} · {layout['name']}.",
                f"Theme: {args.theme}.",
                f"Layout instructions: {layout_prompt}",
            ]
        if color_info:
            color_prompt = color_info["prompt_zh"] if language == "zh" else color_info["prompt_en"]
            parts.insert(1, color_prompt)
        if selected and number:
            decision = resolve(args.model, number)
            traits = decision["prompt_traits"]
            if language == "zh":
                parts.append(f"风格名称：#{number} · {selected['generation_name']}。参考作者/风格名称：{selected['reference']}。")
                if traits:
                    parts.append(f"核心风格特征：{traits}。")
                if decision["use_reference_image"]:
                    parts.append(f"参考图：请上传本地参考图 {decision['reference_path']}。{REFERENCE_ISOLATION_ZH}")
            else:
                parts.append(f"Style name: #{number} · {selected['generation_name']}. Reference author/style name: {selected['reference']}.")
                if traits:
                    parts.append(f"Core style traits: {traits}.")
                if decision["use_reference_image"]:
                    parts.append(f"Reference image: upload local reference image {decision['reference_path']}. {REFERENCE_ISOLATION_EN}")
        if language == "zh":
            if extra_zh:
                parts.append(f"；{extra_zh}")
            parts.append(GRAPHIC_TEXT_SUFFIX)
        else:
            if extra_en:
                parts.append(f"{extra_en}.")
            parts.append(GRAPHIC_TEXT_SUFFIX)
        if recommendation_banner:
            print(f"💡 推荐理由：{recommendation_banner}")
        print(f"Selected layout: {layout['id']} · {layout['name']}")
        if color_info:
            c_label = f"{color_info['id']} · " if color_info.get("id") else ""
            print(f"Selected color: {c_label}{color_info['name_zh']} ({color_info['name_en']})")
        if selected and number:
            print(f"Selected style: #{number} · {selected['generation_name']}")
        print("\nPrompt:")
        print("".join(parts) if language == "zh" else " ".join(parts))
        print("\n已自动使用图文模式。" if language == "zh" else "\nThe selected layout automatically uses graphic-text mode.")
        return

    graphic_text_suffix = GRAPHIC_TEXT_SUFFIX if args.mode == "graphic-text" else ""
    zh_extra = f"；{extra_zh}" if extra_zh else ""
    en_extra = f" {extra_en}." if extra_en else ""

    if not selected and color_info:
        c_label = f"{color_info['id']} · " if color_info.get("id") else ""
        print(f"Selected color: {c_label}{color_info['name_zh']} ({color_info['name_en']})")
        print("\n中文提示词：")
        print(f"{color_info['prompt_zh']}主题：{args.theme}。{zh_extra}{graphic_text_suffix}")
        print("\nEnglish prompt:")
        print(f"{color_info['prompt_en']} Theme: {args.theme}.{en_extra}{graphic_text_suffix}")
        print("\nPaste either prompt into an image AI; this skill does not generate an image.")
        if args.mode == "pure-image":
            print("当前处于纯图模式，可切换为图文模式。")
        return

    assert selected is not None and number is not None
    if recommendation_banner:
        print(f"💡 推荐理由：{recommendation_banner}")
    print(f"Selected style: #{number} · {selected['generation_name']}")
    if color_info:
        c_label = f"{color_info['id']} · " if color_info.get("id") else ""
        print(f"Selected color: {c_label}{color_info['name_zh']} ({color_info['name_en']})")
    print("\n中文提示词：")
    reference_zh = f"参考作者/风格名称：{selected['reference']}。"
    reference_en = f" Reference author/style name: {selected['reference']}."
    decision = resolve(args.model, number)
    traits = decision["prompt_traits"]
    traits_zh = f"核心风格特征：{traits}。" if traits else ""
    traits_en = f" Core style traits: {traits}." if traits else ""
    reference_image_zh = ""
    reference_image_en = ""
    if decision["use_reference_image"] and args.mode == "pure-image":
        reference_image_zh = f"参考图：请上传本地参考图 {decision['reference_path']}。{REFERENCE_ISOLATION_ZH}"
        reference_image_en = f" Reference image: upload local reference image {decision['reference_path']}. {REFERENCE_ISOLATION_EN}"
    color_zh = f"{color_info['prompt_zh']}" if color_info else ""
    color_en = f" {color_info['prompt_en']}" if color_info else ""
    print(f"风格名称：#{number} · {selected['generation_name']}。{color_zh}主题：{args.theme}。{reference_zh}{traits_zh}{reference_image_zh}{zh_extra}{graphic_text_suffix}")
    print("\nEnglish prompt:")
    print(f"Style name: #{number} · {selected['generation_name']}.{color_en} Theme: {args.theme}.{reference_en}{traits_en}{reference_image_en}{en_extra}{graphic_text_suffix}")
    print("\nPaste either prompt into an image AI; this skill does not generate an image.")
    if args.mode == "pure-image":
        print("当前处于纯图模式，可切换为图文模式。")


if __name__ == "__main__":
    main()
