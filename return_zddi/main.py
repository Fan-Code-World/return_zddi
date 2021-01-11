#!/usr/bin/env python
# coding=utf-8
import csv
import time
import datetime
import IPy
import re
import json
import sys
import argparse
import commands
from zddi_interface_dhcp import *
from csv_format import *
from format_config import HandleWindow

# 日志函数
def loger(log_win, s_code = 200):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = now + ' ' + log_win
    print content
    if s_code !=  200:
        f = file('error.log', 'a')
    else:
        f = file('result.log', 'a')
    f.write(content + '\n')
    f.close()

#文件编码转换函数
def File_format_conversion(file_name):
    os.system('cp %s .%s'%(file_name,file_name))
    file_name='.'+file_name
    file_format = commands.getoutput('file -i %s'%(file_name))
    if  'UTF-16' in file_format  or 'utf-16' in file_format  or 'utf-16le' in file_format :
        os.system('iconv -f UTF-16 -t UTF-8 %s > windows_dhcp.txt'%(file_name))
    elif 'iso-8859' in file_format  :
        os.system('iconv -f gbk -t UTF-8 %s > windows_dhcp.txt'%(file_name))
    elif 'utf-8' in file_format  :
        os.system('cp  %s  windows_dhcp.txt   '%(file_name))
    else :
        os.system('iconv -f gb18030 -t utf-8 %s  >  windows_dhcp.txt'%(file_name))
    os.system('rm -r %s '%(file_name))
    file_format = commands.getoutput('file -i windows_dhcp.txt')
    if 'utf-8' in file_format:
        return('succeed')
    else :
        return('error')

#缺失/错误参数校验日志
def warning(add_Type, start, end, network, arguments,Values):
    loger('win_dhcp_file:%s %s==>%s of %s:%s:%s,Values is Null,After checking error!!\n'%(
        add_Type, start, end,network, arguments, Values), 422 )

#触发argparse ，读取指定的相关参数
def main():
    parser = argparse.ArgumentParser() #ArgumentParser类生成一个parser对象
    parser.add_argument('-f',type=str,help='Specify windows_server_dhcp.txt (E.g: -f windows_dhcp.txt) ')
    parser.add_argument('-v','--versions',default='3.11',help='Specify Zddi system version ,support_version 3.10/3.11/3.12 (E.g: -f 3.11)')
    parser.add_argument('-c','--binding',default='no',help='Whether automatic binding is enabled , yes/no  (E.g: -c no)')
    parser.add_argument('-csv',help='Generate CSV format files')
    args=parser.parse_args()
    #return (args.file,args.vis,args.binding)
    return vars(args)

args_str = main()
try:
    args_str['f'].strip("\'") #如果此参数为空，则通过strip触发异常
except:
    print ("green","switchs_file name is required! (E.g: -f switch.csv)")
    sys.exit()

#转换文件
file_return_code = File_format_conversion(args_str['f'])
if file_return_code == 'succeed':
    print ('File conversion successful!')
else :
    print ('File conversion failed')
    sys.exit()



# 从配置文件提取配置字典
win_conf_instance = HandleWindow()
win_conf = win_conf_instance.analyWindow('windows_dhcp.txt')
#生成csv文件
if args_str['csv'] :
    csvformat(win_conf)
    print 'Csv_file_ok'
    sys.exit()
	

# 创建类实例对象
t1 = NetworkManager(cms_node='local.master', cms_ip='127.0.0.1',
                    cms_user='admin', cms_passwd='admin',Automatic_binding=args_str['binding'])

# setup 2:遍历配置字典，创建配置中的网络及网络中包含的资源（地址池、固定地址）
loger("####begin creat network and dhcpresource####")
for host in win_conf:
    # setup 2-1:创建网络，创建时匹配网络备注列表，result_network用于判断是否需要创建网络中的dhcp资源
    result_network = True
    try:
        if win_conf[host].has_key('host_mask_comment'):
            comment = win_conf[host]['host_mask_comment']
    except AttributeError:
        continue 

    network = str(IPy.IP(host).make_net(win_conf[host]['host_mask']))
    if args_str['versions'] == '3.10':
        return_code = t1.return_creatNetwork_one([network], attrs=comment)
    elif args_str['versions'] == '3.11' or args_str['versions'] == '3.12':
        return_code = t1.return_creatNetwork_one([network], attrs=comment)
    if return_code == 200 :
        loger("creat network %s  success" % (network))
    else:
        loger("creat network %s %s failed and the return_code is %s" %
              (network, comment, return_code),return_code)
        result_network = False
    time.sleep(0.1)
    # setup 2-2:创建地址池、保留地址及固定地址
    # setup 2-2-1:分析提取地址池配置参数
    if win_conf[host].has_key('gatway'):
        routers = map(lambda x: re.sub(',', '', x),
                      win_conf[host]['gatway'])
    else:
        routers = []
    if win_conf[host].has_key('domain_name_servers'):
        domain_name_servers = map(lambda x: re.sub(
            ',', '', x), win_conf[host]['domain_name_servers'])
    elif win_conf.has_key('global_domain_name_servers'):
        domain_name_servers = win_conf['global_domain_name_servers']
    else :
        domain_name_servers = []
    
    if win_conf[host].has_key('acls'):
        acls = map(lambda x: total_acls[x], win_conf[host]['acls'])
    else:
        acls = ['any']
    if win_conf[host].has_key('lease_time'):
        lease_time = win_conf[host]['lease_time']
    else:
        lease_time = '43200'
    if win_conf[host].has_key('acls'):
        acls = map(lambda x: total_acls[x], win_conf[host]['acls'])
    else:
        acls = ['any']

    #if win_conf[host].has_key('netbios-name-servers'):
    #    options = [{'space': 'IPv4$DHCP',
    #                'name': 'netbios-name-servers;44;array of ip-address',
    #                'value': win_conf[host]['netbios-name-servers'][0],
    #                'vendorid': '',
    #                'clientid': '',
    #                'force': False}]

    options = []
    if win_conf[host].has_key('vendor-encapsulated-options'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'vendor-encapsulated-options;43;string',
                    'value': win_conf[host]['vendor-encapsulated-options'] ,
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})
        
    if win_conf[host].has_key('domain-name'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'domain-name;15;text',
                    'value': win_conf[host]['domain-name'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #NTP-servers,option42
    if win_conf[host].has_key('ntp-servers'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'ntp-servers;42;array of ip-address',
                    'value': win_conf[host]['ntp-servers'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #netbios-name-servers,option44
    if win_conf[host].has_key('netbios-name-servers'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'netbios-name-servers;44;array of ip-address',
                    'value': win_conf[host]['netbios-name-servers'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    if win_conf[host].has_key('netbios-node-type'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'netbios-node-type;46;unsigned integer 8',
                    'value': win_conf[host]['netbios-node-type'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #option60 海关学院
    if win_conf[host].has_key('vendor-class-identifier'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'vendor-class-identifier;60;string',
                    'value': win_conf[host]['vendor-class-identifier'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #tftp-server,option66 苏州外包职业技术学院
    if win_conf[host].has_key('tftp_servers'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'tftp-server-name;66;text',
                    'value': win_conf[host]['tftp_servers'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #bootfile,option67 苏州外包职业技术学院
    if win_conf[host].has_key('tftp_servers'):
        options.append({'space': 'IPv4$DHCP',
                    'name': 'bootfile-name;67;text',
                    'value': win_conf[host]['tftp_servers'],
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #全局option参数

    #全局option参数
    #option16  农业江西分行
    if win_conf.has_key('global_swap_servers'):
        #直接使用字典的时候会将'[]'带上，同时考虑到可能有多个swap_servers字段，需要重新整理一下
        swap_servers = map(lambda x: re.sub(',', '', x), win_conf['global_swap_servers'])
        options.append({'space': 'IPv4$DHCP',
                    'name': 'swap-server;16;ip-address',
                    'value': ''.join(swap_servers),
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    #option66   农业江西分行
    if win_conf.has_key('global_tftp_servers'):
        #直接使用字典的时候会将'[]'带上，同时考虑到可能有多个swap_servers字段，需要重新整理一下
        tftp_servers = map(lambda x: re.sub(',', '', x), win_conf['global_tftp_servers'])
        options.append({'space': 'IPv4$DHCP',
                    'name': 'tftp-server-name;66;text',
                    'value': ''.join(tftp_servers),
                    'source_match':'option60',
                    'vendorid': '',
                    'clientid': '',
                    'force': False})

    if options and args_str['versions'] != '3.12':
        for i in  options:
            del i['source_match']


        
        
        
    if result_network == True:
        # setup 2-2-2:创建地址池
        if win_conf[host].has_key('pools'):
            for j in win_conf[host]['pools']:

                return_code = t1.return_DynamicPool(
                    network, j[0], j[1], routers, domain_name_servers, lease_time=lease_time, options=options)
                if return_code == 200  :
                    loger("creat pool %s-%s of %s success" %
                          (j[0], j[1], network))
                else:
                    loger("creat pool %s-%s of %s failed and the return_code is %s,routers is %s" %
                          (j[0], j[1], network, return_code,routers),return_code)

                    #网关不在网络中，经过校验提出报错
                        #if  routers[0] in IPy.IP(network) == False  不知道为什么这句怎么样都是False
                    route_code  = routers[0] in IPy.IP(network)
                    if route_code == False:
                        loger('win_dhcp_file: networks:%s,getway:%s,The gateway is not in the network, After checking error!\n'%(
                            network,routers), 422)

                #如果网关为空    
                #if not routers  :
                #    loger('win_dhcp_file: pool %s-%s of %s:getway:%s,Values is Null,After checking error!\n'%(
                #        j[0], j[1], network, routers), 422 )

                #如果网关为空
                if not routers :
                    warning('address_pool', j[0], j[1], network, 'getway', routers)
                #如果DNS服务器参数为空
                if not domain_name_servers :
                    warning('address_pool', j[0], j[1], network, 'DNS server', domain_name_servers)

                time.sleep(0.1)
        # setup 2-2-3:创建保留地址
        excluderange_ip = []
        if win_conf[host].has_key('excluderange'):
            for l in win_conf[host]['excluderange']:                                                  
                #以下四行将所有保留地址放到列表中，供以后固定地址比对
                int_ip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
                ip_int = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
                for i in range(ip_int(l[0]),ip_int(l[1])+1):
                    excluderange_ip.append(int_ip(i))

                return_code = t1.return_creatReservedPool(
                    network, l[0], l[1])
                if return_code == 200 :
                    loger("creat Reserved pool %s-%s of %s success" %
                          (l[0], l[1], network))
                else:
                    loger("creat Reserved pool %s-%s of %s failed and the return_code is %s" %
                          (l[0], l[1], network, return_code), 422)
                time.sleep(0.1)

        # setup 2-2-4:创建固定地址
        if win_conf[host].has_key('Mac'):
            for k in win_conf[host]['Mac']:
                try:
                    comment = '','',k[2],k[3]
                except:
                    comment = []
                return_code = t1.return_creatStaticPool(
                    network, k[0], k[1], routers, domain_name_servers, lease_time, options=options, attrs=comment)
                if return_code == 200 :
                    loger("creat static pool %s==>%s of %s success" %
                          (k[0], k[1], network))
                else:
                    loger("creat static pool %s==>%s of %s failed and the return_code is %s" %
                          (k[0], k[1], network, return_code),422)
                    

                    #如果固定地址在保留地址中则发出告警
                    if k[0] in excluderange_ip:
                        loger(" The reserved address is duplicated with the fixed address \n",422)

                    #MAC地址校验
                    elif not  re.match(r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$", k[1]): 
                        loger(" static_mac  format error ",422)    
                        return_code = t1.return_creatReservedPool(network, k[0], k[0])
                        if return_code == 200 :
                            loger(" static_mac  format error, But creat Reserved pool %s-%s of %s success!!\n" %
                                (k[0], k[0], network),422)
                        

                    time.sleep(0.1)

                    route_code  = routers[0] in IPy.IP(network)
                    if route_code == False:
                        loger('win_dhcp_file: networks:%s,getway:%s,The gateway is not in the network, After checking error!\n'%(network,routers), 422)
                
                #如果网关为空
                if not routers :
                    warning('static_address', k[0], k[1], network, 'getway', routers)
                #如果DNS服务器参数为空
                if not domain_name_servers :
                    warning('static_address', k[0], k[1], network, 'DNS', domain_name_servers)
                    

                time.sleep(0.1)

loger("####Address resources Is created  ####")
os.system('grep optionvalue  windows_dhcp.txt |grep  -wv  "optionvalue 51" |grep -wv  "optionvalue 3" |grep -wv  "optionvalue 6" |grep -wv "optionvalue 15"|grep -wv  "optionvalue 42"|grep -wv "optionvalue 44"|grep -vw "optionvalue 43"|grep -wv "optionvalue 46" |grep -wv "optionvalue 66" |grep -wv "optionvalue 67" |grep -wv "optionvalue 60"  >>  error.log  ')
