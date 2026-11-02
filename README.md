# FlashFuzz
# ⚡ Async HW Register Fuzzer & Memory Mapper

> High-performance, asynchronous hardware fuzzing and peripheral memory mapping suite designed for low-level register vulnerability analysis and timing anomaly detection.

---

## 🛠️ About the Project

**Async HW Register Fuzzer** is a professional-grade testing utility built in Python 3, leveraging `asyncio` for ultra-fast, non-blocking concurrent execution. It targets embedded system peripherals and register arrays to identify crashes, voltage glitch vulnerabilities, buffer boundary leaks, and hidden latency spikes.

Whether you are testing simulated register maps or validating hardware communication protocols, this suite automates stress testing and generates structured diagnostic reports.

---

## 🚀 Key Features

* **⚡ Asynchronous Core:** Powered by Python's `asyncio` to execute dozens of verification vectors in milliseconds.
* **🗺️ Peripheral Memory Mapping:** Scan sequential register blocks (e.g., from `0x40012000` onwards using `--base-reg` and `--steps`) to isolate vulnerable hardware addresses.
* **🎯 Smart Payload Generation:** Injects customized low-level test vectors including:
  * `REG_OVERFLOW` (Register overflow injection)
  * `VOLTAGE_GLITCH` (Simulated power/clock instability)
  * `BUFFER_BOUNDARY_TEST` (Memory boundary limits)
  * `NORMAL_CLOCK_SYNC` (Baseline health checks)
* **⏱️ Latency Spike Analysis:** Detects microsecond-level timing anomalies where a register doesn't crash (`200 OK`) but suffers severe processing delays.
* **📊 Structured JSON Reports:** Automatically exports machine-readable logs and fault summaries for post-analysis.

---

## ⚙️ Installation & Requirements

Ensure you have **Python 3.x** installed. No heavy external libraries required (uses standard Python libraries).

```bash
# Clone the repository
git clone [https://github.com/your-username/async-hw-fuzzer.git](https://github.com/your-username/async-hw-fuzzer.git)
cd async-hw-fuzzer

python hw_master_suite.py --reg 0x40012000 --count 20

python hw_master_suite.py --base-reg 0x40012000 --steps 4 --count 15

python hw_master_suite.py --reg 0x40012000 --type VOLTAGE_GLITCH -v
ArgumentDescriptionDefault
--base-regStarting target register hex address0x40012000
--stepsNumber of sequential registers to map4
--countTest vectors / packets per register10
--typeSpecific payload filter (REG_OVERFLOW, VOLTAGE_GLITCH, etc.)all
--thresholdLatency anomaly threshold in seconds0.010
-v, --verboseEnable real-time live packet loggingFalse

{
    "base_register": "0x40012000",
    "scanned_steps": 4,
    "total_tested": 40,
    "total_critical_faults": 12,
    "results": [
        {
            "register": "0x40012000",
            "packet_id": 1,
            "payload_type": "VOLTAGE_GLITCH",
            "payload_data": "0x50D1_ERR",
            "latency": 0.0117,
            "status_code": 503,
            "status": "ANOMALİ (HATA KODU)"
        }
    ]
}

