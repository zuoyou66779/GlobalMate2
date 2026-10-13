import json
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
DB = BASE / 'globalmate_data.json'
st.set_page_config(page_title='GlobalMate 2.0｜出海运营助手', page_icon='🌍', layout='wide')
st.markdown('''<style>
.stApp{background:linear-gradient(135deg,#f4f7fc,#edf2ff)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#101d37,#183665)}
[data-testid="stSidebar"] *{color:#f4f7ff}
.hero{padding:30px;border-radius:20px;color:white;background:linear-gradient(115deg,#14213d,#244c91,#477de0);margin-bottom:22px}
.hero h1{color:white}.hero p{color:#e5edff}
</style>''', unsafe_allow_html=True)

def load_db():
    try:
        d=json.loads(DB.read_text(encoding='utf-8'))
        if isinstance(d,dict):
            d.setdefault('product',{}); d.setdefault('history',[]); d.setdefault('plans',[]); return d
    except Exception: pass
    return {'product':{},'history':[],'plans':[]}
if 'db' not in st.session_state: st.session_state.db=load_db()
if 'product' not in st.session_state: st.session_state.product=st.session_state.db['product']
if 'history' not in st.session_state: st.session_state.history=st.session_state.db['history']
if 'plans' not in st.session_state: st.session_state.plans=st.session_state.db['plans']
def persist():
    st.session_state.db.update(product=st.session_state.product,history=st.session_state.history,plans=st.session_state.plans)
    DB.write_text(json.dumps(st.session_state.db,ensure_ascii=False,indent=2),encoding='utf-8')
def log(kind,summary):
    p=st.session_state.product
    st.session_state.history.insert(0,{'时间':datetime.now().strftime('%Y-%m-%d %H:%M'),'类型':kind,'产品':p.get('name',''),'市场':p.get('market',''),'摘要':summary})
    st.session_state.history=st.session_state.history[:200]; persist()
def features():
    s=st.session_state.product.get('features','').replace('，',',').replace('、',',').replace('\n',',').replace('；',',')
    return [x.strip() for x in s.split(',') if x.strip()]
def ready(): return bool(st.session_state.product.get('name','').strip() and st.session_state.product.get('features','').strip())
def analysis(p):
    fs=features() or ['产品特点待补充']; market=p.get('market','其他')
    market_tips={'日本':'日语表达要自然；突出尺寸、用法、配送、退换货和售后信息。','美国':'验证目标人群、使用场景、竞品差异、配送与退货预期。','英国':'检查英式英语表达，明确价格、配送和退换货条款。','德国':'说明规格、耐用性、使用限制、合规与售后。','法国':'注意法语本地化，清晰说明产品体验和售后。','加拿大':'确认当地语言需求、物流时效、税费和适用法规。'}
    ch={'跨境电商平台':'优化标题、关键词、主图、规格、FAQ 和评价反馈。','独立站':'完善品牌介绍、信任信息、产品对比、FAQ 和购买路径。','社交媒体':'展示真实使用场景，测试不同内容角度，不要伪造评价。','电子邮件':'仅向合规授权的收件人发送，并提供退订方式。'}
    return {'selling':[f'围绕“{fs[0]}”说明它解决了用户什么问题，并用真实场景展示。',f'把“{fs[1]}”转化成可观察的用户价值。' if len(fs)>1 else '补充具体使用场景，并说明与常见替代方案的区别。','补充可核实的规格、材料、兼容性、保修和使用限制。'],'audience':[f'客户假设：{market}市场中重视“{fs[0]}”的消费者。','次要客户假设：经常遇到该产品所解决问题的人群。','通过竞品差评、关键词和小规模用户反馈验证，不要把假设当成事实。'],'market':market_tips.get(market,'确认目标国家、用户需求、竞品、物流成本和当地合规要求。'),'channels':[ch.get(c,c) for c in p.get('channels',[])] or ['尚未选择销售渠道。'],'checks':['调查目标市场关键词和用户常见问题','比较至少 5 个竞品的售价、评价与差异','核实产品标准、标签、广告规范和知识产权','估算采购、佣金、物流、税费、广告及退货成本']}
def make_copy(p,lang,tone,kind):
    fs=features() or ['产品特点']; name=p['name']; f='、'.join(fs[:3])
    if lang=='日语': title=f'{name}｜毎日の使いやすさを考えたアイテム'; body=f'{name}は、{f}を特徴とする商品です。仕様や使い方をご確認ください。'; cta='商品詳細をチェックしてください。'
    elif lang=='英语': title=f'{name} | Designed for everyday use'; body=f'Meet {name}, featuring {f}. Review the product details to see whether it fits your needs.'; cta='Explore the product details.'
    elif lang=='德语': title=f'{name} – praktisch für den Alltag'; body=f'{name} bietet folgende Merkmale: {f}. Prüfen Sie die Produktdetails.'; cta='Entdecken Sie die Produktdetails.'
    elif lang=='法语': title=f'{name} : pensé pour le quotidien'; body=f'Découvrez {name}, avec les caractéristiques suivantes : {f}. Consultez les détails du produit.'; cta='Consultez les détails du produit.'
    else: title=f'{name}｜为日常使用而设计'; body=f'{name}的特点包括：{f}。请结合实际场景查看规格，确认是否适合需求。'; cta='了解产品详情。'
    if tone=='专业可信': body+=' 文案只描述已提供的信息，具体性能请以实际规格和测试结果为准。'
    elif tone=='轻松亲切': body+=' 不妨先看看详细信息，再判断它是否适合你。'
    else: body=f'{name}：{f}。查看规格和使用说明，确认是否符合需求。'
    if kind=='商品详情页': return f'{title}\n\n产品特点\n'+'\n'.join('• '+x for x in fs[:5])+f'\n\n{body}\n\n{cta}'
    if kind=='推广邮件': return f'主题：了解 {name}\n\n您好！\n\n{body}\n\n{cta}'
    return f'{title}\n\n{body}\n\n{cta}'

with st.sidebar:
    st.markdown('## 🌍 GlobalMate 2.0'); st.caption('出海运营助手 · 零成本原型')
    page=st.radio('功能导航',['工作台首页','产品信息','产品卖点分析','智能出海分析报告','多语言营销文案','海外市场研究','出海运营计划','项目记录'],label_visibility='collapsed')
    st.divider(); st.caption('不调用付费 API；数据保存在项目文件夹。')
p=st.session_state.product
if page=='工作台首页':
    st.markdown('<div class="hero"><h1>🌍 GlobalMate 2.0</h1><p>产品定位、多语言内容、市场研究与运营计划，一站式整理出海工作流。</p></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3); a.metric('产品名称',p.get('name') or '尚未填写'); b.metric('目标市场',p.get('market') or '尚未选择'); c.metric('项目记录',len(st.session_state.history))
    st.subheader('开始使用'); st.write('① 产品信息 → ② 产品卖点分析 → ③ 多语言营销文案 → ④ 海外市场研究 → ⑤ 出海运营计划')
    st.info('本版本使用规则和模板，不联网抓取实时市场数据，也不调用付费 AI API。')
elif page=='产品信息':
    st.title('📦 产品信息'); markets=['日本','美国','英国','德国','法国','加拿大','其他']; langs=['日语','英语','中文','德语','法语']; channels_all=['跨境电商平台','独立站','社交媒体','电子邮件']
    with st.form('product_form'):
        a,b=st.columns(2)
        with a:
            name=st.text_input('产品名称 *',p.get('name',''),placeholder='例如：便携式咖啡机'); feat=st.text_area('产品特点 *（逗号或换行分隔）',p.get('features',''),height=130,placeholder='体积小，方便携带，可重复充电'); price=st.number_input('参考售价（可选）',min_value=0.0,value=float(p.get('price',0) or 0),step=1.0)
        with b:
            market=st.selectbox('目标市场',markets,index=markets.index(p.get('market','日本')) if p.get('market','日本') in markets else 0); lang=st.selectbox('默认营销语言',langs,index=langs.index(p.get('language','日语')) if p.get('language','日语') in langs else 0); channels=st.multiselect('销售渠道',channels_all,default=[x for x in p.get('channels',['跨境电商平台']) if x in channels_all]); audience=st.text_input('目标客户（可选）',p.get('audience',''))
        save=st.form_submit_button('💾 保存产品信息',type='primary',use_container_width=True)
    if save:
        if not name.strip() or not feat.strip(): st.error('请至少填写产品名称和产品特点。')
        else:
            st.session_state.product={'name':name.strip(),'features':feat.strip(),'price':price,'market':market,'language':lang,'channels':channels,'audience':audience.strip()}; persist(); log('产品信息',f'更新产品资料：{name.strip()}'); st.success('保存成功！其他模块可以读取这份资料。')
    if ready():
        with st.expander('查看已保存资料'): st.json(st.session_state.product)
elif page=='产品卖点分析':
    st.title('🧭 产品卖点分析')
    if not ready(): st.warning('请先进入「产品信息」，填写并保存产品名称和特点。'); st.stop()
    r=analysis(p); st.info(f'分析对象：{p["name"]}｜目标市场：{p.get("market","其他")}')
    st.subheader('核心卖点方向')
    for i,x in enumerate(r['selling'],1): st.markdown(f'**{i}.** {x}')
    st.subheader('目标客户假设')
    if p.get('audience'): st.markdown('- 你填写的目标客户：'+p['audience'])
    for x in r['audience']: st.markdown('- '+x)
    st.subheader('本地化提示'); st.info(r['market']); st.subheader('渠道建议')
    for x in r['channels']: st.markdown('- '+x)
    st.subheader('需要验证的事项')
    for x in r['checks']: st.checkbox(x,key='check_'+str(abs(hash(x))))
    if st.button('保存本次分析到项目记录',type='primary'): log('产品卖点分析','；'.join(r['selling'])); st.success('已保存。')
    st.caption('这是初步假设，不是实时市场结论；正式发布前请核实。')
elif page=='智能出海分析报告':
    st.title('🌍 智能出海分析报告')
    st.caption('基于你填写的产品资料生成初步分析，不代表实时市场数据或销量预测。')

    if not ready():
        st.warning('请先到「产品信息」保存产品名称和特点。')
        st.stop()

    p = load_db().get('product', {})
    st.subheader('一、产品基本情况')

    col1, col2 = st.columns(2)
    with col1:
        st.write('**产品名称：**', p.get('name', '未填写'))
        st.write('**目标市场：**', p.get('market', '未填写'))
    with col2:
        st.write('**目标客户：**', p.get('audience', '未填写'))
        st.write('**销售渠道：**', '、'.join(p.get('channels', [])) or '未填写')
    st.divider()
    st.subheader('二、出海准备度评分')

    score = 0
    checks = [
        ('产品名称', bool(p.get('name'))),
        ('产品特点', bool(p.get('features') or p.get('selling_points'))),
        ('目标市场', bool(p.get('market'))),
        ('目标客户', bool(p.get('audience'))),
        ('销售渠道', bool(p.get('channels'))),
    ]

    for label, completed in checks:
        if completed:
            score += 20
        st.write(('✅ ' if completed else '⬜ ') + label)

    st.metric('资料完整度', f'{score}/100')

    if score >= 80:
        st.success('资料较完整，可以开始验证目标客户和市场需求。')
    elif score >= 40:
        st.warning('部分资料尚未完善，建议补充产品特点、目标客户或渠道信息。')
    else:
        st.info('建议先完善产品基本信息，再制定出海计划。')

    st.caption('说明：该分数仅反映资料填写完整程度，不代表产品竞争力、市场份额或实际销量。')
    st.divider()
    st.subheader('三、产品卖点与出海建议')

    features = p.get('features', [])
    if isinstance(features, str):
        features = [x.strip() for x in features.splitlines() if x.strip()]

    if features:
        st.markdown('**已填写的产品特点**')
        for item in features:
            st.write('• ' + str(item))
    else:
        st.info('暂未读取到产品特点，请检查「产品信息」页面。')

    st.markdown('**建议优先验证的方向**')
    st.write('1. 目标客户是否确实需要这些产品特点。')
    st.write('2. 与同类产品相比，哪些特点更有辨识度。')
    st.write('3. 目标市场的价格、语言和使用习惯是否适配。')
    st.write('4. 产品标签、认证、物流和售后要求是否满足目标市场规定。')

    st.divider()
    st.subheader('四、目标客户画像')

    audience = p.get('audience', '尚未填写目标客户')
    market = p.get('market', '尚未填写目标市场')

    st.markdown('**目标客户信息**')
    st.write('目标市场：', market)
    st.write('目标客户：', audience)

    st.markdown('**潜在客户需求假设**')
    st.write('• 客户可能希望产品解决某个明确的问题。')
    st.write('• 客户可能会关注产品价格、质量和使用便利性。')
    st.write('• 不同市场的客户可能有不同的语言和购买习惯。')

    st.markdown('**建议验证的问题**')
    st.write('1. 目标客户目前使用什么产品或解决方案？')
    st.write('2. 他们最在意价格、质量还是便利性？')
    st.write('3. 他们通常通过什么渠道了解和购买产品？')
    st.write('4. 哪些因素可能阻碍他们购买？')

    st.info('以上内容属于初步分析假设，建议通过客户访谈、问卷或小规模测试进行验证。')
    st.divider()
    st.subheader('五、目标市场进入策略')

    st.markdown('**1. 建议评估的销售方式**')
    entry_options = [
        '跨境电商平台：适合先测试产品需求和订单转化。',
        '社交媒体：适合测试内容传播效果和潜在客户兴趣。',
        '独立站：适合建立品牌形象，但需要考虑引流成本。',
        '当地经销商或合作伙伴：适合评估本地销售与售后支持。',
    ]

    for option in entry_options:
        st.write('• ' + option)

    st.markdown('**2. 建议优先验证的推广方向**')
    st.write('• 围绕一个明确的客户需求设计产品介绍。')
    st.write('• 准备两到三种不同的宣传文案，比较客户反馈。')
    st.write('• 测试目标客户更关注价格、质量、便利性还是售后。')

    st.markdown('**3. 进入市场前的风险检查**')
    risk_checks = [
        '核实目标市场的产品认证、标签和进口要求。',
        '确认物流时效、运输成本和退换货流程。',
        '核实目标销售渠道的费用、规则和限制。',
        '评估当地语言、售后服务和支付方式。',
    ]

    for i, risk in enumerate(risk_checks, start=1):
        st.checkbox(risk, key=f'gm_market_risk_{i}')

    st.info('以上内容是通用的市场进入建议。实际选择应结合产品类型、目标国家和预算进一步验证。')
    st.divider()
    st.subheader('六、30 天出海行动计划')

    plan_30_days = [
        ('第 1～7 天：准备阶段', [
            '整理产品资料和核心卖点',
            '明确目标客户和目标市场',
            '收集 3 个同类竞品的信息',
            '列出需要核实的认证与进口要求',
        ]),
        ('第 8～14 天：市场验证阶段', [
            '访谈潜在客户或开展问卷调查',
            '比较竞品的价格、卖点和销售渠道',
            '准备不同版本的营销文案',
            '记录客户反馈和待解决的问题',
        ]),
        ('第 15～21 天：小规模测试阶段', [
            '选择一个合适的渠道进行测试',
            '发布测试内容并记录反馈',
            '整理点击、咨询或其他可获得的数据',
            '根据反馈调整产品定位和文案',
        ]),
        ('第 22～30 天：复盘阶段', [
            '汇总市场测试结果',
            '分析客户反馈和主要问题',
            '评估实际成本与潜在收益',
            '制定下一阶段的运营计划',
        ]),
    ]

    for phase_index, (phase, tasks) in enumerate(plan_30_days, start=1):
        with st.expander(phase, expanded=(phase_index == 1)):
            for task_index, task in enumerate(tasks, start=1):
                st.checkbox(
                    task,
                    key=f'gm_30day_{phase_index}_{task_index}'
                )

    st.caption('说明：这是通用参考计划，请根据产品类型、预算和目标市场调整。')
    st.markdown('**下一步行动清单**')
    actions = [
        '访谈或调查至少 5 位潜在客户。',
        '收集 3 个同类竞品，比较价格、卖点和销售渠道。',
        '根据目标市场的语言习惯调整产品文案。',
        '核实目标市场的产品合规、认证及进口要求。',
        '小范围测试推广内容，再根据反馈进行调整。',
    ]

    for i, action in enumerate(actions, start=1):
        st.checkbox(action, key=f'gm_report_action_{i}')

    report = f"""# GlobalMate 智能出海分析报告

## 一、产品基本情况
- 产品名称：{p.get('name', '未填写')}
- 目标市场：{p.get('market', '未填写')}
- 目标客户：{p.get('audience', '未填写')}

## 二、资料完整度
- 得分：{score}/100
- 说明：此分数反映资料填写情况，不代表实际竞争力或销售表现。

## 三、产品特点
{chr(10).join('- ' + str(x) for x in features) if features else '- 暂未填写'}

## 四、目标客户画像
- 目标市场：{market}
- 目标客户：{audience}

### 潜在客户需求假设
- 客户可能希望产品解决某个明确的问题。
- 客户可能关注产品价格、质量和使用便利性。
- 不同市场的客户可能有不同的语言和购买习惯。

### 建议验证的问题
- 目标客户目前使用什么产品或解决方案？
- 他们最在意价格、质量还是便利性？
- 他们通常通过什么渠道了解和购买产品？
- 哪些因素可能阻碍他们购买？

## 五、目标市场进入策略

### 建议评估的销售方式
- 跨境电商平台：评估产品需求和订单转化。
- 社交媒体：测试内容传播效果和潜在客户兴趣。
- 独立站：评估品牌建设和引流成本。
- 当地经销商或合作伙伴：评估本地销售与售后支持。

### 推广建议
- 围绕明确的客户需求设计产品介绍。
- 准备不同版本的宣传文案，比较客户反馈。
- 验证客户更关注价格、质量、便利性还是售后。

### 市场进入风险检查
- 核实目标市场的认证、标签和进口要求。
- 确认物流时效、运输成本和退换货流程。
- 核实销售渠道的费用、规则和限制。
- 评估当地语言、售后服务和支付方式。

## 六、30 天出海行动计划

### 第 1～7 天：准备阶段
- 整理产品资料和核心卖点
- 明确目标客户和目标市场
- 收集 3 个同类竞品的信息
- 列出需要核实的认证与进口要求

### 第 8～14 天：市场验证阶段
- 访谈潜在客户或开展问卷调查
- 比较竞品的价格、卖点和销售渠道
- 准备不同版本的营销文案
- 记录客户反馈和待解决的问题

### 第 15～21 天：小规模测试阶段
- 选择一个合适的渠道进行测试
- 发布测试内容并记录反馈
- 整理点击、咨询或其他可获得的数据
- 根据反馈调整产品定位和文案

### 第 22～30 天：复盘阶段
- 汇总市场测试结果
- 分析客户反馈和主要问题
- 评估实际成本与潜在收益
- 制定下一阶段的运营计划

## 七、建议验证事项
{chr(10).join('- ' + x for x in actions)}

## 八、重要说明
本报告依据已填写的信息和通用运营建议生成，不包含实时市场数据，不构成销量预测。涉及认证、法规和进口要求时，请向目标市场官方机构或专业服务机构核实。
"""

    st.download_button(
        '📥 下载出海分析报告',
        data=report,
        file_name='GlobalMate_智能出海分析报告.md',
        mime='text/markdown',
        key='gm_download_report'
    )
elif page=='多语言营销文案':
    st.title('✍️ 多语言营销文案')
    if not ready(): st.warning('请先到「产品信息」保存产品名称和特点。'); st.stop()
    a,b,c=st.columns(3)
    with a: lang=st.selectbox('输出语言',['日语','英语','中文','德语','法语'],index=['日语','英语','中文','德语','法语'].index(p.get('language','日语')) if p.get('language','日语') in ['日语','英语','中文','德语','法语'] else 0)
    with b: tone=st.selectbox('文案风格',['专业可信','轻松亲切','简洁直接'])
    with c: kind=st.selectbox('文案类型',['商品详情页','社交媒体短文','推广邮件'])
    if st.button('生成文案初稿',type='primary'): st.session_state.generated_copy=make_copy(p,lang,tone,kind)
    if st.session_state.get('generated_copy'):
        edited=st.text_area('文案内容（可修改）',st.session_state.generated_copy,height=280); st.download_button('下载文案 TXT',edited.encode('utf-8'),'globalmate_copy.txt','text/plain')
        if st.button('保存文案到项目记录'): log('多语言营销文案',edited[:300]); st.success('已保存。')
elif page=='海外市场研究':
    st.title('🔎 海外市场研究')
    if not ready(): st.warning('请先到「产品信息」填写产品资料。'); st.stop()
    st.info('零成本研究工作表：不会自动联网获取实时数据，请填入你查到的真实资料。')
    with st.form('research'):
        keywords=st.text_area('当地语言关键词'); competitors=st.text_area('竞品名称、价格、链接和卖点'); pains=st.text_area('真实用户差评与痛点'); compliance=st.text_area('合规、物流和退货注意事项'); notes=st.text_area('其他观察')
        submit=st.form_submit_button('保存市场研究记录',type='primary')
    if submit: log('海外市场研究',json.dumps({'关键词':keywords,'竞品':competitors,'用户痛点':pains,'合规物流':compliance,'其他':notes},ensure_ascii=False)); st.success('已保存到项目记录。')
    st.subheader('免费研究清单')
    for x in ['搜索当地语言关键词并记录联想词','比较至少 5 个竞品的售价、规格和评价','整理低分评价中重复出现的问题','核实当地标签、广告、知识产权和产品安全要求','估算采购、佣金、物流、税费和退货成本']: st.checkbox(x,key='research_'+str(abs(hash(x))))
elif page=='出海运营计划':
    st.title('🗓️ 出海运营计划')
    if not ready(): st.warning('请先到「产品信息」填写产品资料。'); st.stop()
    start=st.date_input('计划开始日期',value=date.today()); weeks=st.selectbox('计划周期',[1,2,4],index=1,format_func=lambda x:f'{x} 周')
    tasks=[('产品与客户','整理产品规格、确认目标客户、列出用户痛点','产品负责人'),('竞品调查','记录 5 个竞品的价格、评价、卖点与差评','市场研究'),('内容准备','完善标题、产品描述、图片需求和 FAQ','内容制作'),('本地化检查','检查语言、单位、价格、配送和退货信息','本地化'),('小范围测试','选择一个渠道，小规模发布并记录真实反馈','渠道运营'),('复盘优化','根据反馈调整卖点、内容和产品页面','复盘')]
    rows=[]
    for i,(phase,task,owner) in enumerate(tasks):
        if weeks==1 and i>1: continue
        if weeks==2 and i>3: continue
        rows.append({'阶段':phase,'计划日期':(start+timedelta(days=(i//2)*7+(i%2)*3)).isoformat(),'任务':task,'负责人':owner,'状态':'未开始'})
    df=pd.DataFrame(rows); edited=st.data_editor(df,use_container_width=True,hide_index=True,num_rows='dynamic',key='plan_editor')
    if st.button('保存运营计划',type='primary'):
        st.session_state.plans.insert(0,{'时间':datetime.now().strftime('%Y-%m-%d %H:%M'),'产品':p.get('name',''),'市场':p.get('market',''),'任务':edited.to_dict(orient='records')}); st.session_state.plans=st.session_state.plans[:100]; persist(); log('出海运营计划',f'保存了 {len(edited)} 项任务'); st.success('计划已保存。')
    st.download_button('下载当前计划 CSV',edited.to_csv(index=False).encode('utf-8-sig'),'globalmate_plan.csv','text/csv')
elif page=='项目记录':
    st.title('📚 项目记录'); t1,t2=st.tabs(['操作记录','已保存的运营计划'])
    with t1:
        if st.session_state.history:
            h=pd.DataFrame(st.session_state.history); st.dataframe(h,use_container_width=True,hide_index=True); st.download_button('下载操作记录 CSV',h.to_csv(index=False).encode('utf-8-sig'),'globalmate_history.csv','text/csv')
            if st.button('清空操作记录'): st.session_state.history=[]; persist(); st.rerun()
        else: st.info('暂无记录。保存产品、分析或研究内容后会显示在这里。')
    with t2:
        if st.session_state.plans:
            for plan in st.session_state.plans:
                with st.expander(f'{plan.get("时间","")}｜{plan.get("产品","")}｜{plan.get("市场","")}'): st.dataframe(pd.DataFrame(plan.get('任务',[])),use_container_width=True,hide_index=True)
        else: st.info('暂无已保存的运营计划。')
st.markdown('---'); st.caption('GlobalMate 2.0 · 本地运行的零成本原型。请核实市场、合规与产品信息后再用于商业发布。')
