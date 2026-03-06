#!/usr/bin/env python3
"""
MikroTik 设备扫描器 - 类似 Winbox 的扫描功能

Winbox 扫描原理：
1. 监听 UDP 5678 端口的广播报文
2. MikroTik 设备会定期发送发现广播（MAC Telnet/Winbox 协议）
3. 解析广播报文获取设备信息（MAC 地址、IP、身份标识等）

参考：https://wiki.mikrotik.com/wiki/Manual:MAC_Telnet
"""

import socket
import struct
import time
import random
from typing import List, Dict, Optional, Tuple


class MikroTikScanner:
    """MikroTik 设备扫描器（类似 Winbox）"""
    
    # Winbox/MAC Telnet 协议相关
    WINBOX_PORT = 5678
    BROADCAST_ADDR = '255.255.255.255'
    
    # 协议字段类型
    TYPE_IDENTITY = 0x0001
    TYPE_IP = 0x0005
    TYPE_MAC = 0x0006
    TYPE_TIMESTAMP = 0x0007
    TYPE_VERSION = 0x0008
    TYPE_PLATFORM = 0x0009
    TYPE_BOARD = 0x000A
    
    def __init__(self, timeout: float = 3.0):
        """
        初始化扫描器
        
        Args:
            timeout: 监听超时（秒）
        """
        self.timeout = timeout
        self.discovered_devices: List[Dict] = []
    
    def listen_for_broadcasts(self) -> List[Dict]:
        """
        监听 MikroTik 设备的广播报文（Winbox 方式）
        
        Returns:
            发现的设备列表
        """
        print("🔍 监听 MikroTik 广播报文（类似 Winbox）...")
        print(f"   监听端口：{self.WINBOX_PORT}")
        print(f"   超时时间：{self.timeout}秒")
        print()
        
        devices = {}  # 用 MAC 地址去重
        
        try:
            # 创建 UDP socket，绑定到 5678 端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # 绑定到所有接口的 5678 端口
            sock.bind(('0.0.0.0', self.WINBOX_PORT))
            sock.settimeout(1.0)
            
            print("  ✅ 开始监听...\n")
            
            start_time = time.time()
            
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = sock.recvfrom(2048)
                    
                    # 解析 MikroTik 广播报文
                    device = self._parse_discovery_packet(data, addr[0])
                    
                    if device:
                        mac = device.get('mac', '')
                        if mac and mac not in devices:
                            devices[mac] = device
                            print(f"  ✅ 发现：{device.get('identity', 'Unknown')}")
                            print(f"      IP: {addr[0]}")
                            print(f"      MAC: {mac}")
                            if device.get('platform'):
                                print(f"      型号：{device.get('platform')}")
                            if device.get('version'):
                                print(f"      版本：{device.get('version')}")
                            print()
                
                except socket.timeout:
                    continue
                except Exception as e:
                    pass
            
            sock.close()
            
        except PermissionError:
            print("  ❌ 权限不足，无法绑定 5678 端口（需要 root 权限）")
        except OSError as e:
            print(f"  ❌ 端口绑定失败：{e}")
            print("     可能端口已被占用，或需要 root 权限")
        
        self.discovered_devices = list(devices.values())
        return self.discovered_devices
    
    def _parse_discovery_packet(self, data: bytes, source_ip: str) -> Optional[Dict]:
        """
        解析 MikroTik 发现协议报文
        
        报文格式：
        - 6 字节：目标 MAC（通常是 FF:FF:FF:FF:FF:FF）
        - 2 字节：协议类型
        - N 字节：TLV 数据（Type-Length-Value）
        
        Args:
            data: 原始报文数据
            source_ip: 源 IP 地址
        
        Returns:
            解析后的设备信息
        """
        if len(data) < 8:
            return None
        
        device = {
            'ip': source_ip,
            'source': 'broadcast'
        }
        
        try:
            # 跳过前 6 字节（目标 MAC）
            offset = 6
            
            # 读取协议类型（2 字节）
            proto_type = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
            
            # 解析 TLV 数据
            while offset < len(data) - 4:
                # 类型（2 字节）
                tlv_type = struct.unpack('!H', data[offset:offset+2])[0]
                offset += 2
                
                # 长度（2 字节）
                tlv_len = struct.unpack('!H', data[offset:offset+2])[0]
                offset += 2
                
                # 值
                if offset + tlv_len > len(data):
                    break
                
                value = data[offset:offset+tlv_len]
                offset += tlv_len
                
                # 根据类型解析
                if tlv_type == self.TYPE_IDENTITY:
                    device['identity'] = value.decode('utf-8', errors='ignore').strip()
                elif tlv_type == self.TYPE_MAC:
                    if len(value) == 6:
                        device['mac'] = ':'.join([f'{b:02X}' for b in value])
                elif tlv_type == self.TYPE_IP:
                    # 已经有 source_ip 了
                    pass
                elif tlv_type == self.TYPE_PLATFORM:
                    device['platform'] = value.decode('utf-8', errors='ignore').strip()
                elif tlv_type == self.TYPE_VERSION:
                    device['version'] = value.decode('utf-8', errors='ignore').strip()
                elif tlv_type == self.TYPE_BOARD:
                    device['board'] = value.decode('utf-8', errors='ignore').strip()
            
            # 至少要有 MAC 地址才认为是有效的 MikroTik 设备
            if 'mac' in device:
                return device
            
        except Exception as e:
            pass
        
        return None
    
    def send_discovery_request(self) -> List[Dict]:
        """
        主动发送发现请求，触发设备响应
        
        Returns:
            发现的设备列表
        """
        print("🔍 发送发现请求广播...")
        
        devices = {}
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1.0)
            
            # 构建发现请求报文
            # 格式：目标 MAC(6) + 协议类型 (2) + TLV 数据
            my_mac = b'\x00\x00\x00\x00\x00\x00'  # 随便填
            proto_type = struct.pack('!H', 0x0001)  # 发现请求
            
            # 发送请求
            discovery_msg = my_mac + proto_type
            sock.sendto(discovery_msg, (self.BROADCAST_ADDR, self.WINBOX_PORT))
            
            # 接收响应
            start_time = time.time()
            while time.time() - start_time < 3.0:
                try:
                    data, addr = sock.recvfrom(2048)
                    device = self._parse_discovery_packet(data, addr[0])
                    
                    if device:
                        mac = device.get('mac', '')
                        if mac and mac not in devices:
                            devices[mac] = device
                            print(f"  ✅ 发现：{device.get('identity', 'Unknown')} ({addr[0]})")
                except socket.timeout:
                    break
                except:
                    pass
            
            sock.close()
            
        except Exception as e:
            print(f"  ⚠️ 发送请求失败：{e}")
        
        return list(devices.values())
    
    def from_neighbors(self, api_host: str, api_user: str = 'admin', 
                       api_pass: str = '') -> List[Dict]:
        """
        从已连接的 MikroTik 设备获取邻居信息
        
        Args:
            api_host: MikroTik API 地址
            api_user: 用户名
            api_pass: 密码
        
        Returns:
            邻居设备列表
        """
        print(f"🔍 从 {api_host} 获取邻居信息...")
        
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            from client import MikroTikAPI
            
            api = MikroTikAPI(api_host, api_user, api_pass)
            if api.connect() and api.login():
                # 获取邻居
                neighbors = api.run_command('/ip/neighbor/print')
                
                devices = []
                for nbr in neighbors:
                    identity = nbr.get('identity', 'Unknown')
                    address = nbr.get('address', '')
                    mac = nbr.get('mac-address', '')
                    interface = nbr.get('interface', '')
                    platform = nbr.get('platform', '')
                    
                    if address:
                        device = {
                            'ip': address,
                            'identity': identity,
                            'mac': mac,
                            'interface': interface,
                            'platform': platform,
                            'version': nbr.get('version', ''),
                            'source': 'neighbor'
                        }
                        devices.append(device)
                        print(f"  ✅ 发现：{identity} ({address})")
                
                api.disconnect()
                return devices
            else:
                print(f"  ❌ 无法连接到 {api_host}")
        except Exception as e:
            print(f"  ❌ 错误：{e}")
        
        return []
    
    def format_results(self) -> str:
        """格式化扫描结果"""
        if not self.discovered_devices:
            return "  (未发现设备)"
        
        lines = []
        lines.append(f"\n共发现 {len(self.discovered_devices)} 个设备:\n")
        
        for i, device in enumerate(self.discovered_devices, 1):
            identity = device.get('identity', 'Unknown')
            ip = device.get('ip', 'N/A')
            mac = device.get('mac', '')
            platform = device.get('platform', '')
            version = device.get('version', '')
            source = device.get('source', 'unknown')
            
            lines.append(f"  [{i}] {identity}")
            lines.append(f"      IP: {ip}")
            if mac:
                lines.append(f"      MAC: {mac}")
            if platform:
                lines.append(f"      型号：{platform}")
            if version:
                lines.append(f"      版本：{version}")
            
            if source == 'neighbor':
                lines.append(f"      来源：邻居发现")
            elif source == 'broadcast':
                lines.append(f"      来源：广播监听")
            else:
                lines.append(f"      来源：主动发现")
            
            lines.append("")
        
        return "\n".join(lines)


def scan_network() -> str:
    """
    扫描网络中的 MikroTik 设备（Winbox 方式）
    
    Returns:
        格式化的扫描结果
    """
    scanner = MikroTikScanner(timeout=5.0)
    
    # 方法 1: 监听广播
    devices = scanner.listen_for_broadcasts()
    
    # 如果没有发现设备，尝试主动发送请求
    if not devices:
        print("\n  未监听到广播，尝试主动发送发现请求...")
        devices = scanner.send_discovery_request()
    
    return scanner.format_results()


if __name__ == '__main__':
    print(scan_network())
