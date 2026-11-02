import argparse
import asyncio
import json
import random
import time


# 1. BÖLÜM: Akıllı ve Filtrelenebilir Payload Üretici
def generate_hw_payload(packet_id, forced_type=None):
    payload_types = [
        "REG_OVERFLOW",
        "VOLTAGE_GLITCH",
        "BUFFER_BOUNDARY_TEST",
        "NORMAL_CLOCK_SYNC",
    ]
    p_type = (
        forced_type
        if forced_type and forced_type != "all"
        else random.choice(payload_types)
    )

    if p_type != "NORMAL_CLOCK_SYNC":
        payload_data = f"0x{random.randint(0x1000, 0xFFFF):04X}_ERR"
    else:
        payload_data = "0x0000_SYNC_OK"

    return {"id": packet_id, "type": p_type, "data": payload_data}


# 2. BÖLÜM: Donanım Simülasyonu + Zaman Aşımı Analizi
async def fuzz_hardware_register(
    register_addr, payload, latency_threshold, verbose
):
    delay = round(random.uniform(0.001, 0.015), 4)
    await asyncio.sleep(delay)

    if payload["type"] in [
        "REG_OVERFLOW",
        "VOLTAGE_GLITCH",
        "BUFFER_BOUNDARY_TEST",
    ]:
        status_code = random.choice([200, 500, 503, 409])
    else:
        status_code = 200

    is_timing_anomaly = delay > latency_threshold
    is_status_anomaly = status_code >= 400
    is_anomaly = is_status_anomaly or is_timing_anomaly

    if is_status_anomaly:
        status_str = "ANOMALİ (HATA KODU)"
    elif is_timing_anomaly:
        status_str = "ANOMALİ (GECİKME SAPMASI)"
    else:
        status_str = "Stabil"

    result = {
        "register": register_addr,
        "packet_id": payload["id"],
        "payload_type": payload["type"],
        "payload_data": payload["data"],
        "latency": delay,
        "status_code": status_code,
        "status": status_str,
    }

    if verbose:
        print(
            f"[CANLI] Reg: {register_addr} | ID: {result['packet_id']} | Tür:"
            f" {result['payload_type']} | Kod: {result['status_code']}"
        )

    return result


# 3. BÖLÜM: Çoklu Register Bellek Haritalama Motoru
async def run_memory_mapping_scan(
    base_reg_str, reg_count, total_packets, payload_type, latency_threshold, verbose
):
    base_addr = int(base_reg_str, 16)
    master_results = []
    all_anomalies = []

    print(f"[*] Başlangıç Register: {base_reg_str} ({reg_count} Adres taranacak)")
    print(
        f"[*] Filtre: {payload_type} | Eşik: {latency_threshold}s | Vektör/Reg:"
        f" {total_packets}\n"
    )

    start_time = time.time()

    for step in range(reg_count):
        current_addr = hex(base_addr + (step * 4)).upper()
        print(f"[*] Hedef Adres Taranıyor -> {current_addr}")

        tasks = []
        for i in range(1, total_packets + 1):
            payload = generate_hw_payload(i, forced_type=payload_type)
            tasks.append(
                fuzz_hardware_register(
                    current_addr, payload, latency_threshold, verbose
                )
            )

        results = await asyncio.gather(*tasks)
        master_results.extend(results)

        reg_anomalies = [r for r in results if "ANOMALİ" in r["status"]]
        all_anomalies.extend(reg_anomalies)

        if reg_anomalies:
            print(
                f"    [!] {current_addr} adresinde {len(reg_anomalies)} anomali"
                " tespit edildi!"
            )
        else:
            print(f"    [+] {current_addr} kararlı.")

    elapsed = round(time.time() - start_time, 3)
    print(f"\n[*] Bellek Haritalama Taraması Bitti! Toplam Süre: {elapsed} saniye")
    return master_results, all_anomalies


# 4. BÖLÜM: Ana Çalıştırıcı ve CLI
async def main():
    parser = argparse.ArgumentParser(
        description=(
            "FlashFuzz: Gelişmiş Donanım Bellek Haritalama ve Fuzzing Suite"
        )
    )
    parser.add_argument(
        "--base-reg",
        type=str,
        default="0x40012000",
        help="Başlangıç Register Adresi",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=4,
        help="Taranacak ardışık register sayısı",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Her register için test vektör sayısı",
    )
    parser.add_argument(
        "--type",
        type=str,
        default="all",
        choices=[
            "all",
            "REG_OVERFLOW",
            "VOLTAGE_GLITCH",
            "BUFFER_BOUNDARY_TEST",
            "NORMAL_CLOCK_SYNC",
        ],
        help="Spesifik payload filtresi",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.010,
        help="Gecikme anomali eşiği",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Canlı akışı göster",
    )

    args = parser.parse_args()

    results, anomalies = await run_memory_mapping_scan(
        args.base_reg,
        args.steps,
        args.count,
        args.type,
        args.threshold,
        args.verbose,
    )

    report = {
        "base_register": args.base_reg,
        "scanned_steps": args.steps,
        "total_tested": len(results),
        "total_critical_faults": len(anomalies),
        "results": results,
    }

    filename = "flash_fuzz_report.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("      FLASHFUZZ ZAFİYET ÖZET RAPORU")
    print("=" * 60)
    print(f"[*] Taranan Toplam Adres : {args.steps} Register")
    print(f"[*] Toplam Test Vektörü  : {len(results)}")
    print(f"[*] Toplam Kritik Hata   : {len(anomalies)}")

    if anomalies:
        print("\n[!] En Kritik Zafiyet Noktaları (Örnekler):")
        for a in anomalies[:6]:
            print(
                f"   -> Adres: {a['register']} | ID: {a['packet_id']} | Tür:"
                f" {a['payload_type']} | Durum: {a['status']}"
            )
    else:
        print("\n[+] Taranan bellek bloğu tamamen kararlı.")

    print("=" * 60)
    print(f"[*] Haritalama raporu diske kaydedildi: {filename}")


if __name__ == "__main__":
    asyncio.run(main())
