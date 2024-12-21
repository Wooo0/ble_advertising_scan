import asyncio
from bleak import BleakScanner
from datetime import datetime

async def print_device_info(device, advertisement_data):
    print("\n=== Device Information ===")
    print(f"Device Name: {device.name or 'Unknown'}")
    print(f"Address: {device.address}")
    print(f"RSSI: {advertisement_data.rssi} dBm")
    
    print("\n--- Advertisement Data ---")
    
    # 服务 UUID
    if hasattr(advertisement_data, 'service_uuids') and advertisement_data.service_uuids:
        print("\nService UUIDs:")
        for uuid in advertisement_data.service_uuids:
            print(f"  - {uuid}")
    
    # 制造商数据
    if hasattr(advertisement_data, 'manufacturer_data') and advertisement_data.manufacturer_data:
        print("\nManufacturer Data:")
        for company_id, data in advertisement_data.manufacturer_data.items():
            print(f"  Company ID: 0x{company_id:04X}")
            print(f"  Data: {data.hex().upper()}")
            
            # 尝试解析一些常见的制造商数据格式
            try:
                if company_id == 0x004C:  # Apple
                    print("  (Apple device)")
                elif company_id == 0x07D0:  # Tuya
                    print("  (Tuya device)")
                    # 可以在这里添加更多的制造商数据解析
            except Exception as e:
                print(f"  (Error parsing manufacturer specific data: {e})")
            
    # 服务数据
    if hasattr(advertisement_data, 'service_data') and advertisement_data.service_data:
        print("\nService Data:")
        for uuid, data in advertisement_data.service_data.items():
            print(f"  UUID: {uuid}")
            print(f"  Data: {data.hex().upper()}")
            
            # 尝试解析一些常见的服务数据
            try:
                if str(uuid).startswith("0000a201"):  # Tuya Service
                    print("  (Tuya service data)")
                    # 可以在这里添加更多的服务数据解析
            except Exception as e:
                print(f"  (Error parsing service data: {e})")
            
    # 本地名称
    if hasattr(advertisement_data, 'local_name') and advertisement_data.local_name:
        print(f"\nLocal Name: {advertisement_data.local_name}")
        
    # 发射功率
    if hasattr(advertisement_data, 'tx_power') and advertisement_data.tx_power is not None:
        print(f"\nTX Power: {advertisement_data.tx_power} dBm")
        
    # 外观值
    if hasattr(advertisement_data, 'appearance') and advertisement_data.appearance is not None:
        print(f"\nAppearance: {advertisement_data.appearance}")
        
    # 标志（安全检查）
    try:
        if hasattr(advertisement_data, 'flags') and advertisement_data.flags:
            print("\nFlags:")
            flag_meanings = {
                0x01: "LE Limited Discoverable Mode",
                0x02: "LE General Discoverable Mode",
                0x04: "BR/EDR Not Supported",
                0x08: "Simultaneous LE and BR/EDR (Controller)",
                0x10: "Simultaneous LE and BR/EDR (Host)"
            }
            for flag in advertisement_data.flags:
                meaning = flag_meanings.get(flag, "Unknown flag")
                print(f"  - 0x{flag:02X}: {meaning}")
    except AttributeError:
        pass  # 没有flags属性时静默处理

    print("\n" + "="*30)

async def scan_for_ble_devices():
    print("Starting BLE scan...")
    print(f"Scan started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        discovered_devices = {}
        
        def detection_callback(device, advertisement_data):
            discovered_devices[device.address] = (device, advertisement_data)
        
        scanner = BleakScanner(detection_callback)
        await scanner.start()
        await asyncio.sleep(5.0)  # 扫描5秒
        await scanner.stop()
        
        if discovered_devices:
            print(f"\nDiscovered {len(discovered_devices)} BLE device(s):")
            for device, adv_data in discovered_devices.values():
                await print_device_info(device, adv_data)
        else:
            print("\nNo BLE devices found nearby.")
            
    except Exception as e:
        print(f"Error during scanning: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        print(f"\nScan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def save_scan_results(discovered_devices):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data = []
    
    for device, adv_data in discovered_devices.values():
        device_data = {
            "timestamp": datetime.now().isoformat(),
            "name": device.name,
            "address": device.address,
            "rssi": adv_data.rssi,
            "service_uuids": list(adv_data.service_uuids) if hasattr(adv_data, 'service_uuids') and adv_data.service_uuids else [],
            "manufacturer_data": {
                hex(k): list(v) for k, v in adv_data.manufacturer_data.items()
            } if hasattr(adv_data, 'manufacturer_data') and adv_data.manufacturer_data else {},
            "service_data": {
                str(k): list(v) for k, v in adv_data.service_data.items()
            } if hasattr(adv_data, 'service_data') and adv_data.service_data else {},
            "local_name": adv_data.local_name if hasattr(adv_data, 'local_name') else None,
            "tx_power": adv_data.tx_power if hasattr(adv_data, 'tx_power') else None
        }
        data.append(device_data)
    
    with open(f"ble_scan_{timestamp}.json", "w") as f:
        import json
        json.dump(data, f, indent=2)
        print(f"\nScan results saved to: ble_scan_{timestamp}.json")

def main():
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:
        pass
    
    asyncio.run(scan_for_ble_devices())

if __name__ == "__main__":
    main()
