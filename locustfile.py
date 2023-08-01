# Monograph-DB压测
from __future__ import absolute_import
from __future__ import print_function

import random
import time

from locust import User, TaskSet, task, events, constant
from sqlalchemy import create_engine, exc, text

import mysql.connector
import config





def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

    
"""
sqlalchemy doc
    https://docs.sqlalchemy.org/en/20/core/pooling.html
"""    

@singleton
class ConnectionPool(object):
    def __init__(self):
        self.engine = create_engine(config.connection_path, pool_size=config.POOL_SIZE, pool_recycle=config.POOL_RECYCLE, max_overflow=config.POOL_MAX_OVERFLOW)

    def begin(self):
        return self.engine.begin()

    def pool(self):
        return self.engine.pool

if config.USE_PREPARE_STMT == False:
    print("Initialize Connection Pool")
    _p = ConnectionPool()


class PrepareStmtClient:

    """
    MysqlCursorPreared doc
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursorprepared.html
    """
    def __init__(self):
        assert(config.USE_PREPARE_STMT == True)
        super().__init__()
        self.cnx = mysql.connector.Connect(user=config.USER, password=config.PASSWORD, database=config.TS_DB_NAME, host=config.IP_ADDR, port=config.PORT)
        self.cnx.autocommit = True
        self.curprep = self.cnx.cursor(prepared=config.USE_PREPARE_STMT)

    """
    def __del__(self):
        self.curprep.close()
        self.cnx.close()
    """

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                self.curprep.execute(*args, **kwargs)
                rowset_count = 0
                # if self.curprep.rowcount != 0:
                #    rowset = self.curprep.fetchall()
                #    rowset_count = len(rowset)
                
                events.request.fire(
                    request_type="MonographDB-PreparedStmt-Client",
                    name=name,
                    start_time=start_time,
                    response= None,
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=rowset_count,
                    context= {},
                    exception= None
                )
                
            except (Exception, exc.OperationalError) as e:
                events.request.fire(
                    request_type="MonographDB-PreparedStmt-Client",
                    name=name,
                    start_time=start_time,
                    response=None,
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=0,
                    context={},
                    exception=e)

        return wrapper



def execute_query_from_pool(conn_string, query):
    with ConnectionPool().begin() as conn:
        rs = conn.execute(text(query))
        return rs



class MySqlClient:
    def __init__(self):
        assert(config.USE_PREPARE_STMT == False)        

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                
                res = execute_query_from_pool(*args, **kwargs)

                events.request.fire(
                    request_type="MonographDB-Connection-Pool-Client",
                    name=name,
                    start_time=start_time,
                    response= None,
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=res.rowcount,
                    context= {},
                    exception= None
                )
                
            except (Exception, exc.OperationalError) as e:
                events.request.fire(
                    request_type="MonographDB-Connection-Pool-Client",
                    name=name,
                    start_time=start_time,
                    response=None,
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=0,
                    context={},
                    exception=e)

        return wrapper


class CustomTaskSet(TaskSet):
    # conn_string = "mono:mono@10.106.50.14:3300/parking"  # qa
    # conn_string = "sysb:sysb@127.0.0.1:3317/parking"
    conn_string = config.USER  + ":" + config.PASSWORD + "@" + config.IP_ADDR + ":" + str(config.PORT) + "/" + config.TS_DB_NAME
    sql_plateNumber = ['冀R62W63', '渝BLJ765', '渝A852A6', '陕J00339', '粤A37980D', '苏E0931Y',
                       '蒙DW013L', '川A7SK73', '渝BNW650', '沪EH1395', '鲁F388TS', '川AD808P',
                       '京N6A256', '京JR4601', '川A0UA97', '京A69318', '陕A8LQ56', '鄂A10M09',
                       '京HM5967', '鲁AS73F0', '粤A067VQ', '苏ES16H2', '京NWA984', '湘AY4K30',
                       '鄂A8F69M', '京N1XZ53', '京QWG371', '湘A557ZG', '川AW033S', '渝AJE063',
                       '川AG3Z03', '京J69376', '苏E1S18W', '湘A43J67', '京NZ6538', '湘ADB2710',
                       '湘KCS258', '陕A0XS93', '陕A07F29', '辽B1KJ76', '粤G23R26', '鲁Q3135Q',
                       '京Q8JV07', '京FG0578', '川A4S178', '粤BC629Z', '湘AX6E71', '粤C1W965',
                       '辽A56R5N', '粤A2682Z', '鄂A44951', '渝AVM366', '湘A1NE01', '京Q2Y228',
                       '粤LR2585', '粤B892SD', '京QQ11C2', '京PUR155', '粤VMA305', '沪B15S93',
                       '粤FJM575', '渝AQ187P', '渝DJ8625', '渝AU66K2', '陕AM5A19', '京N38E72',
                       '京N103W2', '京EK2320', '川A4E66F', '赣A5998M', '黑E7JS65', '川ABW804',
                       '京KDZ495', '京ND1342', '苏EU51D5', '川A221CA', '京QW0S30', '粤AW848B',
                       '苏E2A55X', '粤B1KB51', '粤BR7Z82', '湘F1230C', '京NL7985', '渝D6B383',
                       '湘ADD6113', '京CLY169', '川A943JK', '粤KZ898L', '沪FEM022', '川A94WE8',
                       '川AER104', '粤L85T90', '京P616J2', '川AQ9D70', '沪C2Q8K1', '粤AC529G',
                       '冀R158X3', '川A3Y19R', '闽DX3M21', '陕A3B07N', '湘A5WH22', '冀C9382D',
                       '粤EC255B', '京Q98WM0', '赣FE5157', '闽C397EF', '渝D56W88', '京HEF335',
                       '京JQ1639', '川A88LS4', '粤BAN291', '沪C3V888', '湘AD86802', '川A1MM92',
                       '沪AFL9076', '川A538HH', '京Y18352', '川ALM624', '渝AF76888', '京N2NJ63',
                       '川AK2188', '湘AB0W23', '鲁A7FK59', '京ADE6137', '皖HGT299', '川A3T9M3',
                       '鄂DSZ552', '沪C3926Y', '粤AL3E18', '沪DX8206', '京NT8Y20', '京NLH269',
                       '粤B858MH', '湘AHQ758', '苏E69LF8', '苏E16G66', '沪AWU601', '京HBY809',
                       '粤A6215J', '川A8HA86', '粤B4K356', '粤ADQ5507', '沪FGT610', '京HY9987',
                       '京N58PA9', '辽PPB316', '湘G2S522', '湘A026N1', '京Q16F90', '沪A1W623',
                       '渝AHN041', '冀R58KU9', '川AL442Q', '苏UYU888', '鲁A7X35P', '陕A8H10L',
                       '沪BUS283', '京FE6568', '粤K7093R', '渝B9D907', '鄂JFC770', '渝AXZ079',
                       '川A709XG', '渝BQU575', '云ATE038', '粤AX269M', '粤BV38Y5', '川A66XY7',
                       '粤B975AR', '闽A1F265', '川AD9037', '沪C3A1B5', '苏JYA338', '贵C79Q19',
                       '皖KT388Q', '川A93789', '川A935WY', '鄂AK4P12', '湘AB56A9', '粤SYT228',
                       '粤AD12503', '渝AKN401', '京P952S1', '川AL314P', '京ADC9110', '京AAB0879',
                       '湘H5AK55', '渝AF39003', '京QK1077', '京H63839', '浙BP1C07', '川A528YS',
                       '陕A9FT15', '京MGD872', '冀FL889S', '京NXQ385', '粤B2WW93', '粤B5J6R0',
                       '粤B18N95', '渝AJE981', '鲁J3733X', '粤AJ5N31', '沪AV508学', '赣C21150',
                       '渝A327NJ', '沪BAX012', '京N71S28', '京Q3RE70', '渝GM2666', '渝A8292D',
                       '粤B091RT', '粤B2C62T', '京AF5326', '粤A9F93N', '粤AQ0M99', '沪AGF8601',
                       '川A4LH44', '苏F3J0J0', '鲁F08N85', '京NA2622', '鲁Q10SA6', '苏E90L9B',
                       '粤AK52J2', '粤A72M23', '京ADJ719', '渝A516Y1', '渝DGK661', '京JKC713',
                       '京N65G17', '粤S7BP76', '渝DQ0590', '陕G0999T', '湘A6V89G', '川A6X7S9',
                       '皖C79CC8', '鲁A7R875', '沪ADE5282', '粤AMD618', '京NQ2351', '粤AU602L',
                       '川A64WU4', '粤B5077G', '苏EB5Q15', '京MHB866', '豫SL5D29', '京NQ9252',
                       '苏N59P27', '粤BDE9979', '京NZ0S92', '京NLQ986', '浙J13A2A', '沪FS0969',
                       '京Q860D5', '京KAE771', '川AT17Q1', '粤BD21183', '川A55WX2', '川AR0482',
                       '川AN827F', '粤AD93V8', '陕A687ES', '京NUX612', '渝ACH016', '川AF09660',
                       '冀R59SR7', '京A3JN58', '皖LL526L', '京PU8D18', '京LV8818', '川A9F056',
                       '渝DU0588', '京N92M69', '湘A6Q86B', '陕AD57251', '川A429YD', '渝A9MP93',
                       '京PKL065', '粤B1798P', '京LE7562', '粤VHY316', '陕D05M38', '川TZ3713',
                       '浙AZ07N0', '川A1B9F8', '陕AJ9C29', '渝AA2E97', '粤A1VS33', '苏BB0N65',
                       '粤B8B6N3', '鄂A7V9D9', '渝BMW355', '京QB5F02', '沪C0R197', '皖NVD119',
                       '苏B857DV', '川AQ66V6', '沪A986L4', '渝G67A10', '沪N06700', '陕A8F77W',
                       '粤S964RZ', '沪FE0293', '渝A238M7', '京KFD920', '京N5A766', '粤A864W8',
                       '京AE5713', '粤A7Q6E3', '渝AH5B60', '京AD56719', '陕A10B1E', '皖AD23916',
                       '湘AM976D', '粤A446YU', '川A1GD91', '苏EA223G', '粤B5D6N3', '苏E61H3F',
                       '皖P91999', '京BU7162', '粤A8BZ97', '苏E9862P', '粤JYH791', '粤L2E813',
                       '陕AD16031', '粤A0J9Y6', '冀B927BR', '粤A7KT94', '京NJS006', '京QC76X3',
                       '京PKT638', '鲁FH5370', '京ADM1321', '粤BC99Q1', '陕A5J09L', '京AYF557',
                       '粤Y94F76', '川A707DY', '陕G58000', '湘A21W90', '陕A3WF16', '粤B3833G',
                       '鄂AA7Y80', '京NB9864', '陕A9M79R', '京AD0737', '川A5P4D5', '川AA57M2',
                       '晋AH567M', '苏M89E59', '黑AT8K99', '渝A35M75', '京N00S60', '京NXT549',
                       '冀R87A10', '京NFD709', '京N700L0', '粤AC087C', '京NP7E07', '京FK5277',
                       '京N041T1', '湘A8N96V', '沪JY3080', '鄂A93AY7', '京FHH870', '京LQ7853',
                       '沪B528C7', '京BP9605', '渝CN6777', '川A801QM', '川A213PW', '京AA8952',
                       '川Y56H82', '粤AP0015', '川ADN905', '鄂A415Q1', '粤J3Q118', '京N1A502',
                       '陕A65AY0', '粤B0L5C9', '京P27122', '京QC33P7', '鄂J6D662', '京NC3816',
                       '川A37V3M', '粤NDA352', '渝AR32R6', '浙A5N3G7', '苏E97135', '粤K0716Q',
                       '苏ECQ003', '湘A730CJ', '陕A73AP8', '京EH9355', '陕AH229Z', '渝DN7266',
                       '京H47647', '苏E1DC57', '粤A8502T', '京AD30567', '粤A4X277', '京A3LT65',
                       '川R9205D', '鄂L57E89', '渝B092X5', '渝AED805', '陕A79M39', '渝BYC503',
                       '京N6ZF30', '粤B5L38W', '冀R97N29', '粤S04X32', '陕A677T8', '川A38Y33',
                       '粤A7HR62', '京NQ9J20', '粤BD96287', '冀F182VD', '晋AD72210', '粤A0N69X',
                       '京AD69917', '粤B8X31W', '渝BEU767', '鄂AA4U51', '渝A708D0', '苏E57P16',
                       '沪A2W022', '陕A9Y13S', '川A1SH97', '川A757LD', '渝AX776L', '苏U2A773',
                       '粤B9L19J', '粤BS40C8', '京N7XE27', '粤A8T71K', '渝AKK394', '粤BH1333',
                       '京PE2115', '渝AEA329', '川A5N88P', '渝A0RY07', '京JN8067', '粤AW729Q',
                       '京Q16HJ8', '渝BBM532', '渝A6Q802', '湘AE33G6', '京Q6V9J0', '鄂A06ZT6',
                       '陕DA8006', '粤AL2W29', '渝AMR552', '渝APY342', '鄂AR9570', '粤S2Q87F',
                       '湘JHL135', '京Q230V3', '湘A9L70J', '粤Z6402澳', '辽NN3838', '京JAW126',
                       '粤BFB6875', '冀R67B96', '京PRM806', '京Y05605', '粤DWB189', '京N8Z417',
                       '陕A0Z0A5', '京NB6163', '粤ADE2592', '京NX5P59', '川A50LY8', '渝AYU284',
                       '豫A7E62C', '冀CJM572', '京N6JY17', '鄂A327ZS', '川AD51366', '陕A8T8J1',
                       '京N5W2M0', '川AZ581K', '沪FE5093', '鲁J7680G', '京N979C2', '京GAU883',
                       '辽A49A99', '苏EK050Z', '川A4T6K4', '鲁A025A2', '京Q61CD1', '湘A3H22R',
                       '京N83XD8', '渝DET737', '京Q0T0Y1', '桂G60526', '苏EBU221', '京NS9H18',
                       '京QV73Q1', '川AA14Y2', '京AAB5983', '粤B75BA0', '京Q6SN28', '粤B39HV2',
                       '京NK6N33', '渝A705PZ', '沪C3Q7T2', '鄂A0D1Y9', '渝AE204S', '粤B4T1G6',
                       '川A38D9V', '苏UKT512', '豫A8U88L', '粤LBM356', '粤R132A9', '川A24B1N',
                       '京HM0399', '川A54CA2', '苏K76B8B', '粤B8L11T', '粤B0X473', '沪BVR357',
                       '京Q2HH12', '粤Y06S10', '京PZL032', '沪B96B99', '赣B125E0', '沪HJ5319',
                       '渝C19A38', '湘AZN788', '陕A15P9K', '川A8A1H4', '京Q75TJ9', '川A4U13E',
                       '粤B7WR57', '川AD26Z9', '渝DJF380', '渝B9B810', '赣C651E3', '粤A28GP8',
                       '川AL1N91', '京MGQ262', '苏E9X618', '川AS6336', '川AP02G9', '京A1JP92',
                       '京Q5SL35', '云MAE222', '京Q5CH63', '沪ARX868', 'JA04054', '川A51908',
                       '京NC0N07', '湘A938YG', '苏E3992L', '陕AZZ401', '京PX9C00', '京ATW860',
                       '渝BZJ119', '渝A861RB', '辽A9BS56', '京EH4486', '鄂AD9H20', '川AG85U2',
                       '鲁J116C2', '川A415CN', '粤YFX134', '京A0ED12', '鲁AC228A', '粤AS14S9',
                       '京ABF712', '渝A17VM8', '吉AW7979', '川A0228K', '川ADC3988', '京P9M699',
                       '湘A57NR6', '苏H0A973', '川A8BM61', '粤S2S2S2', '川AD89469', '粤BCD886',
                       '鄂A5V90V', '川A875QT', '京CKG561', '京NHL224', '京N32P06', '粤B6Z033',
                       '鄂A01HM6', '京Q80NR3', '京P7Q206', '浙F757GY', '渝DER607', '京HEP798',
                       '粤A737NL', '沪FFL168', '苏E395Z3', '京QY5266', '京CLH702', '京PH8N38',
                       '京A3JP76', '渝D1R257', '京M58768', '川DC2759', '粤BWA206', '川AF57885',
                       '粤BX39T6', '京Y87979', '粤V37P95', '苏E0V2M4', '陕UBH598', '粤AV5296',
                       '鲁A890EH', '京JE1451', '京AFG5526', '粤B772NN', '豫QZK228', '苏EW97V8',
                       '渝AUQ368', '京NQ8Z19', '京Q3D8W2', '渝C0X657', '渝DP6985', '苏AKG116',
                       '渝AD057M', '鄂A5HJ13', '渝DCP017', '京Q5R990', '京E88528', '渝BRZ501',
                       '京N1XT03', '粤Q95996', '京PT3L75', '川AGL898', '湘AN6F09', '京N92A89',
                       '沪C378T3', '粤A1P1S9', '渝C519Y7', '京N6MR05', '京GTU459', '云K88Q11',
                       '川A16FR0', '沪ADX9018', '粤A5W57K', '冀RUG585', '沪C198ZB', '冀F52VH7',
                       '冀R9G7R5', '渝FFP808', '苏UBN199', '鄂A36GS8', '苏ER0R57', '京N4RY93',
                       '粤B3A25B', '沪B60C58', '粤A9U2B7', '陕A06M3X', '京N9A892', '贵AJ0E29',
                       '湘AB16Y7', '京N5GR91', '沪BMT219', '京AAC2158', '京Q0AW51', '川AZ63Z5',
                       '陕A23JF3', '粤AF36080', '粤AD60035', '陕A3P09T', '渝AD6Z69', '川A6G575',
                       '川A286TF', '京Q8C926', '苏U3P062', '苏E5X321', '京LMN778', '沪ADG2829',
                       '京A5NG23', '川A4Y61L', '沪ADN1038', '沪LD0968', '沪FJU918', '粤B0C22Z',
                       '鄂CK5700', '京EW9690', '京J66330', '京A1NR06', '川A78W6J', '京NS3J33',
                       '粤BDB4295', '粤AY9M20', '京JK0891', '京PR6Q56', '渝D246M9', '粤K362M8',
                       '京KEY705', '沪AG51921', '云F0487F', '粤AE33Z5', '鲁Y86086', '京MBP791',
                       '渝A70833', '京FD2778', '陕A7D17P', '京JQ3756', '晋B0516L', '鄂AN7H65',
                       '辽JNN782', '川A7BK94', '冀HJP345', '京A3EU18', '京NT5F66', '川AF19253',
                       '粤A9N28N', '京P6RF50', '京LM9556', '川AR565N', '湘ANE595', '渝BMJ761',
                       '鲁ASD297', '京NR2R69', '川A0N645', '鲁A578UH', '京YV9955', '川A60A8P',
                       '京N21B05', '苏ELX136', '川A3Y4F5', '粤SM67B6', '粤B000V2', '沪C9P2Y5',
                       '鄂AF1Y57', '京FB3266', '川A8F41A', '云KLY638', '湘A2X61B', '沪CX253Z',
                       '甘ALV318', '川A28A00', '川J9090E', '川AZ92K6', '川A619A4', '皖AA751S',
                       '京N28ZL6', '苏H0716G', '湘A79LZ3', '川A8Q52D', '川AA30C9', '湘AT2Y56',
                       '苏EK252V', '晋A911AL', '青ARL995', '陕A6MY68', '渝B7B776', '苏E3E99R',
                       '京JC0568', '湘A088S8', '鄂A3392E', '京HGE001', '皖CDU535', '京Q5H5X3',
                       '川A5MB03', '渝AS295F', '渝B75K53', '粤AM29R6', '冀A6AX67', '渝DAZ166',
                       '渝A6N507', '京GBY068', '川A794JE', '渝A99GD0', '粤A9X33G', '沪EZY792',
                       '沪C3W6D2', '湘AFE006', '粤BB48Q2', '京L59835', '京Q92VR9', '苏E5X605',
                       '粤SB6U48', '苏A5686T', '苏U220F0', '渝AXM459', '苏F121BW', '川A6P674',
                       '川AK886W', '苏E5D87D', '京N66CS3', '浙DV6766', '粤Y256N9', '京AFV880',
                       '湘A5XJ61', '粤A994ZZ', '京QT8060', '鄂AN6L00', '川A1577L', '川A09C7T',
                       '闽E05H08', '粤AQ612S', '川A03U4S', '粤L496M6', '渝BTF921', '渝AC2T77',
                       '京MA3337', '辽B9548E', '渝CNH586', '京GMP922', '粤AK357L', '京AUU461',
                       '京N817Z2', '湘A3QZ66', '川A722XK', '川A70YE5', '陕AY7J75', '京QR69Q5',
                       '京EA5135', '京ADK3685', '皖KW362Y', '京P77T07', '川A2J7L3', '粤YMF600',
                       '粤FMT187', '渝A7UL02', '陕JP8555', '沪A6T851', '沪A606W6', '沪FHL685',
                       '京NHG618', '渝A36888', '渝AWT229', '京AEU327', '京N90BV3', '川AG6600',
                       '粤K7958Q', '桂G92628', '京Q0TF03', '川AD53994', '渝A9502Q', '鲁Q8L300',
                       '京Q27K92', '粤B4UD63', '冀R792J1', '浙CH563Z', '渝A9X238', '京M83895',
                       '粤S5236C', '川A8P9P9', '渝A30K37', '川A4CJ23', '粤BM079R', '粤S9ER13',
                       '沪AF60758', '湘A9M75A', '渝A246BX', '京HD8349', '京KM5033', '渝A9VG72',
                       '京A93731', '京LJV388', '川Z98C76', '鄂A7M98K', '渝AL566B', '京QJ09Q9',
                       '辽A7ET07', '粤BV5R00', '粤AD750A', '渝AD06336', '皖HF8013', '粤B3237E',
                       '苏ES66N1', '陕UF5846', '蒙G47888', '渝A16SX8', '粤SE4630', '苏M19L09',
                       '京KAE735', '桂CQ8411', '京P12Z32', '粤AF38V4', '渝BMJ017', '苏EWG533',
                       '苏E59X50', '渝AXQ518', '川A296YL', '粤E16M48', '粤A0NF75', '粤RQD981',
                       '沪AFM9875', '粤B6K041', '渝GGT668', '川A67YX7', '京JU7588', '京A6KT91',
                       '桂ABJ419', '川ADA5214', '鲁J6G626', '苏E68P5S', '粤GQE248', '沪ABX816',
                       '粤AD01L0', '陕AAA801', '京LN7068', '鄂A79YY7', '鲁A8H5B8', '陕AD97086',
                       '京QB6R26', '京KJ0970', '京N675G5', '沪AFL8135', '粤ARU520', '鄂AR9Q15',
                       '云A9G78B', '鲁AKY150', '渝B2Z295', '川A130NP', '渝A990PZ', '苏E0ZS58',
                       '沪DDV902', '渝D66595', '辽AJ348A', '京FBL003', '京MKC337', '鄂A04KY6',
                       '粤A02Z32', '京PC2A76', '京ADE656', '京N27C13', '渝A9KY51', '陕A75S82',
                       '辽PVW870', '豫CA9B62', '京QWZ651', '川ALS702', '川HA5258', '京GFL052',
                       '鄂A987FM', '京AKP357', '京QA56N2', '粤A1298A', '粤B8455U', '沪D54615',
                       '京ADJ6217', '粤AU4H48', '渝AF09399', '沪GA5180', '川A80L3A', '苏AW9J93',
                       '沪FXE380', '陕A7U78Y', '陕A961YG', '苏E333JG', '渝BUA689', '苏EX6858',
                       '川A6D16H', '苏UFS920', '京ADJ9065', '川AN5U58', '鲁JRX582', '渝B78W80',
                       '京QA6L75', '京A1AE65', '苏E9K21S', '京QX7C11', '川AS27K5', '冀B0AR70',
                       '京N6C8F8', '京MT0738', '京ADY3659', '粤A3715X', '豫A0P36G', '川AH65Z8',
                       '渝BAL900', '京QRQ320', '渝AY8T20', '京NK0L18', '鄂A670BB', '湘N7GL85',
                       '陕GZ6262', '川A0L72R', '鲁FB5X86', '皖MCV672', '陕AN9A65', '粤CZ9076',
                       '豫A5920R', '冀R623P0', '苏CE936G', '京P6VU93', '粤D0P789', '渝BKA827',
                       '渝BVX373', '湘A3WM82', '京A8EJ31', '粤AB552S', '甘DR1178', '鄂A0X2B0',
                       '京N09M05', '浙DKL373', '京A5ES10', '苏E3V1F3']

    sql_synid = ['804EA97E-B2C9-4741-99A7-69FF63A69F29', '0E158819-011E-4F68-A076-69FF63A9DC6E',
                 '2A57ACCA-831E-4865-ABC4-69FF63B5DE58', 'B749BAAA-3EE3-4C9E-82EF-69FF63B7111B',
                 '9C31227D-F9B9-49CA-9824-69FF63C0061F', '9554E0E4-C19D-4D39-AAF8-69FF63C1D16F',
                 'D48D4598-8341-4FD5-89D4-69FF63C38D56', 'AFD114AA-C460-4AAD-926E-69FF63CD16B7',
                 '8D45671F-01A3-4E09-9244-69FF63D6D6A0', '15FB80F6-5FAB-40E9-B243-69FF63DD2912',
                 'B55030AF-037B-4032-ADDC-69FF63DF8785', 'A4503C43-4A9D-428D-B6BE-69FF63F21797',
                 '1229C2BF-9F84-4DBE-AB86-69FF63F41F8F', 'DE461260-D00A-41D5-A390-69FF63F60DCF',
                 '278DE63F-3535-4457-8818-69FF63FE51D5', 'C18A6698-219F-4D72-975F-69FF64091903',
                 '91952F11-C038-4E58-9BFE-69FF6437DA1C', '7D834CEE-A1B2-40CB-81DC-69FF6491F410',
                 '9440F601-5522-4C85-9783-69FF64991A30', '93A8FA40-B2A0-4897-BFBD-69FF649E4FA8',
                 '3A901E3C-C38E-48F5-9F09-69FF64AA1C25', '66D6D856-71CE-4FF1-868A-69FF64BE0979',
                 '7E883F97-5135-42A0-A09A-69FF64DDC230', '42E524DD-50C2-4BE2-99FA-69FF64F18BB7',
                 '4490CAF8-500A-43CB-B285-69FF64FA9981', 'CE5A8FDD-1073-4C0D-8E11-69FF650391B5',
                 'C478B298-C84C-4221-A0E9-69FF65129E9F', '426919F2-18C5-4635-BF28-69FF65163585',
                 '69EB947A-D389-49E4-ADD0-69FF6519A941', '2CB05278-7729-4E13-ADC3-69FF6519C27A',
                 '29C4C457-DD48-4E21-82E7-69FF651A1FA4', '3E55D6B2-0218-4E69-9742-69FF651AAC24',
                 '6EE8DB86-ABF1-4FBA-AC05-69FF651D40B1', 'AD049746-FDB1-40F2-8759-69FF65243EB6',
                 '571C6958-E9E2-4EA9-81AB-69FF652CC5AB', '84B085BA-ACB0-48BD-96B6-69FF6531A320',
                 '4A13355B-449C-4223-A4FC-69FF654A9813', '865EA13D-BBBB-4807-B979-69FF65591478',
                 '5E6A3B1D-65A6-46F1-AD85-69FF655963F4', '15D5BEA7-7475-4AF4-A0B9-69FF656313BA',
                 'D8D46EDD-D4F0-46C1-9EA1-69FF657069F4', '2F7730B3-2634-424D-923E-69FF6578C985',
                 '3807F1FE-8853-4C98-9651-69FF657B0D91', 'A811C34C-DBDF-47B7-B03B-69FF657FA895',
                 '411DE234-A244-4854-BFD2-69FF65A19416', '0636F423-B069-4486-901C-69FF65A85B48',
                 '7C416CFD-9AFD-4B85-95AA-69FF65AB6BFA', '214010C4-BC38-40DB-A253-69FF65B75E34',
                 '5C3E2183-2C53-479C-AC21-69FF65BB161A', '23374382-C7DF-4A03-ACFF-69FF65BDEE7A',
                 'BED83D5A-B804-4C72-BACE-69FF65C07B4A', '02DBE871-D8D8-4AF1-92D1-69FF65C451FE',
                 '5A2F0942-589C-407C-8322-69FF65D8EBBE', '7E73D592-1027-4CD4-B32C-69FF65F9CEA7',
                 '4A03D195-0AAA-4AFB-A32A-69FF65FC0144', 'FB581EC9-2BF5-4E8B-9A07-69FF66098C55',
                 'FA9887F8-5052-4A8D-B090-69FF660CDDE4', '0C1FDA45-745C-48AD-B55E-69FF6612FB52',
                 '65EA4C50-96ED-4BC2-98A5-69FF66225770', '52BCBF05-0490-42D3-82E8-69FF66237CC4',
                 '7BB129CD-D9D9-47E1-9406-69FF66266BE0', 'B135900D-BE54-4BD5-B0C5-69FF665BE2C7',
                 '5D68A567-A1A7-4082-98E7-69FF666A90A3', 'B0C6E1DD-C541-48FD-85DF-69FF6683D903',
                 'B671E246-4591-4542-9075-69FF668652C4', 'CD7DDC7A-877D-41CA-BBF0-69FF668C7B1F',
                 'B7882C8F-013A-484F-9A16-69FF669FF586', 'F2657188-E95A-4E11-93DE-69FF66A2428D',
                 'B7A3F251-CB1E-4F0E-A5DB-69FF66BDADAB', '5848AA97-DCA2-46B8-B91F-69FF66E30183',
                 '41198A7B-F0B4-4966-BE56-69FF66E6CCE2', '90F53DD8-4BFC-4623-969E-69FF66F3C898',
                 'B6A60C5C-FDC8-4848-A0FB-69FF66F5C6E0', '9990905C-0C06-4521-B031-69FF66F8FD26',
                 '5CEED8FB-64F9-4149-B0FA-69FF66FA7D9A', 'BD789109-CB8E-4CD0-9D9B-69FF66FB3A22',
                 '89CAF838-7A9C-443B-AF0D-69FF67210A7D', '3716A3F1-285D-4419-957E-69FF67387A9B',
                 'A9B1AE0F-546E-4D29-B6B7-69FF673FA55E', '0C6A42F5-1B60-4BF9-BF6E-69FF6748EE8D',
                 'EBCF1F8F-811A-46BE-BD58-69FF67704CE0', '81A8449D-1CFB-4638-942B-69FF67970680',
                 '38A761E4-FA00-4360-AF5A-69FF679E27B3', '7FDEA52E-9678-48A0-9069-69FF67AAA3F9',
                 '1132EC9F-A7BC-4278-8B74-69FF67AF6FC1', 'F7708F77-1385-40BD-BD9A-69FF67B5C8CA',
                 'FF1111D8-0277-4B44-BBFB-69FF67B9E0A3', '9B447CC9-DB3B-4A39-B703-69FF67BD82B5',
                 '1343861B-E5D8-45C0-95FE-69FF67D0401B', 'E02B7A71-17E4-421E-B82B-69FF67D3EDD6',
                 '09946389-51DF-458B-A2FF-69FF67D5D48D', '73592044-3E6A-44FD-AA3A-69FF67DA146F',
                 '4F145DCF-60B5-402D-B836-69FF67DD8438', '4752E68D-FF14-44C9-886C-69FF67E47F96',
                 '86A1A977-34E9-4C73-9F48-69FF67ECFF02', '0A960C4D-302E-49F1-BBEB-69FF67F75950',
                 'E9D30986-E678-41F7-BD6D-69FF6801EC2D', 'B229C3D7-7C70-42C7-BC6A-69FF68037C72',
                 'AF5E3110-D4D9-4D18-AE09-69FF68102F93', '472F2F31-153C-4E29-B0CC-69FF681A583F',
                 '543035AC-833D-4556-B3FA-69FF6821E609', 'DD7ADC85-110C-43B0-A4DF-69FF68367A33',
                 'BEEF5704-416F-4286-834E-69FF6836DFFB', 'B832EF61-14E7-4E36-AD6F-69FF683A378D',
                 'B35038EB-3FC4-4E8B-A2D7-69FF6844768D', '79404291-6988-4965-BEFF-69FF6845DFDB',
                 '7AE58BA4-E980-41A8-9A6F-69FF6855373A', '82C1C81A-F969-48BC-832E-69FF685B4CB4',
                 'AB7EB324-47FB-4BF4-8400-69FF685CD76E', 'B1801E6B-99D3-46ED-8B0A-69FF685E3EB2',
                 '03DE1632-608E-4E3A-B91E-69FF68A01EC4', 'E25C3468-9858-4B4C-8741-69FF68A699B2',
                 '90D81C9C-F390-42FE-80D7-69FF68A817A0', '52FC4F80-C90E-455D-86FF-69FF68AD6F4B',
                 '2A77651A-3F7C-4197-8F5A-69FF68AFCEA5', 'CDD9ADDF-DA16-434D-819F-69FF68B87A6B',
                 '5D849492-62CE-4084-B828-69FF68B9DE12', '073723EE-E968-435C-8D88-69FF68C18968',
                 '44972710-C1B9-4F56-A743-69FF68C78AFD', '48E3B9B4-8173-4195-B7CC-69FF68D2CEE9',
                 '1D40F5D3-BC80-4413-A891-69FF68D89FC7', '0526EA7B-0132-4213-9486-69FF68FEB6A3',
                 'BFD76DBF-777A-4746-91A4-69FF69059285', '92E46363-07DF-4B16-9AE5-69FF69206DF4',
                 '93ABAF26-B1C6-47CB-926F-69FF692A15C2', '4153D457-7B3E-4878-AD0E-69FF692AF186',
                 '2483378A-F1E5-4C5C-8E1E-69FF69308E0A', 'C92CA446-60CA-4EBF-B69B-69FF69326528',
                 '6CE5BA69-57C7-4D50-8C08-69FF693EC5A6', 'BCBB40D9-C15A-4545-AB74-69FF6941A7B1',
                 '406E1C7C-7050-48F4-82ED-6A0161F0B786', '454A2018-79B9-405F-88E8-6A0161FFE123',
                 'BB365653-586F-459F-81E2-6A016203A2E0', 'FEE8ABEE-2A63-46FA-AA11-6A016206691D',
                 '1C66BBAF-D953-47B1-AF10-6A01620697C5', 'B2121DD4-F708-42CD-A9BA-6A01620E831A',
                 'E5772A60-A9BC-46C6-A0F9-6A01621A173D', '53D904A0-46DD-49FC-96C4-6A01621DDCC9',
                 '71326070-8DA2-40C8-B73C-6A016228BB84', '95C4AE94-8860-4185-BF0C-6A01622C7DED',
                 'FB8AB103-17D2-4EF3-9EFF-6A01623E2132', '7638F91B-2155-4872-BE62-6A0162528BF5',
                 '9AF7C018-5114-4869-8C7A-6A016257C04D', 'F64936FB-E8C8-4E3D-A32C-6A01625D914D',
                 'C5FDA63F-EFB8-47FA-A8FC-6A0162679A7D', '31AA85F0-591A-43ED-BF56-6A0162699400',
                 '758CA8E2-1579-4961-B3D5-6A01626FF2B7', 'BDD043F7-1924-4595-A5AE-6A01627FD76E',
                 '38D48491-0003-4C6A-92D7-6A016281DA29', '64A9E77B-E399-49A5-9F92-6A0162829909',
                 '001B535F-9885-4EAA-B4E7-6A01628BF953', '7F436136-B3F2-4F88-9FA5-6A01628DE041',
                 'A9470AE7-F2BC-4619-990A-6A016290C1F1', '7C5FA098-72DA-486C-B293-6A0162910AD1',
                 '9BE9D70E-688C-4EE4-A690-6A01629D5C86', '19BB2222-0469-4AE4-8852-6A0162A56FAC',
                 '4035C43D-F687-4781-A4EF-6A0162A5897F', '9D0BCAB4-A112-43FB-B2A3-6A0162ABF7AF',
                 '195A5A0B-0FB4-4C2A-B0CE-6A0162C666E1', 'B54236FB-D403-43EB-ADD1-6A0162C66F46',
                 '7C7D9367-57DF-41BF-A99D-6A0162CBE83E', '45B30CB9-050A-47CD-A426-6A0162DADF51',
                 '9CB9322F-0457-467B-A4A9-6A0162DD48D1', '92BE0F3D-FFB4-4695-A3DB-6A0162EBA0EB',
                 'D03E3F64-4D98-482C-A42C-6A0162F35839', '57C2AE71-340F-4954-A336-6A016322E0B4',
                 '9D69EF05-AC5E-4606-BE80-6A01632DBCAF', 'AE931647-3E58-4A10-9681-6A01632F5431',
                 '52FB372D-5460-4E1D-AC28-6A016335C03B', '4486AEAB-BB64-4794-9873-6A01633BDA77',
                 '8B2F3B29-E874-43F6-B133-6A01634B6F7F', 'A4737586-121B-44B8-B0DE-6A01634FD2BA',
                 'A4010741-B2C7-4189-BEEC-6A0163513529', 'F0A664CB-6816-42D9-86A9-6A01635690E7',
                 'B199D1AF-F77B-489F-B6AA-6A01635D296A', '1A688099-D3C8-4BB9-B8F0-6A01636A1A31',
                 '98D1FF73-4A70-4E6C-A2FC-6A01636AE794', '5DD80C68-B6FD-4B17-9FF3-6A01636E71AA',
                 '43E39AF3-9430-4885-A8FC-6A016387F014', '2E15CBA1-BC92-4D53-B72E-6A01638F74A8',
                 '4287D0E8-7531-4C60-9ED2-6A0163A26E6B', '3A7AFCA6-7A31-4C8F-AADD-6A0163A5761B',
                 '771F0022-5488-424D-A29C-6A0163AF44A9', '65B65019-2108-4321-974E-6A0163C45C67',
                 'AC473730-2C60-49A7-8CBB-6A0163CD0ED3', 'EC178336-5C21-46F7-97B5-6A0163D327C7',
                 'D4C4BBFD-6D4B-4DA8-B881-6A0163DA8BBA', '52DD09CD-B5A8-420A-BD06-6A0163DDD0A2',
                 '84F6AA8F-E5DD-4419-AE37-6A0163EFFC26', 'D77BDF45-D328-412F-B609-6A0164274794',
                 'C6CE32B0-7AB1-41BB-8877-6A01643454B3', '17A6D807-5368-4914-A80D-6A016437E930',
                 'FBB2D203-6A43-4FFA-B11C-6A01644448BF', '6C7527AF-7FE3-4813-A17B-6A016444B28D',
                 'A13E0437-664F-4206-817A-6A0164469D8E', 'D012695A-B7EE-4EFC-81EA-6A0164569825',
                 'FEA81551-9A59-4B0C-B458-6A0164691ACD', 'D9FC85F1-48CA-4F25-91F2-6A01646E9099',
                 '3D9EBEC5-17C0-4C94-B9BB-6A01647048C4', '9B0B5926-9D5A-4C54-8376-6A0164773E54',
                 '231FAA1E-B9AA-4571-8F8D-6A0164A4B98B', 'B0C93B8D-1E92-46BC-A15F-6A0164A7E6ED',
                 '8015FA50-D9BB-4B25-9849-6A0164ABA90E', '81C50C29-3B0A-48D7-9EF6-6A0164AD881E',
                 'B4480F83-D40C-42E1-9035-6A0164C7E98F', 'B4882260-6F9E-436B-91DB-6A0164D226D8',
                 '3AFA9D2B-BF9E-4B37-90B0-6A0164E53C19', '8E13F767-73D7-4F1C-850D-6A0164EF760A',
                 '4E5A3C28-13C1-4167-8EB5-6A0164FA7FB0', 'A591ACF3-A395-4C4A-B2F8-6A0165068FA6',
                 '44DAF1F9-DE7C-43D7-BCBA-6A016521F83E', 'BE3FE2F5-CA8E-437A-AC13-6A01654C24B3',
                 '1BABFEA2-2E03-4EA5-ABF8-6A0165658B6B', 'DDCC258B-9BAB-4EFC-B989-6A01656CC99A',
                 '155E498E-EEE2-46C8-AABF-6A01657FA52F', 'A55F67DD-D011-4C3F-B2FF-6A016588A431',
                 '754DA97F-6439-4AA6-B495-6A01658FA50E', 'D272CF5F-B7AE-464A-A545-6A01659064EC',
                 '8A625C67-2250-4D7A-B119-6A0165A36077', '3B6E2239-0E7C-4F7D-A58C-6A0165BB684D',
                 'E815E08A-3BF9-4D73-B84D-6A0165BDBD34', '6BCE309E-9E5B-4F41-B094-6A0165BF831A',
                 '6B04E772-1F48-4E4A-BCC3-6A0165D5D064', '50F05CFB-9137-42F8-8CF3-6A0165E23EB6',
                 'CBEDEBFE-1211-4B8C-8A31-6A0165EBAA90', 'CA919430-233F-4060-8056-6A0165F772C2',
                 'D07A81A0-D9E9-4178-9EF4-6A01660A156A', 'DCDE4E88-DC7C-42B6-A0B3-6A01660C9B7A',
                 '686EE33E-EC61-4290-BF96-6A01660FA1E1', '24AA2CB4-82EA-4869-8C6B-6A016610054E',
                 'D50C122A-393E-4C36-B6AF-6A0166140128', 'CED0F560-62BE-4B9F-A065-6A0166141E1C',
                 'E8D33EAF-FB40-4CC7-9361-6A01661CFEB8', 'F7FFE29F-65D1-4167-BDEC-6A016623B6EF',
                 '8539F20A-923C-4654-B24B-6A01662522AA', 'CE39B47A-AD29-4B8F-BEFE-6A016630159A',
                 '56CD0F0D-2959-439D-AA06-6A0166382613', '6D777EEB-DA1E-45EE-99A7-6A0166382C30',
                 'C338C769-815D-45BB-BF73-6A016648D1F6', 'C2BA578B-DF7B-40D6-8A11-6A01664E7C5A',
                 '09286033-FF6F-4AEB-837F-6A01665894C0', 'BAA9D57D-946D-446C-9BBE-6A01665E5EF3',
                 'F291EE62-B4E8-440C-954B-6A016660BF33', '88434EE5-3E78-4EBB-BAE5-6A01667A2267',
                 '481A3A2C-CEED-4329-92FB-6A01667E19BE', 'C66CE85B-C594-44B4-BA2D-6A01668E16EF',
                 '94877484-5BCC-4771-BEB6-6A01668FA878', '605204E1-EF66-4CB1-9563-6A0166983548',
                 '38253C65-F6A0-4BC8-B865-6A0166AA5453', '54C78A4F-7957-470B-9D37-6A0166B0DA1A',
                 '5D6A387F-D26A-45A0-A8A1-6A0166BB5C83', '7AFF43D2-A32B-4C43-BA02-6A0166C02094',
                 'E0DB92F5-78B8-40A9-A7F5-6A0166C545A0', '62B5B987-459D-47DA-841A-6A0166CE512B',
                 '6DE634FA-B82A-491E-AB12-6A0166D29FED', 'E360D1E2-4C4F-48A3-A472-6A0166DE463A',
                 'AA3E3592-D6B1-4CB4-9001-6A0166E60494', '805E7702-791E-49A4-B721-6A0166F53133',
                 '0C3954B8-4767-443C-8627-6A0166FA7853', '94A3F071-5BDE-4020-AF57-6A0167014328',
                 '541C16B3-05BA-42EB-B1AE-6A016702C631', '2D4F8687-D2AB-4430-AC09-6A0167096115',
                 'E2F00A94-AA21-4C63-8B42-6A0167222679', 'E33DD796-05A9-4FBA-8D43-6A0167240128',
                 'AEE00E37-F92B-42C9-A107-6A0167284664', '5897153F-07F1-4703-AFE9-6A016748FAD6',
                 '45B668C3-86FB-4CB3-A7D6-6A01674DBE94', 'A535BF85-B233-454C-BF17-6A016752A8C4',
                 'A6984D28-616F-4FC0-95E1-6A01675AE9AC', 'B3F7F76D-ACE3-415E-88AA-6A01675E9CB7',
                 '28EA3198-B069-4C18-B6CC-6A01676721A4', 'A3E9A256-6E03-409C-BCA3-6A0167745C68',
                 'B0D2126B-93F0-4991-AB5E-6A01677CF706', '9EBBEFDA-B631-4815-A224-6A01677D5222',
                 '41890AB9-8933-43BA-8C53-6A0167848938', 'B5B713FF-25D3-457A-ADFA-6A01678D4C01',
                 '97B35C8B-6C09-4363-8249-6A01678DE2DF', 'DFC95289-2507-45B4-BA97-6A01678F0FA2',
                 'BE531586-B7CD-4F9D-8D27-6A0167972C80', 'B7D1BAF7-4764-46E0-BC42-6A0167C5C8A9',
                 '0C2A0BF2-1A1E-4A5A-A16D-6A0167D0AEC9', '35C42F30-3EB4-4316-97C0-6A0167DF7163',
                 '30AF1391-05FA-4C52-89AE-6A0167F90D92', '179EA6CD-0D40-4791-9544-6A0168180D59',
                 '3450E8F3-4E0C-4695-8906-6A01681DE080', '22B3A492-A0D1-4BA5-9B59-6A016825006B',
                 '2296743F-14AF-42DE-8183-6A016834BE4B', '31614C3A-91D2-4322-80AC-6A01683BC1D7',
                 '2E5C8D3E-B72E-487B-951C-6A01683C5018', '62C890DA-C54F-4506-A957-6A0168453BEC',
                 '2B8D002A-36C9-477A-AC78-6A01684791C0', '261AA6DE-007F-4E4B-8211-6A01685003DD',
                 '315DEAE5-12FE-4D20-BEC4-6A01685AD375', 'DFEFB250-B7B5-420C-8847-6A016869FBAB',
                 'B5AF95F3-C6D1-42FC-8C66-6A01686AF8B9', '92C43DD1-0E77-405E-B2A3-6A01687004A5',
                 '072563F8-1669-42EA-8B77-6A01687E7A53', 'CE1F3334-9CEA-45F5-B8D1-6A0168886789',
                 '0ADF0059-B73D-41A2-90D6-6A01689348AF', '5C4FC376-3213-4EE4-911C-6A01689A851B',
                 '1A7AEFEB-BD6F-48A6-B076-6A0168A5F7DF', '1931D20E-6013-495B-947B-6A0168A823AB',
                 'A640284D-7EFC-45A9-BFF0-6A0168B00E2E', '0957F8FE-F9A9-4FCE-8D59-6A0168B3B255',
                 '6BFBE771-DBFB-4895-A4CF-6A0168CBEB7D', 'E4C8090E-0616-4C11-AF88-6A0168D14A61',
                 '3D131CFC-C555-44B5-8AFF-6A0168E51B36', 'E4281F7F-3458-4A53-B222-6A0168E5E091',
                 'DEE2D6A1-BC41-478B-82DE-6A0168ED5B35', '5441BB75-1AC5-4A92-B759-6A01690286DA',
                 '39F09AA7-EDF5-4675-B044-6A01690C7FD7', 'A48E99DC-02B1-4B43-973E-6A01691DE101',
                 '0304B97E-57B5-44A3-8349-6A01692CA47F', '85476FC5-D0EF-4470-ADA9-6A0169342A44',
                 'D7FE3621-3C8F-44B8-B040-6A0169391C2D', '62C1C9FE-6AC8-4E9D-A4E4-6A016952AFCD',
                 '2B2A4625-E427-4A06-B8E8-6A0169538F20', '10129154-1443-4930-A4D8-6A01695F52CC',
                 '7ACD6ACA-B9CB-47EB-A945-6A01695F7C31', '268D769C-1CBA-480C-B86B-6A0169666B3A',
                 '5A76C59E-017B-4725-94AA-6A0169743E4D', 'E227D93B-5A9C-4509-9305-6A0169782486',
                 '05C1F6FC-CC28-41A7-B22A-6A016978FBC9', '7B979D94-41CB-490A-BFE4-6A016980702A',
                 'B8F911FC-14BB-4941-B183-6A0169957227', '32C77EBC-C620-4FF8-A259-6A01699EF427',
                 'B83BA8D9-5E3E-4B43-89EF-6A0169AA4CCC', '75A77850-8319-4569-9B39-6A0169BEA1FF',
                 '77786051-DBC0-4080-8742-6A0169C0415F', 'BF9D3B7C-EE6C-4E23-ACDF-6A0169CA9633',
                 '09219FB0-6784-415F-9144-6A0169DB37D9', '3725BDAA-A195-4FEA-9C69-6A0169E608AF',
                 '69BE9393-E016-4889-B08B-6A0169E629B3', '863193C8-1617-4ED9-99E8-6A0169EAE31C',
                 'B5240B2C-C815-4CAA-9673-6A0169F33CD6', '18018DDE-42FF-4D09-A884-6A0169FAA2C2',
                 '0C2F3B5D-1C19-4073-9F60-6A0169FAECC1', '0BF67F52-092A-428E-930E-6A0169FCDBE9',
                 '5B908C2B-BBB0-4029-AA63-6A016A03AEA8', '61381BF1-7CD3-4A50-AD65-6A016A059933',
                 '7B0A47D0-4325-4B0E-9EFD-6A016A29FCF1', '03059152-F565-424D-A657-6A016A2C9A5A',
                 '13855FB0-35BE-48B9-855B-6A016A323CBD', 'FED1DB67-4DF1-4D4C-A1DD-6A016A3FEC30',
                 'CC1DED19-17AA-44D6-94FE-6A016A5F699B', 'F36A4A4E-6325-4B45-B218-6A016A6D72E4',
                 'E5DCDD89-B0E0-4D23-9195-6A016A820973', '1C6F7E78-A280-403B-A6D0-6A016A9F363E',
                 'DF6541E1-B76F-4923-A979-6A016AA61E84', '24FCEABC-92FB-4371-B413-6A016AB27E89',
                 '9EE77871-F6F7-421C-8A45-6A016AB33D97', 'CA7889D7-5F3F-470E-9365-6A016AB53AF8',
                 'DE00DB6F-18A3-4446-9778-6A016AC7D0EB', '27D01A85-24CE-4FC8-841C-6A016ADDE5FF',
                 'DC876D20-146D-41C7-B6DE-6A016AE618E0', '11814964-A7B9-43A6-9AA0-6A016AEC63E9',
                 '4C7093A0-CBE5-4836-89E8-6A016AF2205B', 'E3A5B4C7-CFA8-40B1-8E91-6A016AF31381',
                 '38108828-8683-4AFD-944B-6A016B11C4C1', '8464EF0E-4CAA-4AD1-B934-6A016B2F5CDD',
                 'EFEAE8BF-9404-41C4-977B-6A016B3A7615', '4206E209-9F92-41DE-99A4-6A016B42E5AF',
                 '440B30AF-18AE-4957-8B2F-6A016B482967', '609AE61C-0D84-4473-86D0-6A016B491293',
                 'E064EC37-6350-4AD5-9290-6A016B49B730', 'EDA29517-2BD4-4150-B9F8-6A016B4E60B0',
                 '04A7EDB0-A8E0-44F2-9C07-6A016B50715C', 'D841E018-E269-43AF-931F-6A016B546485',
                 '102F1D36-4960-4382-9BD2-6A016B60C778', '628BC3FC-9102-4575-AF1F-6A016B687434',
                 '1C65EA77-D537-4C36-AED6-6A016B6F760D', 'EF1E6586-D4A7-492C-9FB8-6A016B91E870',
                 '86AE38DF-7DF3-4103-8EF9-6A016B935FE8', '92D21224-0426-45ED-834B-6A016BACC301',
                 '0450A649-EB50-4B1C-8345-6A016BB46F18', 'E86782F9-9469-4875-ABA9-6A016BBBDC18',
                 'A88A8F8C-4FC2-46A3-8BCD-6A016BC841B2', 'AACD1B8B-5831-4900-88B3-6A016BC8F550',
                 '38664F04-2B6B-4D9D-B1B7-6A016BE4D821', '1957DF6D-82BF-403F-BB7D-6A016BEB7448',
                 'BC56B633-B71A-474B-83B8-6A016BEE9902', '77F56927-C51D-43A5-9C69-6A016BFAE05B',
                 '4F8C1710-66E3-48CE-AF68-6A016BFEB9E6', '6A50D79D-40F4-4777-AB03-6A016C13D3D8',
                 '079D7696-A570-4C0E-BBE7-6A016C163145', '119B51C9-B22F-4C7A-AE6E-6A016C17CE09',
                 'C6D97F18-36CE-4141-B4DC-6A016C3413AC', '42AD842D-A682-4110-B879-6A016C35E3DC',
                 'E2C799AF-CAC8-49EE-8313-6A016C384DCC', 'ECE05812-F226-4DCC-B46F-6A016C39F7EE',
                 'CF7FF5AB-83BC-41B8-B4A1-6A016C3A9C05', '65E5BCCD-8FD0-46E0-910A-6A016C3D06C5',
                 '0A5FCBB4-B110-4013-8220-6A016C448D60', '5018CB31-CE9E-431C-A8E0-6A016C4B6B43',
                 '660A103C-148E-48AF-9AB9-6A016C54A730', '9566D2F8-9824-422C-8BA4-6A016C5B265E',
                 '74EC7257-069C-4C0D-B17A-6A016C683AE3', '978E5FAD-1DC4-4FDC-B270-6A016C83667B',
                 'ECE17615-D4B3-4AF6-A2E9-6A016C84B614', '78E3D384-2B3F-4F4B-B2BB-6A016C957E3E',
                 '29B10431-C016-4318-BC04-6A016C9C4283', 'C8358E98-CDCB-4570-A071-6A016CA13529',
                 '531CB71E-8C6E-475B-BA50-6A016CA74892', '33196BB9-83B0-48E4-BF99-6A016CA84272',
                 '831AA9F0-DA1B-4204-A18F-6A016CAC2E04', 'AE3161C9-E2FE-4EA4-B675-6A016CB246A1',
                 '8267B97E-617A-494C-B918-6A016CB39CA5', '44CC52BE-B4D7-4958-A2B9-6A016CB5CF16',
                 '4512E8AB-BEE8-4726-A689-6A016CB6EEA5', 'AEBEC680-BB5D-42A1-8EA2-6A016CBA8056',
                 'AF5D8433-3998-4688-9742-6A016CBB0217', 'A2863886-0C33-48E2-B0BD-6A016CC3A9D3',
                 '6048CA38-1F9B-49D2-9B48-6A016CCA2264', '955A6B3D-01C0-4E5F-B483-6A016CCD67C9',
                 '44D30AC3-2FD9-4B35-91D1-6A016CD2120A', '11A09325-F4B9-445F-8891-6A016CD81A8D',
                 '807C618A-E0D0-4615-B087-6A016CEC27C3', '2C873112-969A-4554-ABD8-6A016CF23726',
                 'CEC7B895-99BB-422E-AA7C-6A016CF5E25C', '3D54DB63-8B92-499C-8DB1-6A016D05FBDF',
                 '61833DCB-D32E-4AF7-9C61-6A016D0A097F', 'AA4306A9-CBE7-44CC-937D-6A016D0EE931',
                 'A274E967-75EC-4DF2-9F57-6A016D235CB8', '98EDAB5D-8D34-4E49-9D06-6A016D245BCE',
                 '00205745-5E8C-4521-9D4B-6A016D2A91D0', '7EF1E08D-A7EE-4B5D-B570-6A016D2C7665',
                 '9959A084-C363-4972-AAA3-6A016D315977', '22D2907B-82F3-42FD-9F19-6A016D39B1D4',
                 'E4A2D499-0E45-4A30-B0A9-6A016D40A7E4', '9FF78666-0CF9-442A-8782-6A016D4E4C9E',
                 'C36343C7-F325-4CE6-BA5D-6A016D5C143D', '7A378181-6388-4E98-8AAF-6A016D5DF7ED',
                 '02A4BAB0-140A-46F2-88A1-6A016D6D57F6', 'D372C1D9-5F77-4B55-AF50-6A016D7CB0B5',
                 '1AF9FE8E-1ABF-4849-AF87-6A016D8A237F', '759A77BA-80C6-4E6F-9C70-6A016DACC707',
                 'E75AE6CF-9A25-4054-BB3B-6A016DB5BDEE', '711778D5-4730-455C-9E62-6A016DB71E2B',
                 '41F08682-E21B-42A8-92EA-6A016DC3E664', '2FB92B73-1627-4BDD-9612-6A016DD20D8A',
                 '0BA535CE-6CAA-4E14-BD63-6A016DD6C484', 'F60A6E07-2240-488F-AC9D-6A016DDDD1E2',
                 'B5E4A913-4B9E-443A-9131-6A016DE24331', 'A06E7D28-54AE-49E3-A612-6A016DE59DAB',
                 '273A93AD-1FCB-4509-AE8B-6A016DEA1BA5', '5A2AB77B-5DEA-404C-A803-6A016DEF5CDC',
                 'FF2084D9-29FC-4C5E-A1CE-6A016DF49FEE', '6B77EFAA-029D-4363-B4FE-6A016DFF7982',
                 '0A994138-BCC2-451D-A1FF-6A016E133E2F', '29B1DCF7-559D-467D-AB31-6A016E3F2D5E',
                 '96FC2AC7-3E63-4FC5-AAC9-6A016E5B3CAF', 'B78A72A5-BE17-46D8-B049-6A016E6230B3',
                 '1C6E98F8-C7C7-4CFA-8990-6A016E6495F9', 'A11F0657-168E-4F4F-BF6A-6A016E663F39',
                 '25637C4F-D1F2-4CC4-9DBE-6A016E7A39E0', '9FF6A6F7-F846-481A-8D03-6A016E7F680F',
                 '3CD7FE63-C46C-450B-9C98-6A016E83003C', '305CE46C-1232-413A-96D6-6A016E84D0BD',
                 '86C4294B-2150-4E7C-9A95-6A016E987A83', '831E8D11-4C37-4808-BA0A-6A016E9EEA8D',
                 'B5756E06-4E0B-4DBA-B219-6A016EABFE92', '2F856CC2-CF4B-4A39-95CC-6A016EB0116F',
                 'E2B58790-304C-4457-980A-6A016EBD3F04', '1039AE02-258B-4D9A-AFEB-6A016ED3324F',
                 '40254B83-B130-4B2F-9215-6A016ED3DC15', '0CB98271-ACED-4CEE-A9FB-6A016EE2E09C',
                 'CA87809B-A84B-43FB-A827-6A016EE34B53', '9B6CCFCE-B30F-48BB-AB5F-6A016EEBE323',
                 'A8342E2F-95BF-4E27-BE1A-6A016EED2A3F', 'EFE1C0B7-7B4D-4471-9E51-6A016EF11BEB',
                 '9D7A4C67-DCE9-4615-9F43-6A016EFDC08B', 'B30C4017-06DE-46AB-8AB6-6A016F0A0EEB',
                 'A33A0253-6852-455A-B8A7-6A016F0DB5CB', 'E526EF69-CE3D-423C-B748-6A016F1FE1B5',
                 '79954F58-F330-497B-A568-6A016F238243', '53017B50-AB8C-4C66-ABBA-6A016F48ECE8',
                 '067B741A-F26C-42CE-A53D-6A016F49CC50', '4DEF8BF4-E134-4C4F-B0DF-6A016F4FDC94',
                 'EA99C1B2-05EF-4BDB-B992-6A016F589559', 'D5A0134A-18DA-451B-B81A-6A016F62974A',
                 '161999CF-A724-49A3-AD16-6A016F67C495', 'CB1447CD-A8F1-4914-BC3C-6A016F6991E3',
                 '25D032D0-F5B4-4D2C-AEEE-6A016F6B0BC6', 'E925F18D-EAB7-4763-AE6D-6A016F86965D',
                 '5830D5DB-BBF8-48BC-B6CE-6A016F977D99', 'CF32E377-4AC7-416C-BAC7-6A016F9D9447',
                 '12D7F027-DB7B-4E10-B9AA-6A016FA69C16', 'CFBB5260-D3EE-496E-9352-6A016FA7E99F',
                 '53D93FBF-9F50-4F45-B3F1-6A016FA845FE', '670EE3EE-9E6F-49F0-86CC-6A016FACA1EC',
                 'D8C9E2D3-DA05-4400-B050-6A016FB1F02A', 'E6CA9348-8E51-421E-88B7-6A016FC91A5F',
                 '2817454F-5041-4480-95DC-6A016FCA9B40', '48B5F1E6-FF2C-45FA-89DD-6A016FD4CDFA',
                 '407DAC7A-3AFF-4834-ACA6-6A016FDCB959', 'B56BB73B-3C72-48D5-82D4-6A0170056F23',
                 'CE3E1D54-F27C-45C9-9295-6A0170194AB1', 'FFC36CAE-362E-4632-B53C-6A01701FE440',
                 '3C1F8297-FC07-4094-9F9B-6A01702591AE', '4C16093C-CB48-4419-9ABF-6A0170273544',
                 'D598D44F-C237-4DD6-A92E-6A017033955A', '857E37BE-C7C0-4C15-9361-6A01703B6097',
                 'CF5FFC31-8B71-4F11-BC1E-6A017040D3B1', '956F4108-332A-4095-BD0B-6A017056CCDA',
                 '75BE9A58-5096-4447-A7BA-6A01705B7B6F', '0EA7B9C6-88C6-4EB6-BB79-6A01705C5A92',
                 '6446A58D-4162-4234-B627-6A01707C3A44', 'F82601E8-C6B8-4183-B949-6A01707F1074',
                 '086CCCDA-832E-4647-9F0E-6A017085BF41', '753AB143-7A1E-4EDD-A484-6A017093C373',
                 '31E8F00C-085B-4B96-A976-6A0170958DF6', '6E4F1071-7AA6-4A41-ABC3-6A01709624E9',
                 '1EF02A4C-0856-4C5A-AEBA-6A0170ADDEF6', 'E9639DCF-DDA6-489E-9457-6A0170B103AB',
                 'F700490C-43AC-40AE-8A45-6A0170C5E159', 'B8DDE6CD-E744-4B34-B978-6A01885790AB',
                 'DAD66E27-BC0E-4587-A971-6A01886E3E15', '242B058D-796B-4642-AE06-6A01887A92D7',
                 'FE2732E4-E2F9-4A8A-9D57-6A018888FEED', '994AE910-8AB3-48F0-9D6B-6A018899CE14',
                 '8DAA3CDE-DB8C-44AA-87AC-6A0188A57C4E', 'BE274755-75DB-4035-BC97-6A0188AED571',
                 'AEB472D8-7638-4CD4-A81F-6A0188B9B48B', '55AD7CB2-A6BC-4429-8185-6A0188C031E5',
                 '2E1D0672-C302-4870-8B73-6A0188C5444A', '0D6FBF8C-2611-4CD5-943A-6A0188CF2CEB',
                 '0B4F605D-13E0-4B69-9C2A-6A0188D1EA8D', '569CD524-3277-4B5A-8313-6A0188D28CC4',
                 'A73EFF29-0197-4888-B398-6A0188D484DE', 'D6C6C884-3F7C-4A17-AE9C-6A0188D7F581',
                 '79E30D27-9069-482C-A55D-6A0188DCB53F', '4DB0D3FD-C64C-4D9D-80EA-6A01890BD87E',
                 '6C448639-EB9B-4B3A-9932-6A0189140152', '70A609E2-9419-4C2D-998E-6A0189226F59',
                 '86D187F5-0665-4374-83DB-6A018925DD16', '0F7582AC-1159-459D-95DC-6A01892A7404',
                 '1690BCA8-1D98-439F-AD43-6A01893DE1D1', 'D5E0EFEB-D8E7-4B35-88F9-6A01893E90A8',
                 '0718113D-CC96-47D6-BBAE-6A01893F7BC7', 'DCE3FBE4-45FB-4297-9500-6A018946C5D6',
                 '1BB0CDE3-07C8-4D2F-88B4-6A01894DDE1E', '5B77B895-1606-4725-B2E8-6A0189524433',
                 '453A91B2-B0B2-4D2E-B694-6A01895B4472', 'DEA10FF0-0364-4971-876A-6A0189629876',
                 '81D9BB72-E798-41AA-ACDC-6A01897DBB9C', '19A1335E-D416-4104-A89C-6A018981F6AE',
                 'B4F74339-5042-4261-A406-6A0189826F23', '5D7805C5-34B7-40EA-9F0F-6A018982EC75',
                 '8130253C-4A7A-4315-99C6-6A018984311D', 'CA84A4D9-DEE3-428B-B369-6A0189901AA3',
                 '2A7AAD99-B9A2-4CC0-A892-6A01899A8F32', '7B335502-B67E-4703-B2DE-6A01899F73F2',
                 'D84D58CC-C0A7-4298-83F2-6A0189A0C8F9', '3ACCD070-4AE4-46A7-84D8-6A0189A9FC37',
                 '6F5DEF9D-B4FF-45BA-892E-6A0189ADA897', '80E11884-9982-4462-A80E-6A0189C2B557',
                 'B088C559-5C4C-4406-8866-6A0189D3B441', '79179285-5118-490C-B154-6A0189D764FC',
                 '0EEFD5D7-7107-4A40-ACD6-6A0189F19C87', 'DE7534BB-DD0A-4D64-9C97-6A0189F1F43F',
                 '5CB80721-93C5-471A-8285-6A018A030C75', 'EB2ACB5F-E277-48DD-94AC-6A018A045AD7',
                 '2F2340DC-DB9E-4A13-9F45-6A018A089923', 'CE4A334D-144A-4F13-9320-6A018A2457A9',
                 '3B540436-0B68-4005-9D6B-6A018A4C11E1', 'F650D108-483B-46A9-A32E-6A018A6466DF',
                 'C989C629-6D8C-4E5C-BEED-6A018A6A8F45', 'DC075A19-D04C-43DD-834D-6A018A6CB0BA',
                 '2058C33E-6BC9-46B1-B599-6A018A6FD6C7', '215417DF-79BD-44C8-8F97-6A018A7B0EED',
                 'BE8C38B5-9FFE-46A3-B769-6A018A7C6868', 'D1DF03D4-CEFB-4B71-8300-6A018A7FEB88',
                 '0FC89A72-173D-4F02-9456-6A018A972418', 'B18B7937-27E6-46CD-95B2-6A018A9E527F',
                 '93C6897B-479C-4FB0-8105-6A018AA4E67B', '633AB37F-2B58-4490-ACE5-6A018ABDE6F0',
                 '56CCC352-A54B-409A-BF40-6A018AC69CC8', 'D6AD4EE5-63AC-46EF-A99A-6A018AEBC710',
                 'DF40F662-A750-4EE3-897E-6A018AFA918F', 'DCB07CB0-2356-4731-B7C3-6A018B0C20F1',
                 'D4E7DD56-2B8A-4293-A148-6A018B0DE01E', 'D9CEC90E-8F45-4125-A766-6A018B0F6B28',
                 '62A08D0A-1753-43C0-BB90-6A018B0F94D1', 'D831475A-82BD-45C3-A431-6A018B14AE34',
                 'BFFE2DD8-18A3-4C44-A16E-6A018B42BBC6', 'C0668D4D-7540-4015-8300-6A018B43CA26',
                 '8B12C62E-F8F4-4E42-957C-6A018B56A2FC', 'F2304FF1-C723-4D55-B7CD-6A018B6BDAF4',
                 'AEAB4072-4516-4E7C-9F48-6A018B7C2892', '8745E299-F527-4E1A-BC3C-6A018B86117D',
                 'E1ADDB86-1153-498E-AB2F-6A018B8A79FE', '0A74F52D-49A9-47A4-A94E-6A018B985A9F',
                 '24FD0784-B7AF-4731-ABF0-6A018BA6C31D', '6428B076-F167-4E3A-96A8-6A018BB629F7',
                 '546185D7-8EC0-43B2-8928-6A018BBB45A3', '800A272B-0C23-446C-9EF6-6A018BBEE13B',
                 '8EA5CEF4-9B6B-43DF-A372-6A018BC72BDA', 'D4A5119B-44F3-4AF6-88ED-6A018BD4AB7C',
                 '0ADD6613-6F1E-40DB-B1EA-6A018BE22560', '0C0E615D-2D87-48E2-9B02-6A018BF89C34',
                 '216298F9-DB2D-445A-B903-6A018BF89C68', '650D0D1D-D3A1-4670-8B34-6A018C1261D1',
                 '6E559FEA-FE63-482B-91C3-6A018C19AAA7', 'CA9BA319-DFAB-445B-A2FF-6A018C2071C3',
                 '25D171FE-98CB-4A26-B486-6A018C21FCFB', '164406B6-0E05-4600-826A-6A018C2246FB',
                 '4EF81D40-D449-4BE5-B8F2-6A018C277F1E', '533BC6CA-1051-4F87-89AD-6A018C279D0C',
                 'DF59E788-176C-48BB-A46B-6A018C39DD19', '96B785FC-DEAC-4CF1-915D-6A018C57C686',
                 '7A2FF5EC-4D73-4EF0-A02A-6A018C695DAB', '5C2E4438-8467-4E7A-92C5-6A018C796124',
                 '57A45E48-5E3F-4AA1-9FDB-6A018C7A1F9A', 'F6BFC7AB-D1FB-40E4-9D11-6A018C7ECAD0',
                 '0DC772BF-81FD-470D-81D5-6A018C8355A2', '294CFE20-55E1-4FDF-B5D5-6A018C902AD3',
                 '17CBC146-5057-47C7-A052-6A018CA1FA38', '4209C430-CB89-4E63-A0A1-6A018CA875AB',
                 'AB68359B-A476-4206-8F78-6A018CAE967E', '62C7A8A3-D619-46D7-A777-6A018D01A42F',
                 '12BFE320-8C9E-42ED-B62D-6A018D05E706', 'B153D61D-22C7-4C9B-8011-6A018D14DD99',
                 'E819B6D6-3375-41B3-86D1-6A018D3E773E', 'B27AF85C-7C1A-412F-A3D5-6A018D51BAE4',
                 'A3CE1B43-4AB9-496B-8975-6A018D5AFC5A', '927D75D5-3DF0-45E4-ACF7-6A018D61EED7',
                 'B8683F3D-F7FD-497C-A4C8-6A018D70C7E4', 'AA14A9AD-F6DB-4530-AB8C-6A018D71D2BF',
                 '2547751E-E818-4E04-BE9F-6A018D743208', '09723921-7E7A-469A-86A2-6A018D815288',
                 'BF4A884A-8A1B-4760-AB42-6A018D837E05', 'DEEF9AA5-676A-4240-947C-6A018DB44856',
                 '1885AF9C-B3F7-4047-9F62-6A018DCED009', '7461E6A0-31CC-45E6-86E2-6A018DDE0A70',
                 '5E716BA2-5407-4BBD-B7E9-6A018DDFA5BC', '83FB8A90-2BD6-4C2C-B74A-6A018DF2BF95',
                 'FCDC0890-5039-467A-B1C5-6A018E00CDC1', 'D51CD808-C049-4FCD-B0C0-6A018E0A1931',
                 '66635BA6-133F-4149-9081-6A018E10839F', '4766E7D0-A9D3-470E-A195-6A018E143597',
                 '6388853E-847E-4868-B457-6A018E1BCBF3', 'E3F0D137-3621-4151-99C6-6A018E1D72AF',
                 'F9378061-8F7B-4DE4-A469-6A018E2403A1', 'B405A215-3F2E-49F9-A227-6A018E25EEC4',
                 '7EE76169-816A-4C25-BE82-6A018E2BEBBF', '82C2A8D7-A501-445D-AD96-6A018E300A43',
                 '96BED49E-9C30-421F-A652-6A018E3CC0EA', 'FA66283A-3F29-4576-814F-6A018E4623D4',
                 'D75644FE-270E-435B-99BD-6A018E47ABE7', '376420B3-B0F7-45FC-9841-6A018E5F513E',
                 'CD3C6AC8-2EDD-44E7-9E4A-6A018E62A3C6', 'F3361697-E01A-42A4-9F30-6A018E6F3949',
                 '87BEBCE0-661C-428F-BDD6-6A018E705B56', '6AA717C9-9363-4962-AB16-6A018E70C12E',
                 'BD715704-C0C9-4701-9AD5-6A018E74E9B7', '654AC4CC-D5D9-42EF-AB63-6A018E895A0C',
                 'F26E2DC5-D229-4F59-B1A9-6A018E9E0980', '78A729C0-1C70-4AC7-84F8-6A018EBE8AAC',
                 '105AD4B9-D993-40A1-9259-6A018EC68999', 'E2DAC343-2F8D-454C-B956-6A018ECA4EDA',
                 '7CAA5B64-7ABA-43AF-8C44-6A018ECDEB82', 'DB17D34E-1CD9-4CA9-8BA0-6A018ED2C87B',
                 '5332E220-E92E-4DB5-8DE0-6A018EDD80BD', 'ED7BE2FF-DEA9-4A42-9DB7-6A018EE0869E',
                 '7363D3CC-A6AD-4434-AD12-6A018EF0D368', '5F3674A6-7D38-4AB6-8120-6A018F0AB307',
                 '25A68E2D-C6EE-407C-BA29-6A018F153F10', 'D18CD05B-BF08-4954-8F41-6A018F191061',
                 'EE9718F3-2271-4F6D-BE14-6A018F1928A9', 'F9E16ED9-F1B5-44A7-9FC0-6A018F30B27D',
                 'EAEB7AF6-FC88-4B62-8427-6A018F46774F', 'EF1760D2-6B00-4683-88FD-6A018F469FAA',
                 '7773EC0D-B128-4A00-B849-6A018F471B93', '2B58D3DE-44ED-40A5-A306-6A018F578005',
                 '26AB51D8-FBA4-4D5D-8290-6A018F7084F9', '691037A1-B0B8-4091-BAA0-6A018F730EDA',
                 'C505B047-70B4-41F7-BF96-6A018F8EC0F5', '716E7B54-435E-4B61-894E-6A018F91E73D',
                 'C0ADCBEE-2947-422F-88EA-6A018F94556E', '40F82FCF-699F-452D-B9D9-6A018F94AEEE',
                 '0721B149-E92F-4CAA-AF00-6A018F9D1C7E', 'F78A4026-CF48-479A-AF2F-6A018FAD4EDF',
                 '652AC782-7F93-4319-8100-6A018FB9405E', 'DA405C01-3A5C-4818-8FAB-6A018FD8A62A',
                 'B0B3C856-CE4D-4D31-B7A9-6A018FDA7686', '3144E27A-D56F-4F41-805C-6A018FF72396',
                 'BD48933B-A3DF-436E-97D8-6A01900EB407', '1341BFB0-21F9-4F3C-90ED-6A019017A84F',
                 '78661C20-104D-438C-930C-6A01901D3F0F', 'C08D87D6-C39F-47F4-98B8-6A0190316CC1',
                 'CD559448-1638-4F72-A8AE-6A019040583C', '0B1BE939-569C-46B8-BBB1-6A019041B632',
                 'B7F9AF68-120C-45BC-B0F9-6A01905C675D', '711E881E-8AA5-459F-95DF-6A01905F9646',
                 '36733324-36C9-41AB-A343-6A019070F044', 'E67B82E0-F8EA-4B3B-9B5E-6A01907894FE',
                 'A1C6D931-3F8C-4AF7-801C-6A01907AB63E', '6AA2E502-65DA-49B3-A8F4-6A0190817289',
                 'C36CA045-F12A-429E-9AC8-6A01908E71CD', '8A0AE1E1-9D22-4206-BD4B-6A019091F9FF',
                 '21A6376A-3FB9-45DA-AC41-6A0190956D4C', '70682705-7239-4638-9D58-6A01A689AEA1',
                 'D9AE4E93-D91C-4F8C-80FB-6A01A68BC28F', '0118D70C-DCDE-464A-B7E2-6A01A6904D65',
                 '9205FD3F-5DD7-4F45-86C4-6A01A6935073', 'CFD26CBC-D6BD-45EB-B71D-6A01A6961A1C',
                 '2BC0C903-6475-4998-A513-6A01A69A9B6C', '0737AF2B-CD24-4A37-BC1C-6A01A69D2DE0',
                 'C86F2A0F-53A8-4059-BE08-6A01A6A35CBF', 'A760F46B-82AA-4D9C-9706-6A01A6AB7032',
                 'F1245E68-281A-465F-9924-6A01A6B52D01', '17A45787-2EA8-4C2B-BB44-6A01A6BDA4CB',
                 '4062ABF6-EE3E-4E7F-A7D3-6A01A6C35993', '0B32084F-3B05-47E4-83CD-6A01A6D6CF74',
                 'E8BA56A9-7868-4571-9767-6A01A6D84525', '5C768456-C922-4FCF-8196-6A01A6DB78BC',
                 'F8CF207F-63DB-4CAF-835B-6A01A6DFE99A', 'DAD66CCE-AA57-4290-9066-6A01A6E8FEDD',
                 'D5A0B4A0-35D2-4F9F-9218-6A01A6EE4A35', '4C6634EC-79D6-49DC-AF5B-6A01A706F342',
                 '8333E61B-F056-40AE-BB42-6A01A709DE27', 'C4B616A8-A4CF-4CEC-B5EA-6A01A7127A19',
                 '60954225-56C3-493D-A9EE-6A01A7133F55', '5D14810E-B2C2-4C33-92B7-6A01A71FFAC4',
                 '00E978F3-F296-4E69-B0E7-6A01A726971F', 'AA56B752-4930-4922-8A02-6A01A7286EE9',
                 'F3F2D68B-FB2C-45E5-936F-6A01A730A321', '261C8FF0-4AA1-4DEE-9CF4-6A01A73F35F9',
                 '97508081-68EB-4F76-AF7C-6A01A746134D', 'B815A642-E06E-49E1-A9BA-6A01A74866BC',
                 '158BFF6F-9D6B-4B44-B2D4-6A01A7615168', 'E0C2488B-7559-4894-8A12-6A01A7710BA0',
                 '85404E6A-D362-46A7-85FB-6A01A78517A6', 'FC64C8C3-A706-4463-9B66-6A01A78722C9',
                 '71EF8A92-CFEC-4CCB-89A0-6A01A79D38EB', '82E224EC-DF7A-415C-940A-6A01A79FAB09',
                 '338626B9-223E-41F4-8B16-6A01A7A05346', '7DFB2F4A-F791-4982-926F-6A01A7AAC3E7',
                 '81B9A278-91A6-4793-A325-6A01A7ADFF0F', 'A27BF909-97F7-48B0-9CDB-6A01A7CA4C83',
                 '6822BE70-9CBD-4B7E-ABFF-6A01A7D88358', '02091FEB-464D-4259-86D7-6A01A7E01ABC',
                 '00E8F460-60F5-4F70-9770-6A01A7E1D8E9', 'C28F0E52-52D1-4372-B389-6A01A7EF6961',
                 '11070EE7-6FD5-48E1-A13A-6A01A7FA0536', '84C3A9DC-C17C-4444-88F4-6A01A7FA680B',
                 'B4603648-C2EC-4B7A-8726-6A01A801879A', 'B988251F-A77D-435E-8A03-6A01A8018841',
                 'A8DB73A2-8430-423D-97B4-6A01A8174EA8', '8D07DD9C-314C-4E04-BCE0-6A01A81FA20A',
                 '41AD9443-DE14-4092-BD2C-6A01A835FC5F', '2417ADB6-6078-4645-BFFB-6A01A840C596',
                 '403F7FCD-B024-458A-A73B-6A01A8510D81', '59A4E624-F323-41DB-A4AE-6A01A858FCDA',
                 '2D46417E-158A-4505-BD33-6A01A875FFD2', '5EE0AA5D-E146-420E-B959-6A01A8765830',
                 '8E0F345A-444C-41B0-AADD-6A01A8778D8C', '6123008B-D108-42E9-BBC9-6A01A878ED99',
                 '0BD91443-2D44-4F6E-8309-6A01A87A6742', '05F9FADE-F2A4-403A-A064-6A01A87D20DD',
                 'E5DAC184-9A88-4EA1-BB8D-6A01A87D4A3F', 'C2B5EE07-4899-4F67-9CCB-6A01A88AD346',
                 '7B6213B0-6832-4976-ABAF-6A01A890C89E', '4ED88994-2808-4669-9E72-6A01A8C4EA14',
                 '6D6B960A-1EF4-4FC5-9B8A-6A01A8CF608D', '616D6473-12EF-47C1-8367-6A01A8D72DD6',
                 '42B157DB-F5B4-4B5C-A87C-6A01A8D91F7A', '59315192-A1DE-4277-B121-6A01A8DFCFF3',
                 '37F2CFA1-2C49-41CB-B7DF-6A01A8E13280', 'FD3FDDFF-35B6-4AA4-A041-6A01A8E4C92D',
                 '1DE6E7BA-2D30-4E8A-850C-6A01A8EFCA11', '24EF83E3-44EF-43A2-8D2A-6A01A8F4C317',
                 '284E9D79-9336-4CEC-ADA4-6A01A8F78BBC', 'F28DA091-EA1D-4C3C-9328-6A01A905AB2E',
                 '413F6966-98BD-458C-AC6E-6A01A906C76B', '55029256-4975-4936-AC8A-6A01A90B37A5',
                 'E1DEACEF-C674-4DB5-831D-6A01A92BFD9E', 'DD5D5536-0DCE-4278-B44B-6A01A937ABAE',
                 '69E3B749-A653-4525-BED1-6A01A93A336D', '708709F3-F09B-4065-92CA-6A01A95472AB',
                 'B5B4AAB8-4C53-4F80-93A4-6A01A95519E0', '782BE614-2831-46BF-AA2D-6A01A9556B79',
                 '9F0D5FD5-2B38-4874-89DC-6A01A955CFB6', '8D0DBC13-8FDD-412E-92BE-6A01A96E1392',
                 'ECCE3E0C-485D-40F8-9911-6A01A9700B7B', '1C267753-DAAC-48AE-9B95-6A01A986EB81',
                 'A0B55BDA-6DFA-40C6-8EE1-6A01A9B0600F', 'B655B4EE-65FB-4264-9A91-6A01A9B1B77D',
                 '38B02D4D-4C9D-49F5-B5FD-6A01A9BB0821', '9F75459A-5DD5-44FA-B335-6A01A9C6CA56',
                 '1677E8D5-60AA-4EBC-AF80-6A01A9D257D6', '30F43A69-A241-4F1C-A2AB-6A01A9EF413D',
                 'C3C9D852-D4A1-4FB2-B6A3-6A01A9F2542D', 'B92F0221-3BC3-4C1E-98BA-6A01A9F44E57',
                 '041F4D7E-5B50-4340-B4FD-6A01A9F46B3F', '6A4908D4-6F49-4148-8C46-6A01A9F816DC',
                 '47BA432D-6428-404A-8EFF-6A01AA034A52', '39C78ED2-B0AC-45E3-B616-6A01AA172007',
                 'B5AAA6E7-0CEE-4601-92CD-6A01AA22D519', '6F793DCD-A657-41DA-8FF7-6A01AA279312',
                 '6F1D4DFE-D66A-4E70-9C66-6A01AA27BFFC', '217F39B7-264E-44C3-8865-6A01AA306A8A',
                 '284E294B-32B8-4D37-8550-6A01AA332913', '50F17CB3-33ED-49E4-A7BC-6A01AA4E0D9F',
                 '22941E22-8930-4B7E-A812-6A01AA68FFFB', '29A00656-5AF3-4150-87A5-6A01AA721BD4',
                 'F4C0C75E-BDFC-451F-8035-6A01AA7B79CE', '996941E6-8577-43D2-B4C1-6A01AA8243FF',
                 '2AEDA65A-6A4C-4442-BFC8-6A01AA85A384', 'C00FF2F6-944C-485F-A7AF-6A01AA9C3EE3',
                 '3054D3D8-7158-46CF-B6D8-6A01AA9E04DF', 'BC5359CD-A6D9-4BF6-9F8D-6A01AAA22CBE',
                 '4EDEA7CE-AAE2-49FF-9302-6A01AAA84547', '58229AF5-38B3-4323-B717-6A01AABB03E1',
                 '1FC22237-7233-4CFC-A4FE-6A01AAC14FB3', '01C903BB-39BB-4E98-9628-6A01AACAD886',
                 '29CB7ACB-2F30-4595-9F04-6A01AAD0B568', '0EB77F2F-D3E0-4D4C-A53F-6A01AAD8C20E',
                 '404FF0AC-BF89-4CEE-ACB5-6A01AAE4F490', '7F2D6973-91AA-4FA9-BEFB-6A01AAF37200',
                 'BFB8AA47-E297-40B5-982B-6A01AAFBAC64', 'DD31CB1A-B60E-498A-870A-6A01AB090AED',
                 '8CDE3930-F2B9-4FC0-ACE8-6A01AB11447B', '265ADBEB-CB64-43CB-8ADC-6A01AB11757D',
                 'D23F20FE-2EE9-40A5-8362-6A01AB14025E', '9DB8DBDE-C3DD-4E82-A597-6A01AB14E5F4',
                 '48D7F7C7-D4F5-44C3-9C67-6A01AB1544AC', '5EA6359A-DC71-413D-90BD-6A01AB30DB13',
                 'C5FB158C-9E7A-4727-AAE7-6A01AB31FD25', '8B043190-FB6E-4168-9E96-6A01AB4CF574',
                 '44CD7004-231A-4FB5-93A7-6A01AB4E4E85', 'E631C7B0-17D5-4153-BD8F-6A01AB6DF7E3',
                 '6BB321A7-3E73-48B8-AFCB-6A01AB7E5704', '796ADCAC-F4E8-4B17-9B99-6A01AB972EFA',
                 '641C3D93-3415-4767-B2E8-6A01AB98FA52', '391D61D2-3CBB-4ECC-AE63-6A01AB9C938B',
                 '472A732F-BC17-4491-BD93-6A01ABB145AC', 'D389CBBC-8F63-468D-A5D4-6A01ABB15EEC',
                 '72C170B8-8BA5-4F34-A1A6-6A01ABB1C36B', 'FBB1BCC9-2D04-4936-92F4-6A01ABB5468F',
                 'CCE44962-4860-4C51-B299-6A01ABBA6FC4', '0E8EF4B9-EDB8-4E44-9E25-6A01ABC92355',
                 'F0F47FCF-9044-41DC-B174-6A01ABDF4366', '222610B3-6500-42C7-A6A6-6A01ABEC08E7',
                 '41F2969E-B81A-453E-8A8F-6A01ABF1A09C', '1315CC32-A59F-4DC5-8AC7-6A01AC0151D1',
                 '5CBB44FF-666F-42AF-A8F1-6A01AC0F2801', '1E80B38C-7F3F-4C62-8E32-6A01AC1AB541',
                 '24921135-AE8F-4B3F-BF46-6A01AC1EC7BF', '4EFDE2D7-23D7-451B-A1EF-6A01AC2E01C0',
                 '1571F328-2292-468E-9288-6A01AC35E981', 'FA2D45D9-8AD9-43C2-A9D9-6A01AC3D16E2',
                 'AB6ABFD1-4980-4511-A297-6A01AC3D7E3F', 'F47E9BA8-8D59-42CA-B19D-6A01AC415881',
                 'EEAA686B-6833-4CF1-AD35-6A01AC427053', '7EE3C1AE-70D5-400A-947E-6A01AC4C476A',
                 '5CAA70EA-BF3B-499C-ADD8-6A01AC530F5E', '35FDEACC-C908-4D60-9733-6A01AC538888',
                 'CD97A491-4DFF-42A6-B8B5-6A01AC548C80', '48C551FB-70EE-41BF-AA96-6A01AC57EDE7',
                 '25C42426-6EAF-4841-A3AB-6A01AC596973', '08016C58-F03C-4319-BE17-6A01AC5E69DB',
                 'BAD70779-48D3-4CEC-85B2-6A01AC5FEB48', 'C0386EBE-CDA1-4BD8-9594-6A01AC6A5337',
                 '5C582F3B-3A9D-4F25-82B3-6A01AC6CA431', '96D3D4B9-1520-4877-8B6C-6A01AC6D6902',
                 '46EAC702-C91D-4060-9FB5-6A01AC80C87A', 'E2B4E291-F2F3-4A56-AE17-6A01AC928332',
                 '119AA7DD-F9AB-40DA-8402-6A01ACA028AD', 'CC68B6A6-72BC-4662-9CA2-6A01ACB0E589',
                 '4EA84015-EE4A-4CE9-8068-6A01ACB8E2B6', '403110ED-5F6F-4E1E-866C-6A01ACC226CB',
                 '1F285373-875E-427C-9C8F-6A01ACC40B97', '526AFD16-AFCF-4BA0-A730-6A01ACC4BE14',
                 'A2B3035F-7729-48D4-A1B8-6A01ACCC4892', '59822BB9-2208-470B-9D00-6A01ACD1B991',
                 '81A30F07-313A-4316-98DE-6A01ACD687ED', '57340AAB-893A-4E9B-B840-6A01ACD84223',
                 '089684C2-B862-401E-8ED4-6A01ACE39D7B', 'AA32219A-1F1C-4F05-81D8-6A01ACE766BA',
                 '18583EE7-4675-4710-8F15-6A01ACEB2D48', 'AF9A8C5F-0D68-4268-9D30-6A01ACF3E9EA',
                 'A292E8E1-1B86-4725-8A8B-6A01AD034AC4', 'E18FC3B6-C0D2-470E-9EA9-6A01AD06500E',
                 '30BD3346-E027-4E51-AA21-6A01AD0D8813', 'A6F2FBD3-26B9-410D-88AA-6A01AD14311D',
                 'FDA9EB33-A3DE-4CB8-97D1-6A01AD19A220', 'D47FF22F-698B-4FBC-A613-6A01AD21DF25',
                 '3D06829C-C848-42B2-A870-6A01AD47E6B4', '8B645482-431D-4B69-94F9-6A01AD539FA3',
                 'E9AC3CD7-5EE6-4966-9C70-6A01AD558FC6', '233E0969-B184-4B87-8206-6A01AD59ECF6',
                 'DE10BFF3-ED05-41C9-96BD-6A01AD62E9EE', '83555531-486A-4825-A84E-6A01AD685EF5',
                 'ADADE5B7-0D29-4F46-853B-6A01AD7531F3', 'BDE08FF8-6D19-4660-8281-6A01AD837A20',
                 '27652867-41A9-4307-A2E1-6A01AD8E3508', '55A94B06-93A3-4DDC-A562-6A01AD94E5AB',
                 '81C01D78-1107-423C-9E00-6A032172812A', '016F616D-B3E8-4298-937F-6A03217309EA',
                 'A9339371-0809-4E69-BCB5-6A03217439DE', '84D050F7-B110-4324-BE70-6A03217CBBB0',
                 '0D1CC037-31B8-4BFE-AC8B-6A03217E6E2A', 'B190E307-D001-4E53-B85A-6A032188715C',
                 '59668316-0E76-415C-9E81-6A03218E8149', '2D728EC0-12D3-4899-9C07-6A0321994DD2',
                 '60072E4A-2CB9-4503-A304-6A0321BB8BF8', 'CB044293-F059-41A5-9156-6A0321BBF19C',
                 'CFBE5FFF-424D-4019-A016-6A0321BD612B', '93D4879E-968E-4223-A92E-6A0321C443F9',
                 '0CA40AC1-2916-4F9C-AFB0-6A0321C9DE93', 'ABFBB773-828B-450C-A2C8-6A0321CC299A',
                 'D87AA003-3A30-4ABB-9C80-6A0321D3544D', '67B513A2-3C1C-479E-B2DA-6A0321D9D636',
                 '51964C87-77A7-46A3-A8FA-6A0321E21878', 'AB78E6E1-3651-426F-9FF8-6A0321EDD911',
                 '1A771204-5089-46AD-886F-6A0321F9C702', 'E93EBAFB-D501-4821-98B3-6A03221468D9',
                 '66B6D5E1-8CA5-4EB8-8578-6A03221F9096', 'F6FF23CF-3A9E-4238-BD02-6A03222D9D51',
                 'E8F0BA27-4D80-475F-9432-6A032232CADC', '69ED4F4C-2545-437F-B33E-6A03223C5FC8',
                 '2067E061-0676-4EDE-9EAA-6A03223CCE0A', 'FFE16663-FA38-48D5-8205-6A03224310AC',
                 '2ED926F8-51F9-41C2-AD9E-6A03225C5032', '4AAC1BBD-8F52-4ABE-A780-6A03225CA3BD',
                 '9F6A0367-9DAD-42F5-8AC2-6A0322608C40', '4EF29F9E-F388-4C97-9E1D-6A032261A798',
                 '18458BE3-0C3D-41E0-AB40-6A03226F076A', '0599FEB3-7DB0-412D-9C9D-6A032282614E',
                 'B0E1E8FC-D7B9-4825-90E5-6A032285A95A', 'DF02F683-5048-42B9-9B08-6A0322977F2A',
                 '9D58F496-E094-4A9F-80A6-6A0322A81BA0', 'A354FBAC-FB8E-4896-8EF4-6A0322AE9117',
                 'C5F2E9CC-6609-4E36-A01D-6A0322B94FE6', '91CDFC6A-F785-47FF-8D86-6A0322C4B3C0',
                 '15B30F29-79D8-40F4-AEC4-6A0322DCF61C', '05DD7F7F-3CEA-417B-80B1-6A0322DD4C73',
                 'A594317D-AF73-4A62-AA4C-6A0322E2640E', '6DF7370C-9873-4D4E-8A72-6A0322EAA2DA',
                 '534A016D-8692-49B0-A196-6A0322F8C4D3', 'A098F54C-7A3C-4F44-99D2-6A0322FCBBA7',
                 '61DB559C-97BC-4B38-BF34-6A0322FCBD57', 'AA6B188B-4C72-48DC-8699-6A0323044986',
                 '1E5AD1F9-3DCA-45A2-B36D-6A03230D5F14', 'EC6BA6A2-89B7-4860-8EBB-6A0323263BE1',
                 '60D726B7-4D80-4968-B458-6A03232C444D', '8D3693F9-9A1D-4AD4-B440-6A032332C3B8',
                 '316C1A3A-D23F-4BC1-A241-6A0323388B36', '756E1543-1686-4524-86EC-6A032344FC6C',
                 '5A01C8CF-D23D-4B02-8D82-6A0323488023', '035D7FDB-B14B-400B-AD64-6A032349C439',
                 '146D74CE-70FA-4DFA-9587-6A0323573A8C', '19377D61-E682-4FBF-B0A4-6A032369AB24',
                 '9FF70B06-386F-43B6-B28A-6A03236A1C77', '48BC536F-E93B-4CA7-9A75-6A03237111B8',
                 '29F8852B-A75D-4646-81F7-6A03237B6B43', '50F3EFF2-6AE5-420A-BE74-6A03237CE823',
                 '95DFC0C8-8274-44FD-BF2F-6A032380A8AB', '8E8589FF-3FAC-4323-8D87-6A0323855463',
                 '753500B4-BA06-428B-83A7-6A032387481D', '07DE262D-FFFD-4D25-A753-6A0323AD044E',
                 '6490212F-F637-4DD5-B51F-6A0323C2EAFB', '65DBB1D3-C94E-42B2-8E09-6A0323C38A1D',
                 '6C365D46-A540-42D9-BACA-6A0323CC0246', 'F6C67505-6DA8-4519-8E81-6A0323F298F0',
                 'F6918BB2-1BCD-4419-9A54-6A0323F34216', 'F9C5395C-D126-4707-B970-6A0323FDC37A',
                 '92164144-12B9-4F9F-B232-6A0324105194', 'E55B3A0A-6795-4529-8928-6A0324128105',
                 '70210D6E-2272-46A6-AADA-6A03241A4F4B', 'A117CA9D-8A96-43A3-AF09-6A032426BFE5',
                 'C9106C3B-6C22-4383-80D6-6A032432D7AE', 'EB20D58F-747B-4FA4-A5C4-6A0324538288',
                 '8D83C943-2CFD-4CF5-BEB0-6A0324618EB4', '82617059-5738-4FF2-9076-6A03247A3CF2',
                 '09F00FEF-32C0-4E65-B2F1-6A03248794AC', 'D027C8CF-5C80-48FE-95BF-6A03248E2E0C',
                 '06EE42C4-1DBB-4CCF-89A9-6A03248FA5DD', '03FBD3D7-E405-4A2E-87A7-6A03249B6ED3',
                 'D078C2D5-E3B0-464B-8BF0-6A03249BD575', '8E819368-D5EB-4AE1-B1C9-6A0324A45B80',
                 'B8485D80-9025-4711-9298-6A0324A7EF23', '94DC8CBD-6A7E-4642-810F-6A0324ACEFE3',
                 '48D94710-7874-40BD-B717-6A0324B11D2C', '35369725-C04C-45BC-8C90-6A0324B8E04B',
                 '798E57BF-C53C-4623-876F-6A0324BC4869', '1316EC2A-8701-4C07-B2FF-6A0324C3C3C8',
                 '5E8EB10E-2F1C-4CE7-98AD-6A0324C669DE', 'D25F3FCF-70C9-4ED0-BDE0-6A0324D4A7AE',
                 'DA52BFAC-F957-4983-BACA-6A0324D82CC5', '4541C534-F4B3-42C0-9812-6A0324DC7346',
                 '2BDF39EE-02CA-4ED8-B2AA-6A0324FBF8CD', 'BECD6D99-EAF9-4236-9CFA-6A03251F79AC',
                 '48548F5B-5922-4ACD-8BE6-6A03253B962A', '36D9F5D7-1F87-4276-BEFD-6A03255781F5',
                 'E6BDB71A-E82E-4693-9C2F-6A032569A6F0', '67DA63D7-8EF6-4F7D-9D34-6A03256CF165',
                 'A8B25306-2522-4AF4-BAD9-6A0325799423', '30DCECE8-CEB6-473F-A5A4-6A032599AA87']

    sql_parkingid = [4291, 8393, 4577, 2379, 8146, 8930, 5617, 2722, 4571, 9972, 6638, 5232, 4137, 2724, 8957, 3135,
                     4040, 221, 2620, 4130, 6024, 233, 4948, 8935, 1580, 2781, 7896, 9620, 6757, 3435, 2030, 2660, 4645,
                     8486, 7282, 4688, 3696, 2819, 2818, 8205, 2675, 7430, 437, 8504, 2260, 2679, 2224, 8379, 2858,
                     5737, 2519, 2987, 2690, 5482, 2808, 3987, 4052, 2698, 4941, 3604, 1861, 2687, 4286, 9568, 439,
                     2834, 9835, 4338, 9686, 8126, 4797, 1854, 6171, 4001, 5896, 2742, 2212, 673, 1649, 5198, 5666,
                     3085, 306, 2781, 8103, 1889, 826, 2455, 689, 2255, 817, 2396, 2601, 2108, 606, 2825, 8836, 2730,
                     2566, 864, 8935, 4973, 3037, 7096, 8116, 5051, 9194, 2617, 8162, 9041, 245, 1394, 8445, 2706, 1939,
                     2794, 2724, 7607, 10279, 6840, 10312, 9849, 5348, 2871, 421, 6614, 2975, 2729, 2601, 2868, 2767,
                     373, 9779, 2684, 1903, 541, 1015, 756, 6283, 2665, 4421, 1170, 8142, 3074, 1514, 2805, 374, 1118,
                     7518, 9004, 1967, 6387, 8935, 6351, 222, 9949, 7470, 2826, 4389, 4568, 6135, 1243, 7240, 6927,
                     4389, 9721, 4655, 6212, 2669, 8147, 5307, 3850, 5030, 6163, 7479, 1797, 880, 8033, 7876, 2775,
                     5240, 2682, 5063, 9611, 4168, 7209, 2602, 716, 781, 4639, 8162, 2502, 9020, 9346, 135, 7766, 9777,
                     8367, 5658, 4050, 1044, 2810, 9746, 680, 9957, 2337, 4858, 91, 3387, 279, 1856, 9683, 859, 2424,
                     2664, 925, 3024, 9887, 1739, 8367, 9620, 4310, 9770, 8557, 1754, 46, 8261, 6136, 6457, 733, 6816,
                     8779, 8457, 608, 1776, 4224, 6724, 5908, 365, 4507, 3608, 5020, 7449, 5124, 8127, 2480, 9995, 9835,
                     7867, 2445, 4942, 2463, 2890, 3076, 8756, 559, 795, 8624, 9980, 3491, 1118, 5826, 4648, 566, 3092,
                     7458, 1648, 4040, 1883, 2631, 6826, 2720, 10267, 6840, 7867, 5232, 2775, 2732, 173, 4777, 2015,
                     8633, 2099, 724, 8920, 8306, 1856, 4513, 1358, 1367, 1192, 5177, 5538, 9741, 1966, 10218, 6978,
                     2379, 8033, 4310, 1748, 8307, 1753, 5620, 2781, 6850, 5146, 2616, 8336, 2881, 1366, 8498, 2802,
                     8083, 4007, 8313, 5501, 4523, 7282, 9918, 537, 8491, 3191, 4975, 8419, 5958, 2536, 3853, 2455,
                     8079, 9711, 3124, 7245, 2955, 458, 2324, 6479, 6142, 4973, 2766, 9248, 5137, 5447, 1332, 5100,
                     4628, 8962, 4902, 514, 724, 5858, 9194, 8399, 2638, 2509, 2780, 3592, 5597, 3404, 9346, 2194, 6520,
                     2903, 2628, 9608, 2802, 2255, 8824, 2648, 9061, 3730, 1120, 3001, 3739, 2652, 9741, 4945, 10233,
                     2722, 1564, 10230, 3825, 1207, 3486, 2519, 621, 2601, 10220, 2768, 5087, 4125, 2682, 4070, 5051,
                     5419, 8602, 2103, 3767, 2652, 1112, 2889, 8146, 2630, 2810, 608, 9768, 77, 437, 46, 8755, 1970,
                     2000, 6284, 373, 5051, 2537, 2761, 10144, 4802, 4655, 9640, 2224, 8818, 3451, 7974, 2821, 8156,
                     4275, 5629, 9664, 6949, 2471, 4338, 4139, 6355, 1951, 6688, 4071, 2687, 2640, 5072, 2480, 2621,
                     9741, 2205, 3795, 1756, 1477, 2641, 3184, 10318, 2767, 3037, 5461, 5361, 9751, 5211, 4291, 2959,
                     3843, 3658, 991, 5545, 9972, 518, 7461, 4211, 1951, 5455, 6197, 961, 8935, 2794, 5056, 6481, 2719,
                     6840, 7197, 1897, 7691, 9085, 3227, 6484, 2379, 6137, 8854, 2066, 1588, 10295, 3193, 10035, 6436,
                     5040, 8141, 2724, 9834, 2279, 5727, 5404, 9656, 9518, 9636, 1967, 1395, 4680, 5326, 2767, 5891,
                     8935, 2993, 3174, 9951, 4970, 1307, 9623, 4131, 1967, 8888, 5559, 3387, 5307, 2642, 9162, 2660,
                     1480, 6638, 6032, 7906, 10408, 9951, 4579, 1703, 1243, 9928, 4858, 4040, 3507, 10254, 4313, 309,
                     8910, 4362, 6162, 9751, 1487, 4906, 4421, 2033, 10362, 2199, 2638, 10280, 3281, 2601, 6851, 5051,
                     8796, 6713, 5620, 7063, 3049, 8678, 7506, 1956, 1950, 2779, 2083, 4643, 9146, 3682, 5001, 10267,
                     2724, 7211, 4051, 374, 9611, 2934, 245, 5756, 5387, 2748, 4507, 2769, 7207, 2725, 5051, 5634, 6887,
                     8290, 4521, 3004, 9699, 2289, 2917, 3700, 6695, 5254, 4975, 10405, 10407, 819, 8147, 8369, 2445,
                     5252, 7267, 7957, 2029, 9664, 2636, 1887, 3356, 2621, 8090, 1966, 9599, 2935, 8968, 3873, 10222,
                     9648, 4588, 2806, 2739, 2379, 3116, 5051, 9641, 8419, 4490, 2193, 2328, 4278, 5250, 7468, 5180,
                     3491, 6572, 4179, 8083, 6606, 4823, 2707, 2695, 3666, 1570, 2710, 8661, 6668, 3752, 3319, 3663,
                     1883, 1789, 4040, 4821, 1192, 3730, 4289, 7147, 334, 7617, 9052, 3767, 1944, 8638, 5737, 4797,
                     2770, 10002, 6778, 3223, 7156, 5395, 9222, 1754, 6364, 3811, 7898, 6840, 8333, 2035, 3933, 5281,
                     1284, 10322, 7898, 1110, 2463, 10373, 5363, 8307, 509, 2233, 7666, 1844, 9619, 5718, 6956, 4698,
                     6266, 10304, 4577, 2687, 2029, 3933, 5137, 9501, 3581, 2655, 8784, 294, 2702, 2706, 957, 8424,
                     2701, 9564, 3933, 1667, 373, 4405, 6959, 9198, 4985, 8398, 3722, 2030, 3312, 2668, 9980, 2547,
                     7028, 3933, 4931, 8935, 3981, 2033, 1034, 3216, 3209, 8382, 6639, 8518, 7956, 3597, 5743, 3507,
                     3524, 1859, 1253, 826, 1964, 3359, 8935, 3476, 1064, 2802, 3312, 2157, 2379, 6038, 3595, 9820,
                     3632, 984, 4138, 2758, 608, 3540, 2358, 8852, 739, 8515, 6109, 6730, 5990, 531, 309, 4337, 3750,
                     5958, 8983, 9664, 5226, 6668, 9721, 2046, 9562, 2739, 4070, 7956, 303, 8757, 3319, 7069, 2961,
                     3092, 1797, 2960, 3938, 8127, 5832, 8757, 1943, 2101, 684, 4050, 5398, 3750, 8210, 6518, 8376,
                     4259, 3873, 8436, 6824, 2959, 6507, 169, 6637, 3758, 7725, 718, 1844, 3215, 4777, 4858, 6423, 6266,
                     173, 9194, 9833, 6466, 1721, 1735, 3490, 9058, 2960, 2630, 8935, 5247, 2445, 9061, 1967, 184, 947,
                     1969, 3663, 5282, 6668, 3420, 1911, 9620, 10188, 5603, 2517, 3178, 6614, 5146, 309, 6305, 4210,
                     8728, 9546, 2128, 3570, 3598, 2433, 803, 8755, 3540, 2283, 10023, 3049, 5051, 5247, 5232, 6904,
                     5156, 6531, 2690, 5529, 10023, 3820, 8935, 8935, 6406, 613, 2711, 5360, 6994, 2212, 5405, 8685,
                     2289, 276, 1778, 4121, 7282, 3202, 9620, 735, 8841, 6844, 1847, 724, 5734, 673, 785, 8751, 10265,
                     9513, 5709, 1395, 2724, 3142, 4870, 2015, 9014, 601, 5544, 6628, 2728, 1325, 9335, 2808, 8399,
                     6228, 3557, 8398, 3037, 6684, 4507, 819, 4909, 8242, 4019, 8242, 5699, 8568, 5990, 3926, 8399,
                     2012, 3573, 9636, 5390, 6339, 5051, 5525, 3356, 9799, 5620, 7452, 8876, 7640, 9984, 2553, 3895,
                     9101, 8935, 7668, 2989, 9034, 7614, 829, 4052, 2736, 3631, 2379, 710, 2292, 5728, 1410, 4519, 8957,
                     437, 1293, 8185, 2295, 6915, 2070, 4982, 1665, 10102, 437, 3676, 6157, 3910, 7461, 4185, 1992,
                     5831, 6935, 5983, 2750, 4858, 5978]

    sql_state = [16136, 14437, 9357, 7536, 15998, 7158, 5352, 22781, 4815, 7096, 20390, 11187, 8361, 10788, 19768, 449,
                 7744, 18572, 20319, 5889, 15846, 14138, 6766, 15878, 4053, 17673, 16394, 18364, 16812, 13474, 14640,
                 19238, 21996, 14617, 7703, 14081, 17672, 16208, 22914, 12111, 17220, 6840, 0, 17142, 20352, 14671,
                 16970, 10314, 15443, 4843, 10493, 2534, 22208, 11205, 9243, 17274, 10074, 5691, 11966, 13783, 9545,
                 22362, 7434, 9283, 17105, 17681, 16304, 3032, 14164, 18968, 15115, 14539, 14411, 11057, 8718, 12566,
                 16824, 7499, 16096, 13876, 22729, 16256, 20883, 0, 21582, 19403, 16947, 7582, 18268, 14397, 13442,
                 12090, 16426, 12617, 9433, 15932, 16051, 22286, 17955, 16004, 19662, 7536, 12406, 8450, 15730, 22544,
                 4106, 11336, 4177, 15724, 3095, 20883, 21995, 7325, 22121, 21768, 21134, 14083, 11192, 14800, 11336,
                 14699, 12170, 10911, 19768, 21739, 17259, 17223, 9769, 16208, 4201, 7493, 7887, 19722, 8842, 17060,
                 14491, 17974, 16387, 4730, 0, 18920, 13542, 17169, 18700, 10438, 11152, 12184, 23291, 1994, 13851,
                 15850, 12002, 11012, 2879, 15784, 13811, 16827, 7624, 10237, 7582, 12021, 5153, 19595, 19768, 12145,
                 13934, 19718, 9348, 15209, 20927, 1846, 11208, 22108, 8618, 14332, 10605, 17084, 22206, 21375, 20577,
                 19744, 7276, 16896, 1467, 20156, 12389, 21030, 16121, 15837, 13017, 6995, 12198, 14016, 22117, 9231,
                 15662, 15165, 17899, 10164, 15815, 3894, 20874, 7536, 21009, 3552, 8390, 12255, 3035, 14177, 7446,
                 14286, 15968, 15662, 7711, 22168, 18970, 7153, 13125, 17336, 3634, 1792, 14640, 1088, 22137, 10928,
                 19749, 21514, 12647, 9695, 16308, 5421, 7063, 1823, 13301, 18893, 1465, 19056, 20631, 8859, 20213,
                 14164, 3997, 16971, 21405, 22595, 8121, 22962, 8408, 20575, 9775, 3346, 8809, 15815, 7833, 16388,
                 18301, 6378, 11971, 15033, 17147, 9433, 20798, 20308, 21851, 10376, 22504, 3776, 8995, 5075, 19213,
                 19740, 21905, 9855, 5421, 20088, 17080, 16723, 4755, 12406, 9013, 16136, 14424, 10254, 9466, 17167,
                 7711, 22117, 10263, 21008, 19035, 15882, 11930, 10979, 8657, 12777, 17642, 19300, 12624, 12255, 11039,
                 17352, 5052, 10052, 7049, 15417, 12232, 19098, 16814, 17841, 21855, 17673, 10206, 6179, 4011, 21520,
                 15694, 13959, 1467, 19505, 21405, 11114, 15064, 20505, 17696, 5976, 10082, 14968, 18364, 19556, 12727,
                 8719, 13506, 14949, 14770, 13605, 17262, 4888, 1723, 12832, 8460, 18682, 0, 13987, 17201, 4097, 16940,
                 8591, 18923, 9139, 15239, 13061, 15517, 13513, 449, 9683, 5725, 19391, 10299, 21031, 16521, 17511,
                 8022, 12789, 21923, 8361, 10063, 4679, 3997, 11612, 14681, 21405, 11057, 21425, 18491, 9619, 0, 15208,
                 20100, 7642, 8842, 19143, 10413, 21698, 17974, 11612, 18682, 13045, 8600, 3757, 11612, 9227, 14179,
                 10472, 3480, 14380, 22121, 453, 2863, 10141, 17658, 10963, 20161, 6331, 4261, 9369, 11575, 22610,
                 17776, 12588, 10103, 7307, 22160, 9656, 13012, 22108, 14628, 2262, 20501, 9793, 4060, 10423, 18385,
                 19329, 12406, 21712, 17718, 7582, 1994, 19744, 16096, 18450, 10918, 14715, 10311, 13047, 15919, 16942,
                 4060, 19750, 16575, 20937, 6461, 2515, 10314, 9246, 13986, 17223, 14132, 14989, 12856, 14812, 22460,
                 14089, 21405, 10284, 20094, 7582, 14018, 8612, 6134, 7624, 16308, 8675, 7945, 5094, 11195, 22316,
                 17165, 15208, 17065, 22085, 14666, 0, 22224, 12157, 4432, 16654, 21710, 14493, 17202, 19557, 4619,
                 18714, 15704, 9769, 18388, 20760, 16256, 8902, 14077, 7189, 11452, 10711, 19705, 15899, 14989, 1125,
                 22861, 15784, 16514, 8302, 14210, 4201, 15234, 15480, 1742, 15579, 19790, 12826, 9349, 17683, 8793,
                 8842, 2893, 1289, 8793, 6319, 22969, 13332, 6110, 15915, 9887, 17195, 23437, 12050, 18968, 19058,
                 16315, 17262, 17693, 18541, 8129, 17197, 20161, 15996, 21698, 17862, 9471, 9301, 15067, 13986, 16965,
                 9068, 5549, 16575, 19299, 16219, 14484, 21392, 14681, 10031, 14195, 20936, 9357, 21405, 13242, 9656,
                 14033, 14719, 9946, 15932, 10283, 10100, 18700, 15037, 20290, 11476, 7887, 20562, 12198, 21905, 16729,
                 17806, 19750, 12941, 0, 16530, 22701, 14472, 19528, 13490, 16641, 1467, 21405, 2645, 2204, 22120,
                 15694, 12255, 15693, 17901, 0, 9146, 8995, 14214, 6141, 15435, 5884, 17202, 19841, 20540, 14210, 15997,
                 6920, 21062, 4258, 15831, 21855, 20600, 6818, 8113, 21262, 13868, 16812, 6995, 18572, 11479, 9119,
                 13149, 16333, 7049, 0, 16507, 11208, 13617, 15704, 22065, 10471, 14317, 17658, 20050, 12066, 4755,
                 21906, 12806, 5701, 20352, 14530, 4330, 8842, 15439, 0, 16012, 20444, 22117, 18682, 20366, 17870,
                 19159, 7281, 22952, 10881, 18450, 18692, 18702, 8560, 15102, 22541, 7582, 20312, 19211, 14077, 16828,
                 7887, 20025, 18364, 9574, 19666, 11187, 17331, 21505, 13828, 7536, 11991, 14609, 8473, 22316, 1692,
                 12647, 20088, 20883, 22680, 21405, 16004, 13696, 14380, 4156, 11179, 9776, 16400, 13541, 6066, 15288,
                 7074, 16592, 4642, 18102, 16500, 19309, 9348, 16142, 12934, 22194, 13554, 7536, 9351, 17152, 15666,
                 15064, 22116, 11760, 20807, 3757, 13696, 7170, 7536, 14105, 16304, 15721, 2324, 4523, 7678, 5658, 1088,
                 20321, 16055, 17201, 0, 17511, 13888, 18887, 16082, 13888, 21008, 17080, 23016, 17173, 16911, 21982,
                 20308, 15869, 20390, 4940, 12699, 16473, 17335, 15815, 20352, 14530, 21514, 449, 8709, 10414, 14332,
                 20662, 20077, 14938, 21220, 2630, 16136, 19143, 5367, 17080, 6805, 14945, 16256, 9656, 7158, 17131,
                 19000, 8842, 8450, 5696, 4815, 14173, 16606, 17683, 14020, 8695, 12717, 7152, 8905, 1935, 14989, 9293,
                 11057, 14808, 5449, 16129, 17186, 15004, 12807, 8251, 9146, 6818, 11395, 2163, 20210, 15426, 10370,
                 8445, 8728, 14179, 16800, 20648, 13195, 20319, 14609, 14681, 21520, 19463, 3580, 21514, 16953, 18809,
                 12691, 18541, 13327, 16096, 5407, 18652, 13111, 5113, 15760, 14530, 21106, 4053, 6578, 16525, 14175,
                 15190, 4743, 20807, 15186, 4472, 15733, 9146, 453, 22349, 22116, 8129, 16638, 22378, 20760, 7050,
                 10368, 4238, 11328, 0, 19105, 15831, 4523, 8913, 6146, 15394, 16968, 21014, 10002, 17262, 4551, 9004,
                 7896, 22108, 8842, 7807, 21955, 6957, 20760, 9545, 21712, 12806, 16006, 15518, 22579, 18809, 1215,
                 22525, 13412, 15730, 14218, 10493, 2048, 6586, 19556, 14530, 17202, 10445, 14380, 15416, 18388, 17289,
                 22861, 22120, 11776, 15724, 19098, 7536, 449, 17499, 0, 19403, 22550, 6791, 0, 21514, 12145, 4337,
                 17874, 7504, 20390, 8621, 18639, 20910, 17872, 5559, 7536, 15239, 0, 4309, 21438, 15724, 15159, 12367,
                 5834, 0, 7063, 17551, 22003, 10462, 13659, 12416, 11356, 4940, 3505, 0, 9508, 18417, 19267, 10579,
                 14576, 21804, 21020, 0, 4720, 13412, 13872, 19365, 16055, 22117, 7152, 3389, 9560, 7799, 15546, 22120,
                 18243, 15106, 17870, 21826, 1792, 19035, 17343, 15086, 18741, 12917, 15692, 8650, 20760, 18197, 21008,
                 3973, 10633, 0, 12050, 17080, 0, 16671, 17131, 15732, 7018, 14770, 17963, 18298, 0, 10788, 16328,
                 10371, 16530, 7167, 12121, 8023, 13634, 18573, 20558, 18433, 15662, 20889, 13442, 9508, 9395, 12810,
                 15267, 21105, 13442, 7382, 19143, 14177, 7590, 449, 6662, 11230, 16305, 9380, 18560, 7012, 20847, 1960,
                 22156, 10568, 19790, 22316, 1467, 15517, 11420, 4720, 15215, 15699, 21639, 453, 15701, 9242, 18584,
                 16137, 20349, 6327, 3456, 21995, 14304, 16340, 15987, 17198, 19155, 11452, 15028, 13594, 8441, 12647,
                 13301, 2507, 9814, 16489, 9242, 14083, 14329, 0, 16077, 10704, 19224, 20148, 9397, 8669, 16388, 13540,
                 5229, 17642, 9034, 16208, 17147, 11966, 16627, 8269, 10376, 17080, 16521, 4418, 20760, 5680, 16723,
                 12881, 20927, 18824, 18670, 13857, 19384, 453, 14080, 15724, 13831, 10414, 20317, 1524, 6327, 18069,
                 16693, 9231, 15662, 17100, 12917, 9068, 14946, 17144, 23805, 11684, 10001, 4880, 12051, 21804, 1465,
                 21313, 8295, 9018, 15757, 17829, 9596, 1125, 8441, 21764, 16519, 5164, 9943, 11420, 9369, 449, 1845,
                 1527, 17681, 17090, 20648, 17186, 12756, 16038, 449, 21099, 15443, 17704, 6606, 9191, 0, 16082, 21262,
                 13662, 17167, 12803, 4443, 15815, 20631, 15693, 4739, 17220, 1833, 12856, 17974, 9471, 20444, 13163,
                 17147, 0, 21905, 16285, 13037, 20575, 19722, 13605, 15362, 10271, 19056, 14326, 19153, 22116, 8220,
                 6995, 17080, 14405, 9794, 9328, 8126, 2587, 8113, 10401, 4927, 4705, 9931, 22117, 7536, 2414, 13525,
                 18388, 13696, 20501, 21405, 8290, 1339, 8467, 9770, 17293, 10370, 1279, 3095, 9946, 16602, 22300,
                 12145, 20318, 9582, 16256, 6327, 20631, 13087, 11865, 16650, 13630, 21257, 9674, 13541, 15394, 15804,
                 16826, 17577, 14314, 21172, 0, 12068, 17142, 17105, 14630, 8482, 8109, 21313, 7536, 16926, 23254,
                 10423, 21257, 21295, 2893, 15882, 19071, 19768, 3095, 2522, 16338, 1398, 11930, 5257, 11012, 449,
                 10317, 21405, 13087, 8295, 8001, 10206, 15771, 8793, 16592, 16891, 7887, 7654, 9368, 16695, 5449,
                 15975, 4228, 22210, 8467, 17167, 18268, 22509, 10414, 10439, 19389, 6461, 1846, 22042, 13827, 17872,
                 16575, 8902, 9887, 15555, 17267, 21149, 16947, 9773, 16566, 14424, 17152, 16942, 14666, 12683, 4500]

    # @task(50)
    def execute_query1(self):
        """普通索引查询"""    
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query1(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee FROM parking_record WHERE " \
                "plate_number = '%s';" % str(random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query1(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee FROM parking_record WHERE " \
                "plate_number = ?;", (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)

    # @task(1)
    def execute_query2(self):
        """普通索引查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query2(
                self.conn_string,
                "SELECT COUNT(1) FROM parking_record WHERE plate_number = '%s';" % str(
                    random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query2(
                "SELECT COUNT(1) FROM parking_record WHERE plate_number = ?;"
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)

    # @task(50)
    def execute_query3(self):
        """普通索引查询降序100条"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query3(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, update_time FROM parking_record " \
                "WHERE plate_number = '%s' ORDER BY entrance_time DESC LIMIT 100;" % str(
                    random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query3(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, update_time FROM parking_record " \
                "WHERE plate_number = ? ORDER BY entrance_time DESC LIMIT 100;"
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)

    # @task(50)
    def execute_query4(self):
        """普通索引多条件查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query4(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, update_time, is_finish FROM " \
                "parking_record WHERE entrance_time = '2021-01-01' AND is_finish = 1 AND plate_number = '%s';" \
                % str(random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query4(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, update_time, is_finish FROM " \
                "parking_record WHERE entrance_time = '2021-01-01' AND is_finish = 1 AND plate_number = ?;" 
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)

    # @task(50)
    def execute_query5(self):
        """普通索引多条件查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query5(
                self.conn_string,
                "SELECT is_finish, SUM(receivable_fee) AS receivable_fee FROM parking_record WHERE synid = '%s'" \
                " AND `status` = 1;" % str(random.choice(CustomTaskSet.sql_synid)))
        else:
            self.client.execute_query5(
                "SELECT is_finish, SUM(receivable_fee) AS receivable_fee FROM parking_record WHERE synid = ?" \
                " AND `status` = 1;"
                , (str(random.choice(CustomTaskSet.sql_synid)), ), False)

    # @task(50)
    def execute_query6(self):
        """唯一索引查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query6(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE synid = '%s';" \
                % str(random.choice(CustomTaskSet.sql_synid)))
        else:
            self.client.execute_query6(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE synid = ?;"
                , (str(random.choice(CustomTaskSet.sql_synid)), ), False)



    # @task(1)
    def execute_query7(self):
        """唯一索引多条件查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query7(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE synid = '%s' AND is_finish = 0 AND " \
                "entrance_time > '2020-01-01';" % str(random.choice(CustomTaskSet.sql_synid)))
        else:
            self.client.execute_query7(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE synid = ? AND is_finish = 0 AND " \
                "entrance_time > '2020-01-01';"
                , (str(random.choice(CustomTaskSet.sql_synid)), ), False)

    # @task(1)
    def execute_query8(self):
        """唯一索引查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query8(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE plate_number = '%s' AND synid = '%s';" \
                % (str(random.choice(CustomTaskSet.sql_plateNumber)), str(random.choice(CustomTaskSet.sql_synid))))
        else:
            self.client.execute_query8(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE plate_number = ? AND synid = ?;"
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), str(random.choice(CustomTaskSet.sql_synid)), ), False)

    # @task(1)
    def execute_query9(self):
        """普通索引查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query9(
                self.conn_string,
                "SELECT SUM(receivable_fee) AS total_receivable_fee, SUM(actual_fee) AS total_actual_fee, " \
                "SUM(online_fee) AS total_online_fee FROM parking_record WHERE plate_number = '%s' AND `status` = 1;" \
                % str(random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query9(
                "SELECT SUM(receivable_fee) AS total_receivable_fee, SUM(actual_fee) AS total_actual_fee, " \
                "SUM(online_fee) AS total_online_fee FROM parking_record WHERE plate_number = % AND `status` = 1;" 
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)


    # @task(1)
    def execute_query10(self):
        """普通索引查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query10(
                self.conn_string,
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE plate_number = '%s' AND " \
                "entrance_car_plate_color = 1 AND entrance_time > '2019-01-01';" \
                % str(random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query10(
                "SELECT id, plate_number, entrance_time, exit_time, receivable_fee, actual_fee, online_fee, " \
                "update_time, is_finish, `status` FROM parking_record WHERE plate_number = ? AND " \
                "entrance_car_plate_color = 1 AND entrance_time > '2019-01-01';"
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)
            
    # @task(1)
    def execute_query11(self):
        """唯一索引联表查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query11(
                self.conn_string,
                "SELECT parkingid, platenumber, exitparkingboxid, entrancetime, exittime, updatetime, receivablefee, " \
                "actualfee, onlinefee, pam2 FROM carout_payment c LEFT JOIN parking_record p ON c.`synid` = p.`synid` " \
                "WHERE updatetime > '2021-01-01' AND receivablefee = 0.00 AND actualfee = 0.00 AND c.`synid` = '%s';" \
                % str(random.choice(CustomTaskSet.sql_synid)))
        else:
            self.client.execute_query11(
                "SELECT parkingid, platenumber, exitparkingboxid, entrancetime, exittime, updatetime, receivablefee, " \
                "actualfee, onlinefee, pam2 FROM carout_payment c LEFT JOIN parking_record p ON c.`synid` = p.`synid` " \
                "WHERE updatetime > '2021-01-01' AND receivablefee = 0.00 AND actualfee = 0.00 AND c.`synid` = ?;"
                , (str(random.choice(CustomTaskSet.sql_synid)), ), False)


    # @task(10)
    def execute_query12(self):
        """普通索引内联查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query12(
                self.conn_string,
                "SELECT row_number() over (ORDER BY plate_number DESC) row_num, parkingid, platenumber, " \
                "exitparkingboxid, entrancetime, exittime, updatetime, receivablefee, actualfee, onlinefee, pam2 " \
                "FROM carout_payment c INNER JOIN parking_record p ON c.`platenumber` = p.`plate_number` WHERE " \
                "entrancetime > '2019-01-01' AND receivablefee != 0.00 AND actualfee = 0.01 AND c.`platenumber` " \
                "= '%s';" % str(random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query12(
                "SELECT row_number() over (ORDER BY plate_number DESC) row_num, parkingid, platenumber, " \
                "exitparkingboxid, entrancetime, exittime, updatetime, receivablefee, actualfee, onlinefee, pam2 " \
                "FROM carout_payment c INNER JOIN parking_record p ON c.`platenumber` = p.`plate_number` WHERE " \
                "entrancetime > '2019-01-01' AND receivablefee != 0.00 AND actualfee = 0.01 AND c.`platenumber` " \
                "= ?;"
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)

    # @task(50)
    def execute_query13(self):
        """唯一索引联表查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query13(
                self.conn_string,
                "SELECT parkingid, platenumber, entrancetime, exittime, updatetime, receivablefee, actualfee, " \
                "onlinefee, couponfee, centerfee, cardfee, buscardfee, pam2, entranceroadname, exitroadname, realname," \
                " cartypename, exitparkingboxname FROM carout_payment c LEFT JOIN parking_record p ON c.`synid` " \
                "= p.synid WHERE entrancetime > '2019-01-01' AND receivablefee != 0.00 AND actualfee = 0.01 " \
                "AND c.`synid` = '%s';" % str(random.choice(CustomTaskSet.sql_synid)))
        else:
            self.client.execute_query13(
                "SELECT parkingid, platenumber, entrancetime, exittime, updatetime, receivablefee, actualfee, " \
                "onlinefee, couponfee, centerfee, cardfee, buscardfee, pam2, entranceroadname, exitroadname, realname," \
                " cartypename, exitparkingboxname FROM carout_payment c LEFT JOIN parking_record p ON c.`synid` " \
                "= p.synid WHERE entrancetime > '2019-01-01' AND receivablefee != 0.00 AND actualfee = 0.01 " \
                "AND c.`synid` = ?;"
                , (str(random.choice(CustomTaskSet.sql_synid)), ), False)

    # @task(1)
    def execute_query14(self):
        """分页普通索引联表查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query14(
                self.conn_string,
                "SELECT row_number() over (ORDER BY plate_number DESC) row_num, platenumber FROM carout_payment c " \
                "LEFT JOIN parking_record p ON c.`platenumber` = p.`plate_number` WHERE entrancetime > '2019-01-01' " \
                "AND receivablefee != 0.00 AND actualfee = 0.01 AND c.platenumber = '%s';" % str(
                    random.choice(CustomTaskSet.sql_plateNumber)))
        else:
            self.client.execute_query14(
                "SELECT row_number() over (ORDER BY plate_number DESC) row_num, platenumber FROM carout_payment c " \
                "LEFT JOIN parking_record p ON c.`platenumber` = p.`plate_number` WHERE entrancetime > '2019-01-01' " \
                "AND receivablefee != 0.00 AND actualfee = 0.01 AND c.platenumber = ?;"
                , (str(random.choice(CustomTaskSet.sql_plateNumber)), ), False)

    # # @task(1)
    def execute_query15(self):
        """查询parking_id普通索引联表查询"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query15(
                self.conn_string,
                "SELECT c.`platenumber` FROM carout_payment c LEFT JOIN parking_record p ON c.`platenumber` = p.`plate_number` " \
                "WHERE c.`parkingid` = %s AND p.`area_id` AND p.`state` = 0 AND p.`status` < 3 AND p.entrance_time = '2022-08-04' GROUP BY c.`platenumber`;" \
                % (random.choice(CustomTaskSet.sql_parkingid)))
        else:
            self.client.execute_query15(
                "SELECT c.`platenumber` FROM carout_payment c LEFT JOIN parking_record p ON c.`platenumber` = p.`plate_number` " \
                "WHERE c.`parkingid` = ? AND p.`area_id` AND p.`state` = 0 AND p.`status` < 3 AND p.entrance_time = '2022-08-04' GROUP BY c.`platenumber`;"
                , (str(random.choice(CustomTaskSet.sql_parkingid)), ), False)


    # @task(1)
    def execute_query16(self):
        """select 查询in parking_id / plate_number order by entrance_time"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_query16(
                self.conn_string,
                "SELECT parking_id, plate_number FROM parking_record ORDER BY entrance_time LIMIT 0, 10;")
        else:
            self.client.execute_query16(
                "SELECT parking_id, plate_number FROM parking_record ORDER BY entrance_time LIMIT 0, 10;")
    
    # @task(50)
    def execute_insert1(self):
        """carout_payment表单条插入"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_insert1(
                self.conn_string,
                "INSERT INTO carout_payment(id,parkingid, platenumber, exitparkingboxid, entrancetime, exittime, ontime, " \
                "updatetime, recordsynid, synid, receivablefee, actualfee, onlinefee, couponfee, centerfee, cardfee, " \
                "buscardfee, adminid, state, upload,upload_insert,upload_update, integralsfee,losemoney,entranceroad," \
                "entranceroadname,exitroad,exitroadname,realname,isfixed,remarks,cartypeid,cartypename,exitparkingboxname," \
                "cpmfee,overcharged) VALUES(NOW(),1004042,'藏QVVVV1',10003994,NOW(),NOW(),NOW(),NOW(),UUID(),UUID()," \
                "0.00,0.00,0.00,0.00,0.00,0.00,0.00,6238,0,2,NOW(),NOW(),0.00,0.00,7362,'入口1',7365,'出口1','搜索',77," \
                "'这是remarks',5251,'2cpd','岗亭1',0.00,0.00);")
        else:
            self.client.execute_insert1(
                "INSERT INTO carout_payment(id,parkingid, platenumber, exitparkingboxid, entrancetime, exittime, ontime, " \
                "updatetime, recordsynid, synid, receivablefee, actualfee, onlinefee, couponfee, centerfee, cardfee, " \
                "buscardfee, adminid, state, upload,upload_insert,upload_update, integralsfee,losemoney,entranceroad," \
                "entranceroadname,exitroad,exitroadname,realname,isfixed,remarks,cartypeid,cartypename,exitparkingboxname," \
                "cpmfee,overcharged) VALUES(NOW(),1004042,'藏QVVVV1',10003994,NOW(),NOW(),NOW(),NOW(),UUID(),UUID()," \
                "0.00,0.00,0.00,0.00,0.00,0.00,0.00,6238,0,2,NOW(),NOW(),0.00,0.00,7362,'入口1',7365,'出口1','搜索',77," \
                "'这是remarks',5251,'2cpd','岗亭1',0.00,0.00);")

    @task(1)
    def execute_insert2(self):
        """parking_record表单条插入"""
        if config.USE_PREPARE_STMT == False:
            self.client.execute_insert2(
                self.conn_string,
                "INSERT INTO parking_record(record_type, entrance_time,entrance_parking_box_id,exit_time,exit_parking_box_id," \
                "receivable_fee,actual_fee,admin_id,ontime,update_time,parking_id,area_id,group_id,is_fixed,state,exit_road," \
                "entrance_road,synid,plate_number,upload_insert,upload_update,remarks,online_fee,`status`) VALUES(77,NOW()," \
                "10003994,NOW(),10003994,0.02,0.00,6238,NOW(),NOW(),1004042,3430,UUID(),77,4937,7365,7362,UUID(),'藏QVVVV1'," \
                "NOW(),NOW(),'这是插入parking_record的数据',0.00,1);")
        else:
            self.client.execute_insert2(
                "INSERT INTO parking_record(record_type, entrance_time,entrance_parking_box_id,exit_time,exit_parking_box_id," \
                "receivable_fee,actual_fee,admin_id,ontime,update_time,parking_id,area_id,group_id,is_fixed,state,exit_road," \
                "entrance_road,synid,plate_number,upload_insert,upload_update,remarks,online_fee,`status`) VALUES(77,NOW()," \
                "10003994,NOW(),10003994,0.02,0.00,6238,NOW(),NOW(),1004042,3430,UUID(),77,4937,7365,7362,UUID(),'藏QVVVV1'," \
                "NOW(),NOW(),'这是插入parking_record的数据',0.00,1);")



    def on_stop(self):
        print("------ Test over ------")


class MySqlLocust(User):
    
    tasks = [CustomTaskSet]

    def __init__(self, env):
        super().__init__(env)
        if config.USE_PREPARE_STMT == False:
            self.client = MySqlClient()
        else:
            self.client = PrepareStmtClient()