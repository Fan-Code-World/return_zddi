#!/usr/bin/env python
# coding=utf-8
import re
import json
import os
import pprint

class HandleWindow:
    #校验mac
    def dispose_mac(self, mac):
        return (':'.join([mac[i:i+2] for i,j in enumerate(mac) if not (i%2)]))

    def analyWindow(self, conf_txt):
        conf_dic = {}
        file = open(conf_txt, 'r');
        for i in file.readlines():
            if 'add scope' in i and 'v6' not in i :
                host = i.split()[5]
                host_mask = i.split()[6]
                conf_dic[host] = {}
                conf_dic[host]['host_mask'] = host_mask 
                    
                conf_dic[host]['host_mask_comment'] = []
                conf_dic[host]['host_mask_comment'].append(i.split()[7].strip('"'))
                #2020-11-6-广州大学windowsdhcp源文件-备注缺少一位
                try:
                    conf_dic[host]['host_mask_comment'].append(i.split()[8].strip('"'))
                except IndexError:
                    conf_dic[host]['host_mask_comment'].append('')
            if 'Scope' in i and 'iprange' in i :
                host = i.split()[4]
                start_ip = i.split()[7].strip('"')
                end_ip = i.split()[8].strip('"')
                conf_dic[host]['pools'] = []
                conf_dic[host]['pools'].append((start_ip, end_ip))
                #print conf_dic[host]['pools']
            if 'Scope' in i and 'optionvalue' in i:
                host = i.split()[4]

                #域名服务器-DNS
                name = []
                if '6' == i.split()[7]:
                    for name_conunt in range(9,len(i.split())):
                        name.append(i.split()[name_conunt].strip().strip( '"' ))
                    conf_dic[host]['domain_name_servers'] = name
                    #print conf_dic[host]['name_server']
                    name = []

                #租约时间
                if '51' == i.split()[7]:
                    less = i.split()[9].strip('"')
                    conf_dic[host]['lease_time'] = less
                    #print conf_dic[host]['less_time']
                #网关
                if '3' == i.split()[7]:
                    #gatway = i.split()[9].strip('"')
                    conf_dic[host]['gatway'] = []
                    conf_dic[host]['gatway'].append(i.split()[9].strip('"'))
                #域名DNS域名
                if '15' == i.split()[7]:
                    option_name = 'domain-name'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #ntp服务器
                if '42' == i.split()[7]:
                    option_name = 'ntp-servers'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #供应商特定信息
                if '43' == i.split()[7]:
                    option_name = 'vendor-encapsulated-options'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #netbios-name-servers
                netbios_name=[]
                if '44' == i.split()[7]:
                    option_name = 'netbios-name-servers'
                    for netbios in range(9,len(i.split())):
                        netbios_name.append(i.split()[netbios].strip().strip( '"' ))
                    option_value = ','.join(netbios_name)
                    conf_dic[host][option_name] = option_value
                    netbios_name=[]
                #WINS/NBT 节点类型
                if '46' == i.split()[7]:
                    option_name = 'netbios-node-type'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #APname option60
                if '60' == i.split()[7]:
                    option_name = 'vendor-class-identifier'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                
                #tftp字段option66
                if '66' == i.split()[7]:
                    option_name = 'tftp_servers'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #tftp字段option67
                if '67' == i.split()[7]:
                    option_name = 'bootfile-name'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value

                #以太网签名-option128---仅分析，不自动添加
                if '128' == i.split()[7]:
                    option_name = 'etherboot-signature'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #ip电话option150---仅分析，不自动添加
                ip_phone = []
                if '150' == i.split()[7]:
                    for name_conunt in range(9,len(i.split())):
                        ip_phone.append(i.split()[name_conunt].strip().strip( '"' ))
                    conf_dic[host]['ip_phone'] = ip_phone
                    ip_phone = []

            if 'Scope' in i and 'reservedip' in i :
                host = i.split()[4]
                Mac_ip = i.split()[7]
                Mac = self.dispose_mac(i.split()[8])
                #print (host)


                #以太网签名-option128---仅分析，不自动添加
                if '128' == i.split()[7]:
                    option_name = 'etherboot-signature'
                    option_value = i.split()[-1].strip('"')
                    conf_dic[host][option_name] = option_value
                #ip电话option150---仅分析，不自动添加
                ip_phone = []
                if '150' == i.split()[7]:
                    for name_conunt in range(9,len(i.split())):
                        ip_phone.append(i.split()[name_conunt].strip().strip( '"' ))
                    conf_dic[host]['ip_phone'] = ip_phone
                    ip_phone = []

            if 'Scope' in i and 'reservedip' in i :
                host = i.split()[4]
                Mac_ip = i.split()[7]
                Mac = self.dispose_mac(i.split()[8])
                #print (host)
                if conf_dic[host].has_key('Mac'):
                    conf_dic[host]['Mac'].append((Mac_ip,Mac,
                        i.split()[9].strip('"'),i.split()[10].strip('"'))) 
                else:
                    conf_dic[host]['Mac'] = []
                    conf_dic[host]['Mac'].append((Mac_ip,Mac,
                        i.split()[9].strip('"'),i.split()[10].strip('"'))) 
                #print conf_dic[host]['Mac_str']
            if 'Scope' in i and 'excluderange' in i :
                host = i.split()[4]
                start_ip = i.split()[7].strip('"')
                end_ip = i.split()[8].strip('"')
                if conf_dic[host].has_key('excluderange'):
                    conf_dic[host]['excluderange'].append((start_ip, end_ip))
                else:
                    conf_dic[host]['excluderange'] = []
                    conf_dic[host]['excluderange'].append((start_ip, end_ip))
                #print conf_dic[host]['excluderange'] 

            #识别win全局域名服务器
            if 'set optionvalue 6' in i and 'Scope' not in i  :
                name = []
                for name_conunt in range(7,len(i.split())):
                    name.append(i.split()[name_conunt].strip().strip( '"' ))
                conf_dic['global_domain_name_servers'] = name

            #识别全局 swap-server-ipadder
            if 'set optionvalue 16' in i and 'Scope' not in i  :
                name = []
                for name_conunt in range(7,len(i.split())):
                    name.append(i.split()[name_conunt].strip().strip( '"' ))
                conf_dic['global_swap_servers'] = name

            #识别全局 tftp-server-ipadder
            if 'set optionvalue 66' in i and 'Scope' not in i  :
                name = []
                for name_conunt in range(7,len(i.split())):
                    name.append(i.split()[name_conunt].strip().strip( '"' ))
                conf_dic['global_tftp_servers'] = name

        file.close()
        return  conf_dic

if __name__ == '__main__':
    t1 = HandleWindow()
    conf_content = t1.analyWindow('windows_dhcp.txt')
    print json.dumps(conf_content,encoding = 'utf-8', ensure_ascii=False)
    #print json.dumps(conf_content,encoding = 'utf-8', ensure_ascii=False,indent=10,separators=(',', ': ')).replace(',','')
    #pprint.pprint(conf_content)

