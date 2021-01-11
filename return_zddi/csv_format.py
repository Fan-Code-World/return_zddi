#!/usr/bin/env python
# coding=utf-8
import csv
import time
import IPy
import re
import io
import copy


def csvformat(win_conf):
    nowdate = time.strftime("%Y%m%d%H%M",time.gmtime())
    nowfile = nowdate + '_windows.csv'
    
    #python2可以用file替代open
    csvfile =  open(nowfile,'w');
    csv_writer = csv.writer(csvfile)
    
    #先写入columns_name
    csv_writer.writerow(['网络地址', 
                         '子网掩码', 
                         '网络/掩码', 
                         '地址类型', 
                         '地址池', 
                         '网关', 
                         'MAC地址', 
                         '租约时间', 
                         '域名服务器', 
                         'addr_pool_comment_A', 
                         'addr_pool_comment_B', 
                         'static_addr_comment_C', 
                         'static_addr_comment_D', 
                         'option'])
    
    #写入多行用writerows
    #csv_writer.writerows([[0,1,3],[1,2,3],[2,3,4]])
    del_list=['lease_time', 'excluderange', 'pools', 'Mac', 'domain_name_servers', 'host_mask', 'host_mask_comment', 'gatway']
    
    for host in win_conf:
        try :
            if win_conf[host].has_key('host_mask_comment'):
                comment = win_conf[host]['host_mask_comment'][0]
                comment2 = win_conf[host]['host_mask_comment'][1]
        except AttributeError:
            continue
        
        network = str(IPy.IP(host).make_net(win_conf[host]['host_mask']))
        if win_conf[host].has_key('gatway'):
            routers = map(lambda x: re.sub(',', '', x),
                          win_conf[host]['gatway'])
        else:
            routers = []
        routers = ','.join(routers)
        
        if win_conf[host].has_key('domain_name_servers'):
            domain_name_servers = map(lambda x: re.sub(
                ',', '', x), win_conf[host]['domain_name_servers'])
        elif win_conf.has_key('global_domain_name_servers'):
            domain_name_servers = win_conf['global_domain_name_servers']
    
        else :
            domain_name_servers = []
        domain_name_servers = ','.join(domain_name_servers)
        
        if win_conf[host].has_key('acls'):
            acls = map(lambda x: total_acls[x], win_conf[host]['acls'])
        else:
            acls = ['any']
        if win_conf[host].has_key('lease_time'):
            lease_time = win_conf[host]['lease_time']
        else:
            lease_time = '43200'
    
        #将option整理为一个列表,循环删除指定列表
        moment_conf = copy.deepcopy(win_conf)
        host_list = moment_conf[host].keys()
        for n in host_list :
            if n in del_list:
                del  moment_conf[host][n]
            #print win_conf[host]
        win_option = moment_conf[host]
        #print win_option
        
        if win_conf[host].has_key('pools'):
            for j in win_conf[host]['pools']:
    
                csv_writer.writerow([ host,
                                      win_conf[host]['host_mask'],
                                      network,
                                      'ipv4地址池',
                                      j[0]+'-'+j[1],
                                      routers,
                                      ' ',
                                      lease_time,
                                      domain_name_servers,
                                      comment,
                                      comment2,
                                      '',
                                      '',
                                      win_option,
                                    ])
    
        if win_conf[host].has_key('excluderange'):
            for l in win_conf[host]['excluderange']:
    
                csv_writer.writerow([ host,
                                      win_conf[host]['host_mask'],
                                      network,
                                      'ipv4保留地址池',
                                      l[0]+'-'+l[1],
                                      ' ',
                                      ' ',
                                      ' ',
                                      ' ',
                                      ' ',
                                     ])
    
        if win_conf[host].has_key('Mac'):
            for k in win_conf[host]['Mac']:
                try:
                    comment = '','',k[2],k[3]
                except:
                    comment = []
            
                csv_writer.writerow([ host,
                                      win_conf[host]['host_mask'],
                                      network,
                                      'ipv4固定地址',
                                      k[0]+'-'+k[0],
                                      routers,
                                      k[1],
                                      lease_time,
                                      domain_name_servers,
                                      '' ,
                                      '' ,
                                      k[2].decode("string_escape"),
                                      k[3].decode("string_escape"),
                                      win_option,
                                    ])
    
    
#grep optionvalue  windows_dhcp.txt |grep  -wv  "optionvalue 51" |grep -wv  "optionvalue 3" |grep -wv  "optionvalue 6" 
