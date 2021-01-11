#!/usr/bin/env python
# coding=utf-8
import json
import os
import IPy
import requests
requests.packages.urllib3.disable_warnings()

class NetworkManager:
    def sendCmd(self, url, params, user, passwd):
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(
            params), headers=headers, auth=(user, passwd), verify=False)    

        return (r.status_code)

    mode = 'curl -l -m 10 -o /dev/null -s -w %{http_code} -X  POST '
    def isIp(self, address):
        try:
            IPy.IP(address)
            return True
        except:
            return False

    def __init__(self,cms_node='local.master', cms_ip='127.0.0.1', cms_user='admin', 
        cms_passwd='admin', Automatic_binding='no', lang='zh'):
        if self.isIp(cms_ip):
            self.__cms_ip = cms_ip
        else:
            print (cms_ip)
            print('cms_ip is illegal')
            raise Exception
        self.__Ipbinding = Automatic_binding
        self.__cms_node = cms_node
        self.__cms_user = cms_user
        self.__cms_passwd = cms_passwd
        self.__cms_lang = lang

    def params_comment(self,attrs=[]):
        params=[]
        if len(attrs) != 0:
            for i in range(1, len(attrs) + 1):
                params.append('"key_%s"'%(i) + ':"%s"'%(attrs[i - 1]))
            params = ','.join(params)
            if params :
                return  ',' + params
            else :
                return ('')
        else:
            return ('')
            
    def host_mask(self, hostmask):
        return (hostmask.split('/')[0] + '$' + hostmask.split('/')[1])
        
    #创建网络资源
    def return_creatNetwork_one(self, networks, attrs=[]):   
        url = 'https://%s:20120/multi-networks' % (self.__cms_ip)
        params = {'comment': '',
                  'templates': '0',
                  'name_value': '默认组',
                  'group_type': 'name',
                  'owners': [self.__cms_node],
                  'networks': networks }
        if len(attrs) != 0:
            for i in range(1, len(attrs) + 1):
                params['key_' + str(i)] = attrs[i - 1]
        return (self.sendCmd(url, params, self.__cms_user, self.__cms_passwd))

    #创建地址池资源
    def return_DynamicPool(self, networks, ip_start, ip_end, routers, 
        domain_name_servers, lease_time,options=[]):

        url = 'https://%s:20120/networks/%s/dhcp-resources' % (
            self.__cms_ip, self.host_mask(networks))
        params = {'comment':'',
                  'type':'dynamic',
                  #'owner':[self.__cms_node],   3.12版本可以加[]
                  'owner':self.__cms_node,
                  'ip_start':ip_start,
                  'ip_end':ip_end,
                  'def_value':'10800',
                  'def_unit':'1',
                  'max_value':'10800',
                  'max_unit':'1',
                  'min_value':'300',
                  'min_unit':'1',
                  'routers':routers,
                  'domain_name_servers':domain_name_servers ,
                  'domain_name':'',
                  'acls':['any'],
                  'options': options, 
                  'auto_bind':self.__Ipbinding,
                  'bootp':'yes',
                  'inherit_default_lease_time':'no',
                  'inherit_max_lease_time':'no',
                  'inherit_min_lease_time':'no',
                  'inherit_domain_name_servers':'no',
                  'inherit_routers':'no',
                  'inherit_domain_name':'yes',
                  'inherit_options':'yes',
                  'inherit_acls':'yes',
                  'inherit_auto_bind':'no',
                  'inherit_bootp':'yes',
                  'max_lease_time':'10800'}

        if  params['options']:
            params['inherit_options']='no'
        return (self.sendCmd(url, params, self.__cms_user, self.__cms_passwd))
    
    #创建保留地址资源
    def return_creatReservedPool(self, networks, ip_start, ip_end):

        url = 'https://%s:20120/networks/%s/dhcp-resources' % (
            self.__cms_ip, self.host_mask(networks))
        params = {'owner':self.__cms_node,
                  'type':'reservation',
                  'ip_start':ip_start,
                  'ip_end':ip_end } 

        return (self.sendCmd(url, params, self.__cms_user, self.__cms_passwd))

    #创建固定地址资源
    def return_creatStaticPool(self, networks, ip_address, mac_address, 
        routers, domain_name_servers,  lease_time, attrs=[], options=[]):

            url =  'https://%s:20120/networks/%s/dhcp-resources' % (
                self.__cms_ip, self.host_mask(networks))
            params = {'comment':'',
                      'owner':[self.__cms_node],
                      #'owner':self.__cms_node,  #3.10版本不需要方括号
                      'type':'static',
                      'ip_start':ip_address,
                      'hardware_ethernet':mac_address,
                      'def_value':'10800',
                      'def_unit':'1',
                      'max_value':'10800',
                      'max_unit':'1',
                      'min_value':'300',
                      'min_unit':'1',
                      'routers':routers,
                      'domain_name_servers':domain_name_servers,
                      'domain_name':'',
                      'options': options, 
                      'inherit_default_lease_time':'no',
                      'inherit_max_lease_time':'no',
                      'inherit_min_lease_time':'no',
                      'inherit_domain_name_servers':'no',
                      'inherit_routers':'no',
                      'inherit_domain_name':'yes',
                      'inherit_options':'yes',
                      'max_lease_time':'86400',
                      'max_lease_time_unit':'1',
                      'default_lease_time':'43200',
                      'default_lease_time_unit':'1',
                      'min_lease_time':'300',
                      'min_lease_time_unit':'1' }

            if len(attrs) != 0:
                for i in range(1, len(attrs) + 1):
                    params['key_' + str(i)] = attrs[i - 1]

            if  params.has_key('options'):
                params['inherit_options']='no'

            return (self.sendCmd(url, params, self.__cms_user, self.__cms_passwd))
                
if __name__ == '__main__':
    t1 = NetworkManager()
    return_code = t1.return_creatNetwork_two(["192.168.1.0/24"],attrs=[])
    print ('code is %s' %(return_code)) 
    #return_code = t1.return_DynamicPool("192.168.1.0/24",'192.168.1.10','192.168.1.20','192.168.1.254',["8.8.8.8"],"300",options=[])
    #print ('code is %s' %(return_code)) 
    #date = t1.return_creatStaticPool("192.168.1.0/24",'192.168.1.100','3c:4a:92:bf:16:3c','192.168.1.254',["8.8.8.8"],"300",options=[])
