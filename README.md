## สมาชิกกลุ่ม
1. 6810110066 นาย ซัซวาลย์ บินสะอิ
2. 6810110055 นาย ชัชนันท์ บุญส่ง
3. 6810110324 นาย วิญญู สิงห์สาธร
4. 6810110448 นาย จิระธาดา พัดบุรี

## ไฟล์แต่ละไฟล์ทำอะไร

- gimbal_pid.py — ไฟล์หลักสำหรับควบคุมหุ่นยนต์ RoboMaster โดยใช้ PID ควบคุมการเลี้ยว yaw/pitch, ตรวจจับ marker, ยิง IR, และบันทึกข้อมูลเวลายิงและมุมกิมบอลลง CSV
- gimbal_response.csv — ไฟล์ข้อมูลเวลาจริงที่บันทึกจาก gimbal เช่น เวลา, มุม yaw, มุม pitch, เป้าหมาย, และสถานะการยิง
- plot_response.py — ไฟล์สำหรับอ่าน CSV แล้ววาดกราฟเปรียบเทียบความสัมพันธ์ระหว่างเวลาและมุม yaw/pitch พร้อมทำเครื่องหมายจุดยิงและเป้าหมายที่ยิง
- gimbal_yaw_pitch_response.png — ภาพกราฟผลลัพธ์ที่สคริปต์สร้างออกมาเพื่อดูแนวโน้มการตอบสนองของกิมบอล
- .gitignore — กำหนดไฟล์ที่ไม่ควรติด Git เช่น virtualenv, cache, และรูปภาพที่เป็น output
- requirements.txt — รายการ dependency ที่ต้องติดตั้งก่อนรันโปรเจค

## วิธีการรันโปรเจค

### 1) ตั้งค่า Python environment

เปิด PowerShell หรือ Command Prompt ในโฟลเดอร์โปรเจคแล้วทำตามขั้นตอนนี้

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

หากใช้ Git Bash หรือ bash อื่น อาจใช้คำสั่ง:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) ติดตั้ง dependency

```powershell
pip install -r requirements.txt
```

### 3) รันโค้ดบันทึกข้อมูลจาก RoboMaster

```powershell
python gimbal_pid.py
```

สิ่งที่เกิดขึ้น:
- เชื่อมต่อกับหุ่นยนต์ RoboMaster
- เริ่มบันทึกข้อมูล yaw/pitch และเวลา
- ตรวจจับ marker และยิง IR ตามลำดับเป้าหมาย
- บันทึกไฟล์ CSV เป็น `gimbal_response.csv`

> คำเตือน: การรันไฟล์นี้ต้องใช้กับหุ่นยนต์ RoboMaster จริง และมีการเชื่อมต่อเครือข่าย/สัญญาณที่พร้อมใช้งาน

### 4) รันสคริปต์เพื่อแสดงกราฟ

หลังจากมีไฟล์ CSV แล้ว ให้รัน:

```powershell
python plot_response.py
```

สิ่งที่เกิดขึ้น:
- อ่านข้อมูลจาก `gimbal_response.csv`
- วาดกราฟ yaw และ pitch แบบระบุจุดยิงแต่ละจังหวะ
- บันทึกภาพ output เป็น `gimbal_yaw_pitch_response.png`

